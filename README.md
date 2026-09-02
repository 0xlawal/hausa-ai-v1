# Chat Application

A modern chat application with FastAPI backend and React frontend, powered by local Ollama LLM.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama installed and running locally

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Ollama (if not already running):
```bash
ollama serve
```

5. Pull a model (if not already available):
```bash
ollama pull llama3.2
```

6. Run the backend:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Endpoints

- `POST /chat` - Send a message and get AI response
- `GET /health` - Check API and Ollama health status
- `GET /conversations/{id}` - Retrieve conversation history
- `DELETE /conversations/{id}` - Delete a conversation

## Configuration

### Backend
- Ollama URL: `http://localhost:11434` (configured in `main.py`)
- Default model: `llama3.2` (adjust `OLLAMA_MODEL` variable as needed)
- CORS origins: localhost:3000 and localhost:5173

### Frontend
- API base URL: `http://localhost:8000` (configured in `useChat.ts`)

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── hooks/
│   │   │   └── useChat.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
```

## Notes

- Conversation history is stored in-memory (backend). For production, use Redis or a database.
- The typing indicator shows while waiting for Ollama response.
- Messages are limited to 4000 characters.
- Conversation history is truncated to last 20 messages to prevent context overflow.

Nb: I wasn't able to upload the model file because it was to large, if needed contact through gmail
