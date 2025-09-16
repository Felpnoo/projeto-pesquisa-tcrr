from typing import Dict
import pdfplumber
from pypdf import PdfReader

def n_pages(path: str) -> int:
    try:
        with pdfplumber.open(path) as pdf:
            return len(pdf.pages)
    except Exception:
        reader = PdfReader(path)
        return len(reader.pages)

def extract_text_by_page(path: str) -> Dict[int, str]:
    texts = {}
    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                texts[i] = page.extract_text() or ""
        return texts
    except Exception:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages, start=1):
            try:
                texts[i] = page.extract_text() or ""
            except Exception:
                texts[i] = ""
        return texts
