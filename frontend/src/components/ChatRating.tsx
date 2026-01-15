/** Chat message rating component with 1-5 star rating and feedback. */

import React, { useState } from 'react';
import { Star, Send, MessageSquare } from 'lucide-react';
import { chatService } from '../services/chatService';

interface ChatRatingProps {
  messageId: string;
  conversationId: string;
  onRatingSubmitted?: () => void;
}

const ChatRating: React.FC<ChatRatingProps> = ({
  messageId,
  conversationId,
  onRatingSubmitted
}) => {
  const [rating, setRating] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [showDetailed, setShowDetailed] = useState(false);

  const handleQuickRating = async (stars: number) => {
    if (stars === rating) {
      setRating(0); // Toggle off
      return;
    }

    setRating(stars);

    try {
      setIsSubmitting(true);
      await chatService.submitQuickRating({
        message_id: messageId,
        conversation_id: conversationId,
        rating: stars,
        feedback: feedback.trim() || undefined
      });

      setIsSubmitted(true);
      onRatingSubmitted?.();
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert('Failed to submit rating. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDetailedFeedback = () => {
    setShowDetailed(true);
  };

  if (isSubmitted) {
    return (
      <div className="flex items-center gap-2 text-sm text-green-600 mt-2">
        <Star size={14} className="fill-current" />
        <span>Thank you for your feedback!</span>
      </div>
    );
  }

  if (showDetailed) {
    return (
      <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Detailed Feedback</h4>
        <p className="text-xs text-gray-600 mb-3">
          Help us improve by rating different aspects of this response:
        </p>

        {/* Rating categories would go here */}
        <div className="text-xs text-gray-500 italic">
          Detailed feedback form coming soon...
        </div>

        <button
          onClick={() => setShowDetailed(false)}
          className="mt-2 text-xs text-blue-600 hover:text-blue-800"
        >
          ← Back to simple rating
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-xs text-gray-500">Rate this response:</span>

      {/* Star rating */}
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => handleQuickRating(star)}
            disabled={isSubmitting}
            className={`transition-colors ${
              star <= rating
                ? 'text-yellow-400 hover:text-yellow-500'
                : 'text-gray-300 hover:text-gray-400'
            } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Star
              size={16}
              className={star <= rating ? 'fill-current' : ''}
            />
          </button>
        ))}
      </div>

      {/* Feedback input */}
      {rating > 0 && (
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Optional feedback..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            className="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
            maxLength={200}
          />

          {isSubmitting ? (
            <div className="text-xs text-gray-500">Submitting...</div>
          ) : (
            <button
              onClick={() => handleQuickRating(rating)}
              className="flex items-center gap-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors"
            >
              <Send size={12} />
              Submit
            </button>
          )}
        </div>
      )}

      {/* Detailed feedback button */}
      <button
        onClick={handleDetailedFeedback}
        className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
      >
        <MessageSquare size={12} />
        Detailed
      </button>
    </div>
  );
};

export default ChatRating;