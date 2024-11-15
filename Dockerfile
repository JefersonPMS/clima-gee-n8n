# Use a imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie os arquivos do seu projeto para o diretório de trabalho
COPY . /app

# Atualize o pip e instale as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Defina a variável de ambiente para o arquivo de credenciais
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/ee-guiapratico4-85863bdf41f1.json"

# Exponha a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
