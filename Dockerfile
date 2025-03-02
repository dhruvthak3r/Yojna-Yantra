
FROM python:3.11-slim AS builder
WORKDIR /app


COPY requirements.txt . 
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim
WORKDIR /app


RUN useradd -m myuser
USER myuser


COPY --from=builder /app/venv /app/venv

COPY . .


EXPOSE 8000


CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
