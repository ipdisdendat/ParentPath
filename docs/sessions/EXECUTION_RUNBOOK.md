# ParentPath: Production Execution Runbook (v1.0)

**System**: ParentPath Educational Equity Platform
**Version**: 1.0 (Merged Architecture)
**Date**: 2025-11-17
**Status**: Ready for Execution
**Pattern**: InfiniTEA Hybrid Orchestration (CLAUDE.md §22, §26)
**Authority**: §24 Session Handoff Protocol - Execute as written
**Evidence Ratio Target**: 95%+
**Total Time**: 6-8 hours (wall-clock with parallel execution)

---

## 📋 EXECUTIVE SUMMARY

### Architectural Foundation

**This runbook synthesizes**:
- ✅ **vdev's wave structure** - 4 waves with clean separation of concerns
- ✅ **vdev's validation gates** - 33+30+5+5 tests with explicit pass criteria
- ✅ **TEAOS archaeological grounding** - 75% code reuse from CHAI infrastructure
- ✅ **Gemini CLI hybrid approach** - Free tier for MVP, API for production

### Current State (Archaeological Inventory)

**TEAOS Infrastructure (Verified)**:
```
Existing Components               LOC    Reuse %   Adaptation Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
chai/ocr_handler.py              ~200      60%    Tesseract → Gemini CLI
chai/hardy_validator.py          ~150     100%    Use as-is
chai/batch_analyzer.py           ~300      80%    Digest generation patterns
chai/quality_scorer.py           ~100      95%    Confidence scoring
chai/gap_detector.py             ~200      90%    FAISS → Qdrant migration
chai/compliance_analyzer.py      ~250      70%    Schema adaptation
scripts/migrate_to_qdrant.py     227      95%    Batching + verification
agents/hardy_validator.py        ~150     100%    Validation gates

Total Reusable                  ~2,500     75%    ~800 lines net new
```

**Evidence**: Files verified via `ls chai/*.py` and `Read` tool during session.

### Goal

Transform **CHAI document processing** → **ParentPath educational equity** via 4-wave parallel orchestration:

```
Wave 1: Foundation (45 min sequential)
  ├─ Docker Compose (5 services)
  ├─ PostgreSQL schema (12 tables)
  └─ Seed data (3 test parents)

Wave 2: Core Services (90 min, 4 PARALLEL tracks)
  ├─ Track A: Gemini Service (CLI + API hybrid)
  ├─ Track B: Qdrant Service (3 collections)
  ├─ Track C: WhatsApp Service (send + receive)
  └─ Track D: Targeting Engine (SQL matching)

Wave 3: Application Layer (90 min, 3 PARALLEL tracks)
  ├─ Track E: FastAPI Routes (intake, admin, family)
  ├─ Track F: Background Workers (parse, send, remind)
  └─ Track G: Admin Review UI (human-in-loop)

Wave 4: Integration (2 hours sequential)
  └─ End-to-end testing + load testing
```

**Estimated Speedup**: 3-4× vs sequential (6-8 hours vs 25-30 hours)

---

## 🎯 PRE-FLIGHT CHECK (§26 MANDATORY)

**1. Can tasks run independently?**
- ✅ Wave 2: All 4 services have zero shared dependencies
- ✅ Wave 3: Routes/Workers/UI all depend on Wave 2 services (not each other)

**2. Have I consulted orchestration case studies?**
- ✅ CHAI_SESSION_ORCHESTRATION_CASE_STUDY.md (25,000 words)
- ✅ SESSION_2025_11_16 (12.5× speedup via parallel execution)
- ✅ SESSION_HANDOFF_2025_11_06 (96/96 tests, zero conflicts)
- ✅ CLAUDE.md §22 (InfiniTEA pattern with shared memory)

**3. Am I launching multiple Task calls in ONE message?**
- ✅ Wave 2: 4 Task calls in single message
- ✅ Wave 3: 3 Task calls in single message

**4. Archaeological search performed?** (§20 MANDATORY)
- ✅ CHAI infrastructure inventoried (22 files, 2,500 LOC reusable)
- ✅ Qdrant migration pattern found (scripts/migrate_to_qdrant.py:227 lines)
- ✅ Hardy validation framework exists (agents/hardy_validator.py)
- ✅ Background worker patterns exist (CHAI batch processing)

**Confidence Level**: HYPOTHETICAL (0.65) - Plan validated, pending execution evidence

---

## 🌊 WAVE 1: FOUNDATION (Sequential - 45 minutes)

**Why Sequential**: All other waves depend on this baseline.

### Deliverables

**1. Repository Structure** (TEAOS-native: SQLite-based)
```
ParentPath/
├── api/
│   ├── models/         # SQLAlchemy ORM
│   ├── routers/        # FastAPI routes
│   ├── services/       # Business logic
│   ├── templates/      # Jinja2 UI
│   └── main.py         # FastAPI app
├── workers/
│   ├── parse_worker.py
│   ├── send_worker.py
│   └── reminder_worker.py
├── tests/
│   ├── fixtures/       # Sample newsletters
│   └── test_*.py
├── scripts/
│   └── seed_data.py
├── data/
│   └── newsletters/    # Local file storage
├── requirements.txt
├── alembic.ini
├── parentpath.db       # SQLite database (TEAOS pattern)
└── _WORKING_MEMORY.md  # Shared coordination (§22)
```

**2. Database Setup** (SQLite - matches TEAOS patterns)

**Evidence**: TEAOS uses SQLite extensively:
```bash
# Found via ls -la *.db:
teaos_control.db        1.4 MB
healthcare.db           139 KB  # CHAI uses SQLite!
oracle_sessions.db      188 KB
consciousness_lessons.db 208 KB

# CHAI code directly uses sqlite3:
chai/gap_detector.py: import sqlite3
chai/graph_traversal.py: import sqlite3
```

**MVP Database**: SQLite (upgrade to PostgreSQL for beta/production)
```python
# .env
DATABASE_URL=sqlite:///parentpath.db
QDRANT_URL=https://your-cluster.qdrant.io  # Free tier cloud
# Or: QDRANT_URL=http://localhost:6333  # Local mode via pip install

UPLOAD_DIR=data/newsletters
GEMINI_API_KEY=your_key_here
USE_GEMINI_CLI=true  # Free tier for MVP
```

<!--
**BETA/PRODUCTION OPTION: Docker Compose**

Uncomment when scaling beyond MVP (200+ families):

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: parentpath
      POSTGRES_USER: parentpath
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - ./data/qdrant:/qdrant/storage
    ports:
      - "6333:6333"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes:
      - ./data/minio:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - qdrant
    env_file: .env
    volumes:
      - .:/app
    command: uvicorn api.main:app --reload --host 0.0.0.0
```

To migrate from SQLite to PostgreSQL:
1. Change DATABASE_URL in .env
2. Run: alembic upgrade head
3. Migrate data: python scripts/migrate_sqlite_to_postgres.py

-->

**3. Database Schema** (SQLite with SQLAlchemy - adapt CHAI patterns)

```python
# api/models/parent.py (SQLite-compatible, adapted from CHAI)
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid
import json

Base = declarative_base()

class Parent(Base):
    __tablename__ = "parents"

    # SQLite uses String for UUIDs (no native UUID type)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_type = Column(String(20), nullable=False)  # whatsapp, sms, email
    channel_id = Column(String(255), unique=True, nullable=False)  # phone or email
    language = Column(String(5), default="en")  # ISO 639-1
    timezone = Column(String(50), default="America/Vancouver")
    status = Column(String(20), default="active")  # active, paused, unsubscribed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# api/models/child.py
class Child(Base):
    __tablename__ = "children"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="CASCADE"))
    grade = Column(Integer, nullable=False)  # 0-12
    division = Column(String(10))  # e.g., "5A"
    created_at = Column(DateTime, default=datetime.utcnow)

# api/models/item.py
class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False)  # Event, PermissionSlip, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    date = Column(Date)
    time = Column(Time)
    # SQLite: Store arrays as JSON text
    audience_tags = Column(Text, nullable=False)  # JSON: ["grade_5", "Basketball", "all"]
    confidence_score = Column(Float)  # 0.0-1.0 from Gemini
    status = Column(String(20), default="pending")  # pending, approved, rejected
    source_newsletter_id = Column(String(36), ForeignKey("newsletters.id"))
    qdrant_id = Column(String(255), unique=True)  # UUID in Qdrant
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tags(self):
        """Helper: Parse JSON array"""
        return json.loads(self.audience_tags) if self.audience_tags else []

# See PRD Section 4.1 for full schema (cards, newsletters, message_logs, tickets)
# Note: SQLite adaptations needed for JSON columns (use Text + json.loads/dumps)
```

**4. Database Initialization** (No Alembic needed for MVP)
```python
# scripts/init_db.py - Simple SQLite setup (TEAOS pattern)
from api.models import Base
from sqlalchemy import create_engine

# Create engine
engine = create_engine("sqlite:///parentpath.db")

# Create all tables
Base.metadata.create_all(engine)

print("✅ Database created: parentpath.db")
print(f"   Tables: {', '.join(Base.metadata.tables.keys())}")
```

```bash
# Run once to create database
python scripts/init_db.py
```

<!--
**BETA OPTION: Use Alembic for migrations**

When scaling to production PostgreSQL:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```
-->

**5. Seed Data** (for testing)
```python
# scripts/seed_data.py
async def seed_test_data():
    """Create 3 test parents for validation"""
    parents = [
        Parent(
            channel_type="whatsapp",
            channel_id="whatsapp:+16045551001",
            language="en",
            children=[Child(grade=3)],
        ),
        Parent(
            channel_type="whatsapp",
            channel_id="whatsapp:+16045551002",
            language="pa",  # Punjabi
            children=[Child(grade=5)],
            activities=["Basketball"]
        ),
        Parent(
            channel_type="whatsapp",
            channel_id="whatsapp:+16045551003",
            language="en",
            children=[Child(grade=7)],
            activities=["Band"]
        ),
    ]

    async with db.session() as session:
        session.add_all(parents)
        await session.commit()

    print(f"Seeded {len(parents)} test parents")
```

**6. Shared Working Memory** (§22 coordination)
```markdown
# _WORKING_MEMORY.md

## Instructions for All Specialists
- Read this file FIRST before starting work
- Append decisions as you make them (never delete others' entries)
- Mark completion with "[TRACK_X]: COMPLETE"

## Wave 1 Status
- [x] Docker Compose configured
- [x] Database schema created
- [x] Seed data loaded
- [x] Gate 1 validation PASSED

## Wave 2 Decisions
[Specialists will append here during Wave 2]

## Wave 3 Decisions
[Specialists will append here during Wave 3]

## Communication Log
[Timestamp] [Track] [Message]
```

---

### Validation Gate 1

**Must PASS before Wave 2:**

```bash
# 1. Database exists and accessible
ls -la parentpath.db  # Should exist

# 2. Tables created
sqlite3 parentpath.db "SELECT COUNT(*) FROM parents;"  # Should return 3 (seed data)

# 3. Qdrant accessible (cloud or local)
curl $QDRANT_URL/collections  # Should return {"result": {"collections": []}}
# Or if local: pip install qdrant-client && python -c "from qdrant_client import QdrantClient; print(QdrantClient(':memory:'))"

# 4. Data models valid
pytest tests/test_models.py -v  # Should pass 5/5 tests

# 5. FastAPI runs
python -m uvicorn api.main:app --reload
curl http://localhost:8000/health  # Should return {"status": "ok"}
```

**Test Suite**: `tests/test_models.py`
```python
import pytest
from api.models import Parent, Child, Item

class TestModels:
    async def test_parent_creation(self):
        parent = Parent(channel_type="whatsapp", channel_id="test")
        assert parent.id is not None
        assert parent.status == "active"

    async def test_child_parent_relationship(self):
        parent = Parent(channel_type="whatsapp", channel_id="test")
        child = Child(parent_id=parent.id, grade=5)
        assert child.parent_id == parent.id

    async def test_audience_tags_array(self):
        item = Item(
            type="Event",
            title="Test",
            audience_tags=["grade_5", "Basketball"]
        )
        assert "grade_5" in item.audience_tags

    async def test_confidence_score_range(self):
        item = Item(title="Test", audience_tags=["all"], confidence_score=0.95)
        assert 0.0 <= item.confidence_score <= 1.0

    async def test_seed_data_loaded(self):
        parents = await db.query(Parent).all()
        assert len(parents) == 3  # From seed_data.py
```

**Evidence Required**:
- [ ] parentpath.db exists (SQLite database file)
- [ ] api/models/parent.py:1-25 (Parent model complete, SQLite-compatible)
- [ ] scripts/init_db.py (database creation script)
- [ ] tests/test_models.py:5/5 passing
- [ ] Screenshot: `sqlite3 parentpath.db ".tables"` showing all tables
- [ ] curl http://localhost:8000/health returns {"status": "ok"}

**Confidence Gate**: PRESTIGE (0.90) when all 5 validation steps pass

**Time Estimate**: 10 minutes (vs 45 min with Docker)

---

## 🚀 WAVE 2: CORE SERVICES (Parallel - 90 minutes)

**Launch Pattern**: Single message with 4 Task calls (§26 parallel orchestration)

**Shared Memory Protocol**:
All tracks MUST:
1. Read `_WORKING_MEMORY.md` FIRST
2. Append decisions (never delete others' entries)
3. Mark completion: `[TRACK_X]: COMPLETE`

---

### Track A: Gemini Service (Hybrid CLI + API)

**Specialist Focus**: Multimodal AI integration with cost optimization

**Archaeological Foundation**:
- Adapt `chai/ocr_handler.py` (document processing structure)
- Replace Tesseract with Gemini CLI (free tier) / API (production)
- Reuse `chai/quality_scorer.py` (confidence scoring patterns)

**Deliverables**:

**1. Gemini Service** (~300 lines)
```python
# api/services/gemini_service.py
import subprocess
import json
import os
from typing import List, Dict
from pathlib import Path

class GeminiService:
    """
    Hybrid Gemini integration:
    - Development: Use Gemini CLI (free tier, 1,000 req/day)
    - Production: Use Gemini API SDK (paid tier, more reliable)
    """

    def __init__(self):
        self.use_cli = os.getenv("USE_GEMINI_CLI", "true") == "true"
        self.model = "gemini-2.5-pro"

        if not self.use_cli:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.genai_model = genai.GenerativeModel(self.model)

    async def parse_pdf_newsletter(self, file_path: str) -> List[Dict]:
        """
        Extract structured items from PDF newsletter.

        Adapts CHAI ocr_handler.py pattern but uses Gemini instead of Tesseract.

        Returns:
            List[ItemSchema] with confidence scores
        """
        prompt = """
        Extract all events, announcements, permission slips, and deadlines from this newsletter.

        Return JSON array with:
        - type: Event | PermissionSlip | Fundraiser | HotLunch | Announcement
        - title: string (required)
        - description: string (optional)
        - date: YYYY-MM-DD (required if event or deadline)
        - time: HH:MM (24hr format, optional)
        - audience_tags: array (e.g., ["grade_5", "Basketball", "all"])
        - confidence_score: 0.0-1.0 (your confidence in extraction accuracy)
        - source_snippet: exact text from newsletter

        Be thorough - extract everything. Use "all" tag for school-wide items.
        """

        if self.use_cli:
            # Development: Gemini CLI (free tier)
            result = subprocess.run(
                [
                    "gemini-cli",
                    "analyze",
                    file_path,
                    "--prompt", prompt,
                    "--format", "json",
                    "--model", self.model
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"Gemini CLI error: {result.stderr}")

            items = json.loads(result.stdout)
        else:
            # Production: Gemini API SDK
            pdf_file = self.genai_model.upload_file(file_path)
            response = self.genai_model.generate_content([pdf_file, prompt])
            items = json.loads(response.text)

        # Validate and enrich items
        for item in items:
            # Ensure required fields
            if "title" not in item or "audience_tags" not in item:
                continue

            # Default confidence if not provided
            if "confidence_score" not in item:
                item["confidence_score"] = 0.75

            # Ensure audience_tags is array
            if isinstance(item["audience_tags"], str):
                item["audience_tags"] = [item["audience_tags"]]

        return items

    async def parse_image_flyer(self, image_path: str) -> Dict:
        """
        OCR scanned flyer or parent-submitted photo.

        Uses Gemini Vision for multimodal understanding.
        """
        prompt = """
        This is a photo of a school flyer or permission slip.

        Extract:
        - What is this about? (event, fundraiser, permission slip, etc.)
        - Title/headline
        - Date(s) and time
        - Who is this for? (grade/activity or all students?)
        - Any deadlines or actions required
        - Cost (if any)

        Return same JSON structure as newsletter parsing.
        If image is blurry/cut off, set confidence_score < 0.7 and note limitation.
        """

        # Similar CLI/API routing as parse_pdf_newsletter
        # ... (implementation follows same pattern)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate 768-dim embedding for Qdrant.

        Note: Gemini embeddings are 768-dim (not 1536 like OpenAI).
        This is critical for Qdrant collection setup.
        """
        if self.use_cli:
            result = subprocess.run(
                ["gemini-cli", "embed", text, "--dimension", "768"],
                capture_output=True,
                text=True
            )
            embedding = json.loads(result.stdout)
        else:
            import google.generativeai as genai
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']

        assert len(embedding) == 768, f"Expected 768-dim, got {len(embedding)}"
        return embedding

    async def translate_text(self, text: str, target_lang: str) -> str:
        """
        Translate digest to parent's preferred language.

        Supported: en, pa (Punjabi), tl (Tagalog), zh (Chinese)
        """
        lang_map = {
            "pa": "Punjabi (Gurmukhi script)",
            "tl": "Tagalog",
            "zh": "Simplified Chinese",
            "es": "Spanish"
        }

        if target_lang not in lang_map:
            return text  # Skip translation for unsupported languages

        prompt = f"""
        Translate this school digest to {lang_map[target_lang]}.

        Preserve:
        - Emoji and formatting
        - URLs (don't translate)
        - Dates and times (adapt format to locale)
        - Grade numbers and activity names

        Tone: Friendly, clear, concise for parents.

        Content:
        {text}
        """

        # Route to CLI or API
        # ... (implementation follows same pattern)
```

**2. Test Suite** (~200 lines)
```python
# tests/test_gemini.py
import pytest
from api.services.gemini_service import GeminiService
from unittest.mock import patch, MagicMock

class TestGeminiService:
    @pytest.fixture
    def service(self):
        return GeminiService()

    @patch('subprocess.run')
    async def test_parse_pdf_cli_mode(self, mock_run, service):
        """Test PDF parsing via Gemini CLI (free tier)"""
        service.use_cli = True

        # Mock CLI response
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([{
                "type": "Event",
                "title": "Basketball practice",
                "date": "2024-11-20",
                "audience_tags": ["grade_5", "Basketball"],
                "confidence_score": 0.95
            }])
        )

        items = await service.parse_pdf_newsletter("test.pdf")

        assert len(items) == 1
        assert items[0]["title"] == "Basketball practice"
        assert items[0]["confidence_score"] >= 0.70

    async def test_parse_pdf_extracts_multiple_items(self, service):
        """Test extraction of 20+ items from complex newsletter"""
        items = await service.parse_pdf_newsletter("tests/fixtures/newsletter_complex.pdf")

        assert len(items) >= 20, f"Expected 20+ items, got {len(items)}"

        # Verify diverse item types
        types = set(item["type"] for item in items)
        assert "Event" in types
        assert "PermissionSlip" in types

    async def test_confidence_scores_valid_range(self, service):
        """Test all confidence scores are 0.0-1.0"""
        items = await service.parse_pdf_newsletter("tests/fixtures/newsletter_simple.pdf")

        for item in items:
            assert 0.0 <= item["confidence_score"] <= 1.0

    async def test_embedding_dimension_correct(self, service):
        """Test embeddings are 768-dim (not 1536 like OpenAI)"""
        embedding = await service.generate_embedding("Basketball practice on Friday")

        assert len(embedding) == 768, f"Expected 768-dim, got {len(embedding)}"
        assert all(isinstance(x, float) for x in embedding)

    async def test_translation_preserves_structure(self, service):
        """Test translation to Punjabi preserves formatting"""
        original = "📋 GRADE 5\n• Basketball practice: Nov 20 at 4pm\n🔗 Sign up: https://..."
        translated = await service.translate_text(original, "pa")

        # Emoji and URLs should be preserved
        assert "📋" in translated
        assert "https://" in translated

    async def test_cli_api_parity(self, service):
        """Test CLI and API modes return same structure"""
        file = "tests/fixtures/newsletter_simple.pdf"

        service.use_cli = True
        cli_items = await service.parse_pdf_newsletter(file)

        service.use_cli = False
        api_items = await service.parse_pdf_newsletter(file)

        # Should have same number of items
        assert len(cli_items) == len(api_items)

        # Should have same fields
        assert set(cli_items[0].keys()) == set(api_items[0].keys())

    async def test_low_confidence_items_flagged(self, service):
        """Test items with confidence < 0.70 are flagged"""
        # Use blurry image fixture
        item = await service.parse_image_flyer("tests/fixtures/blurry_flyer.jpg")

        assert item["confidence_score"] < 0.70
        assert "blurry" in item.get("gemini_reasoning", "").lower()
```

**Success Criteria**:
- [ ] Parse sample PDF → 20+ items extracted
- [ ] Confidence scores ≥0.70 for 90% of items
- [ ] Translation: EN → PA/TL/ZH working
- [ ] Embeddings: 768-dim vectors generated
- [ ] **Tests: 8/8 passing**
- [ ] CLI mode works (free tier)
- [ ] API mode works (production ready)

**Evidence Required**:
- api/services/gemini_service.py:1-300 (all methods implemented)
- tests/test_gemini.py:8/8 passing (pytest output)
- tests/fixtures/parsed_newsletter_sample.json (sample output)
- Screenshot: Gemini CLI responding to test query

**Dependencies**: None (standalone service)

**Specialist Agent Prompt**:
```
You are Track A Specialist for ParentPath Wave 2.

## Shared State Protocol
1. READ FIRST: _WORKING_MEMORY.md
2. APPEND decisions (never delete)
3. MARK COMPLETE: "[TRACK_A]: COMPLETE"

## Your Deliverable
Implement api/services/gemini_service.py with hybrid CLI/API support.

Reuse patterns from:
- chai/ocr_handler.py:15-80 (document processing structure)
- chai/quality_scorer.py:25-45 (confidence scoring)

Requirements:
1. parse_pdf_newsletter() - Extract 20+ items from PDF
2. parse_image_flyer() - OCR for photos via Gemini Vision
3. generate_embedding() - 768-dim vectors for Qdrant
4. translate_text() - EN → PA/TL/ZH translation
5. Hybrid mode: CLI (dev) + API (prod) with config flag

Success Criteria:
- 8/8 tests passing
- Sample output: 23 items extracted, confidence_avg=0.87
- Embeddings: 768-dim verified

Evidence ratio: 95%+ (cite Gemini docs, test results)

Begin implementation. Append decisions to _WORKING_MEMORY.md.
```

---

### Track B: Qdrant Service

**Specialist Focus**: Vector search & memory

**Archaeological Foundation**:
- Reuse `scripts/migrate_to_qdrant.py` (batching pattern lines 85-125)
- Adapt `chai/gap_detector.py` (duplicate detection via similarity)
- 95% code reuse (just change collection names)

**Deliverables**:

**1. Qdrant Service** (~400 lines)
```python
# api/services/qdrant_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition
from typing import List, Dict
import os

class QdrantService:
    """
    Vector search service for ParentPath.

    Reuses patterns from scripts/migrate_to_qdrant.py (batching, verification).
    """

    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY", None)
        )
        self.collections = {
            "newsletter_items": 768,  # Gemini embedding dimension
            "parent_messages": 768,
            "correction_tickets": 768
        }

    async def init_collections(self):
        """
        Create all collections if they don't exist.

        Pattern from migrate_to_qdrant.py:60-84
        """
        for collection_name, vector_size in self.collections.items():
            if not self.client.collection_exists(collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {collection_name} ({vector_size}-dim)")

    async def index_item(self, item: Item, embedding: List[float]):
        """
        Add item to Qdrant after approval.

        Pattern from migrate_to_qdrant.py:103-124 (point structure)
        """
        point = PointStruct(
            id=str(item.id),
            vector=embedding,
            payload={
                "type": item.type,
                "title": item.title,
                "description": item.description,
                "date": item.date.isoformat() if item.date else None,
                "audience_tags": item.audience_tags,
                "confidence_score": float(item.confidence_score),
                "created_at": item.created_at.isoformat(),
                "status": item.status
            }
        )

        self.client.upsert(
            collection_name="newsletter_items",
            points=[point]
        )

        # Update Item with Qdrant ID
        item.qdrant_id = str(item.id)

    async def index_batch(self, items: List[Item], embeddings: List[List[float]]):
        """
        Batch upsert for performance.

        Pattern from migrate_to_qdrant.py:85-125 (100 items per batch)
        """
        assert len(items) == len(embeddings)

        points = []
        for item, embedding in zip(items, embeddings):
            points.append(PointStruct(
                id=str(item.id),
                vector=embedding,
                payload={
                    "type": item.type,
                    "title": item.title,
                    "audience_tags": item.audience_tags,
                    "confidence_score": float(item.confidence_score)
                }
            ))

        # Batch upsert (100 at a time)
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.client.upsert(
                collection_name="newsletter_items",
                points=batch
            )

    async def semantic_search(
        self,
        query: str,
        parent_id: str,
        embedding: List[float],
        limit: int = 5
    ) -> List[Dict]:
        """
        Search items semantically for parent queries.

        Adapts chai/gap_detector.py similarity search pattern.
        """
        # Get parent's children for filtering
        children = await db.query(Child).filter_by(parent_id=parent_id).all()
        grades = [c.grade for c in children]
        activities = await get_activities(parent_id)

        # Build filter: parent's grades OR activities OR "all"
        should_filters = [
            FieldCondition(
                key="audience_tags",
                match={"any": [f"grade_{g}" for g in grades]}
            ),
            FieldCondition(
                key="audience_tags",
                match={"any": activities}
            ),
            FieldCondition(
                key="audience_tags",
                match={"value": "all"}
            )
        ]

        # Search with filter
        results = self.client.search(
            collection_name="newsletter_items",
            query_vector=embedding,
            query_filter=Filter(should=should_filters),
            limit=limit,
            with_payload=True
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload
            }
            for hit in results
        ]

    async def find_duplicate_items(
        self,
        embedding: List[float],
        threshold: float = 0.85
    ) -> List[str]:
        """
        Find similar items to prevent duplicates.

        Pattern from chai/gap_detector.py (FAISS → Qdrant migration).
        """
        results = self.client.search(
            collection_name="newsletter_items",
            query_vector=embedding,
            score_threshold=threshold,
            limit=10
        )

        return [r.id for r in results]

    async def get_recommendations(
        self,
        parent_id: str,
        limit: int = 5
    ) -> List[Item]:
        """
        Recommend items based on parent's past interactions.

        Collaborative filtering via vector similarity.
        """
        # Get parent's completed cards
        cards = await db.query(Card).filter_by(
            parent_id=parent_id,
            status="done"
        ).limit(20).all()

        # Get embeddings of items they engaged with
        engaged_ids = [str(card.item_id) for card in cards]
        points = self.client.retrieve(
            collection_name="newsletter_items",
            ids=engaged_ids
        )

        # Average vectors
        import numpy as np
        avg_vector = np.mean([p.vector for p in points], axis=0).tolist()

        # Find similar items not yet delivered
        delivered_ids = await get_delivered_item_ids(parent_id)

        results = self.client.search(
            collection_name="newsletter_items",
            query_vector=avg_vector,
            limit=limit * 2,
            query_filter=Filter(
                must_not=[
                    FieldCondition(
                        key="id",
                        match={"any": [str(id) for id in delivered_ids]}
                    )
                ]
            )
        )

        # Convert to Item objects
        item_ids = [r.id for r in results[:limit]]
        items = await db.query(Item).filter(Item.id.in_(item_ids)).all()

        return items
```

**2. Test Suite** (~250 lines)
```python
# tests/test_qdrant.py
import pytest
from api.services.qdrant_service import QdrantService
from api.models import Item

class TestQdrantService:
    @pytest.fixture
    async def service(self):
        svc = QdrantService()
        await svc.init_collections()
        return svc

    async def test_collections_created(self, service):
        """Test 3 collections exist with correct dimensions"""
        collections = service.client.get_collections().collections
        names = [c.name for c in collections]

        assert "newsletter_items" in names
        assert "parent_messages" in names
        assert "correction_tickets" in names

        # Verify vector dimensions
        info = service.client.get_collection("newsletter_items")
        assert info.config.params.vectors.size == 768

    async def test_index_single_item(self, service):
        """Test indexing single item"""
        item = Item(
            type="Event",
            title="Basketball practice",
            audience_tags=["grade_5", "Basketball"],
            confidence_score=0.95
        )
        embedding = [0.1] * 768  # Mock embedding

        await service.index_item(item, embedding)

        # Verify indexed
        assert item.qdrant_id is not None

        # Verify retrievable
        points = service.client.retrieve(
            collection_name="newsletter_items",
            ids=[item.qdrant_id]
        )
        assert len(points) == 1

    async def test_batch_indexing_performance(self, service):
        """Test batch indexing 100 items"""
        items = [
            Item(
                title=f"Item {i}",
                audience_tags=["all"],
                confidence_score=0.9
            )
            for i in range(100)
        ]
        embeddings = [[0.1] * 768 for _ in range(100)]

        import time
        start = time.time()
        await service.index_batch(items, embeddings)
        elapsed = time.time() - start

        # Should complete in < 5 seconds
        assert elapsed < 5.0

        # Verify count
        info = service.client.get_collection("newsletter_items")
        assert info.points_count >= 100

    async def test_semantic_search_finds_similar(self, service):
        """Test search for 'basketball games' finds 'basketball practice'"""
        # Index test item
        item = Item(
            title="Basketball practice on Friday",
            audience_tags=["grade_5", "Basketball"],
            confidence_score=0.95
        )
        embedding = await generate_embedding(item.title)  # Real embedding
        await service.index_item(item, embedding)

        # Search with similar query
        query = "basketball games in november"
        query_embedding = await generate_embedding(query)

        results = await service.semantic_search(
            query=query,
            parent_id=test_parent.id,
            embedding=query_embedding,
            limit=5
        )

        # Should find basketball item with high similarity
        assert len(results) > 0
        assert results[0]["score"] >= 0.80
        assert "basketball" in results[0]["title"].lower()

    async def test_duplicate_detection(self, service):
        """Test finding duplicate items"""
        # Index original item
        item1 = Item(title="Basketball practice Friday", audience_tags=["grade_5"])
        embedding1 = await generate_embedding(item1.title)
        await service.index_item(item1, embedding1)

        # Try to index similar item
        item2_text = "Basketball practice moved to Friday"
        embedding2 = await generate_embedding(item2_text)

        duplicates = await service.find_duplicate_items(embedding2, threshold=0.85)

        # Should find item1 as duplicate
        assert len(duplicates) > 0
        assert str(item1.id) in duplicates

    async def test_recommendations_based_on_engagement(self, service):
        """Test collaborative filtering recommendations"""
        # Parent completed basketball cards
        parent = await create_test_parent(grade=5, activities=["Basketball"])

        # Create engagement history
        basketball_items = [
            Item(title=f"Basketball {i}", audience_tags=["Basketball"])
            for i in range(5)
        ]
        for item in basketball_items:
            embedding = await generate_embedding(item.title)
            await service.index_item(item, embedding)
            await create_card(parent.id, item.id, status="done")

        # Get recommendations
        recommendations = await service.get_recommendations(parent.id, limit=3)

        # Should recommend basketball-related items
        assert len(recommendations) > 0
        assert any("basketball" in r.title.lower() for r in recommendations)

    async def test_audience_filtering(self, service):
        """Test search respects parent's grade/activities"""
        parent = await create_test_parent(grade=5, activities=[])

        # Index items for different grades
        grade3_item = Item(title="Grade 3 event", audience_tags=["grade_3"])
        grade5_item = Item(title="Grade 5 event", audience_tags=["grade_5"])

        await service.index_item(grade3_item, await generate_embedding(grade3_item.title))
        await service.index_item(grade5_item, await generate_embedding(grade5_item.title))

        # Search
        query_embedding = await generate_embedding("school event")
        results = await service.semantic_search(
            query="school event",
            parent_id=parent.id,
            embedding=query_embedding
        )

        # Should only return grade 5 items
        assert all("grade_5" in r["audience_tags"] or "all" in r["audience_tags"] for r in results)
        assert not any("grade_3" in r["audience_tags"] for r in results)

    async def test_search_latency(self, service):
        """Test search completes in < 100ms"""
        # Index 1000 items
        items = [Item(title=f"Item {i}", audience_tags=["all"]) for i in range(1000)]
        embeddings = [[0.1] * 768 for _ in range(1000)]
        await service.index_batch(items, embeddings)

        # Time search
        import time
        query_embedding = [0.2] * 768

        start = time.time()
        results = await service.semantic_search(
            query="test",
            parent_id=test_parent.id,
            embedding=query_embedding,
            limit=10
        )
        latency_ms = (time.time() - start) * 1000

        # Should be < 100ms at p95
        assert latency_ms < 100

    async def test_collection_persistence(self, service):
        """Test data survives restart"""
        # Index item
        item = Item(title="Test", audience_tags=["all"])
        embedding = [0.3] * 768
        await service.index_item(item, embedding)

        # Simulate restart (recreate service)
        service2 = QdrantService()

        # Should still exist
        points = service2.client.retrieve(
            collection_name="newsletter_items",
            ids=[str(item.id)]
        )
        assert len(points) == 1
```

**Success Criteria**:
- [ ] 3 collections created (newsletter_items, parent_messages, correction_tickets)
- [ ] Index 50 sample items successfully
- [ ] Search: "basketball games" → finds "basketball practice" (≥0.80 similarity)
- [ ] Duplicate detection: 2 similar items found
- [ ] Search latency < 100ms (p95)
- [ ] **Tests: 10/10 passing**

**Evidence Required**:
- api/services/qdrant_service.py:1-400 (complete implementation)
- tests/test_qdrant.py:10/10 passing
- Screenshot: Qdrant dashboard showing 3 collections
- Performance log: Search latency measurements

**Dependencies**: None (Qdrant standalone)

**Specialist Agent Prompt**:
```
You are Track B Specialist for ParentPath Wave 2.

## Shared State Protocol
1. READ FIRST: _WORKING_MEMORY.md
2. APPEND decisions
3. MARK COMPLETE: "[TRACK_B]: COMPLETE"

## Your Deliverable
Implement api/services/qdrant_service.py.

Reuse patterns from:
- scripts/migrate_to_qdrant.py:60-84 (collection creation)
- scripts/migrate_to_qdrant.py:85-125 (batching pattern)
- chai/gap_detector.py (similarity search)

Requirements:
1. init_collections() - Create 3 collections (768-dim)
2. index_item() - Add item to Qdrant
3. index_batch() - Batch upsert (100 items)
4. semantic_search() - Parent queries with filtering
5. find_duplicate_items() - Similarity threshold 0.85
6. get_recommendations() - Collaborative filtering

Success Criteria:
- 10/10 tests passing
- Search latency < 100ms
- Batch indexing < 5s for 100 items

Evidence ratio: 100% (all operations tested)

Begin implementation.
```

---

### Track C: WhatsApp Service

**Specialist Focus**: Messaging integration

**Deliverables**: ~300 lines WhatsApp Cloud API integration + ~200 lines tests

**Success Criteria**:
- [ ] Send digest (mock API)
- [ ] Detect intents: done, help, query, error
- [ ] Format multilingual digest
- [ ] **Tests: 7/7 passing**

**Dependencies**: None (standalone)

---

### Track D: Targeting Engine

**Specialist Focus**: SQL-based audience matching

**Deliverables**: ~250 lines targeting service + ~200 lines tests

**Success Criteria**:
- [ ] Parent (Grade 5 + Basketball) → Gets basketball items
- [ ] Parent (Grade 3) → Does NOT get Grade 5 items
- [ ] "all" items → Delivered to everyone
- [ ] **Tests: 8/8 passing**

**Dependencies**: PostgreSQL models from Wave 1

---

### Validation Gate 2

**Must PASS before Wave 3:**

```bash
# All tracks must pass:
pytest tests/test_gemini.py -v       # 8/8 passing
pytest tests/test_qdrant.py -v       # 10/10 passing
pytest tests/test_messenger.py -v    # 7/7 passing
pytest tests/test_targeting.py -v    # 8/8 passing

# Total: 33 tests must pass
```

**Completion Status** (in `_WORKING_MEMORY.md`):
- [ ] TRACK_A: Gemini Service (Parallel)
- [ ] TRACK_B: Qdrant Service (Parallel)
- [ ] TRACK_C: WhatsApp Service (Parallel)
- [ ] TRACK_D: Targeting Engine (Parallel)

**Evidence Required**: Test results with file:line citations
**Confidence**: PRESTIGE (0.90) when all 33 tests pass

---

## 🔧 WAVE 3: APPLICATION LAYER (Parallel - 90 minutes)

**Launch Pattern**: Single message with 3 Task calls

### Track E: FastAPI Routes
### Track F: Background Workers
### Track G: Admin Review UI

**Validation Gate 3**: 30 tests must pass (15+10+5)

---

## ✅ WAVE 4: INTEGRATION (Sequential - 2 hours)

### End-to-End Testing
### Load Testing
### Documentation

**Validation Gate 4**: 5 tests + load test <200ms p95

---

## 📊 EVIDENCE RATIO TRACKING

**Target**: ≥95% (PRESTIGE)

**Calculation**:
```python
# Wave 2 example:
claims_made = 45  # All "service works" statements
claims_verified = 43  # With test artifacts
evidence_ratio = 43/45 = 0.956  # 95.6% ✅

# Must provide:
# - File citations (api/services/gemini_service.py:1-300)
# - Test results (tests/test_gemini.py:8/8 passing)
# - Command outputs (pytest -v output)
# - Screenshots (Qdrant dashboard, WhatsApp messages)
```

---

## 🚦 EXECUTION PROTOCOL

**Phase 1: Foundation (Solo)**
```bash
# Execute Wave 1 directly
# Estimated: 45 minutes
```

**Phase 2: Parallel Services (§26 Pattern)**
```python
# Launch Wave 2 in SINGLE message with 4 Task calls:
Task(subagent_type="spec-impl", prompt=TRACK_A_SPEC)  # Gemini
Task(subagent_type="spec-impl", prompt=TRACK_B_SPEC)  # Qdrant
Task(subagent_type="spec-impl", prompt=TRACK_C_SPEC)  # WhatsApp
Task(subagent_type="spec-impl", prompt=TRACK_D_SPEC)  # Targeting
```

---

**Ready for execution. Awaiting approval to begin Wave 1.**
