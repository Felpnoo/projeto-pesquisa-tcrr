# Dockerfile para FastAPI + Gemini
FROM python:3.12-slim

WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências Python
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Uvicorn
EXPOSE 8000

# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV UPLOAD_DIR=uploads

# Comando para rodar o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
