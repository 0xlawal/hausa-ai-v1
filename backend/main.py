from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import uvicorn
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "Hausa AI Backend Running"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        logger.info(f"Received: {request.message}")
        # Use client with 5‑minute timeout
        client = ollama.Client(host="http://localhost:11434", timeout=300.0)
        response = client.chat(
            model="hausa-ai",
            messages=[{"role": "user", "content": request.message}],
            stream=False,
            options={"num_predict": 256, "temperature": 0.7, "top_p": 0.9}
        )
        bot_response = response["message"]["content"]
        logger.info(f"Response: {bot_response[:100]}...")
        return {"response": bot_response, "status": "success"}
    except httpx.TimeoutException:
        logger.error("Ollama timed out")
        return {"response": "Model took too long. Try a shorter question.", "status": "error"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"response": f"Error: {str(e)}", "status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=300)