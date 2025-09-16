# Sistema de Avaliação de Compras Públicas Sustentáveis

## 1. Requisitos
- Python 3.12
- Git
- Docker (opcional, recomendado para evitar problemas de ambiente)

## 2. Clonando o projeto
```bash
git clone https://github.com/Felpnoo/projeto-pesquisa-tcrr.git
cd projeto-pesquisa-tcrr
```

## 3. Configurando ambiente Python (sem Docker)
```bash
cd mvp_sem_rag_openai_pkg2
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configurando variáveis de ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
Abra o arquivo `.env` e preencha sua chave Gemini em `GOOGLE_API_KEY`.

## 5. Rodando o sistema (sem Docker)
```bash
uvicorn app.main:app --reload
```
Acesse no navegador:
```
http://localhost:8000/upload-page
```

## 6. Rodando com Docker (recomendado)
Na pasta `mvp_sem_rag_openai_pkg2`:
```bash
docker build -t meuapp-gemini .
docker run --env-file .env -p 8000:8000 meuapp-gemini
```
Acesse no navegador:
```
http://localhost:8000/upload-page
```

## 7. Tutorial de uso
Veja o arquivo `Como usar o sistema passo a passo.txt` para o guia detalhado do fluxo completo (upload, busca, avaliação, validação e consolidação).

## 8. Dicas e problemas comuns
- Se aparecer erro de pacote, confira se o ambiente virtual está ativado.
- Se usar Docker, não precisa ativar venv nem instalar pacotes manualmente.
- Para dúvidas sobre o fluxo, consulte o tutorial ou peça ajuda.

---
