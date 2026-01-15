/** Shared TypeScript type definitions. */

export type DocumentLayer = 'policy' | 'principle' | 'sop';

export interface Document {
  id: string;
  title: string;
  category?: string;
  tags?: string[];
  uploadedAt: string;
  status: 'processing' | 'completed' | 'error';
  source: 'uploaded' | 'generated';
  fileType?: 'pdf' | 'docx' | 'txt' | 'md';
  documentType?: DocumentType;
  author?: string;
  version?: string;
  layer?: DocumentLayer; // 'policy' | 'principle' | 'sop'
  relatedDocuments?: string[]; // IDs of related documents
  linkedTo?: string[]; // IDs of documents this is linked to
  fileSize?: number; // in bytes
  downloadUrl?: string;
  previewUrl?: string;
  sharePointUrl?: string; // SharePoint file URL
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  language?: string; // Language code: "en", "pl", "ro"
}

export interface ChatResponse {
  response: string;
  sources: string[];
  conversation_id: string;
}

export interface Analytics {
  queryVolume: {
    daily: number;
    weekly: number;
    monthly: number;
    total: number;
  };
  topDocuments: Array<{
    document_id: string;
    title: string;
    query_count: number;
    last_accessed?: string;
    total_chunks_retrieved: number;
  }>;
  topQueries: Array<{
    query: string;
    count: number;
    average_response_time_ms: number;
  }>;
  averageResponseTime: number;
  totalQueries: number;
  timeRange: {
    start: string;
    end: string;
  };
}

export interface DailyMetrics {
  date: string;
  query_count: number;
  unique_conversations: number;
  average_response_time: number;
  documents_accessed: string[];
}

export type DocumentType =
  | 'risk-assessment'
  | 'method-statement'
  | 'safe-work-procedure'
  | 'quality-control-plan'
  | 'inspection-checklist'
  | 'training-record'
  | 'incident-report'
  | 'principle';

export type DocumentFormat = 'docx' | 'pdf' | 'markdown';

export interface RiskAssessmentData {
  activityDescription: string;
  location: string;
  hazards: Array<{
    hazard: string;
    whoMightBeHarmed: string;
    howHarmed: string;
  }>;
  riskRatings: Array<{
    hazard: string;
    likelihood: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost-certain';
    severity: 'negligible' | 'minor' | 'moderate' | 'major' | 'catastrophic';
    existingControls: string;
    additionalControls: string;
    residualLikelihood?: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost-certain';
    residualSeverity?: 'negligible' | 'minor' | 'moderate' | 'major' | 'catastrophic';
  }>;
  responsiblePerson: string;
  reviewDate: string;
}

export interface MethodStatementData {
  activity: string;
  scope: string;
  location: string;
  resources: string[];
  procedure: Array<{
    step: number;
    description: string;
    responsiblePerson?: string;
  }>;
  safetyRequirements: string[];
  qualityChecks: string[];
  responsiblePersons: {
    author: string;
    reviewer?: string;
    approver?: string;
  };
  reviewDate: string;
}

export interface PrincipleData {
  brcClause: string;
  clauseNumber?: string;
  intent: string;
  riskOfNonCompliance: string;
  coreCommitments: string[];
  evidenceExpectations: string[];
  crossFunctionalResponsibilities: Array<{
    function: 'Technical' | 'H&S' | 'Environment' | 'Operations' | 'HR' | string;
    responsibility: string;
  }>;
  decisionLogic?: string;
  rationale?: string;
  analyzeExistingSOPs?: boolean;
  linkedSOPs?: string[];
  relatedPolicyDocuments?: string[];
}

export interface DocumentGenerationRequest {
  documentType: DocumentType;
  format: DocumentFormat;
  title: string;
  category?: string;
  tags?: string[];
  projectReference?: string;
  siteLocation?: string;
  author: string;
  reviewDate?: string;
  version?: string;
  documentReference?: string;
  issueDate?: string;
  layer?: DocumentLayer;
  useStandards: boolean;
  data: RiskAssessmentData | MethodStatementData | PrincipleData | Record<string, any>;
}

export interface DocumentGenerationResponse {
  documentId: string;
  content: string;
  downloadUrl?: string;
  message: string;
  status: 'success' | 'error';
}
