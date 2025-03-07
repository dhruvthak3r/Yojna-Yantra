import os
import json
import numpy as np
import faiss
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from sentence_transformers import SentenceTransformer

from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from models import QueryResponse

def load_faiss_index(index_file):
    return faiss.read_index(index_file)

def load_scheme_data(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)

def query_faiss_index(index, query_text, model_name):
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query_text])  # Returns a NumPy array

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
            "url": document.get("url", "No URL"),
            "benefits" : document.get("benefits","No benefits"),
            "eligiblity" : document.get("eligiblity","No eligiblity"),
            "application-process" : document.get("application_process","no application-process"),
            "documents-required" : document.get("documents_required","no documents-required"),
        }

        documents.append(scheme_info)
    return documents
def generate_response(retrieved_docs, model_name, query_text, project_id):
    try:
        #Format retrieved documents into a context string
        context = "\n\n".join(
            f"Title: {doc['title']}\nDetails: {doc['details']}\nURL: {doc['url']}"
            for doc in retrieved_docs
        )

        llm = ChatVertexAI(
            model=model_name,
            temperature=0.7,
            max_tokens=512,
            max_retries=6,
            project=project_id,
            chat_history = []
        )

        prompt = ChatPromptTemplate.from_messages([ 
            ("system", "You are an AI assistant for government welfare schemes. "
                       "Use ONLY the following information to answer and provide the url for the scheme(s) from the documents fetched and also format the message properly so that it is readable by the users,make sure users get the best possible experience with your responses. Keep answers precise and factual.\n\n"
                       "Relevant Documents:\n{context}"),
            ("human", "Question: {query}")
        ])

        # Format prompt with both context and query
        prompt_value = prompt.invoke({
            "context": context,
            "query": query_text
        })

        response = llm.invoke(prompt_value)
        
        return QueryResponse(
            response_text=response.content,
            documents=retrieved_docs
        )
    except Exception as e:
        raise RuntimeError(f"An error occurred while generating response: {str(e)}")
