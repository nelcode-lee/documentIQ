/** Document generation service for API communication. */

import apiClient from './api';
import type { DocumentGenerationRequest, DocumentGenerationResponse } from '../types';

export const generateService = {
  /**
   * Generate a document
   */
  async generateDocument(request: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    const response = await apiClient.post<DocumentGenerationResponse>(
      '/api/generate/document',
      request
    );
    return response.data;
  },

  /**
   * Generate a risk assessment specifically
   */
  async generateRiskAssessment(request: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    const response = await apiClient.post<DocumentGenerationResponse>(
      '/api/generate/risk-assessment',
      request
    );
    return response.data;
  },
};
