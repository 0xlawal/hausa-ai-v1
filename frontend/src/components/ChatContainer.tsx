import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { ChatInput } from './ChatInput';
import { useChat } from '../hooks/useChat';

export function ChatContainer() {
  const { messages, isLoading, sendMessage, clearConversation } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">Chat</h1>
            <p className="text-sm text-gray-500">
              {messages.length > 0
                ? `${messages.length} messages`
                : 'Start a conversation'}
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearConversation}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              Clear chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-20">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <svg
                  className="w-8 h-8 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M12 16h.01M12 8h.01M12 12a4 4 0 100-8 4 4 0 000 8z"
                  />
                </svg>
              </div>
              <h2 className="text-lg font-medium text-gray-800 mb-2">
                Welcome to Chat
              </h2>
              <p className="text-gray-500 max-w-md">
                Start a conversation by typing a message below. Your messages are
                powered by local AI.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input */}
      <ChatInput
        onSendMessage={sendMessage}
        isLoading={isLoading}
        disabled={false}
      />
    </div>
  );
}
