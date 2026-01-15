"""Document generator for creating templated documents."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.chat_service import ChatService
from app.services.vector_store import VectorStoreManager

class DocumentGenerator:
    """Service for generating professional documents using AI."""

    def __init__(self):
        """Initialize the document generator."""
        self.chat_service = ChatService()
        self.vector_store = VectorStoreManager()

    def _get_layer_guidance(self, layer: Optional[str]) -> str:
        """Get layer-specific guidance for document generation."""
        if layer == "principle":
            return """
        IMPORTANT: This is a PRINCIPLE document (Quality Manual layer).
        Principles bridge Policy and SOPs by answering: "How do we prove we meet each policy clause?"
        Focus on:
        - Explaining how compliance with policy requirements is demonstrated
        - Defining consistent expectations across all functions (Technical, H&S, Environment, Operations, HR)
        - Bridging BRC requirements to practical implementation
        - Providing the framework that SOPs will follow
        - Explaining the "what" and "why" before SOPs define the "how"
        """
        elif layer == "policy":
            return """
        IMPORTANT: This is a POLICY document (BRC Standards layer).
        Focus on high-level requirements and standards from BRC.
        """
        elif layer == "sop":
            return """
        IMPORTANT: This is an SOP document (Standard Operating Procedure layer).
        Focus on practical, step-by-step procedures for implementation.
        """
        return ""

    async def generate_document(
        self,
        document_type: str,
        title: str,
        author: str,
        data: Dict[str, Any],
        use_standards: bool = True,
        format: str = "markdown",
        document_reference: Optional[str] = None,
        issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a document based on type and provided data.

        Args:
            document_type: Type of document (risk-assessment, method-statement, etc.)
            title: Document title
            author: Document author
            data: Document-specific data
            use_standards: Whether to include relevant standards from knowledge base
            format: Output format (markdown, docx, pdf)

        Returns:
            Dict containing generated content
        """

        # Get relevant standards if requested
        standards_context = ""
        if use_standards:
            standards_context = await self._get_relevant_standards(document_type, data)

        # Generate document based on type
        if document_type == "principle":
            content = await self._generate_principle(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "risk-assessment":
            content = await self._generate_risk_assessment(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "method-statement":
            content = await self._generate_method_statement(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "safe-work-procedure":
            content = await self._generate_safe_work_procedure(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "quality-control-plan":
            content = await self._generate_quality_control_plan(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "inspection-checklist":
            content = await self._generate_inspection_checklist(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "training-record":
            content = await self._generate_training_record(title, author, data, standards_context, document_reference, issue_date, layer)
        elif document_type == "incident-report":
            content = await self._generate_incident_report(title, author, data, standards_context, document_reference, issue_date, layer)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")

        return {"content": content}

    async def _get_relevant_standards(self, document_type: str, data: Dict[str, Any]) -> str:
        """Get relevant standards from the knowledge base."""
        try:
            # Create a search query based on document type and data
            search_terms = []

            if document_type == "principle":
                # For Principles, search for related BRC clauses and policy documents
                search_terms.extend(["BRC clause", "policy", "quality manual", "compliance"])
                if "brcClause" in data:
                    search_terms.append(data["brcClause"][:100])
                if "clauseNumber" in data:
                    search_terms.append(f"BRC {data['clauseNumber']}")
            elif document_type == "risk-assessment":
                search_terms.extend(["risk assessment", "hazard", "safety", "control measures"])
                if "activityDescription" in data:
                    search_terms.append(data["activityDescription"][:50])
            elif document_type == "method-statement":
                search_terms.extend(["method statement", "work procedure", "safety procedure"])
                if "activity" in data:
                    search_terms.append(data["activity"])
            else:
                search_terms.append(document_type.replace("-", " "))

            query = " ".join(search_terms)

            # Search the knowledge base
            query_embedding = self.chat_service.embedding_service.generate_embedding(query)
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=5,
                query_text=query
            )

            if results:
                standards_text = "\n\nRelevant Standards from Knowledge Base:\n"
                for result in results:
                    title = result.get('title', 'Unknown Document')
                    content = result.get('content', '')[:500]  # Limit content length
                    standards_text += f"\n**{title}:**\n{content}...\n"
                return standards_text

        except Exception as e:
            print(f"Error getting relevant standards: {e}")

        return ""

    async def _analyze_existing_sops(self, principle_topic: str) -> str:
        """Analyze existing SOPs to extract common themes and identify gaps."""
        try:
            # Search for SOP documents in the knowledge base
            query = f"SOP standard operating procedure {principle_topic}"
            query_embedding = self.chat_service.embedding_service.generate_embedding(query)
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=10,
                query_text=query
            )

            if not results:
                return ""

            # Extract common themes from SOPs
            sop_analysis_prompt = f"""
            Analyze the following SOP documents and extract:
            1. Common controls and procedures across departments
            2. Cross-functional interactions
            3. Consistency indicators
            4. Variability or gaps
            5. Behavior expectations
            6. What should be elevated into a Principle

            SOP Documents:
            {json.dumps([{'title': r.get('title', ''), 'content': r.get('content', '')[:500]} for r in results[:5]], indent=2)}

            Provide a structured analysis focusing on what is common, what is inconsistent, and what should be documented as a Principle.
            """

            analysis_response = await self.chat_service.chat(
                query=sop_analysis_prompt,
                language="en",
                temperature=0.3,
                max_tokens=2000
            )

            return analysis_response["response"]

        except Exception as e:
            print(f"Error analyzing SOPs: {e}")
            return ""

    async def _generate_principle(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a Principle document following the structured template."""
        
        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        
        # Analyze existing SOPs if requested
        sop_analysis = ""
        if data.get('analyzeExistingSOPs'):
            sop_analysis = await self._analyze_existing_sops(data.get('brcClause', title))
        
        prompt = f"""
        Generate a comprehensive Principle document (Quality Manual layer) that bridges Policy and SOPs.
        This document explains "How do we prove we meet each policy clause?"

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        BRC CLAUSE: {data.get('brcClause', '')}
        CLAUSE NUMBER: {data.get('clauseNumber', 'N/A')}

        INTENT OF THE CLAUSE:
        {data.get('intent', '')}

        RISK OF NON-COMPLIANCE:
        {data.get('riskOfNonCompliance', '')}

        CORE ORGANISATIONAL COMMITMENTS:
        {json.dumps(data.get('coreCommitments', []), indent=2)}

        EVIDENCE EXPECTATIONS:
        {json.dumps(data.get('evidenceExpectations', []), indent=2)}

        CROSS-FUNCTIONAL RESPONSIBILITIES:
        {json.dumps(data.get('crossFunctionalResponsibilities', []), indent=2)}

        DECISION LOGIC / RATIONALE:
        {data.get('decisionLogic', 'Not specified')}

        {standards}

        {f'SOP ANALYSIS:\n{sop_analysis}' if sop_analysis else ''}

        Create a professional Principle document following this EXACT structure:

        DOCUMENT HEADER:
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        - BRC Clause Number: {data.get('clauseNumber', 'N/A')}

        DOCUMENT BODY (follow this structure exactly):

        1. BRC CLAUSE REFERENCE
           - Quote the BRC clause or policy requirement
           - Reference number if provided

        2. INTENT OF THE CLAUSE
           - Explain what this clause is intended to achieve
           - Why it exists in the BRC standard
           - {data.get('intent', '')}

        3. RISK OF NON-COMPLIANCE
           - Clearly articulate the risks if this clause is not met
           - Impact on food safety, quality, or regulatory compliance
           - {data.get('riskOfNonCompliance', '')}

        4. CORE ORGANISATIONAL COMMITMENTS
           - List the key commitments the organization makes to meet this clause
           - These are high-level promises that guide all operations
           - {json.dumps(data.get('coreCommitments', []), indent=2)}

        5. EVIDENCE EXPECTATIONS
           - Define what evidence demonstrates compliance with this clause
           - Types of records, documentation, or proof required
           - How compliance is measured and verified
           - {json.dumps(data.get('evidenceExpectations', []), indent=2)}

        6. CROSS-FUNCTIONAL RESPONSIBILITIES
           - Define responsibilities for each function:
             * Technical
             * Health & Safety (H&S)
             * Environment
             * Operations
             * HR
           - Ensure consistent expectations across all functions
           - {json.dumps(data.get('crossFunctionalResponsibilities', []), indent=2)}

        7. DECISION LOGIC / RATIONALE
           - Explain the decision logic behind this Principle
           - Rationale for the approach taken
           - {data.get('decisionLogic', 'Not specified')}

        8. LINKED SOPs AND CONTROLS
           - Reference related SOPs that implement this Principle
           - Key controls that support compliance
           - {f'Include analysis of existing SOPs:\n{sop_analysis}' if sop_analysis else 'Reference SOPs that implement this Principle'}

        9. REVIEW AND APPROVAL
           - Review date: {data.get('reviewDate', datetime.now().strftime('%Y-%m-%d'))}
           - Approval section

        CRITICAL REQUIREMENTS:
        - This is a PRINCIPLE document - it bridges Policy and SOPs
        - Focus on "How do we prove we meet each policy clause?"
        - Define consistent expectations across ALL functions
        - Use professional quality-management language
        - Ensure cross-references to related documents
        - Make it clear how SOPs will implement this Principle
        - Format professionally with clear sections and subsections
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=5000  # More tokens for comprehensive Principle documents
        )

        return response["response"]

    async def _generate_risk_assessment(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a risk assessment document."""

        # Format issue date
        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Risk Assessment document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        ACTIVITY: {data.get('activityDescription', '')}
        LOCATION: {data.get('location', '')}
        RESPONSIBLE PERSON: {data.get('responsiblePerson', '')}
        {layer_guidance}

        HAZARDS:
        {json.dumps(data.get('hazards', []), indent=2)}

        RISK RATINGS:
        {json.dumps(data.get('riskRatings', []), indent=2)}

        {standards}

        Create a professional risk assessment document that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Executive Summary
        2. Activity Description and Scope
        3. Hazard Identification
        4. Risk Assessment Matrix (with likelihood, severity, and risk levels)
        5. Existing Control Measures
        6. Additional Control Measures Required
        7. Residual Risk Assessment
        8. Review and Approval section

        Format the document professionally with clear headings, tables where appropriate, and proper risk scoring (Low/Medium/High/Very High).
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        Include the review date: {data.get('reviewDate', datetime.now().strftime('%Y-%m-%d'))}
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,  # Lower temperature for more structured output
            max_tokens=4000
        )

        return response["response"]

    async def _generate_method_statement(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a method statement document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Method Statement document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        ACTIVITY: {data.get('activity', '')}
        SCOPE: {data.get('scope', '')}
        LOCATION: {data.get('location', '')}

        RESOURCES:
        {json.dumps(data.get('resources', []), indent=2)}

        PROCEDURE STEPS:
        {json.dumps(data.get('procedure', []), indent=2)}

        SAFETY REQUIREMENTS:
        {json.dumps(data.get('safetyRequirements', []), indent=2)}

        QUALITY CHECKS:
        {json.dumps(data.get('qualityChecks', []), indent=2)}

        RESPONSIBLE PERSONS:
        {json.dumps(data.get('responsiblePersons', {}), indent=2)}

        {standards}

        Create a professional method statement document that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Executive Summary
        2. Scope and Objectives
        3. Resources Required
        4. Step-by-step Procedure
        5. Safety Requirements and PPE
        6. Quality Control Measures
        7. Emergency Procedures
        8. Review and Approval section

        Format the document professionally with numbered steps, clear responsibilities, and safety emphasis.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        Include the review date: {data.get('reviewDate', datetime.now().strftime('%Y-%m-%d'))}
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]

    async def _generate_safe_work_procedure(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a safe work procedure document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Safe Work Procedure document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        ACTIVITY: {data.get('activity', '')}
        SCOPE: {data.get('scope', '')}
        LOCATION: {data.get('location', '')}

        PROCEDURE STEPS:
        {json.dumps(data.get('procedure', []), indent=2)}

        SAFETY REQUIREMENTS:
        {json.dumps(data.get('safetyRequirements', []), indent=2)}

        QUALITY CHECKS:
        {json.dumps(data.get('qualityChecks', []), indent=2)}

        {standards}

        Create a professional safe work procedure document that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Purpose and Scope
        2. Responsibilities
        3. Safety Requirements and PPE
        4. Step-by-step Procedure
        5. Quality Control Measures
        6. Emergency Procedures
        7. Training Requirements
        8. Review and Approval section

        Format the document professionally with clear step numbering, safety warnings, and compliance emphasis.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]

    async def _generate_quality_control_plan(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a quality control plan document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Quality Control Plan document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        PROJECT/ACTIVITY: {data.get('activity', '')}
        SCOPE: {data.get('scope', '')}

        QUALITY OBJECTIVES:
        {json.dumps(data.get('qualityObjectives', []), indent=2)}

        CONTROL MEASURES:
        {json.dumps(data.get('controlMeasures', []), indent=2)}

        INSPECTION CRITERIA:
        {json.dumps(data.get('inspectionCriteria', []), indent=2)}

        {standards}

        Create a professional quality control plan that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Quality Objectives and Standards
        2. Quality Control Procedures
        3. Inspection and Testing Requirements
        4. Acceptance Criteria
        5. Non-conformance Procedures
        6. Documentation and Records
        7. Review and Approval section

        Format the document professionally with clear quality standards and measurable criteria.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]

    async def _generate_inspection_checklist(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate an inspection checklist document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Inspection Checklist document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        INSPECTION TYPE: {data.get('inspectionType', '')}
        LOCATION/AREA: {data.get('location', '')}

        CHECKLIST ITEMS:
        {json.dumps(data.get('checklistItems', []), indent=2)}

        CRITICAL ITEMS:
        {json.dumps(data.get('criticalItems', []), indent=2)}

        {standards}

        Create a professional inspection checklist that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Inspection Purpose and Scope
        2. Pre-inspection Requirements
        3. Detailed Checklist Items (Pass/Fail/NA options)
        4. Critical Safety Items
        5. Non-conformance Reporting
        6. Inspection Records and Sign-off
        7. Review and Approval section

        Format as a practical checklist with clear pass/fail criteria and space for comments.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]

    async def _generate_training_record(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate a training record document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Training Record document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        TRAINING COURSE/PROGRAM: {data.get('courseName', '')}
        TRAINING TYPE: {data.get('trainingType', '')}

        LEARNING OBJECTIVES:
        {json.dumps(data.get('objectives', []), indent=2)}

        PARTICIPANTS:
        {json.dumps(data.get('participants', []), indent=2)}

        ASSESSMENT METHODS:
        {json.dumps(data.get('assessments', []), indent=2)}

        {standards}

        Create a professional training record that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Training Program Details
        2. Learning Objectives
        3. Participant Details
        4. Training Content Summary
        5. Assessment Results
        6. Competency Verification
        7. Certification and Records
        8. Review and Approval section

        Format as a formal training record with completion verification and certification details.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]

    async def _generate_incident_report(
        self, title: str, author: str, data: Dict[str, Any], standards: str,
        document_reference: Optional[str] = None, issue_date: Optional[str] = None,
        layer: Optional[str] = None
    ) -> str:
        """Generate an incident report document."""

        formatted_issue_date = issue_date if issue_date else datetime.now().strftime('%Y-%m-%d')
        layer_guidance = self._get_layer_guidance(layer)
        
        prompt = f"""
        Generate a comprehensive Incident Report document with the following information:

        DOCUMENT REFERENCE: {document_reference or 'TBD'}
        ISSUE DATE: {formatted_issue_date}
        TITLE: {title}
        AUTHOR: {author}
        {layer_guidance}
        INCIDENT TYPE: {data.get('incidentType', '')}
        DATE/TIME: {data.get('incidentDateTime', '')}
        LOCATION: {data.get('location', '')}

        INCIDENT DESCRIPTION:
        {data.get('description', '')}

        IMMEDIATE ACTIONS TAKEN:
        {json.dumps(data.get('immediateActions', []), indent=2)}

        PERSONS INVOLVED:
        {json.dumps(data.get('personsInvolved', []), indent=2)}

        ROOT CAUSE ANALYSIS:
        {data.get('rootCause', '')}

        PREVENTIVE ACTIONS:
        {json.dumps(data.get('preventiveActions', []), indent=2)}

        {standards}

        Create a professional incident report that includes:
        
        DOCUMENT HEADER (at the top):
        - Document Reference: {document_reference or 'TBD'}
        - Issue Date: {formatted_issue_date}
        - Document Title: {title}
        - Author: {author}
        
        DOCUMENT BODY:
        1. Incident Summary and Classification
        2. Detailed Description
        3. Immediate Response Actions
        4. Persons Involved and Witnesses
        5. Root Cause Analysis
        6. Corrective and Preventive Actions
        7. Lessons Learned
        8. Review and Approval section

        Format as a formal incident investigation report with clear analysis and action items.
        The Document Reference and Issue Date must appear prominently at the top of the document, before the title.
        """

        response = await self.chat_service.chat(
            query=prompt,
            language="en",
            temperature=0.3,
            max_tokens=4000
        )

        return response["response"]
