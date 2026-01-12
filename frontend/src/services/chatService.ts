/** Chat service for API communication. */

import apiClient from './api';
import type { ChatRequest, ChatResponse } from '../types';

export const chatService = {
  /**
   * Send a chat message to the backend
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/chat', request);
    return response.data;
  },

  /**
   * Send a chat message with streaming support
   */
  async *sendMessageStream(request: ChatRequest): AsyncGenerator<string, void, unknown> {
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/chat/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to stream response');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter((line) => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              yield parsed.content;
            }
          } catch (e) {
            // Ignore JSON parse errors for incomplete chunks
          }
        }
      }
    }
  },
};
