# MVP Sem RAG — Compras Sustentáveis (ChatGPT/OpenAI)

Fluxo: upload PDF → varredura por critério → avaliação LLM → validação → consolidação (escore) → relatório HTML.

## Rodando
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # coloque sua OPENAI_API_KEY e ajuste OPENAI_MODEL se quiser
uvicorn app.main:app --reload
```

## Usando Google Gemini (Generative AI)

Para usar a IA do Google Gemini, instale o pacote:

```bash
pip install google-generativeai
```

Defina as variáveis de ambiente:s, basta iniciar o app n

```bash
export LLM_PROVIDER='GOOGLE'
export GOOGLE_API_KEY='sua-chave-gemini-aqui'
export GOOGLE_MODEL='gemini-pro' # opcional
```

O app irá usar Gemini ao invés de OpenAI.

## Endpoints
- POST /upload
- POST /scan
- POST /evaluate
- POST /validate
- POST /consolidate
- POST /report
