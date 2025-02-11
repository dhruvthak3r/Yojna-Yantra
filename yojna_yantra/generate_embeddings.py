import os
import json
import Scrape
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
import numpy as np

def extract_relevant_fields(scheme):
    combined_text = f"""
    Name: {scheme['name']}
    Details: {scheme['details']}
    Benefits: {scheme['benefits']}
    Eligibility: {scheme['eligibility']}
    Application Process: {scheme['application_process']}
    Documents Required: {scheme['documents_required']}
    """
    return combined_text

def generate_embeddings():
    with open("scheme_details.json", "r", encoding="utf-8") as f:
        data_set = json.load(f)

    texts = [extract_relevant_fields(scheme) for scheme in data_set]

    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    hf_embeddings = HuggingFaceEndpointEmbeddings(
        model=model_name,
        task="feature-extraction",
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
    )

    try:
        text_embeddings = hf_embeddings.embed_documents(texts)

        with open("vector_embeddings.json", "w", encoding="utf-8") as f:
            json.dump(text_embeddings, f, ensure_ascii=False, indent=4)
        
        return text_embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

if __name__ == "__main__":
    generate_embeddings()
