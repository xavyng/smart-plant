FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

COPY backend/ ./backend/
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
