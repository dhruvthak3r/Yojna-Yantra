import faiss
import generate_embeddings
import numpy as np
import json

try:

    with open("vector_embeddings.json", "r", encoding="utf-8") as f:
        text_embeddings = json.load(f)

    embeddings_array = np.array(text_embeddings).astype('float32')
    
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    index.add(embeddings_array)

    faiss.write_index(index, "faiss_index.bin")

except Exception as e:
    print(f"Error generating embeddings: {e}")