from Services import query_faiss_index, load_faiss_index

def test_faiss_query():
    index = load_faiss_index("faiss_index.bin")
    indices = query_faiss_index(index, "hello", "sentence-transformers/all-MiniLM-L6-v2")
    assert indices is not None
