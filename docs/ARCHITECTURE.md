# ParentPath: System Architecture

**Version**: 1.0
**Last Updated**: 2025-11-17
**Status**: Phase 0 Complete, Production Architecture Defined

---

## Overview

ParentPath is a **hybrid intelligence platform** combining:
- **Gemini 2.0 Flash** (multimodal AI) for understanding
- **Qdrant** (vector database) for semantic memory
- **Rule-based systems** for deterministic targeting
- **Human-in-loop** for validation and corrections

This architecture prioritizes **educational equity** through personalized, multilingual, accessible communication.

---

## System Layers

### 1. Intake Layer

**Supported Formats**:
- PDF newsletters (primary)
- Scanned images/photos (OCR via Gemini Vision)
- Email forwarding (SendGrid/Mailgun webhooks)
- WhatsApp photo uploads (parent-submitted)
- CSV imports (pizza lunch orders, attendance)

**Preprocessing**:
- SHA-256 hash deduplication
- File type detection
- Storage (local filesystem or MinIO S3)
- Job queue (Redis for background processing)

---

### 2. Understanding Layer (Gemini)

**Gemini 2.0 Flash** multimodal processing:

```python
# Input: PDF newsletter
# Output: Structured items + confidence scores

{
  "type": "Event",
  "title": "Basketball practice",
  "date": "2024-11-20",
  "time": "16:00",
  "location": "Gym",
  "audience_tags": ["grade_5", "Basketball"],
  "confidence_score": 0.95,
  "embedding": [0.1, 0.2, ..., 0.768]  # 768-dim vector
}
```

**Capabilities**:
- Native PDF text extraction
- Image OCR (scanned flyers)
- Table parsing (embedded CSVs)
- Audio transcription (voice messages)
- Multilingual translation (EN, PA, TL, ZH, ES)

**Free Tier Limits**:
- 15 requests/minute (RPM)
- 1,000,000 tokens/minute (TPM)
- 1,500 requests/day (RPD)

Sufficient for **200 families** (12 newsletters/month + 800 digests/month).

---

### 3. Decision Layer (Hybrid Intelligence)

#### 3A. Qdrant Vector Database

**3 Collections**:

1. **newsletter_items** (768-dim, COSINE distance)
   - Semantic search for parent queries
   - Duplicate detection (similarity > 0.85)
   - Historical RAG (context-aware responses)

2. **parent_messages** (768-dim)
   - Conversation history
   - Intent detection patterns
   - Community insights

3. **correction_tickets** (768-dim)
   - Crowdsourced corrections
   - Auto-validation via similarity
   - Trust scoring

**Operations**:
- Indexing: Batch upsert (100 items)
- Search: <100ms p95 latency
- Storage: Persistent (local or cloud)

#### 3B. PostgreSQL Rules Engine

**Deterministic Logic**:
- Audience targeting (SQL joins)
- Date validation
- Confidence thresholds
- Business rules (permissions, compliance)

**Confidence Gates**:
- ≥90%: Auto-approve
- 70-90%: Human review queue
- <70%: Reject + log reasoning

---

### 4. Review Layer (Human-in-Loop)

#### Admin Review Queue
- Pending items with confidence scores
- Gemini reasoning explanations
- Similar items (Qdrant search)
- One-click approve/edit/reject
- Full audit trail

#### Parent Crowdsourcing
- Error reporting via WhatsApp
- Qdrant similarity matching
- Gemini validation
- Points/gamification system
- Trust scoring (accuracy tracking)

---

### 5. Delivery Layer

#### Household Targeting Engine

**SQL Query** (deterministic, zero-error):
```sql
SELECT DISTINCT p.id
FROM parents p
JOIN children c ON c.parent_id = p.id
JOIN subscriptions s ON s.parent_id = p.id
WHERE
  -- Grade matching
  (c.grade = ANY(item.audience_tags::int[]))
  OR
  -- Activity matching
  (s.activity = ANY(item.audience_tags))
  OR
  -- School-wide
  ('all' = ANY(item.audience_tags))
```

#### Message Formatting

**Gemini Translation**:
- Preserve emoji, URLs, formatting
- Adapt date/time formats to locale
- Maintain friendly, concise tone

**Sections** (emoji-based):
```
📋 GRADE 5
• Basketball practice: Nov 20 at 4pm
• Permission slip due: Nov 18

🏀 BASKETBALL
• Game vs Central: Nov 22 at 3pm
• Team photo day: Nov 25

🔗 Quick Links
[Calendar] [Sign Up] [Settings]
```

#### Multi-Channel Delivery

**Priority Order**:
1. WhatsApp Cloud API (preferred)
2. Twilio SMS (fallback)
3. Email (last resort)

**Delivery Tracking**:
- Message sent
- Delivered (carrier confirmed)
- Read (if supported)
- Failed (with retry logic)

---

## Data Flow

```
Newsletter Upload
  ↓
Hash Check (dedupe)
  ↓
Gemini Parse
  ↓
Items + Embeddings
  ↓
┌─────────────┬─────────────┐
│ Confidence  │  Qdrant     │
│ Gate        │  Duplicate  │
│             │  Check      │
└─────┬───────┴──────┬──────┘
      │              │
      ↓              ↓
  ≥90%: Auto     Found?
  Approve        ↓
      │       Merge Items
      ↓
  Index in Qdrant
      ↓
  SQL Targeting
      ↓
  Create Cards
      ↓
  Generate Digests
      ↓
  Gemini Translate
      ↓
  WhatsApp/SMS Send
      ↓
  Log Delivery
```

---

## Database Schema (Summary)

**Core Tables**:
- `parents` - Family accounts (channel, language, preferences)
- `children` - Kids in household (grade, division)
- `subscriptions` - Activity enrollments
- `items` - Parsed newsletter items
- `newsletters` - Source documents
- `cards` - Personalized digest cards
- `message_logs` - Delivery tracking
- `tickets` - Crowdsourced corrections
- `audit_logs` - Full traceability

**Key Relationships**:
```
parents (1) ←→ (N) children
parents (1) ←→ (N) cards
items (1) ←→ (N) cards
parents (1) ←→ (N) tickets
```

**Indexes**:
- GIN index on `items.audience_tags` (array matching)
- B-tree on `items.date` (temporal queries)
- Unique on `newsletters.file_hash` (deduplication)

---

## API Design

**RESTful Endpoints**:
- `POST /api/v1/intake/upload` - Newsletter upload
- `GET /api/v1/admin/items?status=pending` - Review queue
- `POST /api/v1/admin/items/{id}/approve` - Approve item
- `GET /api/v1/family/settings` - Parent preferences
- `POST /api/v1/webhooks/whatsapp` - Inbound messages

**Authentication**:
- Admin: BasicAuth (MVP) → Google OAuth (production)
- Parents: JWT tokens (signed links in WhatsApp)

**Rate Limiting**:
- 5/hour for uploads (per IP)
- 10/hour for ticket submission (per parent)

---

## Background Workers

**Redis Queue** (RQ or Celery):

1. **Parse Worker**
   - Triggered: Newsletter upload
   - Actions: Gemini parse → Qdrant index → DB insert
   - Frequency: On-demand

2. **Digest Worker**
   - Triggered: Cron (Sunday 5pm)
   - Actions: Target parents → Generate digests → Send
   - Frequency: Weekly

3. **Reminder Worker**
   - Triggered: Cron (daily 8am)
   - Actions: Find deadlines → Send reminders
   - Frequency: Daily

---

## Deployment Options

### MVP (Local Development)
```
SQLite database
Qdrant in-memory or local
Gemini API (free tier)
Local file storage
No Docker required
```

### Beta (200 families)
```
PostgreSQL (Railway/Supabase)
Qdrant Cloud (free tier)
Gemini API (free tier)
MinIO or Cloud Storage
Docker Compose
```

### Production (1000+ families)
```
PostgreSQL (Cloud SQL)
Qdrant Cloud (paid tier)
Gemini API (paid tier with SLA)
Cloud Storage (GCS)
Kubernetes/Cloud Run
Load balancer
Redis cluster
Monitoring (Prometheus + Grafana)
```

---

## Security & Compliance

**Data Privacy**:
- Minimal PII (phone, grade only)
- No student academic records
- No payment information
- 1-year data retention

**FERPA Compliance**:
- Parent-led tool (not school-operated)
- Public information only (newsletters already distributed)
- No controlled student data

**Authentication**:
- JWT tokens (24hr expiry)
- Signed WhatsApp links
- Admin 2FA (production)

---

## Monitoring & Observability

**Metrics** (Prometheus):
- Newsletter parsing latency
- Qdrant search latency
- Gemini API errors & token usage
- WhatsApp delivery success rate
- Parent engagement (DONE replies)

**Logging** (structured JSON):
- All API requests
- Gemini API calls
- Qdrant operations
- Message deliveries
- Errors with stack traces

**Alerting**:
- Gemini API rate limit approaching
- Qdrant search latency >100ms
- WhatsApp delivery failures >5%
- Database connection pool exhausted

---

## Scalability Considerations

**Bottlenecks**:
1. Gemini API rate limits (15 RPM free tier)
2. Qdrant search latency (>1M vectors)
3. PostgreSQL connections (100+ concurrent)

**Mitigation**:
1. Batch newsletter parsing (off-peak hours)
2. Qdrant Cloud paid tier (better perf)
3. Connection pooling + read replicas

**Growth Path**:
- 200 families: MVP architecture sufficient
- 1,000 families: Upgrade to paid tiers
- 10,000 families: Multi-region deployment

---

## Technology Stack

**Language**: Python 3.11+

**Framework**: FastAPI (async)

**Databases**:
- PostgreSQL 15+ (structured data)
- Qdrant (vector search)
- Redis (job queue, cache)

**AI/ML**:
- Google Gemini 2.0 Flash (multimodal)
- Gemini text-embedding-004 (768-dim)

**Infrastructure**:
- Docker + Docker Compose
- Railway (staging) / GCP (production)
- MinIO (S3-compatible storage)

**Monitoring**:
- Prometheus + Grafana
- Sentry (error tracking)

**Testing**:
- pytest (unit, integration)
- Locust (load testing)

---

## Design Principles

1. **Equity First**: Every family gets equal access, regardless of language or tech literacy
2. **Hybrid Intelligence**: AI proposes, rules validate, humans review
3. **Full Traceability**: Every decision logged with reasoning
4. **Zero-Error Targeting**: Deterministic SQL prevents wrong deliveries
5. **Cost-Effective**: <$10/family/year at scale
6. **Open Core**: Parser and targeting engine open-sourced

---

**For implementation details, see**:
- `PRD.md` - Complete technical specifications
- `docs/ORCHESTRATION_RUNBOOK.md` - Execution plan
- `README.md` - Quick start guide

**Status**: Phase 0 complete, ready for Waves 2-4 execution
