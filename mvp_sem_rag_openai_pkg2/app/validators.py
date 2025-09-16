import re
from typing import List
from .models import CriterionResult, ValidateResponse

REGEX_ABNT = re.compile(r'(ABNT\s*(NBR|ISO)?\s*\d{3,5})|(ISO\s*\d{3,5}(-\d+)?)', re.IGNORECASE)
REGEX_NUMBER = re.compile(r'\b(\d+(?:[\.,]\d+)?)\b')

def validate_results(doc_path: str, n_paginas: int, resultados: List[CriterionResult]) -> ValidateResponse:
    erros = []
    for r in resultados:
        if r.presenca in {"sim","parcial","nao"} and len(r.evidencias) == 0:
            erros.append(f"{r.criterio}: conclusão sem evidências.")
        for ev in r.evidencias:
            if not (1 <= ev.pagina <= n_paginas):
                erros.append(f"{r.criterio}: página inválida {ev.pagina}.")
            if not ev.trecho or len(ev.trecho.strip()) < 3:
                erros.append(f"{r.criterio}: trecho de evidência vazio/curto.")
        textos = " ".join([ev.trecho for ev in r.evidencias])
        has_number = bool(REGEX_NUMBER.search(textos))
        if r.presenca == "sim" and not has_number:
            if not REGEX_ABNT.search(textos):
                erros.append(f"{r.criterio}: marcou 'sim' sem número ou norma visível.")
    return ValidateResponse(ok=len(erros)==0, erros=erros)
