# Boss Assistant — deploy anywhere (Railway, Fly.io, Docker, etc.)
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code (exclude .env, tokens via .dockerignore or copy only what's needed)
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD sh -c 'uvicorn chat_server:app --host 0.0.0.0 --port ${PORT}'
