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
   * Download a generated document file
   */
  async downloadDocument(documentId: string): Promise<void> {
    try {
      const response = await apiClient.get<{ downloadUrl: string }>(
        `/api/generate/download/${documentId}`
      );

      if (response.data.downloadUrl) {
        // Create a temporary link and trigger download
        const link = document.createElement('a');
        link.href = response.data.downloadUrl;
        link.download = `document-${documentId}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        throw new Error('Download URL not available');
      }
    } catch (error) {
      console.error('Error downloading document:', error);
      throw new Error('Failed to download document');
    }
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
