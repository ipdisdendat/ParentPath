# ParentPath: Parallel Orchestration Plan (vdev)

**Date**: 2025-11-16
**Pattern**: InfiniTEA Hybrid Orchestration (CLAUDE.md §22, §26)
**Authority**: This document follows §24 Session Handoff Protocol - execute as written

---

## Pre-Flight Check (§26 MANDATORY)

**1. Can tasks run independently?**
✅ YES - Core services (Gemini, Qdrant, WhatsApp) have no shared dependencies
✅ YES - Routes can be built once services exist
✅ YES - Workers depend on services but not on each other

**2. Have I consulted orchestration case studies?**
✅ YES - SESSION_2025_11_16 (12.5× speedup via parallel execution)
✅ YES - SESSION_HANDOFF_2025_11_06 (Orchestration Diffusion, 96/96 tests)
✅ YES - CLAUDE.md §22 (InfiniTEA pattern with shared memory)

**3. Am I launching multiple Task calls in ONE message?**
✅ YES - Waves 2 and 3 will launch parallel tracks in single messages

**Confidence Level**: HYPOTHETICAL (0.65) - Plan validated, pending execution evidence

---

## Architecture: 4 Waves (Sequential) with Parallel Tracks

```
Wave 1 (Foundation) → Sequential baseline
  ↓
Wave 2 (Core Services) → 4 tracks PARALLEL
  ↓
Wave 3 (Application Layer) → 3 tracks PARALLEL
  ↓
Wave 4 (Integration) → Sequential validation
```

**Estimated Time:**
- Sequential: ~25-30 hours
- Parallel (with this plan): ~6-8 hours
- **Target Speedup: 3-4×**

---

## Wave 1: Foundation (Sequential - 45 min)

**Why Sequential**: All other waves depend on this baseline.

### Deliverables
1. **Repository Structure**
   ```
   ParentPath/
   ├── api/
   ├── workers/
   ├── tests/
   ├── docker-compose.yml
   ├── Dockerfile
   ├── requirements.txt
   └── _WORKING_MEMORY.md
   ```

2. **Docker Compose**
   - PostgreSQL 15
   - Redis 7
   - Qdrant latest
   - MinIO (S3)

3. **Database Schema**
   - SQLAlchemy models (parents, children, items, cards, tickets)
   - Alembic migrations
   - Initial seed data

4. **Shared Working Memory**
   - `_WORKING_MEMORY.md` for cross-track coordination
   - Template from CLAUDE.md §22

### Validation Gate 1
```bash
# Must pass before Wave 2:
docker-compose up -d
psql $DATABASE_URL -c "SELECT COUNT(*) FROM parents;"  # Should return 0
curl http://localhost:6333/collections  # Should return []
pytest tests/test_models.py -v  # Should pass
```

**Evidence Required**:
- [ ] docker-compose.yml:1-60 (all services defined)
- [ ] api/models/parent.py:1-30 (Parent model)
- [ ] tests/test_models.py passing (5/5 tests)

**Confidence**: PRESTIGE (0.90) when Gate 1 passes

---

## Wave 2: Core Services (PARALLEL - 90 min)

**Launch Pattern**: Single message with 4 Task calls

### Shared Memory Protocol
All tracks MUST:
1. Read `_WORKING_MEMORY.md` FIRST
2. Append decisions (never delete)
3. Mark completion: `[TRACK_X]: COMPLETE`

### Track A: Gemini Service
**Specialist Focus**: Multimodal AI integration

**Deliverables**:
- `api/services/gemini_service.py` (~300 lines)
  - `parse_pdf_newsletter()` - Extract items from PDF
  - `parse_image_flyer()` - OCR for photos
  - `translate_digest()` - Multilingual translation
  - `generate_embedding()` - 768-dim vectors for Qdrant
- `tests/test_gemini.py` (~200 lines)
  - Mock API responses
  - Test multimodal parsing
  - Test translation accuracy

**Success Criteria**:
- [ ] Parse sample PDF → 20+ items extracted
- [ ] Confidence scores ≥0.70 for all items
- [ ] Translation: EN → PA/TL/ZH working
- [ ] Tests: 8/8 passing

**Dependencies**: None (uses Gemini API only)

---

### Track B: Qdrant Service
**Specialist Focus**: Vector search & memory

**Deliverables**:
- `api/services/qdrant_service.py` (~400 lines)
  - `init_collections()` - Create 3 collections
  - `index_item()` - Add item to vector DB
  - `semantic_search()` - Parent queries
  - `find_duplicate_items()` - Duplicate detection
  - `get_recommendations()` - Collaborative filtering
- `tests/test_qdrant.py` (~250 lines)
  - Test indexing
  - Test semantic search
  - Test duplicate detection

**Success Criteria**:
- [ ] 3 collections created (items, messages, tickets)
- [ ] Index 50 sample items
- [ ] Search: "basketball games" → finds "basketball practice" (≥0.80 similarity)
- [ ] Duplicate detection: 2 similar items found
- [ ] Tests: 10/10 passing

**Dependencies**: None (Qdrant standalone)

---

### Track C: WhatsApp Service
**Specialist Focus**: Messaging integration

**Deliverables**:
- `api/services/messenger_service.py` (~300 lines)
  - `send_whatsapp_message()` - Template messages
  - `send_interactive_message()` - Buttons
  - `parse_inbound_message()` - Intent detection
  - `format_digest()` - Emoji + sections
- `tests/test_messenger.py` (~200 lines)
  - Mock WhatsApp API
  - Test message formatting
  - Test intent detection

**Success Criteria**:
- [ ] Send digest (mock API)
- [ ] Detect intents: done, help, query, error
- [ ] Format multilingual digest
- [ ] Tests: 7/7 passing

**Dependencies**: None (WhatsApp Cloud API standalone)

---

### Track D: Targeting Engine
**Specialist Focus**: SQL-based audience matching

**Deliverables**:
- `api/services/targeting_service.py` (~250 lines)
  - `get_relevant_items()` - SQL filtering by grade/activity
  - `create_cards()` - Generate personalized cards
  - `calculate_audience_size()` - Estimate reach
- `tests/test_targeting.py` (~200 lines)
  - Test grade matching
  - Test activity matching
  - Test "all" audience

**Success Criteria**:
- [ ] Parent (Grade 5 + Basketball) → Gets basketball items
- [ ] Parent (Grade 3) → Does NOT get Grade 5 items
- [ ] "all" items → Delivered to everyone
- [ ] Tests: 8/8 passing

**Dependencies**: PostgreSQL models from Wave 1

---

### Validation Gate 2
```bash
# All tracks must pass before Wave 3:
pytest tests/test_gemini.py -v      # 8/8 passing
pytest tests/test_qdrant.py -v      # 10/10 passing
pytest tests/test_messenger.py -v   # 7/7 passing
pytest tests/test_targeting.py -v   # 8/8 passing
```

**Completion Status** (update `_WORKING_MEMORY.md`):
- [ ] TRACK_A: Gemini Service (Parallel)
- [ ] TRACK_B: Qdrant Service (Parallel)
- [ ] TRACK_C: WhatsApp Service (Parallel)
- [ ] TRACK_D: Targeting Engine (Parallel)

**Evidence Required**: Test results with file:line citations
**Confidence**: PRESTIGE (0.90) when all 33 tests pass

---

## Wave 3: Application Layer (PARALLEL - 90 min)

**Launch Pattern**: Single message with 3 Task calls

### Track E: FastAPI Routes
**Specialist Focus**: HTTP API endpoints

**Deliverables**:
- `api/routers/intake.py` (~200 lines)
  - POST /intake/email - Email webhook
  - POST /intake/upload - Admin upload
  - POST /intake/whatsapp - WhatsApp photo
- `api/routers/admin.py` (~250 lines)
  - GET /items?status=pending - Review queue
  - POST /items/{id}/approve - Approve item
  - GET /newsletters - List newsletters
- `api/routers/family.py` (~200 lines)
  - GET /family/settings - Parent preferences
  - PUT /family/settings - Update preferences
  - GET /family/history - Delivery history
- `tests/test_routes.py` (~300 lines)

**Success Criteria**:
- [ ] All endpoints return 200 OK
- [ ] Pydantic validation working
- [ ] Tests: 15/15 passing

**Dependencies**: Services from Wave 2

---

### Track F: Background Workers
**Specialist Focus**: Async job processing

**Deliverables**:
- `workers/parse_worker.py` (~200 lines)
  - Parse newsletter job
  - Queue management
  - Error handling
- `workers/send_worker.py` (~150 lines)
  - Send digest job
  - Retry logic
- `workers/reminder_worker.py` (~150 lines)
  - Daily reminder scheduler
- `tests/test_workers.py` (~250 lines)

**Success Criteria**:
- [ ] Parse job: Newsletter → 20+ items
- [ ] Send job: Digest delivered to 10 parents
- [ ] Reminder job: Deadlines detected
- [ ] Tests: 10/10 passing

**Dependencies**: Services from Wave 2

---

### Track G: Admin Review UI
**Specialist Focus**: Human-in-loop interface

**Deliverables**:
- `api/templates/review_queue.html` (~200 lines)
  - Pending items table
  - Approve/Reject buttons
  - Gemini reasoning display
  - Qdrant similar items
- `api/templates/dashboard.html` (~150 lines)
  - Parsing stats
  - Engagement metrics
- `tests/test_ui.py` (~100 lines)

**Success Criteria**:
- [ ] Review queue loads
- [ ] Approve button → Item status = "approved"
- [ ] Similar items displayed
- [ ] Tests: 5/5 passing

**Dependencies**: Routes from Track E

---

### Validation Gate 3
```bash
# All tracks must pass before Wave 4:
pytest tests/test_routes.py -v   # 15/15 passing
pytest tests/test_workers.py -v  # 10/10 passing
pytest tests/test_ui.py -v       # 5/5 passing
```

**Completion Status**:
- [ ] TRACK_E: FastAPI Routes (Parallel)
- [ ] TRACK_F: Background Workers (Parallel)
- [ ] TRACK_G: Admin Review UI (Parallel)

**Evidence Required**: Test results + UI screenshots
**Confidence**: PRESTIGE (0.90) when all 30 tests pass

---

## Wave 4: Integration (Sequential - 2 hours)

**Why Sequential**: End-to-end workflow testing requires all components.

### Deliverables

1. **End-to-End Test**
   ```python
   # tests/test_integration.py
   async def test_full_pipeline():
       # 1. Upload newsletter
       newsletter_id = await upload_pdf("sample.pdf")

       # 2. Parse (Gemini)
       await parse_newsletter_job(newsletter_id)

       # 3. Index in Qdrant
       items = await get_items(newsletter_id)
       assert len(items) >= 20

       # 4. Target parents
       parent = await create_test_parent(grade=5)
       cards = await generate_digest(parent.id)
       assert len(cards) > 0

       # 5. Send WhatsApp
       await send_digest_job(parent.id)

       # 6. Verify delivery
       messages = await get_messages(parent.id)
       assert messages[0].status == "sent"
   ```

2. **Performance Testing**
   ```python
   # tests/load_test.py (Locust)
   # 100 concurrent parents
   # 50 searches/min
   # Target: <200ms p95
   ```

3. **Documentation**
   - README.md with setup instructions
   - API docs (OpenAPI/Swagger)
   - Architecture diagram

### Validation Gate 4 (Final)
```bash
# Must pass for PRESTIGE confidence:
pytest tests/test_integration.py -v  # 5/5 passing
locust -f tests/load_test.py --headless -u 100 -r 10 -t 30s
# → p95 < 200ms
docker-compose up -d  # All services healthy
curl http://localhost:8000/health  # {"status": "ok"}
```

**Evidence Required**:
- [ ] Integration tests: 5/5 passing
- [ ] Load test: p95 < 200ms
- [ ] All services: healthy
- [ ] README: complete with examples

**Confidence**: PRESTIGE (0.90) when all gates pass

---

## Execution Protocol

### Phase 1: Foundation (Solo)
```bash
# Execute Wave 1 directly (no parallelization)
# Estimated: 45 minutes
# Create docker-compose.yml, models, migrations
# Run Gate 1 validation
```

### Phase 2: Parallel Services (§26 Pattern)
```python
# Launch Wave 2 in SINGLE message with 4 Task calls:

Task(
    subagent_type="spec-impl",
    description="Gemini Service Implementation",
    prompt=TRACK_A_SPEC
)
Task(
    subagent_type="spec-impl",
    description="Qdrant Service Implementation",
    prompt=TRACK_B_SPEC
)
Task(
    subagent_type="spec-impl",
    description="WhatsApp Service Implementation",
    prompt=TRACK_C_SPEC
)
Task(
    subagent_type="spec-impl",
    description="Targeting Engine Implementation",
    prompt=TRACK_D_SPEC
)
# All execute concurrently
# Coordinate via _WORKING_MEMORY.md
# Estimated: 90 minutes total (vs 6 hours sequential)
```

### Phase 3: Parallel Application (§26 Pattern)
```python
# Launch Wave 3 in SINGLE message with 3 Task calls:

Task(subagent_type="spec-impl", prompt=TRACK_E_SPEC)
Task(subagent_type="spec-impl", prompt=TRACK_F_SPEC)
Task(subagent_type="spec-impl", prompt=TRACK_G_SPEC)
# Estimated: 90 minutes total (vs 5 hours sequential)
```

### Phase 4: Integration (Solo)
```bash
# Execute Wave 4 directly (integration tests)
# Estimated: 2 hours
# Run Gate 4 validation
```

---

## Evidence Ratio Target

**Standard**: ≥90% (CLAUDE.md §2)
**PRESTIGE**: ≥95%

**How to Achieve**:
- All code changes: file:line citations
- All tests: pytest output with pass/fail counts
- All validations: command outputs
- All decisions: append to `_WORKING_MEMORY.md`

**Example Evidence**:
```
✅ Gemini service complete
Evidence: api/services/gemini_service.py:1-300 (parse_pdf_newsletter implemented)
Tests: tests/test_gemini.py:8/8 passing (output: pytest.log:45-52)
Validation: Sample PDF parsed → 23 items extracted (confidence_avg=0.87)
```

---

## Risk Mitigation

### Risk 1: Gemini API Rate Limits
**Mitigation**: Mock API in tests, use exponential backoff in production
**Fallback**: Implement queue with Redis for rate-limited retries

### Risk 2: Qdrant Indexing Slowness
**Mitigation**: Batch upserts (100 items at once)
**Fallback**: Mock Qdrant in tests, use in-memory collection

### Risk 3: WhatsApp Template Approval Delay
**Mitigation**: Start approval process immediately (2-3 days)
**Fallback**: Use Twilio SMS for MVP testing

### Risk 4: Track Dependencies Blocking
**Mitigation**: Clear dependency chain in Wave structure
**Fallback**: If Track X blocked, continue other tracks, come back later

---

## Success Metrics

**Development Speed**:
- ✅ Target: 6-8 hours total (vs 25-30 sequential)
- ✅ Speedup: 3-4× via parallelization
- ✅ Zero merge conflicts (shared memory coordination)

**Code Quality**:
- ✅ Test coverage: ≥80%
- ✅ All validation gates: PASS
- ✅ Evidence ratio: ≥90%

**Deliverables**:
- ✅ 4 core services (~1,250 lines)
- ✅ 3 application components (~850 lines)
- ✅ Tests (~1,500 lines)
- ✅ Documentation complete

---

## Next Steps

**Immediate** (now):
1. User approves this plan
2. Execute Wave 1 (Foundation) - 45 min
3. Run Gate 1 validation

**After Gate 1 PASS**:
1. Launch Wave 2 (4 tracks PARALLEL in single message) - 90 min
2. Monitor `_WORKING_MEMORY.md` for coordination
3. Run Gate 2 validation (33 tests)

**After Gate 2 PASS**:
1. Launch Wave 3 (3 tracks PARALLEL in single message) - 90 min
2. Run Gate 3 validation (30 tests)

**After Gate 3 PASS**:
1. Execute Wave 4 (Integration) - 2 hours
2. Run Gate 4 validation (5 tests + load test)
3. **PRESTIGE confidence achieved** → Ship MVP

---

## References

**Patterns Applied**:
- CLAUDE.md §22: InfiniTEA Hybrid Orchestration
- CLAUDE.md §26: Cross-Referential Lesson Enforcement (parallel execution)
- SESSION_2025_11_16: Parallel orchestration (12.5× speedup)
- SESSION_HANDOFF_2025_11_06: Shared memory coordination (96/96 tests)

**Authority Hierarchy** (§24):
1. This plan (runbook explicit instructions)
2. PRD requirements (feature specifications)
3. CLAUDE.md protocols (baseline standards)

---

**Plan Status**: HYPOTHETICAL (0.65) - Pending execution validation
**Target Confidence**: PRESTIGE (0.90) when all gates pass
**Evidence Tracking**: Via `_WORKING_MEMORY.md` + test artifacts

**Ready to execute. Awaiting user approval to begin Wave 1.**
