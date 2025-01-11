# Use a imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto
COPY . /app

# Atualize o pip e instale as dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta necessária pelo Cloud Run
EXPOSE 8080

# Crie o arquivo de credenciais no runtime e inicie a aplicação
CMD ["/bin/sh", "-c", "echo \"$GOOGLE_APPLICATION_CREDENTIALS\" > /app/credentials.json && uvicorn main:app --host 0.0.0.0 --port 8080"]
