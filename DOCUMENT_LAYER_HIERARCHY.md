# Document Layer Hierarchy

## Overview

The document management system uses a three-layer hierarchy to organize documents according to their purpose and level of detail. This structure ensures clear relationships between high-level requirements and practical implementation.

## Layer Structure

### 1. Policy (BRC Standards Layer)

**Purpose:** High-level requirements and standards from BRC (British Retail Consortium) or other regulatory bodies.

**Characteristics:**
- Defines **WHAT** must be achieved
- Contains regulatory requirements and standards
- Sets the foundation for compliance
- Examples: "All food products must meet BRC Food Safety Standard requirements"

**When to use:** Upload or generate documents that contain official standards, regulations, or high-level policy statements.

---

### 2. Principle (Quality Manual Layer) ⭐ **THE BRIDGE LAYER**

**Purpose:** The critical middle layer that bridges Policy and SOPs. Principles explain **"How do we prove that we meet each policy clause?"**

**Key Functions:**
- **Bridges Policy to SOPs:** Connects high-level BRC requirements to practical procedures
- **Defines Compliance Proof:** Explains how compliance with policy requirements is demonstrated
- **Ensures Consistency:** Defines consistent expectations across all functions:
  - Technical
  - Health & Safety (H&S)
  - Environment
  - Operations
  - HR
- **Provides Framework:** Establishes the framework that SOPs will follow
- **Explains "What" and "Why":** Before SOPs define the "how"

**Characteristics:**
- Answers: "How do we prove we meet each policy clause?"
- Defines the approach and methodology
- Sets expectations for all departments
- Links policy requirements to practical implementation
- Examples: "We demonstrate compliance with BRC food safety requirements through documented HACCP plans, regular audits, and supplier verification processes"

**When to use:** Generate or upload documents that explain:
- How compliance is demonstrated
- The approach taken to meet policy requirements
- Cross-functional expectations
- The framework for operational procedures

---

### 3. SOP (Standard Operating Procedure Layer)

**Purpose:** Practical, step-by-step procedures for implementation.

**Characteristics:**
- Defines **HOW** to perform specific tasks
- Contains detailed procedures and instructions
- Provides actionable steps for staff
- Examples: "Step 1: Wash hands. Step 2: Put on gloves. Step 3: Check temperature..."

**When to use:** Generate or upload documents that contain:
- Detailed operational procedures
- Step-by-step instructions
- Specific task guidance
- Work instructions

---

## Layer Relationships

```
┌─────────────────────────────────────┐
│   POLICY (BRC Standards)            │
│   "WHAT must be achieved"            │
│   High-level requirements            │
└──────────────┬──────────────────────┘
               │
               │ Explained by
               ▼
┌─────────────────────────────────────┐
│   PRINCIPLE (Quality Manual)        │
│   "How do we prove compliance?"      │
│   Bridge between Policy & SOPs       │
│   Consistent expectations            │
└──────────────┬──────────────────────┘
               │
               │ Implemented through
               ▼
┌─────────────────────────────────────┐
│   SOP (Standard Operating Procedure) │
│   "HOW to perform tasks"             │
│   Practical step-by-step procedures  │
└─────────────────────────────────────┘
```

## Why Principles Matter

**Without Principles:**
- Policy requirements remain abstract
- SOPs may not clearly link to policy compliance
- Different departments may interpret requirements differently
- Compliance proof is unclear

**With Principles:**
- Clear explanation of how policy compliance is demonstrated
- Consistent approach across all functions
- SOPs are guided by a clear framework
- Audit and compliance become straightforward

## Best Practices

1. **Start with Policy:** Upload or reference BRC standards and policy documents
2. **Create Principles:** Generate Principle documents that explain how each policy clause is proven
3. **Develop SOPs:** Create SOPs that implement the Principles in practical steps
4. **Link Documents:** Use SharePoint links to connect related documents across layers
5. **Maintain Consistency:** Ensure Principles define expectations consistently across Technical, H&S, Environment, Operations, and HR functions

## Example Flow

**Policy Document:**
> "BRC Standard 3.1.1: The site shall have a documented food safety and quality management system."

**Principle Document (Quality Manual):**
> "We demonstrate compliance with BRC Standard 3.1.1 through:
> - Documented HACCP plans reviewed annually
> - Internal audit program with quarterly reviews
> - Management review meetings with documented actions
> - Supplier verification and approval processes
> 
> All functions (Technical, H&S, Environment, Operations, HR) follow these principles to ensure consistent compliance."

**SOP Document:**
> "Procedure for Conducting Internal Audits:
> Step 1: Schedule audit using audit calendar
> Step 2: Review relevant documentation
> Step 3: Conduct on-site inspection
> Step 4: Document findings
> Step 5: Create corrective action plan
> Step 6: Follow up on actions..."

## Using the System

### When Uploading Documents:
- Select the appropriate layer when uploading
- Use the layer descriptions to guide your selection
- Link related documents using SharePoint links

### When Generating Documents:
- Select the layer from the dropdown
- The system will guide document generation based on the layer
- Principle documents will emphasize compliance proof and cross-functional consistency

### Document Library:
- Filter documents by layer to see the hierarchy
- Use layer badges to quickly identify document types
- Link documents across layers using SharePoint links

---

**Remember:** Principles are the bridge that makes the entire system work. They answer the critical question: "How do we prove we meet each policy clause?" and ensure consistency across all functions.