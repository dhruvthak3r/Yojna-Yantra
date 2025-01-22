import os
import json
import numpy as np
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
import faiss
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from google.auth.exceptions import DefaultCredentialsError
from dotenv import load_dotenv

load_dotenv()

# Step 2: Load FAISS Index
def load_faiss_index(index_file):
    index = faiss.read_index(index_file)
    return index

# Step 3: Query FAISS Index
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

# Step 4: Retrieve Relevant Documents
def retrieve_documents(indices, data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    for idx in indices[0]:  # Assuming indices is a 2D array
        document = data[idx]
        scheme_info = {
            "title": document.get("name", "No Title"),
            "details": document.get("details", "No Description"),
            "url": document.get("url", "No URL")
            
        }
        documents.append(scheme_info)
    
    return documents

# Step 5: Generate Response
def generate_response(retrieved_docs, model_name, query_text, project_id):
    llm = ChatVertexAI(
        model=model_name,
        temperature=0.7,
        max_tokens=None,
        max_retries=6,
        stop=None,
        project=project_id  # Pass the project ID here
    )

    prompt = ChatPromptTemplate([
        ("system", "You are an empathetic AI assistant for assisting users about information about various government welfare schemes in Maharashtra. Answer only factually with the information provided below. It is critical for answers to be correct and precise. Make responses short and to the point."),
        ("human", "{user_input}"),
    ])

    prompt_value = prompt.invoke({
        "user_input": query_text,
    })

    response = llm.invoke(input=prompt_value)  # Corrected argument name

    # Format the response to include the URLs from retrieved_docs
    formatted_docs = "\n\n".join(
        f"Title: {doc['title']}\nDetails: {doc['details']}\nURL: {doc['url']}"
        for doc in retrieved_docs
    )

    formatted_response = {
        "response_text": response.content,
        "documents": formatted_docs
    }

    return formatted_response

if __name__ == "__main__": 
    index_file = "faiss_index.bin"
    data_file = "scheme_details.json"
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model_name = "gemini-1.5-pro-002"  # Replace with the actual model name
    project_id = "loyal-throne-448413-c8"  # Your Google Cloud project ID

    try:
        # Load FAISS index
        index = load_faiss_index(index_file)
        
        # Query FAISS index
        query_text = "have you got any idea about Pradhan Mantri Kaushal Vikas Yojana?"
        indices = query_faiss_index(index, query_text, model_name)
        
        # Retrieve relevant documents
        retrieved_docs = retrieve_documents(indices, data_file)
        
        # Generate response
        response = generate_response(retrieved_docs, llm_model_name, query_text, project_id)
        print(response)
    except DefaultCredentialsError as e:
        print("Error: Google Cloud credentials not found. Please set up your credentials correctly.")
        print(e)

# Example usage of GOOGLE_API_KEY
google_api_key = os.getenv('GOOGLE_API_KEY')