# Dockerfile
FROM python:3.10-slim

# 1) Default Ollama host (Docker for Mac/Windows)
ENV OLLAMA_HOST=http://host.docker.internal:11434

# 2) System deps for spaCy
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc libxml2-dev libxslt1-dev curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3) Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Download the spaCy model
RUN python -m spacy download en_core_web_sm

# 5) Your code
COPY . .

# 6) Launch your REPL
CMD ["python", "main.py"]