/** Document management page. */

import { useState, useEffect, useMemo } from 'react';
import {
  FileText,
  Search,
  Eye,
  Trash2,
  Link2,
  Plus,
  Upload,
  Loader2,
  X,
  Edit2,
  Save,
  Download,
  AlertCircle
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
  const [sortBy, setSortBy] = useState<SortOption>('title');
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
  const [updateSharePointUrl, setUpdateSharePointUrl] = useState('');

  // Load documents
  useEffect(() => {
    const loadDocuments = async () => {
      setLoading(true);
      
      try {
        const docs = await documentService.getDocuments();
        if (docs && docs.length > 0) {
          setDocuments(docs);
        } else {
          setDocuments([]);
        }
      } catch (error) {
        console.error('Error loading documents:', error);
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
  }, [documents, searchQuery, filter, selectedCategory, layerFilter, sortBy]);

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
    setUpdateLayer(doc.layer || '');
    setUpdateSharePointUrl(doc.sharePointUrl || '');
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
        sharePointUrl: updateSharePointUrl || undefined,
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
      setUpdateSharePointUrl('');
    } catch (error) {
      console.error('Error updating document:', error);
      alert('Failed to update document. Please try again.');
    } finally {
      setUpdating(false);
    }
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

  const getLayerBadge = (layer?: DocumentLayer) => {
    if (!layer) return null;
    
    const layerConfig = {
      policy: { label: 'Policy', color: 'bg-red-100 text-red-700 border-red-300', icon: '📋' },
      principle: { label: 'Principle', color: 'bg-amber-100 text-amber-700 border-amber-300', icon: '📐' },
      sop: { label: 'SOP', color: 'bg-emerald-100 text-emerald-700 border-emerald-300', icon: '📝' },
    };
    
    const config = layerConfig[layer];
    if (!config) return null;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold border ${config.color}`}>
        <span>{config.icon}</span>
        {config.label}
      </span>
    );
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

      {/* Important Notes - Collapsible on mobile */}
      <div className="space-y-3 mb-6">
        {/* Document Quality Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
          <div className="flex items-start gap-2 sm:gap-3">
            <FileText size={18} className="text-blue-600 mt-0.5 flex-shrink-0 hidden sm:block" />
            <div>
              <h3 className="text-xs sm:text-sm font-semibold text-blue-900 mb-1">
                Documents are key to response quality
              </h3>
              <p className="text-xs sm:text-sm text-blue-800 hidden sm:block">
                High-quality, well-organized documents ensure accurate AI responses.
              </p>
            </div>
          </div>
        </div>

        {/* Layer Hierarchy Note */}
        <details className="bg-green-50 border border-green-200 rounded-lg">
          <summary className="p-3 sm:p-4 cursor-pointer text-xs sm:text-sm font-semibold text-green-900 flex items-center gap-2">
            <FileText size={18} className="text-green-600 flex-shrink-0 hidden sm:block" />
            Document Layer Hierarchy
          </summary>
          <div className="px-3 sm:px-4 pb-3 sm:pb-4 text-xs sm:text-sm text-green-800 space-y-1">
            <p><strong>Policy:</strong> High-level BRC requirements</p>
            <p><strong>Principle:</strong> Bridge layer linking requirements to SOPs</p>
            <p><strong>SOP:</strong> Step-by-step procedures</p>
          </div>
        </details>
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
          <div className="space-y-3">
            {/* Source Filter Row */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-gray-500 w-full sm:w-auto">Source:</span>
              <div className="flex flex-wrap gap-1">
                {(['all', 'uploaded', 'generated'] as FilterType[]).map((type) => (
                  <button
                    key={type}
                    onClick={() => setFilter(type)}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      filter === type
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Layer Filter Row */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-gray-500 w-full sm:w-auto">Layer:</span>
              <div className="flex flex-wrap gap-1">
                {(['all', 'policy', 'principle', 'sop'] as LayerFilter[]).map((layer) => (
                  <button
                    key={layer}
                    onClick={() => setLayerFilter(layer)}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      layerFilter === layer
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {layer === 'all' ? 'All' : layer.charAt(0).toUpperCase() + layer.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Category and Sort Row */}
            <div className="flex flex-wrap items-center gap-2">
              {categories.length > 0 && (
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1 min-w-0 max-w-[150px]"
                >
                  <option value="all">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              )}

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 ml-auto"
              >
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
                <option value="title">A-Z</option>
                <option value="category">Category</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {filteredDocuments.length} of {documents.length} document(s)
      </div>

      {/* Documents List */}
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
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {/* List Header - Desktop only */}
          <div className="hidden sm:grid sm:grid-cols-12 gap-4 px-4 py-3 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
            <div className="col-span-5">Document</div>
            <div className="col-span-2">Layer</div>
            <div className="col-span-2">Category</div>
            <div className="col-span-1">Type</div>
            <div className="col-span-2 text-right">Actions</div>
          </div>

          {/* Document List Items */}
          <div className="divide-y divide-gray-100">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="group hover:bg-blue-50/50 transition-colors"
              >
                {/* Mobile Layout */}
                <div className="sm:hidden p-3">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selectedDocs.has(doc.id)}
                      onChange={() => toggleSelect(doc.id)}
                      className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <FileText size={16} className="text-gray-400 flex-shrink-0" />
                        <span className="font-medium text-gray-900 text-sm truncate">{doc.title}</span>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap text-xs">
                        {getLayerBadge(doc.layer)}
                        {doc.category && <span className="text-gray-500">{doc.category}</span>}
                        {doc.fileType && <span className="text-gray-400 uppercase">{doc.fileType}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 mt-2 ml-7">
                    {doc.downloadUrl && (
                      <>
                        <button
                          onClick={() => handleViewDocument(doc)}
                          className="p-1.5 text-green-600 hover:bg-green-100 rounded"
                          title="View"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleDownloadDocument(doc)}
                          className="p-1.5 text-blue-600 hover:bg-blue-100 rounded"
                          title="Download"
                        >
                          <Download size={16} />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => handleEdit(doc)}
                      className="p-1.5 text-gray-600 hover:bg-gray-100 rounded"
                      title="Edit"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id, doc.title)}
                      className="p-1.5 text-red-600 hover:bg-red-100 rounded"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                    {doc.sharePointUrl && (
                      <a
                        href={doc.sharePointUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-green-600 hover:bg-green-100 rounded ml-auto"
                        title="Open in SharePoint"
                      >
                        <Link2 size={16} />
                      </a>
                    )}
                  </div>
                </div>

                {/* Desktop Layout */}
                <div className="hidden sm:grid sm:grid-cols-12 gap-4 px-4 py-3 items-center">
                  <div className="col-span-5 flex items-center gap-3 min-w-0">
                    <input
                      type="checkbox"
                      checked={selectedDocs.has(doc.id)}
                      onChange={() => toggleSelect(doc.id)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <FileText size={18} className="text-gray-400 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 text-sm truncate" title={doc.title}>
                        {doc.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(doc.uploadedAt).toLocaleDateString()}
                        {doc.author && ` • ${doc.author}`}
                      </p>
                    </div>
                  </div>
                  <div className="col-span-2">
                    {getLayerBadge(doc.layer)}
                  </div>
                  <div className="col-span-2">
                    <span className="text-sm text-gray-600">{doc.category || '-'}</span>
                  </div>
                  <div className="col-span-1">
                    <span className="text-xs text-gray-500 uppercase">{doc.fileType || '-'}</span>
                  </div>
                  <div className="col-span-2 flex items-center justify-end gap-1">
                    {doc.sharePointUrl && (
                      <a
                        href={doc.sharePointUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-green-600 hover:bg-green-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Open in SharePoint"
                      >
                        <Link2 size={16} />
                      </a>
                    )}
                    {doc.downloadUrl && (
                      <>
                        <button
                          onClick={() => handleViewDocument(doc)}
                          className="p-1.5 text-green-600 hover:bg-green-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                          title="View"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => handleDownloadDocument(doc)}
                          className="p-1.5 text-blue-600 hover:bg-blue-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Download"
                        >
                          <Download size={16} />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => handleEdit(doc)}
                      className="p-1.5 text-gray-600 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Edit"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id, doc.title)}
                      className="p-1.5 text-red-600 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
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

              {/* SharePoint URL */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Official Document Link (SharePoint URL)
                </label>
                <input
                  type="url"
                  value={updateSharePointUrl}
                  onChange={(e) => setUpdateSharePointUrl(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://yourcompany.sharepoint.com/sites/..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Link to the official source document in SharePoint. A link icon will appear in the document list.
                </p>
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

export default Documents;
