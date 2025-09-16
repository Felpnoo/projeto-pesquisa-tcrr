import os, json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv
from pathlib import Path

from .models import (
    ScanRequest, ScanResponse,
    EvaluateRequest, CriterionResult,
    ValidateRequest, ValidateResponse,
    ConsolidateRequest, Consolidated, ReportRequest
)
from .utils_pdf import n_pages, extract_text_by_page
from .validators import validate_results
from .aggregator import consolidate
from .report import render_report_html
from .llm_client import LLMClient

load_dotenv()
app = FastAPI(title="MVP Sem RAG — Compras Sustentáveis")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR","uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

llm = LLMClient()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        f.write(await file.read())
    return {"doc_path": str(dest.resolve())}

@app.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    texts = extract_text_by_page(req.doc_path)
    scores = []
    keys = [k.lower() for k in req.palavras_chave] if req.palavras_chave else []
    for p, t in texts.items():
        tl = (t or "").lower()
        score = sum(tl.count(k) for k in keys) if keys else 0
        if score > 0:
            scores.append((p, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    pages = [p for p,_ in scores][:req.max_paginas]
    with_context = set()
    for p in pages:
        for d in range(-req.contexto, req.contexto+1):
            if 1 <= p + d <= len(texts):
                with_context.add(p+d)
    ordered = sorted(with_context) if with_context else pages
    return ScanResponse(criterio=req.criterio, paginas=ordered)

@app.post("/evaluate", response_model=CriterionResult)
def evaluate(req: EvaluateRequest):
    texts = extract_text_by_page(req.doc_path)
    doc_name = Path(req.doc_path).name
    parts = []
    for p in req.paginas:
        content = texts.get(p, "")
        parts.append(f"--- INICIO_PAGINA {p} ---\n{content}\n--- FIM_PAGINA {p} ---")
    conteudo = "\n\n".join(parts)
    prompt_tpl = (Path(__file__).parent / "prompts" / "evaluate_prompt.txt").read_text(encoding="utf-8")
    prompt = prompt_tpl.format(criterio=req.criterio, conteudo_paginas=conteudo, doc_name=doc_name)
    out = llm.complete_json(prompt, system="Responda apenas com JSON válido compatível com o schema.")
    data = json.loads(out)
    return CriterionResult(**data)

@app.post("/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest):
    return validate_results(req.doc_path, req.n_paginas, req.resultados)

@app.post("/consolidate", response_model=Consolidated)
def consolidate_endpoint(req: ConsolidateRequest):
    return consolidate(req.doc_id, req.resultados, req.pesos or None)

@app.post("/report")
def report(req: ReportRequest):
    out_path = Path("relatorio.html")
    render_report_html(req.consolidated, str(out_path))
    return FileResponse(str(out_path), filename="relatorio.html", media_type="text/html")

@app.get("/upload-page", response_class=HTMLResponse)
def upload_page():
    html_path = Path(__file__).parent / "templates" / "upload.html"
    return html_path.read_text(encoding="utf-8")
