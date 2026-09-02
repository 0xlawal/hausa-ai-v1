import { useState, useCallback, useRef } from 'react';
import { Message, ChatRequest, ChatResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const request: ChatRequest = {
        message: content.trim(),
        conversation_id: conversationId || undefined,
      };

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data: ChatResponse = await response.json();

      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);

      const errorMessageObj: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an issue: ${errorMessage}`,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearConversation,
  };
}
