/** Document service for API communication. */

import apiClient from './api';
import type { Document, DocumentLayer } from '../types';

export interface UploadDocumentRequest {
  file: File;
  title?: string;
  category?: string;
  tags?: string[];
  layer?: DocumentLayer; // 'policy' | 'principle' | 'sop'
}

export interface UploadResponse {
  id: string;
  message: string;
  status: 'success' | 'error';
}

export const documentService = {
  /**
   * Upload a document
   */
  async uploadDocument(data: UploadDocumentRequest): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', data.file);
    
    if (data.title) {
      formData.append('title', data.title);
    }
    if (data.category) {
      formData.append('category', data.category);
    }
    if (data.tags && data.tags.length > 0) {
      formData.append('tags', JSON.stringify(data.tags));
    }
    if (data.layer) {
      formData.append('layer', data.layer);
    }

    const response = await apiClient.post<UploadResponse>(
      '/api/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * Get all documents
   */
  async getDocuments(): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/api/documents');
    return response.data;
  },

  /**
   * Delete a document
   */
  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/api/documents/${id}`);
  },

  /**
   * Update a document
   */
  async updateDocument(
    id: string,
    data: {
      file?: File;
      title?: string;
      category?: string;
      tags?: string[];
      layer?: DocumentLayer;
    }
  ): Promise<UploadResponse> {
    const formData = new FormData();
    
    if (data.file) {
      formData.append('file', data.file);
    }
    if (data.title) {
      formData.append('title', data.title);
    }
    if (data.category) {
      formData.append('category', data.category);
    }
    if (data.tags && data.tags.length > 0) {
      formData.append('tags', JSON.stringify(data.tags));
    }
    if (data.layer) {
      formData.append('layer', data.layer);
    }

    const response = await apiClient.put<UploadResponse>(
      `/api/documents/${id}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * Link documents together
   */
  async linkDocuments(documentId: string, relatedDocumentIds: string[]): Promise<void> {
    await apiClient.post(`/api/documents/${documentId}/link`, {
      relatedDocumentIds,
    });
  },

  /**
   * Get related documents for a document
   */
  async getRelatedDocuments(documentId: string): Promise<Document[]> {
    const response = await apiClient.get<Document[]>(`/api/documents/${documentId}/related`);
    return response.data;
  },

  /**
   * Search documents that can be linked
   */
  async searchDocuments(query: string): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/api/documents', {
      params: { search: query },
    });
    return response.data;
  },
};
