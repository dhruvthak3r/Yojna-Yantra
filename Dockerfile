FROM python:3.11-slim AS builder
WORKDIR /app

# Copy requirements and install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim
WORKDIR /app

# Create a non-root user
RUN useradd -m myuser
USER myuser
# Copy the virtual environment and set correct ownership
COPY --from=builder --chown=myuser:myuser /app/venv /app/venv

# Copy application files and ensure proper ownership
COPY --chown=myuser:myuser . .

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]