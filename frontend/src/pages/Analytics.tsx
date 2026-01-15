/** Analytics dashboard page. */

import { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area, ComposedChart, RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Radar, ScatterChart, Scatter, Treemap
} from 'recharts';
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

  // Prepare chart data with better formatting
  const dailyChartData = dailyMetrics.map((metric) => ({
    date: new Date(metric.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    fullDate: metric.date,
    queries: metric.query_count || 0,
    conversations: metric.unique_conversations || 0,
    avgResponseTime: metric.average_response_time || 0,
    documentsAccessed: metric.documents_accessed?.length || 0,
  }));

  // Calculate hourly distribution (if we had hourly data, for now use daily as proxy)
  const hourlyDistribution = dailyChartData.reduce((acc, item) => {
    acc.push({ time: item.date, queries: item.queries });
    return acc;
  }, [] as Array<{ time: string; queries: number }>);

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

      {/* Summary Cards with Trends */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Queries</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.totalQueries.toLocaleString()}
              </p>
              {dailyChartData.length > 1 && (
                <p className="text-xs text-gray-500 mt-1">
                  {dailyChartData[dailyChartData.length - 1].queries > dailyChartData[dailyChartData.length - 2].queries ? (
                    <span className="text-green-600">↑ Trending up</span>
                  ) : (
                    <span className="text-gray-500">→ Stable</span>
                  )}
                </p>
              )}
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <MessageSquare className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {Math.round(analytics.averageResponseTime)}ms
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {analytics.averageResponseTime < 2000 ? (
                  <span className="text-green-600">✓ Excellent</span>
                ) : analytics.averageResponseTime < 5000 ? (
                  <span className="text-yellow-600">○ Good</span>
                ) : (
                  <span className="text-red-600">⚠ Slow</span>
                )}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <Clock className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Daily Queries</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.queryVolume.daily}
              </p>
              {dailyChartData.length > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  {dailyChartData[dailyChartData.length - 1].conversations} conversations
                </p>
              )}
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <TrendingUp className="text-purple-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Documents Accessed</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {analytics.topDocuments.length}
              </p>
              {analytics.topDocuments.length > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  {analytics.topDocuments[0].query_count} queries on top doc
                </p>
              )}
            </div>
            <div className="bg-orange-100 rounded-full p-3">
              <FileText className="text-orange-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Query Volume Chart - Area Chart for better trend visualization */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Query Volume Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={dailyChartData}>
            <defs>
              <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorConversations" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="queries"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorQueries)"
              name="Queries"
            />
            <Area
              type="monotone"
              dataKey="conversations"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorConversations)"
              name="Conversations"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Response Time Chart - Composed Chart with Bar and Line */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Response Time Performance</h2>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={dailyChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              yAxisId="left"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Response Time (ms)', angle: -90, position: 'insideLeft' }}
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
            <Bar 
              yAxisId="left"
              dataKey="avgResponseTime" 
              fill="#f59e0b" 
              name="Avg Response Time (ms)"
              radius={[4, 4, 0, 0]}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="avgResponseTime" 
              stroke="#ef4444" 
              strokeWidth={2}
              dot={{ fill: '#ef4444', r: 4 }}
              name="Trend"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Correlation - Query Count vs Response Time */}
      {topQueriesData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Query Performance Correlation</h2>
          <p className="text-sm text-gray-600 mb-4">
            Relationship between query frequency and average response time
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={topQueriesData.slice(0, 15)} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                type="number" 
                dataKey="count" 
                name="Query Count"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
                label={{ value: 'Query Count', position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                type="number" 
                dataKey="avgTime" 
                name="Response Time (ms)"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
                label={{ value: 'Avg Response Time (ms)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}
                formatter={(value: number, name: string) => {
                  if (name === 'count') return [value, 'Query Count'];
                  if (name === 'avgTime') return [`${Math.round(value)}ms`, 'Avg Response Time'];
                  return [value, name];
                }}
              />
              <Scatter 
                name="Queries" 
                dataKey="avgTime" 
                fill="#3b82f6"
              >
                {topQueriesData.slice(0, 15).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill="#3b82f6" />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Documents - Horizontal Bar Chart */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Most Accessed Documents</h2>
          {analytics.topDocuments.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topDocumentsData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" stroke="#6b7280" style={{ fontSize: '12px' }} />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    width={120}
                    stroke="#6b7280"
                    style={{ fontSize: '11px' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                    }}
                    formatter={(value: number) => [value, 'Queries']}
                  />
                  <Bar 
                    dataKey="queries" 
                    fill="#3b82f6"
                    radius={[0, 4, 4, 0]}
                  >
                    {topDocumentsData.map((entry, index) => {
                      const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1', '#f97316', '#06b6d4'];
                      return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
                {analytics.topDocuments.slice(0, 5).map((doc, index) => (
                  <div
                    key={doc.document_id}
                    className="flex items-center justify-between p-2 hover:bg-gray-50 rounded"
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="text-sm font-medium text-gray-500 w-6 flex-shrink-0">
                        {index + 1}.
                      </span>
                      <span className="text-sm text-gray-900 truncate" title={doc.title}>{doc.title}</span>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className="text-xs text-gray-500">{doc.total_chunks_retrieved} chunks</span>
                      <span className="text-sm font-semibold text-blue-600">
                        {doc.query_count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <FileText className="mx-auto text-gray-400 mb-3" size={48} />
              <p className="text-gray-600 mb-2">No document access data available yet.</p>
              <p className="text-sm text-gray-500">Start chatting to see which documents are most frequently accessed!</p>
            </div>
          )}
        </div>

        {/* Top Queries - Stacked Bar Chart with Response Time */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Most Popular Queries</h2>
          {(analytics.topQueries && analytics.topQueries.length > 0) ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={topQueriesData.slice(0, 8)} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    type="number" 
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    dataKey="query" 
                    type="category" 
                    width={120}
                    stroke="#6b7280"
                    style={{ fontSize: '11px' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Legend />
                  <Bar 
                    dataKey="count" 
                    fill="#10b981" 
                    name="Query Count"
                    radius={[0, 4, 4, 0]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="avgTime" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', r: 3 }}
                    name="Avg Response Time (ms)"
                  />
                </ComposedChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
                {(analytics.topQueries || []).slice(0, 5).map((query, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between p-2 hover:bg-gray-50 rounded"
                  >
                    <div className="flex items-start gap-2 flex-1 min-w-0">
                      <span className="text-sm font-medium text-gray-500 w-6 flex-shrink-0">
                        {index + 1}.
                      </span>
                      <span className="text-sm text-gray-900 flex-1 break-words" title={query.query}>{query.query}</span>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                      <span className="text-sm font-semibold text-green-600 block">
                        {query.count}x
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(query.average_response_time_ms)}ms
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <MessageSquare className="mx-auto text-gray-400 mb-3" size={48} />
              <p className="text-gray-600 mb-2">No query data available yet.</p>
              <p className="text-sm text-gray-500">Start chatting to see which queries are most popular!</p>
            </div>
          )}
        </div>
      </div>

      {/* Query Volume Breakdown - Bar Chart */}
      <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Query Volume Breakdown</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart 
            data={[
              { period: 'Today', queries: analytics.queryVolume.daily, color: '#3b82f6' },
              { period: 'Last 7 Days', queries: analytics.queryVolume.weekly, color: '#10b981' },
              { period: 'Last 30 Days', queries: analytics.queryVolume.monthly, color: '#f59e0b' },
              { period: 'All Time', queries: analytics.queryVolume.total, color: '#8b5cf6' },
            ]}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="period" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              formatter={(value: number) => [value.toLocaleString(), 'Queries']}
            />
            <Bar 
              dataKey="queries" 
              radius={[8, 8, 0, 0]}
            >
              {[
                { period: 'Today', queries: analytics.queryVolume.daily, color: '#3b82f6' },
                { period: 'Last 7 Days', queries: analytics.queryVolume.weekly, color: '#10b981' },
                { period: 'Last 30 Days', queries: analytics.queryVolume.monthly, color: '#f59e0b' },
                { period: 'All Time', queries: analytics.queryVolume.total, color: '#8b5cf6' },
              ].map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Documents Accessed Over Time */}
      {dailyChartData.some(d => d.documentsAccessed > 0) && (
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Documents Accessed Over Time</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}
              />
              <Bar 
                dataKey="documentsAccessed" 
                fill="#ec4899" 
                name="Documents Accessed"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
