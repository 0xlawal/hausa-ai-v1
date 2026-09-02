export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
        <div className="flex space-x-1.5">
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-typing"
            style={{ animationDelay: '0ms' }}
          />
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-typing"
            style={{ animationDelay: '150ms' }}
          />
          <div
            className="w-2 h-2 bg-gray-400 rounded-full animate-typing"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
}
