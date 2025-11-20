# **ParentPath: AI-Powered Educational Equity Platform**
## **Complete Technical Requirements & Product Requirements Document**

**Version:** 1.0
**Date:** November 16, 2025
**Project Code:** ParentPath (School Digest Enhanced)
**Challenge:** Google AI + Qdrant - Societal Impact Challenge

---

## **TABLE OF CONTENTS**

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Challenge Alignment](#2-product-vision--challenge-alignment)
3. [System Architecture](#3-system-architecture)
4. [Data Models](#4-data-models)
5. [API Specifications](#5-api-specifications)
6. [Integration Requirements](#6-integration-requirements)
7. [Core Workflows](#7-core-workflows)
8. [Security & Compliance](#8-security--compliance)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Success Metrics](#11-success-metrics)
12. [Implementation Timeline](#12-implementation-timeline)
13. [Challenge Submission Package](#13-challenge-submission-package)

---

## **1. EXECUTIVE SUMMARY**

### **1.1 Product Overview**

**ParentPath** is a multimodal AI system that transforms dense school newsletters into personalized, actionable digests delivered via WhatsApp/SMS. The system addresses educational inequity by ensuring every family—regardless of language, tech literacy, or socioeconomic status—has equal access to school opportunities.

### **1.2 Core Innovation**

**Hybrid Intelligence Architecture:**
- **Gemini 2.0 Flash** for multimodal understanding (PDF, images, voice, tables)
- **Qdrant vector database** for semantic search and duplicate detection
- **Rule-based targeting** for zero-error audience matching
- **Human-in-loop review** for full traceability and compliance

### **1.3 Target Users**

**Primary:** Parents of elementary school students (K-7)
**Secondary:** School administrators, parent committees
**Pilot:** St. Matthew's Elementary Grade 7 Graduation Committee (15 families)
**Scale:** 200+ private/public schools in BC (50,000+ families)

### **1.4 Key Metrics**

| Metric | Baseline | Target (4 weeks) |
|--------|----------|------------------|
| Parsing accuracy | Manual (100%) | 95% automated |
| Parent engagement | 20% (newsletter) | 70% (digest) |
| Missed deadlines | 40% complaint rate | <5% |
| Language support | English only | 4 languages |
| Cost per family | N/A | <$10/year |

### **1.5 Technical Stack Summary**

```
Frontend:     Minimal web portal (FastAPI templates)
Backend:      FastAPI + Python 3.11+
Databases:    PostgreSQL 15+ (structured), Qdrant (vectors)
AI/ML:        Gemini 2.0 Flash (multimodal), Gemini embeddings
Storage:      MinIO (S3-compatible) or local filesystem
Messaging:    WhatsApp Cloud API, Twilio SMS
Orchestration: Redis (job queue), NATS (optional event bus)
Deployment:   Docker Compose → Railway/GCP
Monitoring:   Prometheus + Grafana, Sentry
```

---

## **2. PRODUCT VISION & CHALLENGE ALIGNMENT**

### **2.1 Problem Statement**

**Educational Inequity Through Information Overload:**

Current state:
- Schools send 15+ page weekly newsletters (PDF/email)
- 95% content irrelevant to any given family
- No filtering by grade, activity, or language
- Parents miss critical deadlines (permission slips, hot lunch, fundraisers)
- Low-income families disproportionately affected (less time to parse dense docs)
- Non-English speakers excluded (newsletters rarely translated)

**Quantified Impact:**
- 40% of parents report missing important announcements
- 60% permission slip completion rate (should be 95%+)
- School offices spend 10+ hrs/week answering "When is X?" questions
- 80% of families prefer messaging apps over email (WhatsApp > 95% adoption in immigrant communities)

### **2.2 Google AI Challenge Alignment**

**Challenge Requirement: "Intake → Understand → Decide → Review → Deliver"**

| Challenge Phase | ParentPath Implementation |
|-----------------|---------------------------|
| **Intake** | Multi-format: PDF, scanned flyers, CSV, HTML, voice messages |
| **Understand** | Gemini multimodal parsing + OCR + table extraction |
| **Decide** | Hybrid: AI confidence scoring + rule-based targeting + Qdrant similarity |
| **Review** | Human-in-loop approval queue + parent crowdsourced corrections |
| **Deliver** | Personalized WhatsApp digests + multilingual translation + calendar integration |

**Societal Challenge Addressed:** Educational equity, parent engagement, language accessibility

### **2.3 Qdrant Challenge Alignment**

**Challenge Requirement: "Search, Memory, or Recommendations over multimodal data"**

**ParentPath Qdrant Use Cases:**

1. **Semantic Search:**
   - Parent: "When's the next basketball thing?" → Finds "basketball practice" even without exact keywords
   - Admin: "Find all events in November mentioning field trips" → Cross-newsletter search

2. **Memory (RAG):**
   - Store all historical newsletters as vectors
   - Context-aware responses: "Last time basketball practice changed, here's what happened..."
   - Pattern detection: "This deadline is similar to ones parents usually miss"

3. **Recommendations:**
   - "Your child is in Band - you might like Orchestra auditions"
   - "Families with similar profiles attended X event"
   - Duplicate detection: "This item appears in 3 newsletters - consolidate"

4. **Multimodal:**
   - Text embeddings (newsletter content)
   - Image embeddings (scanned flyers via Gemini Vision)
   - Code snippets (if building developer tools later)

### **2.4 Success Criteria (Challenge Submission)**

**Technical Excellence:**
- [ ] Demonstrate Gemini multimodal parsing (PDF, image, table, voice)
- [ ] Implement Qdrant for ≥3 use cases (search, memory, recommendations)
- [ ] Achieve 95%+ parsing accuracy with full traceability
- [ ] Support 4+ languages via Gemini translation

**Societal Impact:**
- [ ] Pilot with real families (not mock data)
- [ ] Measure engagement lift (baseline → pilot)
- [ ] Document accessibility improvements (language, tech literacy)
- [ ] Show cost-effectiveness (<$10/family/year)

**Innovation:**
- [ ] Novel hybrid intelligence (AI + rules + human)
- [ ] Open-source core components (parser, targeting engine)
- [ ] Scalable architecture (1 school → 1000 schools)

---

## **3. SYSTEM ARCHITECTURE**

### **3.1 High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTAKE LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  Email      │  Upload    │  WhatsApp   │  Voice     │  CSV      │
│  Forward    │  Portal    │  Photo      │  Message   │  Import   │
└──────┬──────┴──────┬─────┴──────┬──────┴──────┬─────┴──────┬────┘
       │             │            │             │            │
       └─────────────┴────────────┴─────────────┴────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PREPROCESSING & STORAGE                        │
├─────────────────────────────────────────────────────────────────┤
│  • Hash deduplication                                           │
│  • Format detection (PDF, image, HTML, audio)                   │
│  • Store raw file → MinIO (S3) or local filesystem             │
│  • Enqueue parse job → Redis                                    │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNDERSTANDING LAYER (Gemini)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Gemini 2.0 Flash Multimodal API                  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • PDF text extraction (native)                          │  │
│  │  • Image OCR (scanned flyers, permission slips)          │  │
│  │  • Table parsing (embedded CSVs in PDFs)                 │  │
│  │  • Audio transcription (voice message → text)            │  │
│  │  • Structured extraction → JSON schema                   │  │
│  │  • Confidence scoring per field                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Structured Items + Embeddings                    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  {                                                        │  │
│  │    title: "Basketball practice",                         │  │
│  │    date: "2024-11-20",                                   │  │
│  │    grade: 5,                                             │  │
│  │    activity: "Basketball",                               │  │
│  │    confidence: 0.95,                                     │  │
│  │    embedding: [0.1, 0.2, ..., 0.n]  # 768-dim vector    │  │
│  │  }                                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          DECISION LAYER (Hybrid Intelligence)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐  ┌────────────────────┐               │
│  │   Qdrant Vector    │  │   PostgreSQL       │               │
│  │   Search           │  │   Rules Engine     │               │
│  ├────────────────────┤  ├────────────────────┤               │
│  │ • Duplicate check  │  │ • Confidence gate  │               │
│  │ • Similarity match │  │ • Date validation  │               │
│  │ • Historical RAG   │  │ • SQL targeting    │               │
│  │ • Recommendations  │  │ • Business rules   │               │
│  └────────┬───────────┘  └────────┬───────────┘               │
│           │                       │                           │
│           └───────────┬───────────┘                           │
│                       ▼                                       │
│           ┌─────────────────────┐                            │
│           │  Confidence Score   │                            │
│           ├─────────────────────┤                            │
│           │  ≥90%: Auto-approve │                            │
│           │  70-90%: Review     │                            │
│           │  <70%: Reject + log │                            │
│           └──────────┬──────────┘                            │
└──────────────────────┼──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              REVIEW LAYER (Human-in-Loop)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                Admin Review Queue                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • Pending items with confidence scores                  │  │
│  │  • Gemini reasoning explanation                          │  │
│  │  • Similar past items (Qdrant search)                    │  │
│  │  • One-click: Approve / Edit / Reject                    │  │
│  │  • Audit trail: who, when, why                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Parent Crowdsourced Corrections                │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Parent: "Basketball time changed to 4pm"               │  │
│  │  → Ticket created                                        │  │
│  │  → Qdrant finds original Item                            │  │
│  │  → Gemini validates change                               │  │
│  │  → Auto-approve if high confidence                       │  │
│  │  → Award points to parent                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│             DELIVERY LAYER (Personalized Output)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Household Targeting Engine                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  SQL Query:                                              │  │
│  │  SELECT DISTINCT p.id FROM parents p                     │  │
│  │  JOIN children c ON c.parent_id = p.id                   │  │
│  │  WHERE c.grade IN item.audience_tags                     │  │
│  │     OR c.activities && item.audience_tags                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Gemini Translation & Formatting                │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • Translate to parent's language (EN, PA, TL, ZH)       │  │
│  │  • Format digest (emoji, sections, calendar links)       │  │
│  │  • Generate .ics calendar attachments                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Multi-Channel Delivery                         │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  WhatsApp Cloud API  │  Twilio SMS  │  Email (fallback) │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Store delivery logs → PostgreSQL + Qdrant (for search)        │
└─────────────────────────────────────────────────────────────────┘
```

---

**For the complete PRD with all sections (Data Models, API Specs, Integration Requirements, Workflows, Security, Testing, Deployment, Metrics, Timeline, and Challenge Submission), please refer to the full document.**

This PRD serves as the authoritative specification for ParentPath development, challenge submission, and production deployment.

---

## Quick Reference

- **Architecture Diagrams**: Section 3
- **Database Schema**: Section 4
- **API Endpoints**: Section 5
- **Gemini Integration**: Section 6.1
- **Qdrant Integration**: Section 6.2
- **WhatsApp Integration**: Section 6.3
- **Testing Strategy**: Section 9
- **Deployment Options**: Section 10
- **Success Metrics**: Section 11

**Status**: Living document - updated as implementation progresses
**Last Updated**: 2025-11-17
