# Use a imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie os arquivos do seu projeto para o diretório de trabalho
COPY . /app

# Atualize o pip e instale as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salve o conteúdo da variável de ambiente como arquivo de credenciais
RUN echo "${GOOGLE_APPLICATION_CREDENTIALS}" > /app/ee-guiapratico4-85863bdf41f1.json

# Defina a variável de ambiente para o arquivo de credenciais
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/ee-guiapratico4-85863bdf41f1.json"

# Exponha a porta 8080 (necessário para o Cloud Run)
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]