import os
import asyncio
import json
import uvicorn
import requests
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from google.oauth2 import service_account
from models import QueryRequest


from Services import (
    load_faiss_index,
    load_scheme_data,
    query_faiss_index,
    retrieve_documents,
    generate_response,
    QueryResponse
)


load_dotenv()

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL ="https://chatbot-492327799816.asia-south1.run.app"

 # Manually load the service account credentials
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.index = await asyncio.to_thread(load_faiss_index, os.getenv("FAISS_INDEX_FILE"))
    app.state.scheme_data = await asyncio.to_thread(load_scheme_data, os.getenv("SCHEME_DETAILS_FILE"))
    app.state.embedding_model = os.getenv("EMBEDDING_MODEL")
    app.state.llm_model = os.getenv("LLM_MODEL")
    app.state.project_id = os.getenv("GOOGLE_PROJECT_ID")
    
    # Set up Telegram Webhook
    set_webhook_response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json={"url": f"{WEBHOOK_URL}/chat.telegram"})
    if not set_webhook_response.json().get("ok"):
        print("Failed to set webhook:", set_webhook_response.json())

    yield  # End of lifespan

# Initialize FastAPI App
app = FastAPI(lifespan=lifespan)

# Telegram Webhook Handler
@app.post("/chat.telegram",response_model=QueryResponse)
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_query = update["message"]["text"]

            await process_telegram_query(chat_id, user_query)

        return {"status": "ok"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Process the user query and send response

async def process_telegram_query(chat_id: int, query_text: str):
    try:
        indices = await asyncio.to_thread(
            query_faiss_index,
            app.state.index,
            query_text,
            app.state.embedding_model
        )
        
        retrieved_docs = await asyncio.to_thread(
            retrieve_documents,
            indices,
            app.state.scheme_data
        )
        
        response = await asyncio.to_thread(
            generate_response,
            retrieved_docs=retrieved_docs,
            model_name=app.state.llm_model,
            query_text=query_text,
            project_id=app.state.project_id
        )
        
        # Log the response to check its structur
        
        message = response.response_text if isinstance(response, QueryResponse) else "Sorry, I couldn't process that."
        
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
    
    except Exception as e:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": f"An error occurred! : {str(e)}"}
        )

# Fetch chat history (if needed)
@app.get("/getUpdates/")
async def fetch_chat_history():
    response = requests.get(f"{TELEGRAM_API_URL}/getUpdates")
    return response.json()

# Run Application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)