# Use a imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie os arquivos do seu projeto para o diretório de trabalho
COPY . /app

# Atualize o pip e instale as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instale o Google Cloud SDK para acessar o Secret Manager
RUN apt-get update && apt-get install -y curl

# Baixe o segredo do Secret Manager e salve como arquivo de credenciais
RUN curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    "https://secretmanager.googleapis.com/v1/projects/152190816099/secrets/senha-gee/versions/latest:access" \
    --output /app/ee-guiapratico4-85863bdf41f1.json

# Defina a variável de ambiente para o arquivo de credenciais
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/ee-guiapratico4-85863bdf41f1.json"

# Exponha a porta 8080 (necessário para o Cloud Run)
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]