/** Analytics dashboard page. */

import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsService } from '../services/analyticsService';
import type { Analytics, DailyMetrics } from '../types';
import { TrendingUp, Clock, FileText, MessageSquare, RefreshCw } from 'lucide-react';

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summary, daily] = await Promise.all([
        analyticsService.getSummary(days),
        analyticsService.getDailyMetrics(days),
      ]);
      
      setAnalytics(summary);
      setDailyMetrics(daily);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Wait a bit before trying to load analytics (gives backend time to start)
    const timeoutId = setTimeout(() => {
      fetchAnalytics();
    }, 2000);

    return () => clearTimeout(timeoutId);
  }, [days]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-blue-500" size={32} />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    const isConnectionError = error.includes('Network Error') || error.includes('ERR_CONNECTION_REFUSED') || error.includes('Failed to fetch');
    
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-sm border border-red-200">
        <div className="max-w-md mx-auto">
          <div className="bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="text-red-600" size={32} />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {isConnectionError ? 'Backend Not Available' : 'Error Loading Analytics'}
          </h2>
          <p className="text-gray-600 mb-4">
            {isConnectionError 
              ? 'The backend server is not running. Please start the backend server and try again.'
              : error}
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={fetchAnalytics}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
          {isConnectionError && (
            <p className="text-xs text-gray-500 mt-4">
              Backend should be running at: http://localhost:8000
            </p>
          )}
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No analytics data available</p>
      </div>
    );
  }

  // Prepare chart data
  const dailyChartData = dailyMetrics.map((metric) => ({
    date: new Date(metric.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    queries: metric.query_count,
    conversations: metric.unique_conversations,
    avgResponseTime: metric.average_response_time,
  }));

  const topDocumentsData = analytics.topDocuments.slice(0, 10).map((doc) => ({
    name: doc.title.length > 30 ? doc.title.substring(0, 30) + '...' : doc.title,
    queries: doc.query_count,
    chunks: doc.total_chunks_retrieved,
  }));

  const topQueriesData = (analytics.topQueries || []).slice(0, 10).map((q) => ({
    query: q.query.length > 40 ? q.query.substring(0, 40) + '...' : q.query,
    count: q.count,
    avgTime: Math.round(q.average_response_time_ms),
  }));

  return (
    <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">
            Track usage metrics and system performance
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm flex items-center gap-2"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Queries</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.totalQueries.toLocaleString()}
              </p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <MessageSquare className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {Math.round(analytics.averageResponseTime)}ms
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <Clock className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Daily Queries</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.queryVolume.daily}
              </p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <TrendingUp className="text-purple-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Documents Accessed</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.topDocuments.length}
              </p>
            </div>
            <div className="bg-orange-100 rounded-full p-3">
              <FileText className="text-orange-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Query Volume Chart */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Query Volume Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="queries"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Queries"
            />
            <Line
              type="monotone"
              dataKey="conversations"
              stroke="#10b981"
              strokeWidth={2}
              name="Conversations"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Response Time Chart */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Average Response Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="avgResponseTime"
              stroke="#10b981"
              strokeWidth={2}
              name="Response Time (ms)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Documents */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Most Accessed Documents</h2>
          {analytics.topDocuments.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topDocumentsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="queries" fill="#3b82f6" name="Queries" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {analytics.topDocuments.slice(0, 5).map((doc, index) => (
                  <div
                    key={doc.document_id}
                    className="flex items-center justify-between p-2 hover:bg-gray-50 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-500 w-6">
                        {index + 1}.
                      </span>
                      <span className="text-sm text-gray-900">{doc.title}</span>
                    </div>
                    <span className="text-sm font-semibold text-blue-600">
                      {doc.query_count}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-600 text-center py-8">No document access data available yet. Start chatting to see analytics!</p>
          )}
        </div>

        {/* Top Queries */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Most Popular Queries</h2>
          {(analytics.topQueries && analytics.topQueries.length > 0) ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topQueriesData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="query" type="category" width={150} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10b981" name="Count" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {(analytics.topQueries || []).slice(0, 5).map((query, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between p-2 hover:bg-gray-50 rounded"
                  >
                    <div className="flex items-start gap-2 flex-1">
                      <span className="text-sm font-medium text-gray-500 w-6">
                        {index + 1}.
                      </span>
                      <span className="text-sm text-gray-900 flex-1">{query.query}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-green-600 block">
                        {query.count}
                      </span>
                      <span className="text-xs text-gray-500">
                        {query.average_response_time_ms}ms
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
              <p className="text-gray-600 text-center py-8">No query data available yet. Start chatting to see analytics!</p>
          )}
        </div>
      </div>

      {/* Query Volume Breakdown */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mt-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Query Volume Breakdown</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">
              {analytics.queryVolume.daily}
            </p>
            <p className="text-sm text-gray-600 mt-1">Today</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">
              {analytics.queryVolume.weekly}
            </p>
            <p className="text-sm text-gray-600 mt-1">Last 7 Days</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">
              {analytics.queryVolume.monthly}
            </p>
            <p className="text-sm text-gray-600 mt-1">Last 30 Days</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">
              {analytics.queryVolume.total}
            </p>
            <p className="text-sm text-gray-600 mt-1">All Time</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
