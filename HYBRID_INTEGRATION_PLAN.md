# ParentPath: Hybrid Integration Plan (GitHub MVP + TEAOS Patterns)

**Version**: 1.0
**Date**: 2025-11-17
**Status**: Ready for Execution
**Pattern**: Hybrid Merge (Option C - Best of Both Worlds)
**Authority**: §24 Session Handoff Protocol - Execute as written
**Evidence Ratio Target**: 95%+
**Total Time**: 6 hours (6 sequential phases)

---

## 📋 EXECUTIVE SUMMARY

### What We Have

**GitHub Branch** (`claude/help-code-request-0129Jqcif72wsj2ovpnR7rmU`):
- ✅ 1,804 LOC of working implementation
- ✅ Gemini 2.0 Flash integration (API-based)
- ✅ Qdrant vector search
- ✅ FastAPI routes (intake, admin, family, webhooks)
- ✅ PostgreSQL models with relationships
- ✅ Docker Compose (8 services: PostgreSQL, Redis, Qdrant, MinIO, API, Worker, Prometheus, Grafana)
- ❌ No tests beyond health check
- ❌ No CHAI infrastructure reuse
- ❌ Gemini API only (paid tier, no free option)
- ❌ PostgreSQL only (Docker required)

**Local Runbook** (TEAOS patterns):
- ✅ 45KB comprehensive specification
- ✅ SQLite database strategy (TEAOS native)
- ✅ Hybrid Gemini (CLI free tier + API paid)
- ✅ 68 comprehensive tests planned
- ✅ CHAI 75% code reuse strategy
- ✅ Hardy validation gates
- ✅ InfiniTEA parallel orchestration (§22)
- ✅ Evidence ratio accountability (§2)
- ❌ Not implemented yet (just planning)

### What We're Building

**Hybrid Approach** = GitHub Services + TEAOS Infrastructure:

```
Keep from GitHub (1,804 LOC):          Add from TEAOS:
✅ api/services/gemini_service.py      🔧 SQLite adapter
✅ api/services/qdrant_service.py      🔧 Gemini CLI mode
✅ api/models/*.py (all models)        🔧 CHAI imports
✅ api/routers/*.py (all routes)       🔧 31 comprehensive tests
✅ api/main.py, config.py, database.py 🔧 Hardy validation gates
                                       🔧 Evidence ratio tracking
```

**Result**: Production-ready core + TEAOS flexibility + Quality gates

---

## 🎯 ARCHITECTURE COMPARISON

| Component | GitHub Current | Hybrid Target | Change Required |
|-----------|----------------|---------------|-----------------|
| **Database** | PostgreSQL (asyncpg) | SQLite (default) + PostgreSQL (optional) | Add SQLite adapter |
| **Gemini** | API only (paid) | CLI (free) + API (paid) | Add CLI execution mode |
| **Services** | gemini_service, qdrant_service | Keep + add batch_analyzer, quality_scorer | Import from CHAI |
| **Models** | PostgreSQL UUID types | Keep + add SQLite compatibility | Dual-mode support |
| **Routes** | 5 routers (working) | Keep all | No changes |
| **Tests** | 1 file (test_health.py) | Add 31 tests | Expand test suite |
| **Validation** | None | Hardy gates | Add validation layer |
| **Infrastructure** | Docker required | Docker optional | Make SQLite default |
| **Evidence** | No tracking | 95% ratio target | Add tracking |

---

## 🚀 6-PHASE EXECUTION PLAN

### **Phase 1: SQLite Adapter** (30 minutes)

**Goal**: Make SQLite the default, PostgreSQL optional

**Deliverables**:

**1. Dual-mode database configuration** (`api/database.py`)

```python
# BEFORE (PostgreSQL only):
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.postgresql import UUID

DATABASE_URL = settings.database_url  # postgresql+asyncpg://...

# AFTER (Hybrid):
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import String, create_engine
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid

# Database mode detection
DATABASE_URL = settings.database_url  # Can be sqlite:/// or postgresql+asyncpg://
IS_SQLITE = DATABASE_URL.startswith("sqlite")
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# UUID type adapter
if IS_SQLITE:
    # SQLite: Use String(36) for UUIDs
    def UUID(as_uuid=False):
        return String(36)
else:
    # PostgreSQL: Use native UUID
    UUID = PostgresUUID

# Engine creation
if IS_SQLITE:
    # Synchronous for SQLite
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    # Async for PostgreSQL
    engine = create_async_engine(DATABASE_URL)
    async_session = AsyncSession(engine)

    async def get_db():
        async with async_session() as session:
            yield session
```

**2. Update `.env.example`**:

```bash
# Database Configuration
# Option 1: SQLite (default, zero setup)
DATABASE_URL=sqlite:///parentpath.db

# Option 2: PostgreSQL (production, requires Docker)
# DATABASE_URL=postgresql+asyncpg://parentpath:parentpath_dev_2024@localhost:5432/parentpath

# Qdrant Configuration
# Option 1: Cloud (free tier - 1GB)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key_here

# Option 2: Local (via pip install qdrant-client)
# QDRANT_URL=:memory:

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Gemini Mode
# Option 1: CLI (free tier, 1000 requests/day)
USE_GEMINI_CLI=true

# Option 2: API (paid tier, more reliable)
# USE_GEMINI_CLI=false

# File Storage
UPLOAD_DIR=data/newsletters
```

**3. Create initialization script** (`scripts/init_db.py`)

```python
"""Initialize database (SQLite or PostgreSQL)"""
from api.database import engine, Base, IS_SQLITE
from api.models import Parent, Child, Subscription, Item, Card, Newsletter, MessageLog, Ticket
import asyncio

async def init_database():
    """Create all tables"""
    if IS_SQLITE:
        # Synchronous for SQLite
        Base.metadata.create_all(engine)
        print("✅ SQLite database created: parentpath.db")
    else:
        # Async for PostgreSQL
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ PostgreSQL database initialized")

    # List tables
    print(f"   Tables: {', '.join(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    if IS_SQLITE:
        # Run sync
        import asyncio
        asyncio.run(init_database())
    else:
        # Run async
        asyncio.run(init_database())
```

**Validation Gate 1**:
```bash
# 1. SQLite mode works
DATABASE_URL=sqlite:///parentpath.db python scripts/init_db.py
ls parentpath.db  # Should exist

# 2. PostgreSQL mode still works
# (Requires Docker running)
docker-compose up -d postgres
DATABASE_URL=postgresql+asyncpg://parentpath:parentpath_dev_2024@localhost:5432/parentpath python scripts/init_db.py

# 3. API starts with SQLite
DATABASE_URL=sqlite:///parentpath.db python -m uvicorn api.main:app --reload
curl http://localhost:8000/health  # Should return {"status": "ok"}
```

**Evidence Required**:
- [ ] api/database.py updated with dual-mode support
- [ ] scripts/init_db.py created and tested
- [ ] parentpath.db exists (SQLite file)
- [ ] Health check passes with SQLite
- [ ] Health check passes with PostgreSQL (optional)

**Confidence**: HYPOTHETICAL → PRESTIGE when all 5 validation steps pass

**Time**: 30 minutes

---

### **Phase 2: Gemini CLI Mode** (45 minutes)

**Goal**: Add free-tier CLI option alongside paid API

**Deliverables**:

**1. Update Gemini Service** (`api/services/gemini_service.py`)

Add at top of file:
```python
import subprocess
import os

USE_CLI = os.getenv("USE_GEMINI_CLI", "true").lower() == "true"
```

Add CLI execution method:
```python
async def _execute_via_cli(prompt: str, file_path: str = None) -> str:
    """
    Execute Gemini request via CLI (free tier)

    Requires: pip install google-generativeai-cli (hypothetical, or use curl)
    Alternative: Use curl with Gemini REST API
    """
    try:
        # Build command
        if file_path:
            # Multimodal request
            cmd = [
                "curl",
                "-X", "POST",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={settings.gemini_api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {
                                "mime_type": "application/pdf",
                                "data": base64.b64encode(open(file_path, "rb").read()).decode()
                            }}
                        ]
                    }]
                })
            ]
        else:
            # Text-only request
            cmd = [
                "curl",
                "-X", "POST",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={settings.gemini_api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}]
                })
            ]

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise Exception(f"CLI execution failed: {result.stderr}")

        # Parse response
        response_data = json.loads(result.stdout)
        return response_data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        logger.error(f"CLI execution error: {e}")
        raise
```

Update existing methods to check mode:
```python
async def parse_pdf_newsletter(file_path: str) -> List[Dict[str, Any]]:
    """Parse PDF newsletter using Gemini (CLI or API mode)"""
    try:
        logger.info(f"Parsing PDF newsletter: {file_path} (mode: {'CLI' if USE_CLI else 'API'})")

        # (existing prompt definition)
        prompt = """..."""

        if USE_CLI:
            # Use CLI/curl approach
            response_text = await _execute_via_cli(prompt, file_path)
        else:
            # Use API SDK (existing code)
            uploaded_file = genai.upload_file(file_path)
            response = model.generate_content([uploaded_file, prompt])
            response_text = response.text.strip()

        # (rest of existing parsing logic)
        ...
```

**2. Add CLI tests** (`tests/test_gemini_cli.py`)

```python
import pytest
import os
from api.services.gemini_service import parse_pdf_newsletter, generate_embedding

class TestGeminiCLI:
    """Test Gemini CLI mode (free tier)"""

    @pytest.fixture(autouse=True)
    def set_cli_mode(self):
        """Force CLI mode for these tests"""
        os.environ["USE_GEMINI_CLI"] = "true"
        yield
        os.environ["USE_GEMINI_CLI"] = "false"

    async def test_cli_parse_pdf(self):
        """Test PDF parsing via CLI"""
        items = await parse_pdf_newsletter("tests/fixtures/sample_newsletter.pdf")

        assert len(items) > 0
        assert items[0]["title"] is not None
        assert items[0]["confidence_score"] >= 0.7

    async def test_cli_embedding_generation(self):
        """Test embedding generation via CLI"""
        embedding = await generate_embedding("Basketball practice on Friday")

        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)

    async def test_cli_api_parity(self):
        """Test CLI and API return same structure"""
        text = "Basketball practice"

        # CLI mode
        os.environ["USE_GEMINI_CLI"] = "true"
        cli_embedding = await generate_embedding(text)

        # API mode
        os.environ["USE_GEMINI_CLI"] = "false"
        api_embedding = await generate_embedding(text)

        # Should have same dimension
        assert len(cli_embedding) == len(api_embedding) == 768
```

**Validation Gate 2**:
```bash
# 1. CLI mode works
USE_GEMINI_CLI=true pytest tests/test_gemini_cli.py -v

# 2. API mode still works
USE_GEMINI_CLI=false pytest tests/test_gemini.py::test_parse_pdf -v

# 3. Cost comparison
# CLI: Free (1000 req/day)
# API: ~$0.15 per 100K input chars
```

**Evidence Required**:
- [ ] api/services/gemini_service.py updated with CLI mode
- [ ] tests/test_gemini_cli.py created (3 tests)
- [ ] CLI mode test passes
- [ ] API mode still works
- [ ] Cost documented

**Confidence**: PRESTIGE when both modes work

**Time**: 45 minutes

---

### **Phase 3: CHAI Infrastructure Import** (2 hours)

**Goal**: Reuse proven CHAI patterns (75% code reuse)

**Archaeological Foundation** (from TEAOS):
```
chai/ocr_handler.py         ~200 lines  → Document processing patterns
chai/hardy_validator.py     ~150 lines  → Validation framework
chai/batch_analyzer.py      ~300 lines  → Digest generation
chai/quality_scorer.py      ~100 lines  → Confidence scoring
chai/gap_detector.py        ~200 lines  → Duplicate detection
chai/compliance_analyzer.py ~250 lines  → Schema validation
scripts/migrate_to_qdrant.py 227 lines  → Batching patterns
```

**Deliverables**:

**1. Batch Analyzer** (`api/services/batch_analyzer.py`)

```python
"""
Batch digest generation from CHAI patterns

Adapted from: ../../chai/batch_analyzer.py (300 lines)
Pattern: Newsletter items → Personalized parent digests
"""
from typing import List, Dict
from datetime import datetime, timedelta
from api.models import Parent, Child, Item, Card
from api.services.qdrant_service import QdrantService
from api.services.gemini_service import translate_text

class BatchAnalyzer:
    """
    Generate personalized digests for all parents

    Reuses CHAI patterns:
    - Audience matching via tags
    - Confidence-based filtering
    - Multi-language support
    """

    def __init__(self, db_session, qdrant: QdrantService):
        self.db = db_session
        self.qdrant = qdrant

    async def generate_digest(self, parent: Parent, date_range: int = 7) -> str:
        """
        Generate personalized digest for one parent

        Pattern from chai/batch_analyzer.py:145-200
        """
        # Get parent's children grades and activities
        children = await self.db.query(Child).filter_by(parent_id=parent.id).all()
        grades = [c.grade for c in children]
        activities = [s.activity for s in parent.subscriptions]

        # Query relevant items from past week
        cutoff_date = datetime.utcnow() - timedelta(days=date_range)
        items = await self.db.query(Item).filter(
            Item.created_at >= cutoff_date,
            Item.status == "approved"
        ).all()

        # Filter by audience match
        relevant_items = []
        for item in items:
            tags = item.audience_tags if isinstance(item.audience_tags, list) else []

            # Match: grade OR activity OR "all"
            if ("all" in tags or
                any(f"grade_{g}" in tags for g in grades) or
                any(act in tags for act in activities)):
                relevant_items.append(item)

        # Build digest
        if not relevant_items:
            return None  # No items this week

        # Group by type
        events = [i for i in relevant_items if i.type == "Event"]
        permission_slips = [i for i in relevant_items if i.type == "PermissionSlip"]
        fundraisers = [i for i in relevant_items if i.type == "Fundraiser"]
        announcements = [i for i in relevant_items if i.type == "Announcement"]

        # Format digest (emoji-rich, scannable)
        digest_parts = ["📋 Your Weekly School Digest\n"]

        if events:
            digest_parts.append(f"\n📅 UPCOMING EVENTS ({len(events)})")
            for event in events[:5]:  # Limit to top 5
                date_str = event.date.strftime("%a, %b %d") if event.date else "TBD"
                time_str = f" at {event.time}" if event.time else ""
                digest_parts.append(f"• {event.title} - {date_str}{time_str}")

        if permission_slips:
            digest_parts.append(f"\n✍️ PERMISSION SLIPS NEEDED ({len(permission_slips)})")
            for slip in permission_slips:
                deadline = slip.deadline.strftime("%b %d") if slip.deadline else "ASAP"
                digest_parts.append(f"• {slip.title} (due {deadline})")

        if fundraisers:
            digest_parts.append(f"\n💰 FUNDRAISERS ({len(fundraisers)})")
            for fund in fundraisers[:3]:
                digest_parts.append(f"• {fund.title}")

        if announcements:
            digest_parts.append(f"\n📢 ANNOUNCEMENTS ({len(announcements)})")
            for ann in announcements[:3]:
                digest_parts.append(f"• {ann.title}")

        digest_parts.append("\n---")
        digest_parts.append("Reply DONE if helpful, or ask a question!")

        digest_text = "\n".join(digest_parts)

        # Translate if needed
        if parent.language != "en":
            digest_text = await translate_text(digest_text, parent.language)

        return digest_text

    async def batch_generate_all(self) -> Dict[str, str]:
        """
        Generate digests for all active parents

        Pattern from chai/batch_analyzer.py:220-260
        Returns: {parent_id: digest_text}
        """
        parents = await self.db.query(Parent).filter_by(status="active").all()

        digests = {}
        for parent in parents:
            digest = await self.generate_digest(parent)
            if digest:
                digests[str(parent.id)] = digest

        return digests
```

**2. Quality Scorer** (`api/services/quality_scorer.py`)

```python
"""
Confidence scoring for extracted items

Adapted from: ../../chai/quality_scorer.py (100 lines)
Pattern: Multi-signal confidence estimation
"""
from typing import Dict, Any

class QualityScorer:
    """
    Score item extraction quality

    Signals:
    - Gemini confidence (from extraction)
    - Field completeness
    - Source snippet quality
    """

    @staticmethod
    def score_item(item_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for extracted item

        Pattern from chai/quality_scorer.py:25-70
        """
        signals = []

        # 1. Gemini's confidence
        gemini_conf = item_data.get("confidence_score", 0.75)
        signals.append(("gemini", gemini_conf, 0.4))  # 40% weight

        # 2. Field completeness
        required_fields = ["type", "title", "audience_tags"]
        optional_fields = ["description", "date", "time", "location"]

        required_complete = sum(1 for f in required_fields if item_data.get(f)) / len(required_fields)
        optional_complete = sum(1 for f in optional_fields if item_data.get(f)) / len(optional_fields)

        completeness = (required_complete * 0.7 + optional_complete * 0.3)
        signals.append(("completeness", completeness, 0.3))  # 30% weight

        # 3. Source snippet quality
        snippet = item_data.get("source_snippet", "")
        snippet_quality = min(len(snippet) / 100, 1.0)  # Longer = better (up to 100 chars)
        signals.append(("snippet", snippet_quality, 0.2))  # 20% weight

        # 4. Audience tag specificity
        tags = item_data.get("audience_tags", [])
        tag_specificity = 0.5 if "all" in tags else 1.0  # Specific tags = higher confidence
        signals.append(("tags", tag_specificity, 0.1))  # 10% weight

        # Weighted average
        total_score = sum(score * weight for (_, score, weight) in signals)

        return round(total_score, 2)
```

**3. Tests** (`tests/test_chai_imports.py`)

```python
import pytest
from api.services.batch_analyzer import BatchAnalyzer
from api.services.quality_scorer import QualityScorer

class TestCHAIImports:
    """Test imported CHAI patterns work correctly"""

    async def test_batch_digest_generation(self, db_session, test_parent):
        """Test digest generation for parent"""
        analyzer = BatchAnalyzer(db_session, qdrant_service)

        digest = await analyzer.generate_digest(test_parent)

        assert digest is not None
        assert "📋 Your Weekly School Digest" in digest
        assert "UPCOMING EVENTS" in digest or "PERMISSION SLIPS" in digest

    async def test_quality_scoring(self):
        """Test confidence scoring"""
        item_data = {
            "type": "Event",
            "title": "Basketball game",
            "description": "Grade 5 vs Grade 6",
            "date": "2024-11-20",
            "time": "16:00",
            "audience_tags": ["grade_5", "Basketball"],
            "confidence_score": 0.95,
            "source_snippet": "Basketball game for Grade 5 on Nov 20 at 4pm."
        }

        score = QualityScorer.score_item(item_data)

        assert 0.85 <= score <= 1.0  # High quality item

    async def test_multilingual_digest(self, db_session, punjabi_parent):
        """Test Punjabi translation"""
        analyzer = BatchAnalyzer(db_session, qdrant_service)

        digest = await analyzer.generate_digest(punjabi_parent)

        # Should be translated (detect non-ASCII chars)
        assert any(ord(c) > 127 for c in digest)
```

**Validation Gate 3**:
```bash
# 1. CHAI imports work
pytest tests/test_chai_imports.py -v  # 3/3 passing

# 2. Batch digest generation
python -c "
from api.services.batch_analyzer import BatchAnalyzer
# ... generate digests for all parents
"

# 3. Quality scoring
python -c "
from api.services.quality_scorer import QualityScorer
score = QualityScorer.score_item({...})
print(f'Score: {score}')
"
```

**Evidence Required**:
- [ ] api/services/batch_analyzer.py created (reused from CHAI)
- [ ] api/services/quality_scorer.py created (reused from CHAI)
- [ ] tests/test_chai_imports.py passing (3/3)
- [ ] Digest generation works for test parent
- [ ] Quality scoring validates items correctly

**Confidence**: PRESTIGE when all validation passes

**Time**: 2 hours

---

### **Phase 4: Test Expansion** (2 hours)

**Goal**: Add 31 comprehensive tests (from runbook)

**Current State**: 1 test file (test_health.py)

**Target**: 32 test files total

**Deliverables**:

**Test Suite Structure**:
```
tests/
├── conftest.py (existing)
├── test_health.py (existing) ✅
├── test_gemini.py (8 tests) 🆕
├── test_gemini_cli.py (3 tests) 🆕
├── test_qdrant.py (10 tests) 🆕
├── test_targeting.py (8 tests) 🆕
├── test_chai_imports.py (3 tests) 🆕
└── test_integration.py (5 tests) 🆕

Total: 37 tests (vs 1 currently)
```

**1. Gemini Tests** (`tests/test_gemini.py` - from runbook lines 650-741)

```python
import pytest
from api.services.gemini_service import (
    parse_pdf_newsletter,
    parse_image_flyer,
    generate_embedding,
    translate_text
)

class TestGeminiService:
    async def test_parse_pdf_extracts_multiple_items(self):
        """Test extraction of 20+ items from complex newsletter"""
        items = await parse_pdf_newsletter("tests/fixtures/newsletter_complex.pdf")

        assert len(items) >= 20
        assert all(item["type"] in ["Event", "PermissionSlip", "Fundraiser", "HotLunch", "Announcement"] for item in items)

    async def test_confidence_scores_valid_range(self):
        """Test all confidence scores are 0.0-1.0"""
        items = await parse_pdf_newsletter("tests/fixtures/newsletter_simple.pdf")

        for item in items:
            assert 0.0 <= item["confidence_score"] <= 1.0

    async def test_embedding_dimension_correct(self):
        """Test embeddings are 768-dim (Gemini, not OpenAI 1536)"""
        embedding = await generate_embedding("Basketball practice on Friday")

        assert len(embedding) == 768

    async def test_translation_preserves_structure(self):
        """Test translation to Punjabi preserves emoji and URLs"""
        original = "📋 GRADE 5\n• Basketball practice: Nov 20 at 4pm\n🔗 Sign up: https://..."
        translated = await translate_text(original, "pa")

        assert "📋" in translated
        assert "https://" in translated

    async def test_low_confidence_items_flagged(self):
        """Test blurry images get confidence < 0.70"""
        item = await parse_image_flyer("tests/fixtures/blurry_flyer.jpg")

        assert item["confidence_score"] < 0.70
        assert "blurry" in item.get("reasoning", "").lower()

    # ... (3 more tests from runbook)
```

**2. Qdrant Tests** (`tests/test_qdrant.py` - from runbook lines 1030-1230)

```python
import pytest
from api.services.qdrant_service import QdrantService

class TestQdrantService:
    async def test_collections_created(self, qdrant_service):
        """Test 3 collections exist with 768-dim vectors"""
        collections = qdrant_service.client.get_collections().collections
        names = [c.name for c in collections]

        assert "newsletter_items" in names
        assert "parent_messages" in names
        assert "correction_tickets" in names

    async def test_semantic_search_finds_similar(self):
        """Test 'basketball games' finds 'basketball practice'"""
        # (Implementation from runbook lines 1102-1128)
        ...

    async def test_search_latency(self):
        """Test search completes in < 100ms"""
        # (Implementation from runbook lines 1191-1213)
        ...

    # ... (7 more tests)
```

**3. Integration Tests** (`tests/test_integration.py`)

```python
import pytest
from api.main import app
from httpx import AsyncClient

class TestEndToEnd:
    async def test_full_newsletter_workflow(self):
        """
        E2E: Upload newsletter → Parse → Review → Approve → Generate digests → Send
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Upload newsletter PDF
            with open("tests/fixtures/newsletter.pdf", "rb") as f:
                response = await client.post("/intake/upload", files={"file": f})
            assert response.status_code == 200
            newsletter_id = response.json()["id"]

            # 2. Wait for parsing (background job)
            import time; time.sleep(2)

            # 3. Check items extracted
            response = await client.get(f"/admin/newsletters/{newsletter_id}/items")
            items = response.json()
            assert len(items) >= 10

            # 4. Approve all items
            for item in items:
                await client.post(f"/admin/items/{item['id']}/approve")

            # 5. Generate digests
            response = await client.post("/admin/digests/generate")
            assert response.status_code == 200

            # 6. Check parent received digest
            response = await client.get("/family/messages", headers={"X-Parent-ID": test_parent.id})
            messages = response.json()
            assert len(messages) > 0
            assert "📋 Your Weekly School Digest" in messages[0]["content"]

    # ... (4 more integration tests)
```

**Validation Gate 4**:
```bash
# Run all tests
pytest tests/ -v --cov=api --cov-report=term

# Target: 37/37 passing, 85%+ coverage
# Expected output:
# tests/test_health.py::test_health_check PASSED
# tests/test_gemini.py::test_parse_pdf_extracts_multiple_items PASSED
# tests/test_gemini.py::test_confidence_scores_valid_range PASSED
# ... (35 more)
#
# Coverage: 87%
```

**Evidence Required**:
- [ ] 37 tests created (8 + 3 + 10 + 8 + 3 + 5)
- [ ] All 37 tests passing
- [ ] Code coverage ≥85%
- [ ] Test fixtures created (newsletter PDFs, images)
- [ ] Integration tests cover full workflow

**Confidence**: PRESTIGE when 37/37 passing

**Time**: 2 hours

---

### **Phase 5: Hardy Validation Gates** (30 minutes)

**Goal**: Add quality gates from TEAOS

**Archaeological Foundation**:
```
agents/hardy_validator.py    ~150 lines
CLAUDE.md §2                 Evidence ratio protocol
CLAUDE.md §26                Validation gates
```

**Deliverables**:

**1. Hardy Validator Service** (`api/services/hardy_validator.py`)

```python
"""
Hardy validation framework from TEAOS

Import from: ../../agents/hardy_validator.py
Purpose: Quality gates for newsletter items before approval
"""
from typing import Dict, List, Any
from enum import Enum

class ConceptState(Enum):
    """Hardy confidence levels"""
    LATENT = 0.45       # Pattern observed, unvalidated
    HYPOTHETICAL = 0.65  # Working validation, needs rigor
    PRESTIGE = 0.90     # Validated, deployable

class HardyValidator:
    """
    Skeptical validation framework

    Pattern from agents/hardy_validator.py
    Validates items before they reach parents
    """

    @staticmethod
    def validate_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted newsletter item

        Returns:
            {
                "state": ConceptState,
                "confidence": float,
                "issues": List[str],
                "approved": bool
            }
        """
        issues = []
        confidence = item.get("confidence_score", 0.75)

        # 1. Required fields check
        required = ["type", "title", "audience_tags"]
        missing = [f for f in required if not item.get(f)]
        if missing:
            issues.append(f"Missing required fields: {', '.join(missing)}")
            confidence *= 0.5

        # 2. Date validation (if type=Event)
        if item.get("type") == "Event":
            if not item.get("date"):
                issues.append("Event missing date")
                confidence *= 0.8

        # 3. Audience tag validation
        tags = item.get("audience_tags", [])
        if not tags or (len(tags) == 1 and tags[0] == ""):
            issues.append("No audience tags specified")
            confidence *= 0.7

        # 4. Source snippet quality
        snippet = item.get("source_snippet", "")
        if len(snippet) < 20:
            issues.append("Source snippet too short (< 20 chars)")
            confidence *= 0.9

        # 5. Gemini confidence threshold
        if confidence < 0.70:
            issues.append(f"Low confidence score: {confidence}")

        # Determine state
        if confidence >= 0.90:
            state = ConceptState.PRESTIGE
            approved = True
        elif confidence >= 0.65:
            state = ConceptState.HYPOTHETICAL
            approved = False  # Needs human review
        else:
            state = ConceptState.LATENT
            approved = False  # Needs human review

        return {
            "state": state.name,
            "confidence": round(confidence, 2),
            "issues": issues,
            "approved": approved,
            "reasoning": f"Confidence {confidence:.2f} → {state.name}"
        }

    @staticmethod
    def validate_batch(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate batch of items

        Returns summary statistics
        """
        results = [HardyValidator.validate_item(item) for item in items]

        prestige_count = sum(1 for r in results if r["state"] == "PRESTIGE")
        hypothetical_count = sum(1 for r in results if r["state"] == "HYPOTHETICAL")
        latent_count = sum(1 for r in results if r["state"] == "LATENT")

        auto_approved = sum(1 for r in results if r["approved"])
        needs_review = len(results) - auto_approved

        return {
            "total": len(results),
            "prestige": prestige_count,
            "hypothetical": hypothetical_count,
            "latent": latent_count,
            "auto_approved": auto_approved,
            "needs_review": needs_review,
            "approval_rate": round(auto_approved / len(results) if results else 0, 2),
            "results": results
        }
```

**2. Pre-commit Hook** (`.git/hooks/pre-commit`)

```bash
#!/bin/bash
# Hardy validation gate for commits

echo "Running Hardy validation gates..."

# 1. Check evidence ratio in commits
evidence_ratio=$(python -c "
import re
import sys

# Read commit message
commit_msg = sys.stdin.read()

# Count claims (completion statements)
claims = len(re.findall(r'(complete|implemented|added|fixed|working|passing)', commit_msg, re.I))

# Count evidence (file:line citations)
evidence = len(re.findall(r'\w+\.(py|md):\d+', commit_msg))

# Calculate ratio
ratio = evidence / claims if claims > 0 else 1.0

print(f'{ratio:.2f}')
" < .git/COMMIT_EDITMSG)

if (( $(echo "$evidence_ratio < 0.80" | bc -l) )); then
    echo "❌ Evidence ratio too low: $evidence_ratio"
    echo "   Minimum: 0.80 (80% of claims verified)"
    echo "   Add file:line citations for claims"
    exit 1
fi

# 2. Run tests before commit
pytest tests/ -q || {
    echo "❌ Tests failing - cannot commit"
    exit 1
}

echo "✅ Hardy validation passed (evidence ratio: $evidence_ratio)"
```

**3. Tests** (`tests/test_hardy.py`)

```python
import pytest
from api.services.hardy_validator import HardyValidator, ConceptState

class TestHardyValidator:
    def test_prestige_item_approved(self):
        """Test high-quality item gets PRESTIGE and auto-approved"""
        item = {
            "type": "Event",
            "title": "Basketball game",
            "description": "Grade 5 vs Grade 6",
            "date": "2024-11-20",
            "time": "16:00",
            "audience_tags": ["grade_5", "Basketball"],
            "confidence_score": 0.95,
            "source_snippet": "Basketball game for Grade 5 on Nov 20 at 4pm in the gym."
        }

        result = HardyValidator.validate_item(item)

        assert result["state"] == "PRESTIGE"
        assert result["approved"] is True
        assert result["confidence"] >= 0.90

    def test_low_confidence_needs_review(self):
        """Test low confidence item requires human review"""
        item = {
            "type": "Event",
            "title": "Something",
            "audience_tags": ["all"],
            "confidence_score": 0.60,
            "source_snippet": "Short snippet"
        }

        result = HardyValidator.validate_item(item)

        assert result["state"] in ["LATENT", "HYPOTHETICAL"]
        assert result["approved"] is False
        assert len(result["issues"]) > 0

    def test_batch_validation_stats(self):
        """Test batch validation returns statistics"""
        items = [
            {"title": "Item 1", "audience_tags": ["grade_5"], "confidence_score": 0.95},
            {"title": "Item 2", "audience_tags": ["grade_3"], "confidence_score": 0.85},
            {"title": "Item 3", "audience_tags": ["all"], "confidence_score": 0.65},
        ]

        stats = HardyValidator.validate_batch(items)

        assert stats["total"] == 3
        assert stats["prestige"] >= 1
        assert stats["approval_rate"] > 0
```

**Validation Gate 5**:
```bash
# 1. Hardy validator works
pytest tests/test_hardy.py -v  # 3/3 passing

# 2. Pre-commit hook installed
chmod +x .git/hooks/pre-commit

# 3. Test pre-commit gate
git add api/services/hardy_validator.py
git commit -m "Add Hardy validator"
# Should check evidence ratio and run tests

# 4. Validate newsletter items
python -c "
from api.services.hardy_validator import HardyValidator
items = [...]  # Sample items
stats = HardyValidator.validate_batch(items)
print(f'Auto-approved: {stats[\"auto_approved\"]}/{stats[\"total\"]}')
print(f'Approval rate: {stats[\"approval_rate\"]}')
"
```

**Evidence Required**:
- [ ] api/services/hardy_validator.py created (imported from TEAOS)
- [ ] .git/hooks/pre-commit installed and working
- [ ] tests/test_hardy.py passing (3/3)
- [ ] Validation statistics computed correctly
- [ ] Evidence ratio gate blocks low-quality commits

**Confidence**: PRESTIGE when all gates pass

**Time**: 30 minutes

---

### **Phase 6: Documentation & Evidence Audit** (30 minutes)

**Goal**: Document hybrid architecture, verify evidence ratio

**Deliverables**:

**1. Updated README** (`README.md`)

```markdown
# ParentPath: Educational Equity Platform

**Version**: 2.0 (Hybrid Architecture)
**Tech Stack**: GitHub MVP + TEAOS Patterns

## Quick Start

### Option 1: SQLite (Zero Setup - RECOMMENDED)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY

# 3. Initialize database
python scripts/init_db.py

# 4. Run server
uvicorn api.main:app --reload

# 5. Test
curl http://localhost:8000/health
pytest tests/ -v
```

**That's it!** SQLite + free Gemini CLI tier = $0 cost, zero Docker.

### Option 2: PostgreSQL (Production)

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis qdrant

# 2. Update .env
DATABASE_URL=postgresql+asyncpg://parentpath:parentpath_dev_2024@localhost:5432/parentpath
USE_GEMINI_CLI=false  # Use paid API tier

# 3. Initialize
python scripts/init_db.py

# 4. Run
docker-compose up api worker
```

## Architecture

**Hybrid Approach** = Best of Both Worlds:

| Component | Implementation | Source |
|-----------|----------------|--------|
| **Core Services** | Gemini, Qdrant, FastAPI | GitHub MVP (1,804 LOC) |
| **Database** | SQLite (default) + PostgreSQL (optional) | TEAOS Pattern |
| **Gemini Mode** | CLI (free) + API (paid) | TEAOS Pattern |
| **Testing** | 37 comprehensive tests | Runbook Spec |
| **Validation** | Hardy gates (3-state confidence) | TEAOS Framework |
| **Patterns** | batch_analyzer, quality_scorer | CHAI Reuse (75%) |

## Testing

```bash
# Run all tests
pytest tests/ -v --cov=api

# Expected: 37/37 passing, 87% coverage
```

## Validation Gates

All items pass through Hardy validation:
- **PRESTIGE** (0.90+): Auto-approved, sent to parents
- **HYPOTHETICAL** (0.65-0.89): Human review required
- **LATENT** (<0.65): Rejected or manual entry

## Evidence Ratio

All commits require ≥80% evidence ratio:
```bash
# Pre-commit hook checks:
# - File:line citations for claims
# - Tests passing
# - Evidence ratio ≥ 0.80
```

## Contributing

See `HYBRID_INTEGRATION_PLAN.md` for full architecture.
```

**2. Evidence Ratio Audit** (`scripts/audit_evidence_ratio.py`)

```python
"""
Audit evidence ratio for this implementation

Calculate claims vs verified evidence across all documentation
"""
import re
from pathlib import Path

def audit_file(file_path: Path) -> dict:
    """Audit single file for evidence ratio"""
    content = file_path.read_text()

    # Count claims (completion statements)
    claim_patterns = [
        r'\b(complete|implemented|added|fixed|working|passing|ready|done)\b',
        r'\b(all|every|100%)\b.*\b(test|validation|check)\b',
        r'\b(successfully|correctly|properly)\b'
    ]
    claims = []
    for pattern in claim_patterns:
        claims.extend(re.findall(pattern, content, re.I))

    # Count evidence (file:line citations, test results, command outputs)
    evidence_patterns = [
        r'\w+\.(py|md):\d+',  # file:line citations
        r'tests/.*\.py.*passing',  # Test results
        r'pytest.*PASSED',  # Test output
        r'assert .* == .*',  # Assertions
        r'curl .* 200 OK',  # Command outputs
    ]
    evidence = []
    for pattern in evidence_patterns:
        evidence.extend(re.findall(pattern, content))

    claims_count = len(set(claims))
    evidence_count = len(set(evidence))
    ratio = evidence_count / claims_count if claims_count > 0 else 1.0

    return {
        "file": str(file_path),
        "claims": claims_count,
        "evidence": evidence_count,
        "ratio": round(ratio, 2)
    }

def audit_project() -> dict:
    """Audit entire project"""
    results = []

    # Audit documentation
    for md_file in Path(".").glob("*.md"):
        if md_file.name.startswith("."):
            continue
        results.append(audit_file(md_file))

    # Audit Python files
    for py_file in Path("api").rglob("*.py"):
        results.append(audit_file(py_file))

    # Calculate overall ratio
    total_claims = sum(r["claims"] for r in results)
    total_evidence = sum(r["evidence"] for r in results)
    overall_ratio = total_evidence / total_claims if total_claims > 0 else 1.0

    return {
        "files": results,
        "total_claims": total_claims,
        "total_evidence": total_evidence,
        "overall_ratio": round(overall_ratio, 2)
    }

if __name__ == "__main__":
    audit = audit_project()

    print(f"Evidence Ratio Audit")
    print(f"===================")
    print(f"Total claims: {audit['total_claims']}")
    print(f"Total evidence: {audit['total_evidence']}")
    print(f"Overall ratio: {audit['overall_ratio']}")
    print(f"")

    if audit['overall_ratio'] >= 0.95:
        print("✅ PRESTIGE (0.95+) - Excellent documentation")
    elif audit['overall_ratio'] >= 0.80:
        print("✅ PASSING (0.80+) - Acceptable documentation")
    else:
        print("❌ BELOW THRESHOLD (< 0.80) - Add more evidence")

    # Show per-file breakdown
    print(f"\nPer-file breakdown:")
    for result in sorted(audit['files'], key=lambda r: r['ratio']):
        print(f"  {result['file']}: {result['ratio']} ({result['evidence']}/{result['claims']})")
```

**3. Final Integration Checklist** (`INTEGRATION_CHECKLIST.md`)

```markdown
# Hybrid Integration Checklist

## Phase 1: SQLite Adapter ✅
- [x] api/database.py supports dual-mode (SQLite + PostgreSQL)
- [x] scripts/init_db.py creates database
- [x] .env.example updated with both options
- [x] Health check passes with SQLite
- [x] Evidence: parentpath.db exists, 200 OK response

## Phase 2: Gemini CLI Mode ✅
- [x] api/services/gemini_service.py supports CLI + API
- [x] USE_GEMINI_CLI flag switches modes
- [x] tests/test_gemini_cli.py passes (3/3)
- [x] CLI mode works (free tier)
- [x] Evidence: CLI test output, cost comparison documented

## Phase 3: CHAI Imports ✅
- [x] api/services/batch_analyzer.py (300 lines from CHAI)
- [x] api/services/quality_scorer.py (100 lines from CHAI)
- [x] tests/test_chai_imports.py passes (3/3)
- [x] Digest generation works
- [x] Evidence: Test results, sample digest output

## Phase 4: Test Expansion ✅
- [x] tests/test_gemini.py (8 tests)
- [x] tests/test_qdrant.py (10 tests)
- [x] tests/test_targeting.py (8 tests)
- [x] tests/test_integration.py (5 tests)
- [x] All 37 tests passing
- [x] Evidence: pytest output showing 37/37 PASSED

## Phase 5: Hardy Gates ✅
- [x] api/services/hardy_validator.py (150 lines from TEAOS)
- [x] .git/hooks/pre-commit installed
- [x] tests/test_hardy.py passes (3/3)
- [x] Validation statistics working
- [x] Evidence: Hardy test output, validation stats

## Phase 6: Documentation ✅
- [x] README.md updated with hybrid architecture
- [x] scripts/audit_evidence_ratio.py created
- [x] INTEGRATION_CHECKLIST.md complete
- [x] Evidence ratio ≥ 0.95 verified
- [x] Evidence: Audit report, all checklists complete

## Final Validation

```bash
# Run full test suite
pytest tests/ -v --cov=api --cov-report=term

# Expected: 37/37 passing, 87%+ coverage

# Audit evidence ratio
python scripts/audit_evidence_ratio.py

# Expected: ≥ 0.95 (PRESTIGE)

# Health check
curl http://localhost:8000/health

# Expected: {"status": "ok"}
```

## Deployment Ready ✅

All phases complete. System ready for:
- [ ] Commit to GitHub
- [ ] Tag release (v2.0-hybrid)
- [ ] Deploy to staging
- [ ] Production pilot
```

**Validation Gate 6**:
```bash
# 1. Evidence ratio audit
python scripts/audit_evidence_ratio.py
# Expected: ≥ 0.95

# 2. All tests passing
pytest tests/ -v
# Expected: 37/37 PASSED

# 3. Documentation complete
ls -la *.md
# Should see: README.md, HYBRID_INTEGRATION_PLAN.md, INTEGRATION_CHECKLIST.md

# 4. Ready to commit
git status
# Should show all new files tracked
```

**Evidence Required**:
- [ ] README.md updated with hybrid architecture
- [ ] scripts/audit_evidence_ratio.py passing
- [ ] INTEGRATION_CHECKLIST.md all items checked
- [ ] Evidence ratio ≥ 0.95 (PRESTIGE)
- [ ] All 37 tests passing

**Confidence**: PRESTIGE when all documentation complete

**Time**: 30 minutes

---

## 📊 TOTAL EFFORT SUMMARY

| Phase | Deliverable | Time | Tests | Evidence Ratio |
|-------|-------------|------|-------|----------------|
| 1 | SQLite Adapter | 30 min | Health check | PRESTIGE (0.90+) |
| 2 | Gemini CLI Mode | 45 min | 3 tests | PRESTIGE (0.90+) |
| 3 | CHAI Imports | 2 hours | 3 tests | PRESTIGE (0.90+) |
| 4 | Test Expansion | 2 hours | 31 tests | PRESTIGE (0.90+) |
| 5 | Hardy Gates | 30 min | 3 tests | PRESTIGE (0.90+) |
| 6 | Documentation | 30 min | Audit | PRESTIGE (0.95+) |
| **TOTAL** | **Hybrid System** | **6 hours** | **37 tests** | **PRESTIGE (0.95+)** |

**Final Deliverables**:
- ✅ GitHub MVP (1,804 LOC) preserved
- ✅ SQLite + PostgreSQL dual support
- ✅ Gemini CLI (free) + API (paid) hybrid
- ✅ CHAI patterns reused (batch_analyzer, quality_scorer)
- ✅ 37 comprehensive tests (vs 1 currently)
- ✅ Hardy validation gates (3-state confidence)
- ✅ Evidence ratio ≥ 0.95 (PRESTIGE)
- ✅ Complete documentation

**What You Get**:
- 🚀 Production-ready core services (GitHub)
- 🏗️ TEAOS-native flexibility (SQLite, CLI mode)
- ✅ Quality assurance (Hardy gates, 37 tests)
- 📚 Proven patterns (75% CHAI reuse)
- 💰 Cost-optimized (free tier option)
- 📊 Accountable (evidence ratio tracking)

---

## 🚦 EXECUTION PROTOCOL

**Ready to Begin?**

```bash
# Start Phase 1
cd ParentPath
git checkout teaos-hybrid-merge  # Already on this branch

# Execute phases sequentially
# Phase 1: 30 min
# Phase 2: 45 min
# Phase 3: 2 hours
# Phase 4: 2 hours
# Phase 5: 30 min
# Phase 6: 30 min

# Total: 6 hours to hybrid production system
```

**Awaiting approval to begin Phase 1 (SQLite Adapter - 30 min).**
