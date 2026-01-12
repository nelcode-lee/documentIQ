# Cost Breakdown for RAG System Technologies

## Overview

This document provides a detailed cost breakdown for the technologies used in the Cranswick Technical Standards Agent RAG (Retrieval Augmented Generation) system.

**Last Updated:** January 2025  
**Note:** All prices are in USD and are estimates based on published pricing. Actual costs may vary based on usage patterns, regional pricing, and enterprise agreements.

### Architecture Diagram

📐 **System Architecture View:** [View Architectural Diagram](https://www.figma.com/board/THCfeBYbAn1ArqOtXupYJE/Untitled?node-id=0-1&t=VOIPzkigmo2TA8Fg-1)

This diagram provides a visual overview of the system architecture, showing how all components interact.

---

## Technology Stack

### 1. **OpenAI API** (Standard OpenAI)
- **Embeddings Model:** `text-embedding-ada-002`
- **Chat Model:** `gpt-4` (configurable to `gpt-3.5-turbo` or `gpt-4-turbo`)

### 2. **Azure AI Search** (formerly Azure Cognitive Search)
- Vector storage and hybrid search
- Document indexing

### 3. **Azure Blob Storage**
- Original document file storage

### 4. **Compute/Hosting** (Not specified - options included)
- Backend (FastAPI) hosting
- Frontend (React/Vite) hosting

---

## Detailed Cost Breakdown

### 1. OpenAI API Costs

#### Embeddings (`text-embedding-ada-002`)
- **Price:** $0.0001 per 1K tokens (~750 words)
- **Alternative:** `text-embedding-3-small` at $0.00002 per 1K tokens (80% cheaper!)

**Usage Scenarios:**
- **Document Upload:** Each document chunked into ~500 token pieces
  - 10-page document ≈ 5,000 tokens ≈ $0.0005 per document upload
  - 100 documents/month ≈ $0.05/month

- **Query Embedding:** ~50 tokens per query
  - 1,000 queries/month ≈ 50K tokens ≈ $0.005/month
  - 10,000 queries/month ≈ 500K tokens ≈ $0.05/month

**Monthly Embedding Costs:**
| Documents Uploaded | Queries | Monthly Cost |
|-------------------|---------|--------------|
| 10 docs | 100 queries | ~$0.01 |
| 50 docs | 500 queries | ~$0.03 |
| 100 docs | 1,000 queries | ~$0.10 |
| 500 docs | 5,000 queries | ~$0.50 |
| 1,000 docs | 10,000 queries | ~$1.00 |

#### Chat Completions

**GPT-4 (Current Configuration):**
- Input: **$0.03 per 1K tokens**
- Output: **$0.06 per 1K tokens**
- Average query: ~2,000 input tokens (context) + 700 output tokens (response)
- Cost per query: ~$(0.03 × 2) + $(0.06 × 0.7) = **~$0.082 per query**

**GPT-3.5-turbo (Recommended for cost savings):**
- Input: **$0.0015 per 1K tokens**
- Output: **$0.002 per 1K tokens**
- Average query: ~2,000 input tokens + 700 output tokens
- Cost per query: ~$(0.0015 × 2) + $(0.002 × 0.7) = **~$0.0044 per query** (95% cheaper!)

**GPT-4-turbo (Balance of quality/speed/cost):**
- Input: **$0.01 per 1K tokens**
- Output: **$0.03 per 1K tokens**
- Average query: ~2,000 input tokens + 700 output tokens
- Cost per query: ~$(0.01 × 2) + $(0.03 × 0.7) = **~$0.041 per query** (50% cheaper than GPT-4)

**Monthly Chat Completion Costs:**

| Model | Queries/Month | Monthly Cost |
|-------|--------------|--------------|
| **GPT-4** | 100 | $8.20 |
| | 500 | $41.00 |
| | 1,000 | $82.00 |
| | 5,000 | $410.00 |
| | 10,000 | $820.00 |
| **GPT-3.5-turbo** | 100 | $0.44 |
| | 500 | $2.20 |
| | 1,000 | $4.40 |
| | 5,000 | $22.00 |
| | 10,000 | $44.00 |
| **GPT-4-turbo** | 100 | $4.10 |
| | 500 | $20.50 |
| | 1,000 | $41.00 |
| | 5,000 | $205.00 |
| | 10,000 | $410.00 |

---

### 2. Azure AI Search Costs

Azure AI Search pricing is based on **Search Units (SU)** which include compute, storage, and operations.

#### Pricing Tiers:
- **Free Tier:** 50 MB storage, 3 indexes (development/testing only)
- **Basic:** $75/month per SU (3 replicas, 2 partitions = 1 SU)
  - Storage: 2 GB per partition
  - ~25K searches/day included, then $0.20 per 1,000 searches
- **Standard S1:** $250/month per SU
  - Storage: 25 GB per partition
  - ~200K searches/day included
- **Standard S2:** $1,000/month per SU
  - Storage: 100 GB per partition
  - ~1.6M searches/day included
- **Standard S3:** $2,000/month per SU
  - Storage: 200 GB per partition
  - ~3.2M searches/day included

**Recommendation for This System:**
- **Basic Tier ($75/month)** is sufficient for:
  - < 1,000 documents
  - < 100K searches/month
  - Small to medium enterprise use

**Monthly Azure AI Search Costs:**

| Usage Level | Tier | Monthly Cost |
|-------------|------|--------------|
| Development/Testing | Free | $0 |
| Small (< 100 docs, < 10K searches) | Basic | $75 |
| Medium (< 1K docs, < 100K searches) | Basic | $75 |
| Large (< 5K docs, < 500K searches) | Standard S1 | $250 |
| Enterprise (> 5K docs, > 500K searches) | Standard S2 | $1,000+ |

**Additional Costs:**
- **Indexer operations:** Included in tier
- **Storage:** Included in tier (2-200 GB depending on tier)
- **Extra searches:** $0.20 per 1,000 searches beyond tier limits (Basic tier)

---

### 3. Azure Blob Storage Costs

Azure Blob Storage is very cost-effective for document storage.

#### Pricing (Hot Access Tier):
- **Storage:** $0.018 per GB/month (first 50 TB)
- **Write operations:** $0.005 per 10,000 transactions
- **Read operations:** $0.0004 per 10,000 transactions

**Usage Scenarios:**
- Average document: ~5 MB (PDF, DOCX)
- 100 documents ≈ 500 MB ≈ $0.009/month
- 1,000 documents ≈ 5 GB ≈ $0.09/month
- 10,000 documents ≈ 50 GB ≈ $0.90/month

**Monthly Azure Blob Storage Costs:**

| Documents | Storage (GB) | Monthly Cost |
|-----------|--------------|--------------|
| 100 | 0.5 | ~$0.01 |
| 500 | 2.5 | ~$0.05 |
| 1,000 | 5 | ~$0.09 |
| 5,000 | 25 | ~$0.45 |
| 10,000 | 50 | ~$0.90 |

**Note:** Write/read operations are negligible (typically < $0.10/month even with heavy usage).

---

### 4. Compute/Hosting Costs

The backend (FastAPI) and frontend (React) need hosting. Options and costs:

#### Option A: Azure App Service (Recommended for Azure Integration)
- **Basic B1:** $13/month (1 core, 1.75 GB RAM)
- **Standard S1:** $70/month (1 core, 1.75 GB RAM, auto-scale, staging slots)
- **Standard S2:** $140/month (2 cores, 3.5 GB RAM)

**Recommendation:** Basic B1 ($13/month) for small to medium use, Standard S1 ($70/month) for production with auto-scaling.

#### Option B: Azure Container Instances
- **Per vCPU:** ~$0.000012/second (~$31/month per vCPU)
- **Per GB RAM:** ~$0.0000015/second (~$4/month per GB)
- Typical: 1 vCPU, 1 GB RAM ≈ $35/month

#### Option C: Azure Virtual Machines
- **B1s (1 vCPU, 1 GB RAM):** ~$10/month
- **B2s (2 vCPU, 4 GB RAM):** ~$40/month

#### Option D: Frontend Hosting (Static Site)
- **Azure Static Web Apps:** Free tier available, $9/month for custom domains
- **Azure Blob Storage Static Website:** $0.018/GB storage + $0.005 per 10K operations (essentially free for small sites)

**Monthly Compute/Hosting Costs:**

| Setup | Backend | Frontend | Total |
|-------|---------|----------|-------|
| **Development** | Azure App Service Basic B1 ($13) | Static Web Apps Free ($0) | **$13/month** |
| **Production (Small)** | Azure App Service Standard S1 ($70) | Static Web Apps ($9) | **$79/month** |
| **Production (Medium)** | Azure App Service Standard S2 ($140) | Static Web Apps ($9) | **$149/month** |
| **Container Option** | Azure Container Instances ($35) | Static Web Apps ($9) | **$44/month** |

---

## Total Monthly Cost Scenarios

### Scenario 1: Small Organization (< 100 documents, 500 queries/month)
**Model: GPT-3.5-turbo**

| Service | Cost |
|---------|------|
| OpenAI Embeddings | $0.03 |
| OpenAI Chat (GPT-3.5-turbo) | $2.20 |
| Azure AI Search (Basic) | $75.00 |
| Azure Blob Storage | $0.01 |
| Compute/Hosting (Basic) | $13.00 |
| **Total** | **~$90.24/month** |

### Scenario 2: Medium Organization (500 documents, 2,000 queries/month)
**Model: GPT-4-turbo**

| Service | Cost |
|---------|------|
| OpenAI Embeddings | $0.10 |
| OpenAI Chat (GPT-4-turbo) | $82.00 |
| Azure AI Search (Basic) | $75.00 |
| Azure Blob Storage | $0.05 |
| Compute/Hosting (Standard S1) | $70.00 |
| **Total** | **~$227.15/month** |

**With GPT-3.5-turbo:** ~$149.15/month (save $78/month)

### Scenario 3: Large Organization (2,000 documents, 10,000 queries/month)
**Model: GPT-4**

| Service | Cost |
|---------|------|
| OpenAI Embeddings | $0.50 |
| OpenAI Chat (GPT-4) | $820.00 |
| Azure AI Search (Standard S1) | $250.00 |
| Azure Blob Storage | $0.18 |
| Compute/Hosting (Standard S2) | $140.00 |
| **Total** | **~$1,210.68/month** |

**With GPT-4-turbo:** ~$631.68/month (save $579/month)  
**With GPT-3.5-turbo:** ~$314.68/month (save $896/month - 74% reduction!)

### Scenario 4: Enterprise (10,000 documents, 50,000 queries/month)
**Model: GPT-4-turbo (recommended for balance)**

| Service | Cost |
|---------|------|
| OpenAI Embeddings | $1.00 |
| OpenAI Chat (GPT-4-turbo) | $2,050.00 |
| Azure AI Search (Standard S2) | $1,000.00 |
| Azure Blob Storage | $0.90 |
| Compute/Hosting (Standard S2) | $140.00 |
| **Total** | **~$3,191.90/month** |

**With GPT-3.5-turbo:** ~$1,154.90/month (save $2,037/month - 64% reduction!)

---

## Cost Optimization Recommendations

### 🎯 High Impact Cost Savings

1. **Switch from GPT-4 to GPT-3.5-turbo** (if quality is acceptable)
   - **Savings:** 95% reduction in chat costs
   - **Trade-off:** Slightly lower response quality
   - **Action:** Change `OPENAI_MODEL=gpt-3.5-turbo` in `.env`

2. **Use GPT-4-turbo instead of GPT-4**
   - **Savings:** 50% reduction in chat costs
   - **Trade-off:** Minimal (GPT-4-turbo is often faster and newer)
   - **Action:** Change `OPENAI_MODEL=gpt-4-turbo` in `.env`

3. **Optimize chunk size and context**
   - Reduce `top_k` from 7 to 5 (already optimized)
   - Reduce `max_tokens` from 700 to 500 (if acceptable)
   - **Potential savings:** 10-20% on chat costs

### 💡 Medium Impact Savings

4. **Use `text-embedding-3-small` instead of `text-embedding-ada-002`**
   - **Savings:** 80% reduction in embedding costs
   - **Bonus:** Better performance
   - **Action:** Change `OPENAI_EMBEDDING_MODEL=text-embedding-3-small` in `.env`

5. **Start with Azure App Service Basic tier**
   - Upgrade only when needed (auto-scaling available)
   - **Savings:** $57/month vs Standard S1

6. **Use Free tier Azure AI Search for development**
   - **Savings:** $75/month during development/testing

### ⚡ Long-term Optimizations

7. **Implement response caching**
   - Cache common queries/responses
   - **Potential savings:** 20-30% on chat costs for repeated queries

8. **Batch document processing**
   - Process multiple documents in single operations
   - **Potential savings:** Minimal, but improves efficiency

9. **Monitor and optimize search index**
   - Remove unused indexes
   - Optimize index structure
   - **Potential savings:** Avoid unnecessary tier upgrades

---

## Annual Cost Projections

### Small Organization (500 queries/month, GPT-3.5-turbo)
- **Monthly:** ~$90/month
- **Annual:** **~$1,080/year**

### Medium Organization (2,000 queries/month, GPT-4-turbo)
- **Monthly:** ~$227/month
- **Annual:** **~$2,724/year**

### Large Organization (10,000 queries/month, GPT-4)
- **Monthly:** ~$1,211/month (or $315/month with GPT-3.5-turbo)
- **Annual:** **~$14,532/year** (or **~$3,780/year** with GPT-3.5-turbo)

### Enterprise (50,000 queries/month, GPT-4-turbo)
- **Monthly:** ~$3,192/month (or $1,155/month with GPT-3.5-turbo)
- **Annual:** **~$38,304/year** (or **~$13,860/year** with GPT-3.5-turbo)

---

## Cost Comparison: GPT-4 vs GPT-3.5-turbo

| Usage Level | GPT-4 Annual | GPT-3.5-turbo Annual | Savings |
|-------------|--------------|---------------------|---------|
| 500 queries/month | $984 | $52.80 | $931.20 (95%) |
| 2,000 queries/month | $3,936 | $105.60 | $3,830.40 (97%) |
| 10,000 queries/month | $19,680 | $528.00 | $19,152.00 (97%) |
| 50,000 queries/month | $98,400 | $2,640.00 | $95,760.00 (97%) |

**Note:** GPT-3.5-turbo is often sufficient for technical document Q&A and can provide 95%+ cost savings!

---

## Important Notes

1. **Prices are estimates** - Actual costs depend on:
   - Regional pricing differences
   - Enterprise agreements/discounts
   - Actual usage patterns
   - Azure reserved capacity discounts

2. **OpenAI API pricing** - Based on published pricing as of January 2025. Check [OpenAI Pricing](https://openai.com/pricing) for latest rates.

3. **Azure pricing** - Based on published pricing. Enterprise customers may receive discounts. Check [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) for exact costs.

4. **Model selection** - The biggest cost driver is the chat model choice:
   - **GPT-4:** Best quality, highest cost
   - **GPT-4-turbo:** Best balance of quality/speed/cost
   - **GPT-3.5-turbo:** Good quality for technical docs, 95% cheaper

5. **Scaling considerations** - Costs scale linearly with:
   - Number of queries
   - Document uploads (one-time embedding cost)
   - Storage (very cheap - Azure Blob Storage)

---

## Next Steps

1. **Start with GPT-3.5-turbo** to minimize costs
2. **Monitor usage** for first month to establish baseline
3. **Upgrade to GPT-4-turbo** if quality needs improvement
4. **Use Azure cost management** tools to track spending
5. **Set up budget alerts** in Azure Portal

---

**Questions or need help optimizing costs?** Review the optimization recommendations above or consider consulting with an Azure/OpenAI expert.
