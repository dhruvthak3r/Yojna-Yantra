FROM Python:3.11 AS build

RUN useradd --create-home builder
WORKDIR /home/builder
USER builder

RUN python -m venv venv
ENV PATH="/home/builder/venv/bin:$PATH"

COPY --chown=builder:builder requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=builder:builder rag_pipeline/ ./rag_pipeline/

FROM Python:3.11 AS final

RUN useradd --create-home builder
WORKDIR /home/builder
USER builder

COPY --from=build --chown=builder:builder /home/builder/venv /home/builder/venv
ENV PATH="/home/builder/venv/bin:$PATH"

COPY --from=build --chown=builder:builder /home/builder/rag_pipeline /home/builder/rag_pipeline

WORKDIR /home/builder/rag_pipeline

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
