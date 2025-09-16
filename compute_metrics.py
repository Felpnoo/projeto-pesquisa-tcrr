#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_metrics.py
Lê: rotulos_ouro.csv (ouro), baseline.csv, outputs/*/resultados.json e outputs/summary.csv
Gera: T1_F1.csv, T2_coverage.csv, T3_mae.csv e gráficos simples.
Uso:
  python compute_metrics.py --root . --gold rotulos_ouro.csv --outputs outputs --baseline baseline.csv --pesos pesos.json
"""

import argparse, os, json, glob, math
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_gold(path_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(path_csv, dtype=str).fillna("")
    # normaliza
    df["criterio"] = df["criterio"].str.strip().str.lower()
    df["presenca_gold"] = df["presenca"].str.strip().str.lower()
    keep = ["doc_id","criterio","presenca_gold","paginas_evidencia","observacoes","orgao","data","uf","risco_greenwashing"]
    for col in keep:
        if col not in df.columns:
            df[col] = ""
    return df[keep]

def try_load_mvp_results(outputs_dir: Path) -> pd.DataFrame:
    # Tenta ler mvp_results.csv; se não houver, varre resultados.json em outputs/<doc_id>/resultados.json
    csv_path = outputs_dir / "mvp_results.csv"
    rows = []
    if csv_path.exists():
        df = pd.read_csv(csv_path, dtype=str).fillna("")
        # Esperado: doc_id, criterio, presenca_mvp, evidencias_count (opcional)
        if "evidencias_count" not in df.columns:
            df["evidencias_count"] = ""
        df["criterio"] = df["criterio"].str.lower()
        return df[["doc_id","criterio","presenca_mvp","evidencias_count"]]
    # fallback: parseia jsons
    for res_path in outputs_dir.glob("**/resultados.json"):
        doc_id = res_path.parent.name
        try:
            data = json.loads(res_path.read_text(encoding="utf-8"))
            # data é lista de objetos por critério
            for obj in data:
                criterio = str(obj.get("criterio","")).strip().lower()
                presenca = str(obj.get("presenca","")).strip().lower()
                evid = obj.get("evidencias", []) or []
                rows.append({
                    "doc_id": doc_id,
                    "criterio": criterio,
                    "presenca_mvp": presenca,
                    "evidencias_count": len(evid)
                })
        except Exception as e:
            print(f"[WARN] falha ao ler {res_path}: {e}")
    if not rows:
        print("[WARN] Nenhum resultado MVP encontrado em outputs/")
    return pd.DataFrame(rows, columns=["doc_id","criterio","presenca_mvp","evidencias_count"]).fillna("")

def try_load_baseline(path_csv: Path) -> pd.DataFrame:
    if not path_csv.exists():
        print("[WARN] baseline.csv não encontrado; métricas do baseline serão omitidas.")
        return pd.DataFrame(columns=["doc_id","criterio","presenca_baseline"])
    df = pd.read_csv(path_csv, dtype=str).fillna("")
    df["criterio"] = df["criterio"].str.strip().str.lower()
    df["presenca_baseline"] = df["presenca_baseline"].str.strip().str.lower()
    return df[["doc_id","criterio","presenca_baseline"]]

def try_load_summary(outputs_dir: Path) -> pd.DataFrame:
    path = outputs_dir / "summary.csv"
    if not path.exists():
        print("[INFO] outputs/summary.csv não encontrado; escore MVP será recalculado a partir dos resultados por critério.")
        return pd.DataFrame(columns=["doc_id","escore_aderencia"])
    df = pd.read_csv(path, dtype=str).fillna("")
    # tenta converter para float
    if "escore_aderencia" in df.columns:
        try:
            df["escore_aderencia"] = df["escore_aderencia"].astype(float)
        except Exception:
            pass
    return df

SCORE_MAP = {"sim": 1.0, "parcial": 0.5, "nao": 0.0, "insuficiente": 0.0}

def compute_human_scores(gold: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    rows = []
    for (doc_id), g in gold.groupby("doc_id"):
        total_w = 0.0
        acc = 0.0
        for _, r in g.iterrows():
            criterio = r["criterio"]
            w = float(pesos.get(criterio, 0.0))
            total_w += w
            acc += w * SCORE_MAP.get(r["presenca_gold"], 0.0)
        score = 0.0 if total_w == 0 else 100.0 * acc / total_w
        rows.append({"doc_id": doc_id, "escore_humano": round(score, 2)})
    return pd.DataFrame(rows)

def compute_scores_from_preds(preds: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    rows = []
    for (doc_id), g in preds.groupby("doc_id"):
        total_w = 0.0
        acc = 0.0
        for _, r in g.iterrows():
            criterio = r["criterio"]
            w = float(pesos.get(criterio, 0.0))
            total_w += w
            acc += w * SCORE_MAP.get(r["presenca_mvp"], 0.0)
        score = 0.0 if total_w == 0 else 100.0 * acc / total_w
        rows.append({"doc_id": doc_id, "escore_mvp_calc": round(score, 2)})
    return pd.DataFrame(rows)

def f1_macro(y_true: list, y_pred: list, labels=("sim","parcial","nao")) -> float:
    # F1 macro entre sim/parcial/nao (ignora "insuficiente")
    def f1_for_label(lbl):
        tp = sum((yt==lbl) and (yp==lbl) for yt, yp in zip(y_true, y_pred))
        fp = sum((yt!=lbl) and (yp==lbl) for yt, yp in zip(y_true, y_pred))
        fn = sum((yt==lbl) and (yp!=lbl) for yt, yp in zip(y_true, y_pred))
        if tp == 0 and (fp>0 or fn>0):
            return 0.0
        if tp == 0 and fp == 0 and fn == 0:
            return 0.0
        prec = tp / (tp + fp) if (tp+fp)>0 else 0.0
        rec  = tp / (tp + fn) if (tp+fn)>0 else 0.0
        if prec+rec == 0:
            return 0.0
        return 2*prec*rec/(prec+rec)
    vals = [f1_for_label(lbl) for lbl in labels]
    return float(np.mean(vals))

def build_t1_f1(gold: pd.DataFrame, preds: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    # Merge para cada critério e doc
    m = gold.merge(preds, on=["doc_id","criterio"], how="inner")
    # Filtra classes alvo
    m = m[m["presenca_gold"].isin(["sim","parcial","nao"])]
    rows = []
    for criterio, g in m.groupby("criterio"):
        y_true = g["presenca_gold"].tolist()
        y_mvp  = g["presenca_mvp"].tolist()
        f1_mvp = f1_macro(y_true, y_mvp)
        # baseline
        if not baseline.empty:
            b = g.merge(baseline, on=["doc_id","criterio"], how="left")
            y_base = b["presenca_baseline"].fillna("nao").tolist()
            f1_base = f1_macro(y_true, y_base)
        else:
            f1_base = np.nan
        rows.append({"criterio": criterio, "F1_mvp": round(f1_mvp,3), "F1_baseline": (round(f1_base,3) if not math.isnan(f1_base) else "") , "n": len(g)})
    # GERAL
    if len(m)>0:
        y_true = m["presenca_gold"].tolist()
        y_mvp  = m["presenca_mvp"].tolist()
        f1_mvp = f1_macro(y_true, y_mvp)
        if not baseline.empty:
            mm = m.merge(baseline, on=["doc_id","criterio"], how="left")
            y_base = mm["presenca_baseline"].fillna("nao").tolist()
            f1_base = f1_macro(y_true, y_base)
        else:
            f1_base = np.nan
        rows.append({"criterio":"GERAL","F1_mvp": round(f1_mvp,3), "F1_baseline": (round(f1_base,3) if not math.isnan(f1_base) else ""), "n": len(m)})
    return pd.DataFrame(rows)

def build_t2_coverage(preds: pd.DataFrame) -> pd.DataFrame:
    p = preds.copy()
    p["need_citation"] = p["presenca_mvp"].apply(lambda x: x in ["sim","parcial","nao"])
    p["has_citation"] = p["evidencias_count"].astype(str).replace({"": "0"}).astype(int) >= 1
    total_need = int(p["need_citation"].sum())
    total_has  = int((p["need_citation"] & p["has_citation"]).sum())
    coverage = 0.0 if total_need==0 else 100.0 * total_has / total_need
    return pd.DataFrame([{
        "total_conclusoes_com_citacao_necessaria": total_need,
        "total_conclusoes_com_citacao_presente": total_has,
        "coverage_percent": round(coverage,2)
    }])

def build_t3_mae(gold: pd.DataFrame, preds: pd.DataFrame, summary: pd.DataFrame, pesos: dict, out_dir: Path) -> pd.DataFrame:
    dh = compute_human_scores(gold, pesos)  # escore_humano
    if "escore_aderencia" in summary.columns and summary.shape[0]>0:
        dm = summary[["doc_id","escore_aderencia"]].copy()
        # Garante float
        dm["escore_aderencia"] = pd.to_numeric(dm["escore_aderencia"], errors="coerce")
        dm = dm.rename(columns={"escore_aderencia":"escore_mvp"})
    else:
        dm_calc = compute_scores_from_preds(preds, pesos)
        dm = dm_calc.rename(columns={"escore_mvp_calc":"escore_mvp"})
    m = dh.merge(dm, on="doc_id", how="inner")
    m["erro_abs"] = (m["escore_humano"] - m["escore_mvp"]).abs()
    mae = m["erro_abs"].mean() if len(m)>0 else np.nan
    # Salva também um CSV por doc
    m_sorted = m.sort_values("erro_abs", ascending=False)
    return m_sorted, mae

def plot_bar(df: pd.DataFrame, xcol: str, ycols: list, title: str, png_path: Path):
    plt.figure()
    # Sem cores definidas, um eixo por coluna lado a lado
    idx = np.arange(len(df))
    width = 0.35
    if len(ycols) == 2:
        plt.bar(idx - width/2, df[ycols[0]].astype(float).values, width, label=ycols[0])
        plt.bar(idx + width/2, df[ycols[1]].astype(float).values, width, label=ycols[1])
        plt.xticks(idx, df[xcol].tolist(), rotation=45, ha="right")
        plt.title(title)
        plt.legend()
    else:
        plt.bar(idx, df[ycols[0]].astype(float).values, width)
        plt.xticks(idx, df[xcol].tolist(), rotation=45, ha="right")
        plt.title(title)
    plt.tight_layout()
    plt.savefig(png_path, dpi=160)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Pasta raiz do projeto")
    ap.add_argument("--gold", default="rotulos_ouro.csv", help="CSV com rótulos ouro")
    ap.add_argument("--outputs", default="outputs", help="Pasta de saídas do MVP")
    ap.add_argument("--baseline", default="baseline.csv", help="CSV do baseline")
    ap.add_argument("--pesos", default="pesos.json", help="Arquivo JSON com pesos por critério")
    ap.add_argument("--outdir", default="metrics_out", help="Pasta para salvar as tabelas/figuras")
    args = ap.parse_args()

    root = Path(args.root)
    out_dir = root / args.outdir
    out_dir.mkdir(parents=True, exist_ok=True)

    gold = load_gold(root / args.gold)
    preds = try_load_mvp_results(root / args.outputs)
    baseline = try_load_baseline(root / args.baseline)
    summary = try_load_summary(root / args.outputs)
    pesos = {}
    if (root / args.pesos).exists():
        try:
            pesos = json.loads((root/args.pesos).read_text(encoding="utf-8"))
        except Exception as e:
            print("[WARN] falha ao ler pesos.json, usando default vazio:", e)

    # T1: F1 por critério e geral
    t1 = build_t1_f1(gold, preds, baseline)
    t1_path = out_dir / "T1_F1.csv"
    t1.to_csv(t1_path, index=False)

    # T2: Coverage de citação do MVP
    t2 = build_t2_coverage(preds)
    t2_path = out_dir / "T2_coverage.csv"
    t2.to_csv(t2_path, index=False)

    # T3: MAE de escore (doc-level)
    t3_docs, mae = build_t3_mae(gold, preds, summary, pesos, out_dir)
    t3_path = out_dir / "T3_mae.csv"
    t3_docs.to_csv(t3_path, index=False)
    mae_path = out_dir / "T3_mae_overall.txt"
    mae_path.write_text(f"MAE: {mae:.3f}\n", encoding="utf-8")

    # Gráficos (opcionais, simples)
    try:
        if not t1.empty:
            # Remove linha GERAL para o gráfico por critério
            t1_plot = t1[t1["criterio"] != "GERAL"].copy()
            # Preenche F1_baseline vazio com NaN
            t1_plot["F1_baseline"] = pd.to_numeric(t1_plot["F1_baseline"], errors="coerce")
            t1_plot["F1_mvp"] = pd.to_numeric(t1_plot["F1_mvp"], errors="coerce")
            plot_bar(t1_plot, "criterio", ["F1_mvp","F1_baseline"], "F1 por critério (MVP vs Baseline)", out_dir / "fig_F1.png")
        if not t3_docs.empty:
            # Top 15 piores erros
            top = t3_docs.head(15)[["doc_id","erro_abs"]].copy()
            plot_bar(top, "doc_id", ["erro_abs"], "Erro absoluto por documento (Top 15)", out_dir / "fig_MAE.png")
    except Exception as e:
        print("[WARN] falha ao gerar gráficos:", e)

    print("Arquivos gerados em:", out_dir.resolve())
    print(" -", t1_path.name, "|", t2_path.name, "|", t3_path.name, "|", mae_path.name)
    print("Figuras (se geradas): fig_F1.png, fig_MAE.png")

if __name__ == "__main__":
    main()
