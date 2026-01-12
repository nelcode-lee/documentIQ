/** Analytics service for fetching analytics data. */

import apiClient from './api';
import type { Analytics, DailyMetrics } from '../types';

// Transform snake_case to camelCase
const transformAnalytics = (data: any): Analytics => {
  return {
    queryVolume: data.query_volume || data.queryVolume || { daily: 0, weekly: 0, monthly: 0, total: 0 },
    topDocuments: (data.top_documents || data.topDocuments || []).map((doc: any) => ({
      document_id: doc.document_id,
      title: doc.title,
      query_count: doc.query_count,
      last_accessed: doc.last_accessed,
      total_chunks_retrieved: doc.total_chunks_retrieved || 0,
    })),
    topQueries: data.top_queries || data.topQueries || [],
    averageResponseTime: data.average_response_time || data.averageResponseTime || 0,
    totalQueries: data.total_queries || data.totalQueries || 0,
    timeRange: data.time_range || data.timeRange || { start: '', end: '' },
  };
};

export const analyticsService = {
  /**
   * Get comprehensive analytics summary.
   */
  async getSummary(days: number = 30): Promise<Analytics> {
    const response = await apiClient.get('/api/analytics/summary', {
      params: { days },
    });
    return transformAnalytics(response.data);
  },

  /**
   * Get query volume metrics.
   */
  async getQueryVolume(days: number = 30) {
    const response = await apiClient.get('/api/analytics/query-volume', {
      params: { days },
    });
    return response.data;
  },

  /**
   * Get top queries.
   */
  async getTopQueries(limit: number = 10, days: number = 30) {
    const response = await apiClient.get('/api/analytics/top-queries', {
      params: { limit, days },
    });
    return response.data;
  },

  /**
   * Get top documents.
   */
  async getTopDocuments(limit: number = 10, days: number = 30) {
    const response = await apiClient.get('/api/analytics/top-documents', {
      params: { limit, days },
    });
    return response.data;
  },

  /**
   * Get average response time.
   */
  async getAverageResponseTime(days: number = 30) {
    const response = await apiClient.get('/api/analytics/response-time', {
      params: { days },
    });
    return response.data;
  },

  /**
   * Get daily metrics breakdown.
   */
  async getDailyMetrics(days: number = 30): Promise<DailyMetrics[]> {
    const response = await apiClient.get<DailyMetrics[]>('/api/analytics/daily-metrics', {
      params: { days },
    });
    return response.data;
  },
};
