from typing import Dict, List
from .models import CriterionResult, Consolidated

DEFAULT_WEIGHTS = {
    "eficiencia_energetica": 0.25,
    "normas_tecnicas": 0.20,
    "emissoes": 0.20,
    "uso_de_agua": 0.15,
    "materiais_reciclabilidade": 0.10,
    "rotulagem": 0.10,
}

SCORE_MAP = {"sim":1.0, "parcial":0.5, "nao":0.0, "insuficiente":0.0}

def consolidate(doc_id: str, resultados: List[CriterionResult], pesos: Dict[str, float] | None = None) -> Consolidated:
    pesos = pesos or DEFAULT_WEIGHTS
    total = 0.0
    used = 0.0
    flags_gw = []
    insuficientes = []

    for r in resultados:
        w = pesos.get(r.criterio, 0.0)
        s = SCORE_MAP.get(r.presenca, 0.0)
        total += w * s
        used += w
        if r.risco_greenwashing == "alto":
            flags_gw.append(r.criterio)
        if r.presenca == "insuficiente":
            insuficientes.append(r.criterio)

    escore = 0.0 if used == 0 else round(100 * total / used, 2)
    return Consolidated(
        doc_id=doc_id,
        escore_aderencia=escore,
        flags={"greenwashing_alto": flags_gw, "itens_insuficientes": insuficientes},
        resultados=resultados
    )
