# Stage 1 - Build dependencies
FROM python:3.11-slim AS build

# Create a non-root user
RUN useradd --create-home builder
WORKDIR /home/builder
USER builder

# Create virtual environment
RUN python -m venv /home/builder/venv
ENV PATH="/home/builder/venv/bin:$PATH"

# Install dependencies
COPY --chown=builder:builder requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary app files
COPY --chown=builder:builder . /home/builder/rag_pipeline

# Stage 2 - Final lightweight image
FROM python:3.11-slim AS final

RUN useradd --create-home builder
WORKDIR /home/builder
USER builder

# Copy venv from build stage
COPY --from=build --chown=builder:builder /home/builder/venv /home/builder/venv
ENV PATH="/home/builder/venv/bin:$PATH"

# Copy application files (only needed ones)
COPY --from=build --chown=builder:builder /home/builder/rag_pipeline /home/builder/rag_pipeline

WORKDIR /home/builder/rag_pipeline

# Expose the correct port for Cloud Run
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
