from fastapi import FastAPI, HTTPException
from pydantic import  BaseModel
from contextlib import asynccontextmanager
import os
import asyncio
from dotenv import load_dotenv
from rag_pipeline.Services import (
    load_faiss_index,
    load_scheme_data,
    query_faiss_index,
    retrieve_documents,
    generate_response,
    QueryResponse
)

load_dotenv()

class QueryRequest(BaseModel):
    query_text: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load resources at startup
    app.state.index = await asyncio.to_thread(load_faiss_index, "faiss_index.bin")
    app.state.scheme_data = await asyncio.to_thread(load_scheme_data, "scheme_details.json")
    app.state.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    app.state.llm_model = "gemini-1.5-pro-002"
    app.state.project_id = os.getenv("GOOGLE_PROJECT_ID")
    yield
    # Clean up resources if needed
    app.state.index.reset()
    del app.state.index
    del app.state.scheme_data

app = FastAPI(lifespan=lifespan)

@app.post("/query/", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    try:
        # Process query through the pipeline
        indices = await asyncio.to_thread(
            query_faiss_index,
            app.state.index,
            request.query_text,
            app.state.embedding_model
        )
        
        retrieved_docs = await asyncio.to_thread(
            retrieve_documents,
            indices,
            app.state.scheme_data
        )
        
        response = await asyncio.to_thread(
            generate_response,
            retrieved_docs,
            app.state.llm_model,
            request.query_text,
            app.state.project_id
        )
        
        return response.content
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)