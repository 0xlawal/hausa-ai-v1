from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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
        # Dummy responses for production (Render doesn't have Ollama)
        hausa_responses = {
            "sannu": "Sannu! Ina kwana kuma tsoron, godiya.",
            "ina kwana": "Ina gida ne, na giji. Me ke faruwa?",
            "yaya lafiya": "Lafiya lau, godiya ne kasuwa.",
            "shi ne": "Kai, shi ne gida nai.",
            "hello": "Sannu! Welcome to Hausa AI.",
        }
        
        message_lower = request.message.lower().strip()
        
        # Check if message matches any response
        for key, response in hausa_responses.items():
            if key in message_lower:
                return {
                    "response": response,
                    "status": "success"
                }
        
        # Default response
        default_response = f"You said: '{request.message}'. This is V1 (demo mode). Try: Sannu, ina kwana, yaya lafiya"
        return {
            "response": default_response,
            "status": "success"
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "status": "error"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)