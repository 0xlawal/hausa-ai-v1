import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-md'
            : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md'
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </div>
        <div
          className={`text-xs mt-2 ${
            isUser ? 'text-primary-100' : 'text-gray-500'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
