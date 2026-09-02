export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  timestamp: string;
  model: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}
