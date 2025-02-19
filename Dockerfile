# Build Stage (Installing dependencies in a virtual environment)
FROM python:3.11-slim AS builder
WORKDIR /app

# Install dependencies
COPY requirements.txt . 
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final Stage (Small Image)
FROM python:3.11-slim
WORKDIR /app

# Create a non-root user
RUN useradd -m myuser
USER myuser

# Copy virtual environment from the builder stage
COPY --from=builder /app/venv /app/venv

# Ensure the virtual environment is used
ENV PATH="/app/venv/bin:$PATH"

# Install Uvicorn explicitly
RUN pip install --no-cache-dir uvicorn

# Copy the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Start FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
