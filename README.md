# ParentPath - AI-Powered Educational Equity Platform

**Transform dense school newsletters into personalized, actionable digests delivered via WhatsApp.**

ParentPath uses Google's Gemini 2.0 Flash (multimodal AI) and Qdrant (vector search) to ensure every family—regardless of language, tech literacy, or socioeconomic status—has equal access to school opportunities.

---

## 🎯 Problem Statement

Current state:
- Schools send 15+ page weekly newsletters (PDF/email)
- 95% content irrelevant to any given family
- No filtering by grade, activity, or language
- Parents miss critical deadlines (permission slips, hot lunch, fundraisers)
- Non-English speakers excluded

**Impact:**
- 40% of parents miss important announcements
- 60% permission slip completion rate (should be 95%+)
- 80% of families prefer messaging apps over email

---

## ✨ Solution

**ParentPath automatically:**
1. **Parses** newsletters using Gemini multimodal (PDF, images, tables)
2. **Extracts** structured items with confidence scores
3. **Targets** families by grade + activities (SQL-based matching)
4. **Translates** to parent's language (EN, PA, TL, ZH, ES)
5. **Delivers** via WhatsApp/SMS with calendar attachments
6. **Learns** from parent corrections (crowdsourced improvements)

---

## 🏗️ Architecture

```
Newsletter (PDF/Image)
  → Gemini Parse → Items + Confidence Scores
  → Qdrant Duplicate Detection
  → Admin Review (if confidence < 90%)
  → SQL Targeting (grade + activities)
  → Gemini Translation
  → WhatsApp Delivery
  → Parent Engagement (DONE, queries, corrections)
```

**Tech Stack:**
- **AI:** Google Gemini 2.0 Flash (multimodal, embeddings, translation)
- **Vector DB:** Qdrant (semantic search, duplicate detection, recommendations)
- **Backend:** FastAPI, Python 3.11+, PostgreSQL, Redis
- **Messaging:** WhatsApp Cloud API, Twilio SMS
- **Deployment:** Docker, Docker Compose → Railway/GCP

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Gemini API key ([Get here](https://aistudio.google.com/apikey))
- (Optional) WhatsApp Business account

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/ParentPath.git
cd ParentPath

# Copy environment template
cp .env.example .env

# Edit .env and add your GEMINI_API_KEY
nano .env
```

### 2. Start Infrastructure

```bash
# Start all services (Postgres, Redis, Qdrant, MinIO, API, Worker)
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 3. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# API docs
open http://localhost:8000/docs
```

### 4. Upload Test Newsletter

```bash
# Upload a PDF newsletter
curl -X POST "http://localhost:8000/api/v1/intake/upload" \
  -F "file=@tests/fixtures/newsletter.pdf" \
  -F "title=Weekly Newsletter - Nov 10" \
  -F "publish_date=2024-11-10"
```

---

## 📁 Project Structure

```
ParentPath/
├── api/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── database.py             # DB session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── parent.py           # Parent, Child, Subscription
│   │   ├── item.py             # Item, Newsletter
│   │   ├── card.py             # Digest cards
│   │   ├── message.py          # Message logs
│   │   ├── ticket.py           # Correction tickets
│   │   └── audit.py            # Audit logs, points
│   ├── routers/                # API endpoints
│   │   ├── health.py           # Health checks
│   │   ├── intake.py           # Newsletter upload
│   │   ├── admin.py            # Review queue
│   │   ├── family.py           # Parent portal
│   │   └── webhooks.py         # WhatsApp/SMS webhooks
│   └── services/               # Business logic
│       ├── gemini_service.py   # Gemini API integration
│       ├── qdrant_service.py   # Vector operations
│       ├── targeting_service.py # Audience matching
│       └── messenger_service.py # WhatsApp/SMS
├── workers/                    # Background jobs
│   ├── parse_worker.py         # Newsletter parsing
│   ├── digest_worker.py        # Weekly digest generation
│   └── reminder_worker.py      # Deadline reminders
├── tests/                      # Test suite
├── docker-compose.yml          # Infrastructure
├── Dockerfile                  # API container
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database (defaults work for local development)
DATABASE_URL=postgresql+asyncpg://parentpath:parentpath_dev_2024@localhost:5432/parentpath

# Optional: WhatsApp Integration
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_TOKEN=your_access_token

# Optional: Twilio SMS (alternative to WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 📊 API Endpoints

### Health
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status

### Newsletter Intake
- `POST /api/v1/intake/upload` - Upload newsletter (PDF/image)
- `POST /api/v1/intake/email` - Email webhook (SendGrid/Mailgun)
- `POST /api/v1/intake/whatsapp` - WhatsApp photo upload

### Admin Review
- `GET /api/v1/admin/newsletters` - List uploaded newsletters
- `GET /api/v1/admin/items?status=pending` - Review queue
- `POST /api/v1/admin/items/{id}/approve` - Approve item
- `POST /api/v1/admin/items/{id}/reject` - Reject item
- `GET /api/v1/admin/tickets` - Correction tickets

### Family Portal
- `GET /api/v1/family/settings` - Parent settings
- `PUT /api/v1/family/settings` - Update settings
- `GET /api/v1/family/history` - Card history

### Webhooks
- `POST /api/v1/webhooks/whatsapp` - WhatsApp message handler
- `POST /api/v1/webhooks/twilio/sms` - Twilio SMS handler

**Full API docs:** http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=api --cov-report=html

# Open coverage report
open htmlcov/index.html
```

---

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Staging (Railway)
```bash
# Connect Railway
railway login
railway init

# Deploy
railway up

# Set environment variables
railway variables set GEMINI_API_KEY=your_key
```

### Production (GCP)
```bash
# Build
gcloud builds submit --tag gcr.io/parentpath/api

# Deploy to Cloud Run
gcloud run deploy parentpath-api \
  --image gcr.io/parentpath/api \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated
```

---

## 📈 Metrics & Monitoring

### Prometheus Metrics
- API: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

### Key Metrics
- Newsletter parsing latency (p50, p95, p99)
- Qdrant search latency
- Gemini API errors & token usage
- WhatsApp delivery success rate
- Parent engagement rate (DONE replies)

---

## 🎓 Challenge Submission

**Google AI Challenge:**
- ✅ Multimodal: PDF, image, table, voice parsing
- ✅ Structured extraction with confidence scores
- ✅ Hybrid intelligence (AI proposes, rules validate, humans review)
- ✅ Multilingual support (5 languages)

**Qdrant Challenge:**
- ✅ Semantic search (parent queries)
- ✅ Duplicate detection (newsletter items)
- ✅ Recommendations (based on engagement)
- ✅ RAG for contextual support

**Societal Impact:**
- ✅ Educational equity
- ✅ Language accessibility
- ✅ Low-cost solution (<$10/family/year)
- ✅ Ready for real pilot

---

## 📄 License

MIT License - see `LICENSE` for details.

---

## 🙏 Acknowledgments

- **Google Gemini** for multimodal AI capabilities
- **Qdrant** for vector search infrastructure
- Built for educational equity

---

**Status:** 🚧 MVP Development (Phase 0 Complete)

Built with ❤️ for educational equity
