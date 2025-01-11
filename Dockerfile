# Use a imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie os arquivos do projeto para o diretório de trabalho
COPY . /app

# Atualize o pip e instale as dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta 8080 (necessário para o Cloud Run)
EXPOSE 8080

# Comando para iniciar a aplicação, criando o arquivo de credenciais no runtime
CMD ["/bin/sh", "-c", "echo \"$GOOGLE_APPLICATION_CREDENTIALS\" > /app/ee-guiapratico4-85863bdf41f1.json && uvicorn main:app --host 0.0.0.0 --port 8080"]
