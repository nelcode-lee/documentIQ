/** Document generation page. */

import { useState } from 'react';
import { FileText, Download, Eye, Loader2, Plus, Trash2 } from 'lucide-react';
import type { 
  DocumentType, 
  DocumentFormat, 
  DocumentGenerationRequest,
  RiskAssessmentData,
  MethodStatementData,
  PrincipleData,
  DocumentLayer
} from '../types';
import { generateService } from '../services/generateService';

const DOCUMENT_TYPES: { value: DocumentType; label: string; description: string }[] = [
  { value: 'principle', label: 'Principle (Quality Manual)', description: 'Bridge Policy and SOPs - explains how to prove compliance with policy clauses' },
  { value: 'risk-assessment', label: 'Risk Assessment', description: 'Identify hazards and assess risks with control measures' },
  { value: 'method-statement', label: 'Method Statement', description: 'Detailed procedure for carrying out work safely' },
  { value: 'safe-work-procedure', label: 'Safe Work Procedure', description: 'Step-by-step safe working instructions' },
  { value: 'quality-control-plan', label: 'Quality Control Plan', description: 'Quality assurance and control procedures' },
  { value: 'inspection-checklist', label: 'Inspection Checklist', description: 'Checklist for inspections and audits' },
  { value: 'training-record', label: 'Training Record', description: 'Document training completion and competencies' },
  { value: 'incident-report', label: 'Incident Report', description: 'Record and analyze incidents or near-misses' },
];

const FORMATS: { value: DocumentFormat; label: string }[] = [
  { value: 'docx', label: 'Microsoft Word (DOCX)' },
  { value: 'pdf', label: 'PDF Document' },
  { value: 'markdown', label: 'Markdown' },
];

const LIKELIHOOD_OPTIONS = [
  { value: 'rare', label: 'Rare', score: 1 },
  { value: 'unlikely', label: 'Unlikely', score: 2 },
  { value: 'possible', label: 'Possible', score: 3 },
  { value: 'likely', label: 'Likely', score: 4 },
  { value: 'almost-certain', label: 'Almost Certain', score: 5 },
];

const SEVERITY_OPTIONS = [
  { value: 'negligible', label: 'Negligible', score: 1 },
  { value: 'minor', label: 'Minor', score: 2 },
  { value: 'moderate', label: 'Moderate', score: 3 },
  { value: 'major', label: 'Major', score: 4 },
  { value: 'catastrophic', label: 'Catastrophic', score: 5 },
];

const Generate = () => {
  const [documentType, setDocumentType] = useState<DocumentType>('risk-assessment');
  const [format, setFormat] = useState<DocumentFormat>('docx');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [projectReference, setProjectReference] = useState('');
  const [siteLocation, setSiteLocation] = useState('');
  const [author, setAuthor] = useState('');
  const [reviewDate, setReviewDate] = useState('');
  const [version, setVersion] = useState('1.0');
  const [documentReference, setDocumentReference] = useState('');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [layer, setLayer] = useState<DocumentLayer | ''>('');
  const [useStandards, setUseStandards] = useState(true);
  const [preview, setPreview] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDocumentId, setGeneratedDocumentId] = useState<string | null>(null);

  // Risk Assessment specific fields
  const [riskData, setRiskData] = useState<RiskAssessmentData>({
    activityDescription: '',
    location: '',
    hazards: [{ hazard: '', whoMightBeHarmed: '', howHarmed: '' }],
    riskRatings: [],
    responsiblePerson: '',
    reviewDate: new Date().toISOString().split('T')[0],
  });

  // Method Statement specific fields
  const [methodData, setMethodData] = useState<MethodStatementData>({
    activity: '',
    scope: '',
    location: '',
    resources: [''],
    procedure: [{ step: 1, description: '', responsiblePerson: '' }],
    safetyRequirements: [''],
    qualityChecks: [''],
    responsiblePersons: { author: '', reviewer: '', approver: '' },
    reviewDate: new Date().toISOString().split('T')[0],
  });

  // Principle specific fields
  const [principleData, setPrincipleData] = useState<PrincipleData>({
    brcClause: '',
    clauseNumber: '',
    intent: '',
    riskOfNonCompliance: '',
    coreCommitments: [''],
    evidenceExpectations: [''],
    crossFunctionalResponsibilities: [
      { function: 'Technical', responsibility: '' },
      { function: 'H&S', responsibility: '' },
      { function: 'Environment', responsibility: '' },
      { function: 'Operations', responsibility: '' },
      { function: 'HR', responsibility: '' },
    ],
    decisionLogic: '',
    rationale: '',
    analyzeExistingSOPs: true,
    linkedSOPs: [],
    relatedPolicyDocuments: [],
  });

  const calculateRiskScore = (likelihood: string, severity: string): number => {
    const lScore = LIKELIHOOD_OPTIONS.find(o => o.value === likelihood)?.score || 0;
    const sScore = SEVERITY_OPTIONS.find(o => o.value === severity)?.score || 0;
    return lScore * sScore;
  };

  const getRiskLevel = (score: number): { level: string; color: string } => {
    if (score <= 4) return { level: 'Low', color: 'green' };
    if (score <= 9) return { level: 'Medium', color: 'yellow' };
    if (score <= 15) return { level: 'High', color: 'orange' };
    return { level: 'Very High', color: 'red' };
  };

  const handleAddHazard = () => {
    setRiskData({
      ...riskData,
      hazards: [...riskData.hazards, { hazard: '', whoMightBeHarmed: '', howHarmed: '' }],
    });
  };

  const handleRemoveHazard = (index: number) => {
    setRiskData({
      ...riskData,
      hazards: riskData.hazards.filter((_, i) => i !== index),
    });
  };

  const handleHazardChange = (index: number, field: string, value: string) => {
    const updatedHazards = [...riskData.hazards];
    updatedHazards[index] = { ...updatedHazards[index], [field]: value };
    setRiskData({ ...riskData, hazards: updatedHazards });

    // Auto-populate risk ratings
    const hazardName = field === 'hazard' ? value : updatedHazards[index].hazard;
    if (hazardName && !riskData.riskRatings.find(r => r.hazard === hazardName)) {
      setRiskData({
        ...riskData,
        hazards: updatedHazards,
        riskRatings: [
          ...riskData.riskRatings,
          { hazard: hazardName, likelihood: 'possible', severity: 'moderate', existingControls: '', additionalControls: '' },
        ],
      });
    }
  };

  const handleAddProcedureStep = () => {
    setMethodData({
      ...methodData,
      procedure: [...methodData.procedure, { step: methodData.procedure.length + 1, description: '', responsiblePerson: '' }],
    });
  };

  const handleGenerate = async () => {
    if (!title.trim() || !author.trim()) {
      alert('Please fill in all required fields (Title and Author)');
      return;
    }

    // Validate Principle-specific required fields
    if (documentType === 'principle') {
      if (!principleData.brcClause.trim()) {
        alert('Please enter the BRC Clause or Policy Requirement');
        return;
      }
      if (!principleData.intent.trim()) {
        alert('Please enter the Intent of the Clause');
        return;
      }
      if (!principleData.riskOfNonCompliance.trim()) {
        alert('Please enter the Risk of Non-Compliance');
        return;
      }
      if (principleData.coreCommitments.length === 0 || !principleData.coreCommitments[0].trim()) {
        alert('Please add at least one Core Organisational Commitment');
        return;
      }
      if (principleData.evidenceExpectations.length === 0 || !principleData.evidenceExpectations[0].trim()) {
        alert('Please add at least one Evidence Expectation');
        return;
      }
    }

    setIsGenerating(true);
    setPreview('');

    try {
      // Prepare Principle data - clean up empty values
      let preparedPrincipleData = principleData;
      if (documentType === 'principle') {
        preparedPrincipleData = {
          ...principleData,
          coreCommitments: principleData.coreCommitments.filter(c => c.trim()),
          evidenceExpectations: principleData.evidenceExpectations.filter(e => e.trim()),
          crossFunctionalResponsibilities: principleData.crossFunctionalResponsibilities.filter(
            r => r.function.trim() || r.responsibility.trim()
          ),
        };
      }

      const request: DocumentGenerationRequest = {
        documentType,
        format,
        title,
        category: category || undefined,
        tags: tags.split(',').map(t => t.trim()).filter(t => t) || undefined,
        projectReference: projectReference || undefined,
        siteLocation: siteLocation || undefined,
        author,
        reviewDate: reviewDate || undefined,
        version,
        documentReference: documentReference || undefined,
        issueDate: issueDate || undefined,
        layer: documentType === 'principle' ? 'principle' : (layer || undefined),
        useStandards,
        data: documentType === 'risk-assessment' 
          ? riskData 
          : documentType === 'principle' 
          ? preparedPrincipleData
          : methodData,
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
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Generate Document</h1>
        <p className="text-gray-600 mt-2 text-sm sm:text-base">
          Create standardized documents using AI-powered templates
        </p>
      </div>

      {/* Layer Hierarchy Explanation */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">Document Layer Hierarchy</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <div className="flex items-start gap-2">
            <span className="font-medium">1. Policy (BRC Standards):</span>
            <span>High-level requirements and standards from BRC</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-medium">2. Principle (Quality Manual):</span>
            <span>The bridge layer - explains "How do we prove we meet each policy clause?" Defines consistent expectations across all functions (Technical, H&S, Environment, Operations, HR). Links BRC requirements to practical SOPs.</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-medium">3. SOP (Standard Operating Procedure):</span>
            <span>Practical step-by-step procedures for implementation</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form Section */}
        <div className="space-y-6">
          {/* Document Type & Format */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Type & Format</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Type *
                </label>
                <select
                  value={documentType}
                  onChange={(e) => {
                    const newType = e.target.value as DocumentType;
                    setDocumentType(newType);
                    // Auto-set layer to 'principle' when Principle document type is selected
                    if (newType === 'principle') {
                      setLayer('principle');
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                >
                  {DOCUMENT_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {DOCUMENT_TYPES.find(t => t.value === documentType)?.description}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Output Format *
                </label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value as DocumentFormat)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
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

          {/* Document Metadata */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  placeholder="Enter document title"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Reference
                  </label>
                  <input
                    type="text"
                    value={documentReference}
                    onChange={(e) => setDocumentReference(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="e.g., DOC-2024-001"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Document reference number or code
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Issue Date *
                  </label>
                  <input
                    type="date"
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Date when document is issued
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="e.g., Safety, Quality"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="1.0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  placeholder="safety, compliance, standards"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Reference
                </label>
                <input
                  type="text"
                  value={projectReference}
                  onChange={(e) => setProjectReference(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  placeholder="Project code or reference"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Site Location
                </label>
                <input
                  type="text"
                  value={siteLocation}
                  onChange={(e) => setSiteLocation(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  placeholder="Site name or address"
                />
              </div>

              {documentType !== 'principle' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Layer
                  </label>
                  <select
                    value={layer}
                    onChange={(e) => setLayer(e.target.value as DocumentLayer || '')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base bg-white"
                  >
                    <option value="">Select Layer (Optional)</option>
                    <option value="policy">Policy (BRC Standards)</option>
                    <option value="principle">Principle (Quality Manual)</option>
                    <option value="sop">SOP (Standard Operating Procedure)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {layer === 'principle' && 'Principle documents bridge Policy and SOPs by explaining how to prove compliance with policy clauses.'}
                    {layer === 'policy' && 'Policy documents contain high-level BRC requirements and standards.'}
                    {layer === 'sop' && 'SOP documents contain practical step-by-step procedures for implementation.'}
                    {!layer && 'Classify this document by its layer in the hierarchy.'}
                  </p>
                </div>
              )}
              {documentType === 'principle' && (
                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                  <p className="text-xs text-purple-800">
                    <strong>Principle Document:</strong> This document will be automatically classified as a Principle (Quality Manual layer) that bridges Policy and SOPs.
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Author *
                  </label>
                  <input
                    type="text"
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Your name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Review Date
                  </label>
                  <input
                    type="date"
                    value={reviewDate}
                    onChange={(e) => setReviewDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="useStandards"
                  checked={useStandards}
                  onChange={(e) => setUseStandards(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="useStandards" className="text-sm text-gray-700">
                  Use relevant technical standards from knowledge base
                </label>
              </div>
            </div>
          </div>

          {/* Document-Specific Fields */}
          {documentType === 'risk-assessment' && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment Details</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Activity Description *
                  </label>
                  <textarea
                    value={riskData.activityDescription}
                    onChange={(e) => setRiskData({ ...riskData, activityDescription: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="Describe the activity or task"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location *
                  </label>
                  <input
                    type="text"
                    value={riskData.location}
                    onChange={(e) => setRiskData({ ...riskData, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Where will this activity take place?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hazards *
                  </label>
                  {riskData.hazards.map((hazard, index) => (
                    <div key={index} className="mb-4 p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-sm font-medium text-gray-700">Hazard {index + 1}</span>
                        {riskData.hazards.length > 1 && (
                          <button
                            onClick={() => handleRemoveHazard(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                      <div className="space-y-3">
                        <input
                          type="text"
                          value={hazard.hazard}
                          onChange={(e) => handleHazardChange(index, 'hazard', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                          placeholder="What is the hazard?"
                        />
                        <input
                          type="text"
                          value={hazard.whoMightBeHarmed}
                          onChange={(e) => handleHazardChange(index, 'whoMightBeHarmed', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                          placeholder="Who might be harmed?"
                        />
                        <input
                          type="text"
                          value={hazard.howHarmed}
                          onChange={(e) => handleHazardChange(index, 'howHarmed', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                          placeholder="How might they be harmed?"
                        />
                      </div>
                    </div>
                  ))}
                  <button
                    onClick={handleAddHazard}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Hazard
                  </button>
                </div>

                {/* Risk Ratings Table */}
                {riskData.riskRatings.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Risk Ratings & Controls
                    </label>
                    <div className="space-y-3">
                      {riskData.riskRatings.map((rating, index) => {
                        const initialScore = calculateRiskScore(rating.likelihood, rating.severity);
                        const residualScore = rating.residualLikelihood && rating.residualSeverity
                          ? calculateRiskScore(rating.residualLikelihood, rating.residualSeverity)
                          : null;
                        const initialLevel = getRiskLevel(initialScore);
                        const residualLevel = residualScore ? getRiskLevel(residualScore) : null;

                        return (
                          <div key={index} className="p-4 border border-gray-200 rounded-lg">
                            <h4 className="font-medium text-gray-900 mb-3">{rating.hazard}</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                              <div>
                                <label className="block text-xs text-gray-600 mb-1">Likelihood</label>
                                <select
                                  value={rating.likelihood}
                                  onChange={(e) => {
                                    const updated = [...riskData.riskRatings];
                                    updated[index].likelihood = e.target.value as any;
                                    setRiskData({ ...riskData, riskRatings: updated });
                                  }}
                                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                >
                                  {LIKELIHOOD_OPTIONS.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                  ))}
                                </select>
                              </div>
                              <div>
                                <label className="block text-xs text-gray-600 mb-1">Severity</label>
                                <select
                                  value={rating.severity}
                                  onChange={(e) => {
                                    const updated = [...riskData.riskRatings];
                                    updated[index].severity = e.target.value as any;
                                    setRiskData({ ...riskData, riskRatings: updated });
                                  }}
                                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                >
                                  {SEVERITY_OPTIONS.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                  ))}
                                </select>
                              </div>
                            </div>
                            <div className="mb-3">
                              <span className={`px-2 py-1 rounded text-xs font-medium bg-${initialLevel.color}-100 text-${initialLevel.color}-800`}>
                                Initial Risk: {initialLevel.level} (Score: {initialScore})
                              </span>
                            </div>
                            <div className="space-y-2">
                              <textarea
                                value={rating.existingControls}
                                onChange={(e) => {
                                  const updated = [...riskData.riskRatings];
                                  updated[index].existingControls = e.target.value;
                                  setRiskData({ ...riskData, riskRatings: updated });
                                }}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                rows={2}
                                placeholder="Existing control measures"
                              />
                              <textarea
                                value={rating.additionalControls}
                                onChange={(e) => {
                                  const updated = [...riskData.riskRatings];
                                  updated[index].additionalControls = e.target.value;
                                  setRiskData({ ...riskData, riskRatings: updated });
                                }}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                rows={2}
                                placeholder="Additional control measures required"
                              />
                            </div>
                            {residualLevel && (
                              <div className="mt-2">
                                <span className={`px-2 py-1 rounded text-xs font-medium bg-${residualLevel.color}-100 text-${residualLevel.color}-800`}>
                                  Residual Risk: {residualLevel.level} (Score: {residualScore})
                                </span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Responsible Person *
                  </label>
                  <input
                    type="text"
                    value={riskData.responsiblePerson}
                    onChange={(e) => setRiskData({ ...riskData, responsiblePerson: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Name of responsible person"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Method Statement Fields */}
          {documentType === 'method-statement' && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Method Statement Details</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Activity *
                  </label>
                  <input
                    type="text"
                    value={methodData.activity}
                    onChange={(e) => setMethodData({ ...methodData, activity: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Activity or task name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scope *
                  </label>
                  <textarea
                    value={methodData.scope}
                    onChange={(e) => setMethodData({ ...methodData, scope: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="Describe the scope of work"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Resources Required
                  </label>
                  {methodData.resources.map((resource, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={resource}
                        onChange={(e) => {
                          const updated = [...methodData.resources];
                          updated[index] = e.target.value;
                          setMethodData({ ...methodData, resources: updated });
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                        placeholder={`Resource ${index + 1}`}
                      />
                      <button
                        onClick={() => {
                          setMethodData({
                            ...methodData,
                            resources: methodData.resources.filter((_, i) => i !== index),
                          });
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => setMethodData({ ...methodData, resources: [...methodData.resources, ''] })}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Resource
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Procedure Steps
                  </label>
                  {methodData.procedure.map((step, index) => (
                    <div key={index} className="mb-3 p-3 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">Step {step.step}</span>
                        <button
                          onClick={() => {
                            setMethodData({
                              ...methodData,
                              procedure: methodData.procedure.filter((_, i) => i !== index).map((s, i) => ({ ...s, step: i + 1 })),
                            });
                          }}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                      <textarea
                        value={step.description}
                        onChange={(e) => {
                          const updated = [...methodData.procedure];
                          updated[index].description = e.target.value;
                          setMethodData({ ...methodData, procedure: updated });
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base mb-2"
                        rows={2}
                        placeholder="Step description"
                      />
                      <input
                        type="text"
                        value={step.responsiblePerson || ''}
                        onChange={(e) => {
                          const updated = [...methodData.procedure];
                          updated[index].responsiblePerson = e.target.value;
                          setMethodData({ ...methodData, procedure: updated });
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                        placeholder="Responsible person (optional)"
                      />
                    </div>
                  ))}
                  <button
                    onClick={handleAddProcedureStep}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Step
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Principle Fields */}
          {documentType === 'principle' && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Principle Document Details</h2>
              
              {/* Methodology Explanation */}
              <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-l-4 border-purple-500 rounded-lg">
                <h3 className="text-sm font-semibold text-purple-900 mb-2">📋 Principle Document Methodology</h3>
                <p className="text-xs text-gray-700 mb-3">
                  <strong>Principle documents are the critical bridge layer</strong> between Policy (BRC Standards) and SOPs (Standard Operating Procedures).
                </p>
                <div className="text-xs text-gray-700 space-y-1 mb-3">
                  <p><strong>Key Purpose:</strong> Principles answer: <em>"How do we prove that we meet each policy clause?"</em></p>
                  <p><strong>Core Functions:</strong></p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    <li><strong>Bridge Policy to SOPs:</strong> Connect high-level BRC requirements to practical procedures</li>
                    <li><strong>Define Compliance Proof:</strong> Explain how compliance with policy requirements is demonstrated</li>
                    <li><strong>Ensure Consistency:</strong> Define consistent expectations across all functions (Technical, H&S, Environment, Operations, HR)</li>
                    <li><strong>Provide Framework:</strong> Establish the framework that SOPs will follow</li>
                    <li><strong>Explain "What" and "Why":</strong> Before SOPs define the "how"</li>
                  </ul>
                </div>
                <div className="text-xs text-gray-600 italic border-t border-purple-200 pt-2">
                  <strong>Layer Hierarchy:</strong> Policy (WHAT) → Principle (HOW TO PROVE) → SOP (HOW TO DO)
                </div>
              </div>
              
              <div className="space-y-4">
                {/* BRC Clause */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    BRC Clause / Policy Requirement *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    The Policy layer requirement that this Principle bridges to SOPs. This is the "WHAT" that must be achieved.
                  </p>
                  <textarea
                    value={principleData.brcClause}
                    onChange={(e) => setPrincipleData({ ...principleData, brcClause: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="Paste the BRC clause or policy requirement this Principle addresses"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Clause Number (Optional)
                    </label>
                    <input
                      type="text"
                      value={principleData.clauseNumber}
                      onChange={(e) => setPrincipleData({ ...principleData, clauseNumber: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                      placeholder="e.g., 3.1.1"
                    />
                  </div>
                </div>

                {/* Intent */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Intent of the Clause *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Explain what this clause is intended to achieve and why it exists in the BRC standard. This helps define the "WHY" before SOPs define the "HOW".
                  </p>
                  <textarea
                    value={principleData.intent}
                    onChange={(e) => setPrincipleData({ ...principleData, intent: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="What is the intent/purpose of this BRC clause?"
                  />
                </div>

                {/* Risk of Non-Compliance */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Risk of Non-Compliance *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Clearly articulate the risks if this clause is not met. This demonstrates the importance of compliance and guides the evidence requirements.
                  </p>
                  <textarea
                    value={principleData.riskOfNonCompliance}
                    onChange={(e) => setPrincipleData({ ...principleData, riskOfNonCompliance: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="What are the risks if we don't comply with this clause?"
                  />
                </div>

                {/* Core Organisational Commitments */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Core Organisational Commitments *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Key commitments the organization makes to meet this clause. These are high-level promises that guide all operations and provide the framework SOPs will follow.
                  </p>
                  {principleData.coreCommitments.map((commitment, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={commitment}
                        onChange={(e) => {
                          const updated = [...principleData.coreCommitments];
                          updated[index] = e.target.value;
                          setPrincipleData({ ...principleData, coreCommitments: updated });
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                        placeholder={`Commitment ${index + 1}`}
                      />
                      <button
                        onClick={() => {
                          setPrincipleData({
                            ...principleData,
                            coreCommitments: principleData.coreCommitments.filter((_, i) => i !== index),
                          });
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => setPrincipleData({ ...principleData, coreCommitments: [...principleData.coreCommitments, ''] })}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Commitment
                  </button>
                </div>

                {/* Evidence Expectations */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Evidence Expectations *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    <strong>Critical for Principle documents:</strong> What evidence demonstrates compliance with this clause? This answers "How do we prove we meet each policy clause?" - the core purpose of Principle documents.
                  </p>
                  {principleData.evidenceExpectations.map((evidence, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={evidence}
                        onChange={(e) => {
                          const updated = [...principleData.evidenceExpectations];
                          updated[index] = e.target.value;
                          setPrincipleData({ ...principleData, evidenceExpectations: updated });
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                        placeholder={`Evidence type ${index + 1} (e.g., documented records, audit reports)`}
                      />
                      <button
                        onClick={() => {
                          setPrincipleData({
                            ...principleData,
                            evidenceExpectations: principleData.evidenceExpectations.filter((_, i) => i !== index),
                          });
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => setPrincipleData({ ...principleData, evidenceExpectations: [...principleData.evidenceExpectations, ''] })}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Evidence Type
                  </button>
                </div>

                {/* Cross-Functional Responsibilities */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cross-Functional Responsibilities *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    <strong>Ensures consistency across all functions:</strong> Define responsibilities for Technical, H&S, Environment, Operations, and HR. This is a key function of Principle documents - ensuring consistent expectations across all departments.
                  </p>
                  {principleData.crossFunctionalResponsibilities.map((resp, index) => (
                    <div key={index} className="mb-3 p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <input
                          type="text"
                          value={resp.function}
                          onChange={(e) => {
                            const updated = [...principleData.crossFunctionalResponsibilities];
                            updated[index].function = e.target.value;
                            setPrincipleData({ ...principleData, crossFunctionalResponsibilities: updated });
                          }}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base font-medium"
                          placeholder="Function (e.g., Technical, H&S, Environment, Operations, HR)"
                        />
                      </div>
                      <textarea
                        value={resp.responsibility}
                        onChange={(e) => {
                          const updated = [...principleData.crossFunctionalResponsibilities];
                          updated[index].responsibility = e.target.value;
                          setPrincipleData({ ...principleData, crossFunctionalResponsibilities: updated });
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                        rows={2}
                        placeholder={`${resp.function || 'Function'} responsibility for this Principle`}
                      />
                    </div>
                  ))}
                  <button
                    onClick={() => setPrincipleData({ 
                      ...principleData, 
                      crossFunctionalResponsibilities: [...principleData.crossFunctionalResponsibilities, { function: '', responsibility: '' }] 
                    })}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Function
                  </button>
                </div>

                {/* Decision Logic / Rationale */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Decision Logic / Rationale (Optional)
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Explain the decision logic or rationale behind this Principle. This helps future users understand the approach and methodology chosen.
                  </p>
                  <textarea
                    value={principleData.decisionLogic || ''}
                    onChange={(e) => setPrincipleData({ ...principleData, decisionLogic: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
                    rows={3}
                    placeholder="Explain the decision logic or rationale behind this Principle"
                  />
                </div>

                {/* Analyze Existing SOPs */}
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <input
                      type="checkbox"
                      id="analyzeSOPs"
                      checked={principleData.analyzeExistingSOPs}
                      onChange={(e) => setPrincipleData({ ...principleData, analyzeExistingSOPs: e.target.checked })}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
                    />
                    <div>
                      <label htmlFor="analyzeSOPs" className="text-sm font-medium text-gray-700 block mb-1">
                        Analyze existing SOPs to extract common themes and identify gaps
                      </label>
                      <p className="text-xs text-gray-600">
                        The system will analyze existing SOPs to identify: common controls across departments, cross-functional interactions, consistency/variability indicators, and gaps that should be elevated into this Principle document.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !title.trim() || !author.trim()}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium text-sm sm:text-base flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Generating Document...
              </>
            ) : (
              <>
                <FileText size={18} />
                Generate Document
              </>
            )}
          </button>
        </div>

        {/* Preview Section */}
        <div className="lg:sticky lg:top-4 lg:h-[calc(100vh-2rem)]">
          <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 shadow-sm h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Eye size={20} />
                Preview
              </h2>
              {preview && (
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                >
                  <Download size={16} />
                  Download
                </button>
              )}
            </div>
            <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 border border-gray-200">
              {preview ? (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-xs sm:text-sm font-mono text-gray-800">
                    {preview}
                  </pre>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <FileText size={48} className="mx-auto mb-3 text-gray-300" />
                    <p className="text-sm">Generated document preview will appear here</p>
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
