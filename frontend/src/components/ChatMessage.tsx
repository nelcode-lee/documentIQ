/** Individual chat message component. */

import type { ChatMessage as ChatMessageType } from '../types';
import { Copy, FileText } from 'lucide-react';
import ChatRating from './ChatRating';

interface ChatMessageProps {
  message: ChatMessageType;
  messageId?: string;
  conversationId?: string;
  onCopy?: (content: string) => void;
}

const ChatMessage = ({ message, messageId, conversationId, onCopy }: ChatMessageProps) => {
  const isUser = message.role === 'user';

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content);
    } else {
      navigator.clipboard.writeText(message.content);
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 sm:mb-4`}>
      <div
        className={`max-w-[85%] sm:max-w-3xl rounded-lg px-3 sm:px-4 py-2 sm:py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200 text-gray-900'
        }`}
      >
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words text-sm sm:text-base">{message.content}</div>

        {/* Rating component for assistant messages */}
        {!isUser && messageId && conversationId && (
          <ChatRating
            messageId={messageId}
            conversationId={conversationId}
          />
        )}

        {/* Sources (for assistant messages) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-gray-200">
            <div className="flex items-center gap-1 sm:gap-2 text-xs text-gray-600 mb-1 sm:mb-2">
              <FileText size={12} className="sm:w-3.5 sm:h-3.5" />
              <span className="font-semibold">Sources:</span>
            </div>
            <ul className="list-disc list-inside space-y-0.5 sm:space-y-1 text-xs text-gray-600">
              {message.sources.map((source, index) => (
                <li key={index} className="break-words">{source}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Timestamp and actions */}
        <div className="flex items-center justify-between mt-1 sm:mt-2 pt-1 sm:pt-2 border-t border-gray-200/30">
          <span className="text-xs opacity-70">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          <button
            onClick={handleCopy}
            className={`text-xs opacity-70 hover:opacity-100 flex items-center gap-1 ${
              isUser ? 'text-white' : 'text-gray-600'
            }`}
            title="Copy message"
          >
            <Copy size={12} className="sm:w-3 sm:h-3" />
            <span className="hidden sm:inline">Copy</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
