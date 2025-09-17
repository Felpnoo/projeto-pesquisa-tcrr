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

## Instruções para usuários Windows

> **Recomendação:** Use Docker para evitar problemas de ambiente no Windows.

### Usando Docker (principal)
1. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/) para Windows.
2. Abra o terminal (PowerShell ou CMD) e navegue até a pasta do projeto:
   ```powershell
   cd caminho\para\projeto-pesquisa-tcrr\mvp_sem_rag_openai_pkg2
   ```
3. Construa a imagem Docker:
   ```powershell
   docker build -t meuapp-gemini .
   ```
4. Copie o arquivo de exemplo de ambiente:
   ```powershell
   copy .env.example .env
   # Edite .env e coloque sua chave Gemini
   ```
5. Rode o container:
   ```powershell
   docker run --env-file .env -p 8000:8000 meuapp-gemini
   ```
6. Acesse no navegador:
   ```
   http://localhost:8000/upload-page
   ```

### (Opcional) Ambiente Python local
1. Instale o [Python 3.12 para Windows](https://www.python.org/downloads/windows/).
2. Crie e ative o ambiente virtual:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instale as dependências:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Copie o arquivo de exemplo:
   ```powershell
   copy .env.example .env
   # Edite .env e coloque sua chave Gemini
   ```
5. Rode o servidor:
   ```powershell
   uvicorn app.main:app --reload
   ```
6. Acesse no navegador:
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
