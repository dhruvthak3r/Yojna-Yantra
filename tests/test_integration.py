from sentence_transformers import SentenceTransformer
from Services import query_faiss_index,load_faiss_index

index = load_faiss_index("faiss_index.bin")

indices = query_faiss_index(index, "hello", "sentence-transformers/all-MiniLM-L6-v2")

assert indices is not None