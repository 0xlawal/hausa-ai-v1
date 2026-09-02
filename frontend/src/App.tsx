import React, { useState, useRef, useEffect } from 'react';
import './App.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // ---------- TIMEOUT HANDLING (from Claude) ----------
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) throw new Error('Backend error');

      const data = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response received.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      clearTimeout(timeoutId);
      let errorMsg = '⚠️ Error connecting to the server. Please try again.';
      if (error.name === 'AbortError') {
        errorMsg = '⏳ Request timed out (model is thinking too long). Try a shorter question.';
      } else if (error.message) {
        errorMsg = `⚠️ ${error.message}`;
      }
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">🇳🇬</span>
              <span className="logo-text">Hausa AI</span>
            </div>
            <div className="header-actions">
              <button onClick={clearChat} className="clear-btn" title="Clear conversation">
                🗑️
              </button>
            </div>
          </div>
        </header>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h2>Start a conversation</h2>
              <p>Ask me anything in Hausa – I'm here to help!</p>
              <p className="example">Try: <em>"Sannu! Yaya lafiya?"</em></p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                <div className="avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-bubble">
                  <div className="message-content">{msg.content}</div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="avatar">🤖</div>
              <div className="message-bubble loading">
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="input-area">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message in Hausa…"
            rows={1}
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading || !input.trim()}>
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;