/** Chat interface page. */

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Trash2, Lightbulb, Info, X } from 'lucide-react';
import ChatMessage from '../components/ChatMessage';
import type { ChatMessage as ChatMessageType } from '../types';
import { chatService } from '../services/chatService';
import { analyticsService } from '../services/analyticsService';
import { useLanguage } from '../contexts/LanguageContext';
import type { Language } from '../i18n/translations';

const languages: { code: Language; name: string; flag: string }[] = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'pl', name: 'Polski', flag: '🇵🇱' },
  { code: 'ro', name: 'Română', flag: '🇷🇴' },
];

const Chat = () => {
  const { language: selectedLanguage, setLanguage: setSelectedLanguage, t } = useLanguage();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [topSearchedTerms, setTopSearchedTerms] = useState<string[]>([]);
  const [showInfoModal, setShowInfoModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Load top searched queries from analytics - reloads when language changes
  useEffect(() => {
    const loadTopQueries = async () => {
      try {
        console.log('[Chat] Loading top queries from analytics...');
        const topQueries = await analyticsService.getTopQueries(5, 30);
        console.log('[Chat] Top queries received:', JSON.stringify(topQueries, null, 2));
        
        // Handle different response formats
        let queries: string[] = [];
        if (Array.isArray(topQueries) && topQueries.length > 0) {
          // Extract just the query text from objects
          queries = topQueries.map((q: any) => {
            if (typeof q === 'string') {
              return q;
            } else if (q && typeof q === 'object') {
              // Backend returns: { query: string, count: number, average_response_time_ms: number }
              const queryText = q.query || q.text || q.query_text || q.message || '';
              console.log('[Chat] Extracted query from object:', { original: q, extracted: queryText });
              return queryText;
            }
            return '';
          }).filter((q: string) => q && q.trim().length > 0);
        }
        
        console.log('[Chat] Extracted queries (after filtering):', queries);
        
        if (queries.length > 0) {
          setTopSearchedTerms(queries);
          console.log('[Chat] ✅ Set top searched terms:', queries);
        } else {
          // Use translated defaults if empty
          console.warn('[Chat] ⚠️ No queries found in analytics, using default questions');
          setTopSearchedTerms(t.defaultQuestions);
        }
      } catch (error) {
        // Log error details for debugging
        console.error('[Chat] ❌ Error loading top queries:', error);
        if (error instanceof Error) {
          console.error('[Chat] Error details:', error.message, error.stack);
        }
        console.warn('[Chat] Using default questions due to error');
        setTopSearchedTerms(t.defaultQuestions);
      }
    };

    // Load immediately - backend should be running
    loadTopQueries();
  }, [selectedLanguage, t]); // Reload when language or translations change

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Generate unique IDs for rating system
    const userMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const assistantMessageId = `msg-${Date.now() + 1}-${Math.random().toString(36).substr(2, 9)}`;

    const userMessage: ChatMessageType = {
      id: userMessageId,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

           try {
             // Debug: log the selected language
             console.log('[DEBUG] Sending message with language:', selectedLanguage);

             // For now, use non-streaming API (you can switch to streaming later)
             const response = await chatService.sendMessage({
               message: userMessage.content,
               conversation_id: conversationId,
               language: selectedLanguage,
             });

      const assistantMessage: ChatMessageType = {
        id: assistantMessageId,
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        timestamp: new Date(),
      };

      // Update conversation ID if this is the first message
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      setMessages((prev) => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
      
      // Refresh top queries after sending a message (with delay to let analytics update)
      setTimeout(async () => {
        try {
          console.log('[Chat] Refreshing top queries after message...');
          const topQueries = await analyticsService.getTopQueries(5, 30);
          console.log('[Chat] Refreshed top queries:', topQueries);
          
          // Handle different response formats
          let queries: string[] = [];
          if (Array.isArray(topQueries) && topQueries.length > 0) {
            queries = topQueries.map((q: any) => {
              if (typeof q === 'string') {
                return q;
              } else if (q && typeof q === 'object') {
                // Backend returns: { query: string, count: number, average_response_time_ms: number }
                return q.query || q.text || q.query_text || q.message || '';
              }
              return '';
            }).filter((q: string) => q && q.trim().length > 0);
          }
          
          if (queries.length > 0) {
            setTopSearchedTerms(queries);
            console.log('[Chat] ✅ Updated top searched terms:', queries);
          } else {
            // Only fall back to defaults if we don't have any queries yet
            if (topSearchedTerms.length === 0) {
              setTopSearchedTerms(t.defaultQuestions);
            }
          }
        } catch (err) {
          // Log error but don't disrupt chat flow
          console.error('[Chat] Error refreshing top queries:', err);
          // Keep existing queries or use defaults
          if (topSearchedTerms.length === 0) {
            setTopSearchedTerms(t.defaultQuestions);
          }
        }
      }, 1000); // Wait 1 second for analytics to be processed
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: t.error + ': Please try again or check if the backend is running.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([]);
    setConversationId(undefined);
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleQuickSelect = (term: string) => {
    setInput(term);
    inputRef.current?.focus();
    // Optionally auto-send
    // handleSend();
  };

  const handleExampleClick = (example: string) => {
    setInput(example);
    setShowInfoModal(false);
    inputRef.current?.focus();
  };

  // Use analytics data if available, otherwise use translated defaults
  const popularQuestions = topSearchedTerms.length > 0 
    ? topSearchedTerms 
    : t.defaultQuestions;
  
  // Debug: Log when queries change
  useEffect(() => {
    console.log('[Chat] Top searched terms updated:', topSearchedTerms);
    console.log('[Chat] Popular questions to display:', popularQuestions);
  }, [topSearchedTerms, popularQuestions]);

  // Helper to truncate long questions for display
  const truncateQuestion = (text: string, maxLength: number = 60) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] sm:h-[calc(100vh-12rem)] max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{t.chatTitle}</h1>
            {/* Info Button */}
            <button
              onClick={() => setShowInfoModal(true)}
              className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 hover:bg-blue-200 text-blue-600 transition-colors"
              title={t.howToUse}
              aria-label={t.howToUse}
            >
              <Info size={18} />
            </button>
          </div>
          <p className="text-gray-600 mt-1 text-sm sm:text-base">
            {t.chatSubtitle}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Language Selection */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 hidden sm:inline">{t.language}:</span>
            <div className="flex gap-1 bg-white border border-gray-300 rounded-lg p-1">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setSelectedLanguage(lang.code)}
                  className={`px-2 py-1 rounded text-lg transition-all ${
                    selectedLanguage === lang.code
                      ? 'bg-blue-100 scale-110'
                      : 'hover:bg-gray-100'
                  }`}
                  title={lang.name}
                  aria-label={`Select ${lang.name}`}
                >
                  {lang.flag}
                </button>
              ))}
            </div>
          </div>
          
          {messages.length > 0 && (
            <button
              onClick={handleClear}
              className="flex items-center justify-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Trash2 size={16} />
              <span className="hidden sm:inline">{t.clearChat}</span>
              <span className="sm:hidden">{t.clear}</span>
            </button>
          )}
        </div>
      </div>

      {/* Quick Search Terms - Show when no messages */}
      {messages.length === 0 && popularQuestions.length > 0 && (
        <div className="mb-4">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-4 sm:p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-blue-600">💡</span>
              {topSearchedTerms.length > 0 ? t.mostPopularQuestions : t.popularQuestions}
            </h3>
            <div className="flex flex-wrap gap-2">
              {popularQuestions.slice(0, 5).map((term, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickSelect(term)}
                  className="px-3 py-2 bg-white border border-blue-200 rounded-lg text-xs sm:text-sm text-gray-700 hover:bg-blue-50 hover:border-blue-300 transition-colors text-left"
                  title={term}
                >
                  {truncateQuestion(term, 50)}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-3 sm:p-6 mb-4 border border-gray-200">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center px-4 max-w-2xl">
              <div className="mb-6">
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                  {t.greeting}
                </h2>
                <p className="text-base sm:text-lg text-gray-600">
                  {t.greetingSubtitle}
                </p>
              </div>
              <div className="flex justify-center mb-4">
                <button
                  onClick={() => setShowInfoModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base"
                >
                  <Info size={18} />
                  <span>{t.howToUse}</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                messageId={message.id}
                conversationId={conversationId}
                onCopy={handleCopy}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-white border border-gray-200 rounded-lg px-3 sm:px-4 py-2 sm:py-3">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-xs sm:text-sm">{t.thinking}</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4 shadow-sm">
        <div className="flex items-end gap-2 sm:gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t.typeMessage}
            className="flex-1 min-h-[50px] sm:min-h-[60px] max-h-32 px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-3 sm:px-6 py-2 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-1 sm:gap-2 font-medium text-sm sm:text-base flex-shrink-0"
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span className="hidden sm:inline">{t.loading}</span>
              </>
            ) : (
              <>
                <Send size={18} />
                <span className="hidden sm:inline">{t.send}</span>
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 hidden sm:block">
          {t.poweredBy}
        </p>
      </div>

      {/* Info Modal */}
      {showInfoModal && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowInfoModal(false)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Info size={24} className="text-blue-600" />
                {t.howToUse}
              </h2>
              <button
                onClick={() => setShowInfoModal(false)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                aria-label={t.close}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Example Prompts */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Lightbulb size={20} className="text-yellow-500" />
                  {t.examplePrompts}
                </h3>
                <div className="space-y-2">
                  <button
                    onClick={() => handleExampleClick(t.examplePrompt1)}
                    className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors text-sm"
                  >
                    {t.examplePrompt1}
                  </button>
                  <button
                    onClick={() => handleExampleClick(t.examplePrompt2)}
                    className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors text-sm"
                  >
                    {t.examplePrompt2}
                  </button>
                  <button
                    onClick={() => handleExampleClick(t.examplePrompt3)}
                    className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors text-sm"
                  >
                    {t.examplePrompt3}
                  </button>
                </div>
              </div>

              {/* Tips */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {t.tipsForBetterQueries}
                </h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <span className="text-blue-600 font-bold mt-1">•</span>
                    <span className="text-gray-700 text-sm sm:text-base">{t.tipBeSpecific}</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-600 font-bold mt-1">•</span>
                    <span className="text-gray-700 text-sm sm:text-base">{t.tipAskQuestions}</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-600 font-bold mt-1">•</span>
                    <span className="text-gray-700 text-sm sm:text-base">{t.tipRequestExamples}</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-blue-600 font-bold mt-1">•</span>
                    <span className="text-gray-700 text-sm sm:text-base">{t.tipAskForSteps}</span>
                  </li>
                </ul>
              </div>

              {/* Additional Help */}
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">
                  <strong>Tip:</strong> Click on any example prompt above to use it in your query. 
                  You can also click on the popular questions below to quickly get started.
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
              <button
                onClick={() => setShowInfoModal(false)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {t.close}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
