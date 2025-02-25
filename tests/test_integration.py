import pytest
import asyncio
import os
from Services import (
    generate_response,
    retrieve_documents,
    query_faiss_index,
    load_faiss_index,
    load_scheme_data,
)
from huggingface_hub import login
from models import QueryResponse

login(os.getenv("HUGGINGFACE_API_KEY"))  # Replace with your actual token

@pytest.mark.asyncio
async def test_generate_response():
    """Tests the generate_response function with FAISS index and scheme data retrieval."""
    
    # Load FAISS index and scheme data asynchronously
    index = await asyncio.to_thread(load_faiss_index, "faiss_index.bin")
    scheme_data = await asyncio.to_thread(load_scheme_data, "scheme_details.json")
    
    # Define input query and model
    query_text = "hello"
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

    # Query FAISS index
    indices = await asyncio.to_thread(query_faiss_index, index, query_text, embedding_model)

    # Retrieve relevant documents
    retrieved_docs = await asyncio.to_thread(retrieve_documents, indices, scheme_data)

    # Generate response
    response = await asyncio.to_thread(
        generate_response,
        retrieved_docs,
        "gemini-1.5-pro-002",
        query_text,
        os.getenv("GOOGLE_PROJECT_ID")
    )

    # Assertions (Modify as per expected results)
    assert response is  None
