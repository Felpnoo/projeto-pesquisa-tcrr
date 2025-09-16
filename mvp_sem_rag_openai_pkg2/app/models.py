from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

Presence = Literal["sim", "parcial", "nao", "insuficiente"]
Risk = Literal["baixo", "medio", "alto"]

class ScanRequest(BaseModel):
    doc_path: str = Field(..., description="Caminho do PDF no servidor")
    criterio: str
    palavras_chave: List[str] = Field(default_factory=list)
    max_paginas: int = 6
    contexto: int = 1  # páginas antes/depois

class ScanResponse(BaseModel):
    criterio: str
    paginas: List[int]

class EvaluateRequest(BaseModel):
    doc_path: str
    criterio: str
    paginas: List[int]

class Evidence(BaseModel):
    doc: str
    pagina: int
    trecho: str

class CriterionResult(BaseModel):
    criterio: str
    presenca: Presence
    risco_greenwashing: Risk
    evidencias: List[Evidence] = Field(default_factory=list)
    observacoes: Optional[str] = ""

class ValidateRequest(BaseModel):
    doc_path: str
    n_paginas: int
    resultados: List[CriterionResult]

class ValidateResponse(BaseModel):
    ok: bool
    erros: List[str] = Field(default_factory=list)

class ConsolidateRequest(BaseModel):
    doc_id: str
    orgao: Optional[str] = ""
    modalidade: Optional[str] = ""
    data: Optional[str] = ""  # YYYY-MM-DD
    pesos: Dict[str, float] = Field(default_factory=dict)  # criterio -> peso
    resultados: List[CriterionResult]

class Consolidated(BaseModel):
    doc_id: str
    escore_aderencia: float
    flags: Dict[str, List[str]]
    resultados: List[CriterionResult]

class ReportRequest(BaseModel):
    consolidated: Consolidated
