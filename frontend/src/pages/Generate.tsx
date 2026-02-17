/** Principle Document Generator - Simplified version that leverages AI and existing documents */

import { useState } from 'react';
import { FileText, Download, Eye, Loader2, Search, BookOpen, Sparkles, Info } from 'lucide-react';
import type { DocumentFormat } from '../types';
import { generateService } from '../services/generateService';

const FORMATS: { value: DocumentFormat; label: string }[] = [
  { value: 'pdf', label: 'PDF Document (Branded)' },
  { value: 'docx', label: 'Microsoft Word (DOCX)' },
  { value: 'markdown', label: 'Markdown' },
];

const Generate = () => {
  // Simple required fields
  const [title, setTitle] = useState('');
  const [brcClauseSearch, setBrcClauseSearch] = useState('');
  const [author, setAuthor] = useState('');
  const [format, setFormat] = useState<DocumentFormat>('pdf');
  
  // Optional fields (collapsed by default)
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [documentReference, setDocumentReference] = useState('');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [version, setVersion] = useState('1.0');
  const [additionalContext, setAdditionalContext] = useState('');
  
  // Output
  const [preview, setPreview] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDocumentId, setGeneratedDocumentId] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!title.trim()) {
      alert('Please enter a title for the Principle document');
      return;
    }
    if (!brcClauseSearch.trim()) {
      alert('Please enter a BRC clause number or description to search for');
      return;
    }
    if (!author.trim()) {
      alert('Please enter the author name');
      return;
    }

    setIsGenerating(true);
    setPreview('');

    try {
      // Simplified request - AI will do the heavy lifting
      const request = {
        documentType: 'principle' as const,
        format,
        title,
        author,
        documentReference: documentReference || undefined,
        issueDate: issueDate || undefined,
        version,
        layer: 'principle' as const,
        useStandards: true,  // Always search knowledge base
        data: {
          brcClause: brcClauseSearch,  // This will be used to search
          clauseNumber: brcClauseSearch.match(/\d+\.?\d*\.?\d*/)?.[0] || '',
          intent: '',  // AI will generate
          riskOfNonCompliance: '',  // AI will generate
          coreCommitments: [],  // AI will generate
          evidenceExpectations: [],  // AI will generate
          crossFunctionalResponsibilities: [],  // AI will generate
          analyzeExistingSOPs: true,  // Always analyze SOPs
          additionalContext: additionalContext || undefined,
        },
      };

      const response = await generateService.generateDocument(request);
      setPreview(response.content);
      setGeneratedDocumentId(response.documentId);
    } catch (error: any) {
      console.error('Error generating document:', error);
      alert(error.response?.data?.detail || 'Failed to generate document. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (generatedDocumentId) {
      try {
        await generateService.downloadDocument(generatedDocumentId);
      } catch (error) {
        console.error('Error downloading document:', error);
        alert('Failed to download document. Please try again.');
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BookOpen className="text-purple-600" size={32} />
          Principle Generator
        </h1>
        <p className="text-gray-600 mt-2 text-sm sm:text-base">
          Create Principle documents that bridge BRC Policy to SOPs - powered by AI
        </p>
      </div>

      {/* How it works */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-5 mb-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center gap-2">
          <Sparkles size={20} className="text-purple-600" />
          How it Works
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <div className="flex items-center gap-2 font-semibold text-purple-800 mb-2">
              <span className="w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs">1</span>
              Enter BRC Clause
            </div>
            <div className="text-gray-600">Enter a clause number or search term (e.g., "1.1.1" or "food safety policy")</div>
          </div>
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <div className="flex items-center gap-2 font-semibold text-purple-800 mb-2">
              <span className="w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs">2</span>
              AI Searches & Analyzes
            </div>
            <div className="text-gray-600">AI retrieves relevant policies from your library and analyzes related SOPs</div>
          </div>
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <div className="flex items-center gap-2 font-semibold text-purple-800 mb-2">
              <span className="w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs">3</span>
              Principle Generated
            </div>
            <div className="text-gray-600">Complete Principle document with evidence, responsibilities & SOP links</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form Section */}
        <div className="space-y-6">
          {/* Main Form - Simple */}
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText size={20} className="text-purple-600" />
              Create Principle Document
            </h2>
            
            <div className="space-y-4">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Principle Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base"
                  placeholder="e.g., Food Safety Management Principle"
                />
              </div>

              {/* BRC Clause Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  BRC Clause / Policy Search *
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={brcClauseSearch}
                    onChange={(e) => setBrcClauseSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base"
                    placeholder="e.g., 1.1.1 or 'food safety policy' or 'HACCP'"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Enter a clause number, topic, or keyword - AI will search your document library
                </p>
              </div>

              {/* Author */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author *
                </label>
                <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base"
                  placeholder="Your name"
                />
              </div>

              {/* Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Output Format
                </label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value as DocumentFormat)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-base bg-white"
                >
                  {FORMATS.map((fmt) => (
                    <option key={fmt.value} value={fmt.value}>
                      {fmt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Advanced Options (Collapsible) */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full px-5 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm font-medium text-gray-700">Advanced Options</span>
              <span className={`transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>
            
            {showAdvanced && (
              <div className="px-5 pb-5 pt-2 border-t border-gray-100 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Document Reference
                    </label>
                    <input
                      type="text"
                      value={documentReference}
                      onChange={(e) => setDocumentReference(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                      placeholder="e.g., PRIN-001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Version
                    </label>
                    <input
                      type="text"
                      value={version}
                      onChange={(e) => setVersion(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                      placeholder="1.0"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Issue Date
                  </label>
                  <input
                    type="date"
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Additional Context (Optional)
                  </label>
                  <textarea
                    value={additionalContext}
                    onChange={(e) => setAdditionalContext(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    rows={3}
                    placeholder="Any specific focus areas, site considerations, or additional requirements..."
                  />
                </div>
              </div>
            )}
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Info size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">AI-Powered Generation</p>
                <p>The AI will automatically:</p>
                <ul className="list-disc list-inside mt-1 space-y-1 text-blue-700">
                  <li>Search your document library for relevant BRC policies</li>
                  <li>Analyze existing SOPs to identify common themes</li>
                  <li>Generate evidence expectations and compliance proof</li>
                  <li>Define cross-functional responsibilities (Technical, H&S, Ops, etc.)</li>
                  <li>Create linked SOP references</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !title.trim() || !brcClauseSearch.trim() || !author.trim()}
            className="w-full px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold text-lg flex items-center justify-center gap-3 shadow-lg"
          >
            {isGenerating ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                <span>Searching documents & generating...</span>
              </>
            ) : (
              <>
                <Sparkles size={24} />
                <span>Generate Principle Document</span>
              </>
            )}
          </button>
        </div>

        {/* Preview Section */}
        <div className="lg:sticky lg:top-4 lg:h-[calc(100vh-2rem)]">
          <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Eye size={20} className="text-purple-600" />
                Preview
              </h2>
              {preview && (
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                >
                  <Download size={16} />
                  Download {format.toUpperCase()}
                </button>
              )}
            </div>
            <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 border border-gray-200">
              {preview ? (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-xs sm:text-sm font-mono text-gray-800 leading-relaxed">
                    {preview}
                  </pre>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center max-w-sm">
                    <BookOpen size={56} className="mx-auto mb-4 text-purple-200" />
                    <p className="text-base font-medium mb-2">Ready to Generate</p>
                    <p className="text-sm text-gray-400">
                      Enter a BRC clause or topic above, and AI will create a complete Principle document by searching your existing policies and SOPs.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Generate;
