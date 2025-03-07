from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    char_id : int
    query_text: str

class QueryResponse(BaseModel):
    response_text: str
    documents: List[dict]
