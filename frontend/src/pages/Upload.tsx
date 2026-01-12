/** Document upload page. */

import { useState, useRef, useCallback } from 'react';
import { Upload as UploadIcon, X, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { documentService, type UploadDocumentRequest } from '../services/documentService';
import type { DocumentLayer } from '../types';

interface FileWithMetadata {
  file: File;
  title?: string;
  category?: string;
  tags?: string[];
  layer?: DocumentLayer;
  status?: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
  progress?: number;
}

const Upload = () => {
  const [files, setFiles] = useState<FileWithMetadata[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingCount, setUploadingCount] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const acceptedFileTypes = ['.pdf', '.docx', '.txt'];
  const maxFileSize = 50 * 1024 * 1024; // 50MB

  const validateFile = (file: File): string | null => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!acceptedFileTypes.includes(extension)) {
      return `File type ${extension} is not supported. Please upload PDF, DOCX, or TXT files.`;
    }

    if (file.size > maxFileSize) {
      return `File size exceeds the maximum limit of ${maxFileSize / (1024 * 1024)}MB.`;
    }

    return null;
  };

  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles: FileWithMetadata[] = [];
    
    Array.from(selectedFiles).forEach((file) => {
      const error = validateFile(file);
      if (!error) {
        // Use filename without extension as default title
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
        newFiles.push({
          file,
          title: nameWithoutExt,
          status: 'pending',
        });
      } else {
        // Add file with error status
        newFiles.push({
          file,
          status: 'error',
          error,
        });
      }
    });

    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files);
    // Reset input so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const updateFileMetadata = (index: number, updates: Partial<FileWithMetadata>) => {
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, ...updates } : f))
    );
  };

  const handleUpload = async (index: number) => {
    const fileData = files[index];
    if (!fileData || fileData.status === 'uploading' || fileData.status === 'success') {
      return;
    }

    updateFileMetadata(index, { status: 'uploading', error: undefined, progress: 0 });
    setUploadingCount((prev) => prev + 1);

    try {
      const uploadData: UploadDocumentRequest = {
        file: fileData.file,
        title: fileData.title || fileData.file.name,
        category: fileData.category,
        tags: fileData.tags?.filter((tag) => tag.trim() !== ''),
        layer: fileData.layer,
      };

      await documentService.uploadDocument(uploadData);
      
      updateFileMetadata(index, { status: 'success', progress: 100 });
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Failed to upload document. Please try again.';
      updateFileMetadata(index, { status: 'error', error: errorMessage });
    } finally {
      setUploadingCount((prev) => prev - 1);
    }
  };

  const handleUploadAll = async () => {
    const pendingFiles = files
      .map((f, i) => ({ file: f, index: i }))
      .filter(({ file }) => file.status === 'pending');

    for (const { index } of pendingFiles) {
      await handleUpload(index);
    }
  };

  const handleTagInput = (index: number, value: string) => {
    const tags = value.split(',').map((tag) => tag.trim()).filter((tag) => tag);
    updateFileMetadata(index, { tags });
  };

  const pendingFiles = files.filter((f) => f.status === 'pending' || f.status === 'error');
  const hasSuccessFiles = files.some((f) => f.status === 'success');

  return (
    <div className="max-w-4xl mx-auto w-full">
      {/* Header */}
      <div className="mb-4 sm:mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Upload Documents</h1>
        <p className="text-gray-600 mt-2 text-sm sm:text-base">
          Upload PDF, DOCX, or TXT files to add them to the knowledge base
        </p>
      </div>

      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-6 sm:p-12 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
      >
        <UploadIcon
          size={40}
          className={`mx-auto mb-3 sm:mb-4 sm:w-12 sm:h-12 ${
            isDragging ? 'text-blue-500' : 'text-gray-400'
          }`}
        />
        <p className="text-base sm:text-lg font-medium text-gray-700 mb-2">
          Drag and drop files here, or click to select
        </p>
        <p className="text-xs sm:text-sm text-gray-500 mb-4">
          Supported formats: PDF, DOCX, TXT (Max size: 50MB)
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-4 sm:px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm sm:text-base"
        >
          Select Files
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          onChange={handleFileInputChange}
          className="hidden"
        />
      </div>

      {/* Files List */}
      {files.length > 0 && (
        <div className="mt-6 sm:mt-8 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-3">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
              Files to Upload ({files.length})
            </h2>
            {pendingFiles.length > 0 && (
              <button
                onClick={handleUploadAll}
                disabled={uploadingCount > 0}
                className="px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 text-sm sm:text-base w-full sm:w-auto"
              >
                {uploadingCount > 0 ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span className="hidden sm:inline">Uploading...</span>
                    <span className="sm:hidden">Uploading</span>
                  </>
                ) : (
                  <>
                    <UploadIcon size={16} />
                    Upload All
                  </>
                )}
              </button>
            )}
          </div>

          {files.map((fileData, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6 shadow-sm"
            >
              <div className="flex items-start justify-between mb-3 sm:mb-4 gap-2">
                <div className="flex items-start gap-2 sm:gap-3 flex-1 min-w-0">
                  <FileText size={20} className="text-gray-400 mt-1 flex-shrink-0 sm:w-6 sm:h-6" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm sm:text-base break-words">{fileData.file.name}</p>
                    <p className="text-xs sm:text-sm text-gray-500">
                      {(fileData.file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                  {fileData.status === 'success' && (
                    <CheckCircle size={18} className="text-green-500 sm:w-5 sm:h-5" />
                  )}
                  {fileData.status === 'error' && (
                    <AlertCircle size={18} className="text-red-500 sm:w-5 sm:h-5" />
                  )}
                  {fileData.status === 'uploading' && (
                    <Loader2 size={18} className="text-blue-500 animate-spin sm:w-5 sm:h-5" />
                  )}
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors p-1"
                  >
                    <X size={18} className="sm:w-5 sm:h-5" />
                  </button>
                </div>
              </div>

              {/* Metadata Fields */}
              {fileData.status !== 'success' && fileData.status !== 'error' && (
                <div className="space-y-3 sm:space-y-4 mb-3 sm:mb-4">
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
                      Title *
                    </label>
                    <input
                      type="text"
                      value={fileData.title || ''}
                      onChange={(e) =>
                        updateFileMetadata(index, { title: e.target.value })
                      }
                      className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter document title"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
                      Layer
                    </label>
                    <select
                      value={fileData.layer || ''}
                      onChange={(e) =>
                        updateFileMetadata(index, { layer: e.target.value as DocumentLayer || undefined })
                      }
                      className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    >
                      <option value="">Select Layer (Optional)</option>
                      <option value="policy">Policy (BRC Standards)</option>
                      <option value="principle">Principle (Quality Manual)</option>
                      <option value="sop">SOP (Standard Operating Procedure)</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Classify document by layer: Policy (high-level requirements), Principle (how to meet requirements), or SOP (practical steps)
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
                      Category
                    </label>
                    <input
                      type="text"
                      value={fileData.category || ''}
                      onChange={(e) =>
                        updateFileMetadata(index, { category: e.target.value })
                      }
                      className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Safety, Quality, Operations"
                    />
                  </div>

                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
                      Tags (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={fileData.tags?.join(', ') || ''}
                      onChange={(e) => handleTagInput(index, e.target.value)}
                      className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., safety, compliance, standards"
                    />
                  </div>
                </div>
              )}

              {/* Error Message */}
              {fileData.status === 'error' && fileData.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <p className="text-sm text-red-700">{fileData.error}</p>
                </div>
              )}

              {/* Success Message */}
              {fileData.status === 'success' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                  <p className="text-sm text-green-700">
                    Document uploaded successfully!
                  </p>
                </div>
              )}

              {/* Upload Button */}
              {fileData.status === 'pending' && (
                <button
                  onClick={() => handleUpload(index)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm sm:text-base"
                >
                  Upload
                </button>
              )}

              {/* Retry Button */}
              {fileData.status === 'error' && (
                <button
                  onClick={() => {
                    updateFileMetadata(index, { status: 'pending', error: undefined });
                    handleUpload(index);
                  }}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm sm:text-base"
                >
                  Retry Upload
                </button>
              )}
            </div>
          ))}

          {/* Success Summary */}
          {hasSuccessFiles && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-700">
                {files.filter((f) => f.status === 'success').length} document(s) uploaded
                successfully!
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Upload;
