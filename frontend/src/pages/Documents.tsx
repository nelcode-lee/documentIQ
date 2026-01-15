/** Document management page. */

import { useState, useEffect, useMemo } from 'react';
import {
  FileText,
  Search,
  Filter,
  Eye,
  Trash2,
  Link2,
  Plus,
  Upload,
  FileCheck,
  AlertCircle,
  Loader2,
  X,
  Tag,
  Calendar,
  User,
  FileType,
  Edit2,
  Save,
  Download
} from 'lucide-react';
import type { Document, DocumentLayer } from '../types';
import { documentService } from '../services/documentService';
import { Link } from 'react-router-dom';

type FilterType = 'all' | 'uploaded' | 'generated';
type LayerFilter = 'all' | 'policy' | 'principle' | 'sop';
type SortOption = 'newest' | 'oldest' | 'title' | 'category';

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<FilterType>('all');
  const [layerFilter, setLayerFilter] = useState<LayerFilter>('all');
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
  const [showLinkDialog, setShowLinkDialog] = useState(false);
  const [linkingDocId, setLinkingDocId] = useState<string | null>(null);
  const [sharePointUrl, setSharePointUrl] = useState('');
  const [editingDoc, setEditingDoc] = useState<Document | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; title: string } | null>(null);
  const [updating, setUpdating] = useState(false);
  const [updateFile, setUpdateFile] = useState<File | null>(null);
  const [updateTitle, setUpdateTitle] = useState('');
  const [updateCategory, setUpdateCategory] = useState('');
  const [updateTags, setUpdateTags] = useState('');
  const [updateLayer, setUpdateLayer] = useState<DocumentLayer | ''>('');

  // Load documents
  useEffect(() => {
    const loadDocuments = async () => {
      setLoading(true);
      
      try {
        const docs = await documentService.getDocuments();
        if (docs && docs.length > 0) {
          setDocuments(docs);
        } else {
          // If no documents, keep empty array (don't show placeholders)
          setDocuments([]);
        }
      } catch (error) {
        console.error('Error loading documents:', error);
        // Show error but don't use placeholder data
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    loadDocuments();
  }, []);

  // Filter and sort documents using useMemo for better performance
  const filteredDocuments = useMemo(() => {
    let filtered = [...documents];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((doc) =>
        doc.title.toLowerCase().includes(query) ||
        doc.category?.toLowerCase().includes(query) ||
        doc.tags?.some((tag) => tag.toLowerCase().includes(query)) ||
        doc.author?.toLowerCase().includes(query)
      );
    }

    // Apply source filter
    if (filter !== 'all') {
      filtered = filtered.filter((doc) => doc.source === filter);
    }

    // Apply category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter((doc) => doc.category === selectedCategory);
    }

    // Apply layer filter
    if (layerFilter !== 'all') {
      filtered = filtered.filter((doc) => doc.layer === layerFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime();
        case 'oldest':
          return new Date(a.uploadedAt).getTime() - new Date(b.uploadedAt).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        case 'category':
          return (a.category || '').localeCompare(b.category || '');
        default:
          return 0;
      }
    });

    return filtered;
  }, [documents, searchQuery, filter, selectedCategory, sortBy]);

  const categories = useMemo(() => {
    return Array.from(
      new Set(documents.map((doc) => doc.category).filter(Boolean))
    ) as string[];
  }, [documents]);

  const handleDelete = (id: string, title: string) => {
    setDeleteConfirm({ id, title });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    
    try {
      await documentService.deleteDocument(deleteConfirm.id);
      setDocuments(documents.filter((doc) => doc.id !== deleteConfirm.id));
      setDeleteConfirm(null);
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Failed to delete document. Please try again.');
    }
  };

  const handleEdit = (doc: Document) => {
    setEditingDoc(doc);
    setUpdateTitle(doc.title);
    setUpdateCategory(doc.category || '');
    setUpdateTags(doc.tags?.join(', ') || '');
    setUpdateFile(null);
  };

  const handleUpdate = async () => {
    if (!editingDoc) return;
    
    setUpdating(true);
    try {
      await documentService.updateDocument(editingDoc.id, {
        file: updateFile || undefined,
        title: updateTitle || undefined,
        category: updateCategory || undefined,
        tags: updateTags ? updateTags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
        layer: updateLayer || undefined,
      });
      
      // Reload documents
      const updatedDocs = await documentService.getDocuments();
      setDocuments(updatedDocs);
      
      setEditingDoc(null);
      setUpdateFile(null);
      setUpdateTitle('');
      setUpdateCategory('');
      setUpdateTags('');
      setUpdateLayer('');
    } catch (error) {
      console.error('Error updating document:', error);
      alert('Failed to update document. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const handleLinkDocuments = (docId: string) => {
    setLinkingDocId(docId);
    setShowLinkDialog(true);
    // Pre-populate SharePoint URL if document already has one
    const doc = documents.find(d => d.id === docId);
    setSharePointUrl(doc?.sharePointUrl || '');
  };

  const handleSaveSharePointLink = async () => {
    if (!linkingDocId || !sharePointUrl.trim()) {
      alert('Please enter a valid SharePoint URL');
      return;
    }

    try {
      await documentService.updateSharePointLink(linkingDocId, sharePointUrl.trim());
      
      // Update local state
      setDocuments(documents.map(doc => 
        doc.id === linkingDocId 
          ? { ...doc, sharePointUrl: sharePointUrl.trim() }
          : doc
      ));
      
      setShowLinkDialog(false);
      setLinkingDocId(null);
      setSharePointUrl('');
    } catch (error) {
      console.error('Error saving SharePoint link:', error);
      alert('Failed to save SharePoint link. Please try again.');
    }
  };

  const handleViewDocument = (doc: Document) => {
    // For now, just show an alert - in future could open a preview modal
    if (doc.downloadUrl) {
      window.open(doc.downloadUrl, '_blank');
    } else {
      alert('Document download URL not available');
    }
  };

  const handleDownloadDocument = (doc: Document) => {
    if (doc.downloadUrl) {
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = doc.downloadUrl;
      link.download = `${doc.title}.${doc.fileType || 'pdf'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      alert('Document download URL not available');
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedDocs);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedDocs(newSelected);
  };

  const getStatusBadge = (status: Document['status']) => {
    switch (status) {
      case 'completed':
        return (
          <span className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <FileCheck size={12} />
            Ready
          </span>
        );
      case 'processing':
        return (
          <span className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Loader2 size={12} className="animate-spin" />
            Processing
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertCircle size={12} />
            Error
          </span>
        );
      default:
        return null;
    }
  };

  const getLayerBadge = (layer?: DocumentLayer) => {
    if (!layer) return null;
    
    const layerConfig = {
      policy: { label: 'Policy', color: 'bg-blue-100 text-blue-800 border-blue-200' },
      principle: { label: 'Principle', color: 'bg-purple-100 text-purple-800 border-purple-200' },
      sop: { label: 'SOP', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
    };
    
    const config = layerConfig[layer];
    if (!config) return null;
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold border ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Document Library</h1>
            <p className="text-gray-600 mt-2 text-sm sm:text-base">
              Manage and organize your uploaded and generated documents
            </p>
          </div>
          <Link
            to="/upload"
            className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base font-medium self-start sm:self-auto"
          >
            <Plus size={18} />
            Upload Document
          </Link>
        </div>
      </div>

      {/* Important Notes */}
      <div className="space-y-4 mb-6">
        {/* Document Quality Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <FileText size={20} className="text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-blue-900 mb-1">
                Documents are key to response quality
              </h3>
              <p className="text-sm text-blue-800">
                Effective document management is essential and required. High-quality, well-organized documents
                ensure accurate, relevant, and contextually appropriate responses from the AI assistant.
                Regular review and maintenance of your document library directly impacts response quality.
              </p>
            </div>
          </div>
        </div>

        {/* Layer Hierarchy Note */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <FileText size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-green-900 mb-1">
                Document Layer Hierarchy
              </h3>
              <div className="text-sm text-green-800 space-y-1">
                <p><strong>Policy:</strong> High-level BRC requirements and standards</p>
                <p><strong>Principle (Quality Manual):</strong> The bridge layer - explains "How do we prove we meet each policy clause?" Defines consistent expectations across all functions (Technical, H&S, Environment, Operations, HR). Links BRC requirements to practical SOPs.</p>
                <p><strong>SOP:</strong> Practical step-by-step procedures for implementation</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm mb-6">
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents by title, category, tags, or author..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            )}
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter size={18} className="text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filter:</span>
            </div>

            {/* Source Filter */}
            <div className="flex gap-2">
              {(['all', 'uploaded', 'generated'] as FilterType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setFilter(type)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filter === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>

            {/* Layer Filter */}
            <div className="flex gap-2">
              {(['all', 'policy', 'principle', 'sop'] as LayerFilter[]).map((layer) => (
                <button
                  key={layer}
                  onClick={() => setLayerFilter(layer)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    layerFilter === layer
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {layer === 'all' ? 'All Layers' : layer.charAt(0).toUpperCase() + layer.slice(1)}
                </button>
              ))}
            </div>

            {/* Category Filter */}
            {categories.length > 0 && (
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            )}

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ml-auto"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="title">Title A-Z</option>
              <option value="category">Category</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {filteredDocuments.length} of {documents.length} document(s)
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={32} className="animate-spin text-blue-600" />
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FileText size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-gray-600 mb-2">No documents found</p>
          <p className="text-sm text-gray-500">
            {searchQuery || filter !== 'all' || selectedCategory !== 'all'
              ? 'Try adjusting your filters'
              : 'Upload your first document to get started'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-4 sm:p-6 flex flex-col"
            >
              {/* Document Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div
                    className={`p-2 rounded-lg flex-shrink-0 ${
                      doc.source === 'uploaded'
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-green-100 text-green-600'
                    }`}
                  >
                    {doc.source === 'uploaded' ? <Upload size={20} /> : <FileCheck size={20} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900 text-sm sm:text-base line-clamp-2 flex-1">
                        {doc.title}
                      </h3>
                      {getLayerBadge(doc.layer)}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {getStatusBadge(doc.status)}
                      {doc.source === 'generated' && doc.documentType && (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                          {doc.documentType.replace('-', ' ')}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={selectedDocs.has(doc.id)}
                  onChange={() => toggleSelect(doc.id)}
                  className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>

              {/* Document Metadata */}
              <div className="space-y-2 mb-4 text-xs sm:text-sm text-gray-600">
                {doc.category && (
                  <div className="flex items-center gap-2">
                    <Tag size={14} />
                    <span>{doc.category}</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Calendar size={14} />
                  <span>{new Date(doc.uploadedAt).toLocaleDateString()}</span>
                </div>
                {doc.author && (
                  <div className="flex items-center gap-2">
                    <User size={14} />
                    <span>{doc.author}</span>
                  </div>
                )}
                {doc.fileType && (
                  <div className="flex items-center gap-2">
                    <FileType size={14} />
                    <span className="uppercase">{doc.fileType}</span>
                    {doc.fileSize && <span className="text-gray-400">• {formatFileSize(doc.fileSize)}</span>}
                  </div>
                )}
                {doc.version && (
                  <div className="text-gray-500">
                    Version {doc.version}
                  </div>
                )}
              </div>

              {/* Tags */}
              {doc.tags && doc.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {doc.tags.slice(0, 3).map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700"
                    >
                      {tag}
                    </span>
                  ))}
                  {doc.tags.length > 3 && (
                    <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                      +{doc.tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Related Documents Indicator */}
              {doc.relatedDocuments && doc.relatedDocuments.length > 0 && (
                <div className="mb-4 p-2 bg-blue-50 rounded text-xs text-blue-700">
                  <Link2 size={12} className="inline mr-1" />
                  Linked to {doc.relatedDocuments.length} document(s)
                </div>
              )}

              {/* SharePoint Link Indicator */}
              {doc.sharePointUrl && (
                <div className="mb-4 p-2 bg-green-50 rounded text-xs">
                  <a
                    href={doc.sharePointUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-700 hover:text-green-900 flex items-center gap-1"
                  >
                    <Link2 size={12} />
                    <span className="underline">Open in SharePoint</span>
                  </a>
                </div>
              )}

              {/* Actions */}
              <div className="mt-auto pt-4 border-t border-gray-200 flex items-center gap-2">
                {doc.downloadUrl && (
                  <>
                    <button
                      onClick={() => handleViewDocument(doc)}
                      className="flex items-center gap-1 px-2 py-1.5 text-xs sm:text-sm text-green-600 hover:bg-green-50 rounded transition-colors flex-1 justify-center"
                      title="View document"
                    >
                      <Eye size={14} />
                      <span className="hidden sm:inline">View</span>
                    </button>
                    <button
                      onClick={() => handleDownloadDocument(doc)}
                      className="flex items-center gap-1 px-2 py-1.5 text-xs sm:text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors flex-1 justify-center"
                      title="Download document"
                    >
                      <Download size={14} />
                      <span className="hidden sm:inline">Download</span>
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleEdit(doc)}
                  className="flex items-center gap-1 px-2 py-1.5 text-xs sm:text-sm text-gray-600 hover:bg-gray-50 rounded transition-colors flex-1 justify-center"
                  title="Edit document"
                >
                  <Edit2 size={14} />
                  <span className="hidden sm:inline">Edit</span>
                </button>
                <button
                  onClick={() => handleLinkDocuments(doc.id)}
                  className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  title="Link documents"
                >
                  <Link2 size={16} />
                </button>
                <button
                  onClick={() => handleDelete(doc.id, doc.title)}
                  className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete document"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Document Modal */}
      {editingDoc && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => !updating && setEditingDoc(null)}
        >
          <div 
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Edit2 size={24} className="text-blue-600" />
                Update Document
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Update document metadata or replace the file to keep information accurate
              </p>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Title *
                </label>
                <input
                  type="text"
                  value={updateTitle}
                  onChange={(e) => setUpdateTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter document title"
                  required
                />
              </div>

              {/* Layer */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Layer
                </label>
                <select
                  value={updateLayer}
                  onChange={(e) => setUpdateLayer(e.target.value as DocumentLayer || '')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                >
                  <option value="">Select Layer (Optional)</option>
                  <option value="policy">Policy (BRC Standards)</option>
                  <option value="principle">Principle (Quality Manual)</option>
                  <option value="sop">SOP (Standard Operating Procedure)</option>
                </select>
                <div className="text-xs text-gray-600 mt-1 space-y-1">
                  <p><strong>Policy:</strong> High-level BRC requirements and standards</p>
                  <p><strong>Principle:</strong> Bridge layer - explains "How do we prove we meet each policy clause?" Defines consistent expectations across functions (Technical, H&S, Environment, Operations, HR)</p>
                  <p><strong>SOP:</strong> Practical step-by-step procedures</p>
                </div>
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <input
                  type="text"
                  value={updateCategory}
                  onChange={(e) => setUpdateCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter category"
                  list="categories"
                />
                <datalist id="categories">
                  {categories.map((cat) => (
                    <option key={cat} value={cat} />
                  ))}
                </datalist>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={updateTags}
                  onChange={(e) => setUpdateTags(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="tag1, tag2, tag3"
                />
              </div>

              {/* File Replacement (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Replace File (Optional)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => setUpdateFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="file-input"
                    disabled={updating}
                  />
                  <label
                    htmlFor="file-input"
                    className="cursor-pointer flex flex-col items-center gap-2"
                  >
                    <Upload size={32} className="text-gray-400" />
                    <span className="text-sm text-gray-600">
                      {updateFile ? updateFile.name : 'Click to select new file (PDF, DOCX, TXT)'}
                    </span>
                    {updateFile && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setUpdateFile(null);
                        }}
                        className="text-xs text-red-600 hover:text-red-700"
                      >
                        Remove file
                      </button>
                    )}
                  </label>
                </div>
                {updateFile && (
                  <p className="text-xs text-gray-500 mt-2">
                    ⚠️ Uploading a new file will delete the old document and re-process it. This ensures the latest information is available.
                  </p>
                )}
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => !updating && setEditingDoc(null)}
                disabled={updating}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdate}
                disabled={updating || !updateTitle.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {updating ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Updating...
                  </>
                ) : (
                  <>
                    <Save size={16} />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setDeleteConfirm(null)}
        >
          <div 
            className="bg-white rounded-lg max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertCircle size={24} className="text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Delete Document</h2>
                <p className="text-sm text-gray-600">This action cannot be undone</p>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700">
                Are you sure you want to delete <strong>"{deleteConfirm.title}"</strong>?
              </p>
              <p className="text-sm text-gray-500 mt-2">
                This will permanently delete:
              </p>
              <ul className="text-sm text-gray-500 mt-1 ml-4 list-disc">
                <li>The document file from storage</li>
                <li>All indexed content and embeddings</li>
                <li>All associated metadata</li>
              </ul>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
              >
                <Trash2 size={16} />
                Delete Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Link SharePoint Dialog */}
      {showLinkDialog && linkingDocId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Link2 size={24} className="text-blue-600" />
                Link to SharePoint
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Link this document to its source file in SharePoint
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SharePoint File URL *
                  </label>
                  <input
                    type="url"
                    value={sharePointUrl}
                    onChange={(e) => setSharePointUrl(e.target.value)}
                    placeholder="https://yourcompany.sharepoint.com/sites/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Paste the full SharePoint file URL. This will create a link to the source document.
                  </p>
                </div>

                {documents.find(d => d.id === linkingDocId)?.sharePointUrl && (
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-xs font-medium text-blue-900 mb-1">Current SharePoint Link:</p>
                    <a
                      href={documents.find(d => d.id === linkingDocId)?.sharePointUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800 break-all"
                    >
                      {documents.find(d => d.id === linkingDocId)?.sharePointUrl}
                    </a>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowLinkDialog(false);
                    setLinkingDocId(null);
                    setSharePointUrl('');
                  }}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveSharePointLink}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <Link2 size={16} />
                  Save SharePoint Link
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Placeholder documents for demonstration
const getPlaceholderDocuments = (): Document[] => {
  const now = new Date();
  return [
    // Uploaded documents
    {
      id: '1',
      title: 'Health and Safety Policy 2024',
      category: 'Safety',
      tags: ['safety', 'policy', 'compliance'],
      uploadedAt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'completed',
      source: 'uploaded',
      fileType: 'pdf',
      fileSize: 2048576,
      author: 'Safety Team',
      version: '2.1',
    },
    {
      id: '2',
      title: 'Quality Management System Manual',
      category: 'Quality',
      tags: ['quality', 'qms', 'standards'],
      uploadedAt: new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'completed',
      source: 'uploaded',
      fileType: 'docx',
      fileSize: 5242880,
      author: 'Quality Manager',
      version: '1.0',
    },
    {
      id: '3',
      title: 'Environmental Procedures Guide',
      category: 'Environmental',
      tags: ['environmental', 'procedures', 'compliance'],
      uploadedAt: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'processing',
      source: 'uploaded',
      fileType: 'pdf',
      fileSize: 1536000,
    },
    // Generated documents
    {
      id: '4',
      title: 'Risk Assessment - Warehouse Operations',
      category: 'Safety',
      tags: ['risk-assessment', 'warehouse', 'operations'],
      uploadedAt: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'completed',
      source: 'generated',
      documentType: 'risk-assessment',
      fileType: 'docx',
      fileSize: 512000,
      author: 'John Smith',
      version: '1.0',
      relatedDocuments: ['1'],
    },
    {
      id: '5',
      title: 'Method Statement - Equipment Installation',
      category: 'Operations',
      tags: ['method-statement', 'equipment', 'installation'],
      uploadedAt: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'completed',
      source: 'generated',
      documentType: 'method-statement',
      fileType: 'pdf',
      fileSize: 768000,
      author: 'Sarah Johnson',
      version: '1.0',
    },
    {
      id: '6',
      title: 'Safe Work Procedure - High-Risk Tasks',
      category: 'Safety',
      tags: ['safe-work-procedure', 'high-risk', 'tasks'],
      uploadedAt: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'completed',
      source: 'generated',
      documentType: 'safe-work-procedure',
      fileType: 'docx',
      fileSize: 384000,
      author: 'Mike Wilson',
      version: '2.0',
      relatedDocuments: ['1', '4'],
    },
  ];
};

export default Documents;
