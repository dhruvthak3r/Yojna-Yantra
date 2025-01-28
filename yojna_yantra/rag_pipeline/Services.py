import os
import json
import numpy as np
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
import faiss
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from google.auth.exceptions import DefaultCredentialsError
from pydantic import BaseModel

class QueryResponse(BaseModel):
    response_text: str
    documents: list[dict]

def load_faiss_index(index_file):
    return faiss.read_index(index_file)

def load_scheme_data(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)

def query_faiss_index(index, query_text, model_name):
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    hf_embeddings = HuggingFaceEndpointEmbeddings(
        model=model_name,
        task="feature-extraction",
        huggingfacehub_api_token=api_key,
    )
    
    query_embedding = hf_embeddings.embed_documents([query_text])
    query_embedding = np.array(query_embedding).astype('float32')
    
    D, I = index.search(query_embedding, k=5)
    return I

def retrieve_documents(indices, scheme_data):
    documents = []
    for idx in indices[0]:
        document = scheme_data[idx]
        scheme_info = {
            "title": document.get("name", "No Title"),
            "details": document.get("details", "No Description"),
            "url": document.get("url", "No URL")
        }
        documents.append(scheme_info)
    return documents

def generate_response(retrieved_docs, model_name, query_text, project_id):
    try:
        llm = ChatVertexAI(
            model=model_name,
            temperature=0.7,
            max_tokens=None,
            max_retries=6,
            stop=None,
            project=project_id
        )

        prompt = ChatPromptTemplate([
            ("system", "You are an empathetic AI assistant for assisting users about information about various government welfare schemes in Maharashtra. Answer only factually with the information provided below. It is critical for answers to be correct and precise. Make responses short and to the point."),
            ("human", "{user_input}"),
        ])

        prompt_value = prompt.invoke({"user_input": query_text})
        response = llm.invoke(input=prompt_value)

        return QueryResponse(
            response_text=response.content,
            documents=retrieved_docs
        )
    except DefaultCredentialsError as e:
        raise RuntimeError("Google Cloud credentials not found") from e