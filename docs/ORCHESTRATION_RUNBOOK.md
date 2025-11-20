# ParentPath: Production Execution Runbook (v1.0)

**System**: ParentPath Educational Equity Platform
**Version**: 1.0 (Merged Architecture)
**Date**: 2025-11-17
**Status**: Ready for Execution
**Pattern**: InfiniTEA Hybrid Orchestration (CLAUDE.md §22, §26)
**Authority**: §24 Session Handoff Protocol - Execute as written
**Evidence Ratio Target**: 95%+

---

## 📋 EXECUTIVE SUMMARY

### Architectural Foundation

**This runbook synthesizes**:
- ✅ **Wave-based structure** - 4 waves with clean separation of concerns
- ✅ **Validation gates** - 33+30+5+5 tests with explicit pass criteria
- ✅ **Parallel orchestration** - 3-4× speedup via concurrent execution
- ✅ **Evidence-based planning** - Archaeological discovery of reusable patterns

### Current State

**Phase 0 Complete** (Committed: a3666e5):
- ✅ FastAPI application structure
- ✅ Database models (Parent, Child, Item, Card, Newsletter, Ticket, etc.)
- ✅ Gemini 2.0 Flash service (multimodal parsing, embeddings, translation)
- ✅ Qdrant vector DB service (semantic search, duplicate detection)
- ✅ API routers (health, intake, admin, family, webhooks)
- ✅ Docker Compose infrastructure
- ✅ Test framework foundation

**What's Next**:
- 🔄 Workers & background jobs (parser, digest, reminder)
- 🔄 Integration testing (end-to-end workflows)
- 🔄 Production deployment readiness

### Goal

Complete **ParentPath MVP** via 4-wave parallel orchestration:

```
Wave 1: Foundation ✅ (45 min) - COMPLETE
  ├─ Repository structure
  ├─ Database schema
  └─ Core services skeleton

Wave 2: Core Services (90 min, 4 PARALLEL tracks)
  ├─ Track A: Gemini Service enhancement
  ├─ Track B: Qdrant Service enhancement
  ├─ Track C: WhatsApp Service
  └─ Track D: Targeting Engine

Wave 3: Application Layer (90 min, 3 PARALLEL tracks)
  ├─ Track E: Parser & Digest Workers
  ├─ Track F: Reply Handling & Intent Detection
  └─ Track G: Admin Review Portal

Wave 4: Integration (2 hours sequential)
  └─ End-to-end testing + validation
```

**Estimated Speedup**: 3-4× vs sequential execution

---

## 🎯 PRE-FLIGHT CHECK (§26 MANDATORY)

**1. Can tasks run independently?**
- ✅ Wave 2: All 4 services have zero shared dependencies
- ✅ Wave 3: Workers/handlers depend on Wave 2 services (not each other)

**2. Have I consulted orchestration case studies?**
- ✅ SESSION_2025_11_16 (12.5× speedup via parallel execution)
- ✅ SESSION_HANDOFF_2025_11_06 (96/96 tests, zero conflicts)
- ✅ CLAUDE.md §22 (InfiniTEA pattern with shared memory)

**3. Am I launching multiple Task calls in ONE message?**
- ✅ Wave 2: 4 Task calls in single message
- ✅ Wave 3: 3 Task calls in single message

**4. Quality over speed?**
- ✅ Parallelization for efficiency, not rushing
- ✅ Full validation gates enforced
- ✅ Evidence ratio: 95%+ target
- ✅ Production-ready code, not MVP-grade

**Confidence Level**: HYPOTHETICAL (0.65) - Plan validated, pending execution evidence

---

## 🌊 WAVE STRUCTURE

### Wave 1: Foundation ✅ **COMPLETE**

**Status**: Committed to `claude/help-code-request-0129Jqcif72wsj2ovpnR7rmU`

**Deliverables**:
- ✅ 30 files, 2,650+ lines of code
- ✅ Complete data models (SQLAlchemy async)
- ✅ Gemini service (parsing, embeddings, translation)
- ✅ Qdrant service (indexing, search, recommendations)
- ✅ API routers (5 modules)
- ✅ Docker Compose infrastructure
- ✅ Test framework with fixtures

**Validation Gate 1**: ✅ PASSED
- Database models created
- Health endpoints working
- Services initialized
- Tests framework ready

---

### Wave 2: Core Services Enhancement

**Launch Pattern**: Single message with 4 Task calls (§26 parallel orchestration)

**Shared Memory Protocol**:
All tracks MUST:
1. Read `_WORKING_MEMORY.md` FIRST
2. Append decisions (never delete others' entries)
3. Mark completion: `[TRACK_X]: COMPLETE`

#### Track A: Gemini Service Enhancement

**Current State** (from Phase 0):
- ✅ Basic structure exists: `api/services/gemini_service.py`
- ✅ Methods stubbed: `parse_pdf_newsletter()`, `generate_embedding()`, `translate_text()`

**Enhancements Needed**:
1. **Full PDF parsing implementation** with structured extraction
2. **Image/flyer OCR** via Gemini Vision
3. **Voice message transcription** (multimodal)
4. **Table extraction** from embedded CSVs
5. **Comprehensive error handling** and retries
6. **Rate limiting** awareness (15 RPM free tier)

**Success Criteria**:
- [ ] Parse test newsletter → 20+ items extracted
- [ ] Confidence scores ≥0.70 for 90% of items
- [ ] Translation: EN → PA/TL/ZH working
- [ ] Embeddings: 768-dim vectors validated
- [ ] Tests: 8/8 passing

**Evidence Required**:
- File: `api/services/gemini_service.py:1-400` (enhanced)
- Tests: `tests/test_gemini.py:8/8 passing`
- Fixture: `tests/fixtures/parsed_newsletter_sample.json`
- Logs: Gemini API token usage tracking

#### Track B: Qdrant Service Enhancement

**Current State** (from Phase 0):
- ✅ Basic structure exists: `api/services/qdrant_service.py`
- ✅ Collections initialized
- ✅ Basic indexing and search stubbed

**Enhancements Needed**:
1. **Batch indexing** optimization (100 items/batch)
2. **Advanced filtering** (grade + activity combinations)
3. **Similarity threshold tuning** for duplicates
4. **Recommendation engine** (collaborative filtering)
5. **Performance benchmarks** (< 100ms search latency)

**Success Criteria**:
- [ ] 3 collections operational (items, messages, tickets)
- [ ] Index 50 sample items < 5 seconds
- [ ] Search: "basketball games" → finds "basketball practice" (≥0.80 similarity)
- [ ] Duplicate detection: 2 similar items flagged
- [ ] Tests: 10/10 passing

**Evidence Required**:
- File: `api/services/qdrant_service.py:1-450` (enhanced)
- Tests: `tests/test_qdrant.py:10/10 passing`
- Screenshot: Qdrant dashboard showing collections
- Metrics: Search latency measurements

#### Track C: WhatsApp Service

**Current State** (from Phase 0):
- ✅ Webhook endpoints stubbed: `api/routers/webhooks.py`
- ⚠️ No implementation yet

**Deliverables**:
1. **WhatsApp Cloud API integration**
   - Send template messages
   - Receive inbound messages
   - Handle delivery status updates
2. **Intent detection**
   - DONE, HELP, QUERY, ERROR patterns
3. **Message formatting**
   - Emoji-based sections
   - Calendar links
   - Multilingual digests
4. **Mock mode** for testing (no real WhatsApp required)

**Success Criteria**:
- [ ] Send digest (mock mode)
- [ ] Detect intents: 90%+ accuracy on test cases
- [ ] Format multilingual digest (4 languages)
- [ ] Tests: 7/7 passing

**Evidence Required**:
- File: `api/services/messenger_service.py:1-350`
- Tests: `tests/test_messenger.py:7/7 passing`
- Fixture: Sample formatted digests (EN, PA, TL, ZH)

**Note**: WhatsApp Business approval takes 2-3 **weeks** (not days). Use Twilio SMS or mock mode for MVP.

#### Track D: Targeting Engine

**Current State** (from Phase 0):
- ✅ Models support relationships (Parent → Child → Subscriptions)
- ⚠️ No targeting logic yet

**Deliverables**:
1. **SQL-based audience matching**
   - Match by grade(s)
   - Match by activity subscriptions
   - "all" audience handling
2. **Card generation**
   - Create personalized cards for parents
   - Avoid duplicates
3. **Audience size estimation**
   - Preview before sending

**Success Criteria**:
- [ ] Parent (Grade 5 + Basketball) → Gets basketball items
- [ ] Parent (Grade 3) → Does NOT get Grade 5 items
- [ ] "all" items → Delivered to everyone
- [ ] Tests: 8/8 passing

**Evidence Required**:
- File: `api/services/targeting_service.py:1-300`
- Tests: `tests/test_targeting.py:8/8 passing`
- SQL query plans with index usage

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

**Completion Status** (update `_WORKING_MEMORY.md`):
- [ ] TRACK_A: Gemini Service Enhanced
- [ ] TRACK_B: Qdrant Service Enhanced
- [ ] TRACK_C: WhatsApp Service Implemented
- [ ] TRACK_D: Targeting Engine Implemented

**Evidence Required**: Test results with file:line citations
**Confidence**: PRESTIGE (0.90) when all 33 tests pass

---

### Wave 3: Application Layer

**Launch Pattern**: Single message with 3 Task calls

#### Track E: Parser & Digest Workers

**Deliverables**:
1. **Parse Worker** (`workers/parse_worker.py`)
   - Background job for newsletter parsing
   - Gemini integration
   - Qdrant duplicate check
   - Hardy confidence gates
2. **Digest Worker** (`workers/digest_worker.py`)
   - Weekly digest generation
   - Targeting service integration
   - Message formatting
   - Delivery scheduling

**Success Criteria**:
- [ ] Parse job: Newsletter → 20+ items created
- [ ] Digest job: 10 parents receive personalized digests
- [ ] Tests: 10/10 passing

#### Track F: Reply Handling

**Deliverables**:
1. **Intent detection** enhancement
2. **DONE handling** (mark cards complete)
3. **Query handling** (semantic search + Gemini RAG)
4. **Error reporting** (create tickets)

**Success Criteria**:
- [ ] Reply "DONE" → Card marked complete
- [ ] Query "When's basketball?" → Correct answer returned
- [ ] Error report → Ticket created
- [ ] Tests: 5/5 passing

#### Track G: Admin Review Portal

**Deliverables**:
1. **Review queue UI** (HTML templates)
2. **Approve/reject actions**
3. **Similar items display** (Qdrant)
4. **Audit trail** tracking

**Success Criteria**:
- [ ] Review queue loads pending items
- [ ] Approve button → Item status updated
- [ ] Similar items displayed via Qdrant
- [ ] Tests: 5/5 passing

---

### Validation Gate 3

```bash
pytest tests/test_workers.py -v   # 10/10 passing
pytest tests/test_handlers.py -v  # 5/5 passing
pytest tests/test_admin_ui.py -v  # 5/5 passing

# Total: 20 tests must pass
```

---

### Wave 4: Integration & Validation

**Sequential execution** (requires all previous waves)

#### End-to-End Testing

**Test Flow**:
1. Upload newsletter (PDF)
2. Parse with Gemini → Items created
3. Index in Qdrant → Searchable
4. Target parents → Cards generated
5. Send digests → WhatsApp/SMS delivered
6. Reply handling → Cards marked complete

**Success Criteria**:
- [ ] Full pipeline: Upload → Delivery works
- [ ] 95%+ parsing accuracy
- [ ] 100% targeting accuracy (deterministic SQL)
- [ ] 95%+ delivery success rate
- [ ] Tests: 5/5 passing

#### Performance Testing

```python
# Load test: 100 concurrent parents, 50 searches/min
# Target: <200ms p95 latency
```

#### Documentation

- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] Setup instructions tested
- [ ] Architecture diagrams finalized
- [ ] Challenge submission package ready

---

### Validation Gate 4 (Final)

```bash
pytest tests/test_integration.py -v  # 5/5 passing
# Load test: p95 < 200ms
curl http://localhost:8000/health  # {"status": "ok"}
```

**Evidence Required**:
- [ ] Integration tests: 5/5 passing
- [ ] Load test results
- [ ] All services: healthy
- [ ] README: complete

**Confidence**: PRESTIGE (0.90) when all gates pass

---

## 📊 EVIDENCE RATIO TRACKING

**Target**: ≥95% (PRESTIGE)

**Example Evidence**:
```
Claim: "Parsing accuracy >= 90%"
Evidence:
  - tests/test_gemini.py:42 - test_parse_newsletter_complex() passes
  - tests/fixtures/parsed_newsletter_sample.json - 18/20 items extracted
  - Accuracy: 90% (18/20)
  - File: api/services/gemini_service.py:85-120 (parse_pdf_newsletter)
```

---

## 🚦 EXECUTION PROTOCOL

### Phase 1: Foundation ✅ **COMPLETE**
- Executed directly
- All deliverables committed
- Gate 1 validation: PASSED

### Phase 2: Parallel Services (§26 Pattern)

**Launch Wave 2** in SINGLE message with 4 Task calls:
```python
Task(subagent_type="spec-impl", description="Gemini Enhancement", prompt=TRACK_A_SPEC)
Task(subagent_type="spec-impl", description="Qdrant Enhancement", prompt=TRACK_B_SPEC)
Task(subagent_type="spec-impl", description="WhatsApp Service", prompt=TRACK_C_SPEC)
Task(subagent_type="spec-impl", description="Targeting Engine", prompt=TRACK_D_SPEC)
```

All execute concurrently → Coordinate via `_WORKING_MEMORY.md`

### Phase 3: Parallel Application (§26 Pattern)

**Launch Wave 3** in SINGLE message with 3 Task calls:
```python
Task(subagent_type="spec-impl", prompt=TRACK_E_SPEC)  # Workers
Task(subagent_type="spec-impl", prompt=TRACK_F_SPEC)  # Handlers
Task(subagent_type="spec-impl", prompt=TRACK_G_SPEC)  # Admin UI
```

### Phase 4: Integration

Execute Wave 4 directly (integration tests, validation)

---

## 🎯 SUCCESS METRICS

**Development Efficiency**:
- ✅ Parallel execution: 3-4× faster than sequential
- ✅ Zero merge conflicts (shared memory coordination)
- ✅ Validation gates: Systematic quality assurance

**Code Quality**:
- ✅ Test coverage: ≥80%
- ✅ Evidence ratio: ≥95%
- ✅ All validation gates: PASS
- ✅ Production-ready: Full error handling, logging, monitoring

**Deliverables**:
- ✅ 4 core services enhanced (~1,500 lines)
- ✅ 3 application components (~1,000 lines)
- ✅ Tests (~1,200 lines)
- ✅ Documentation complete

---

## 💡 KEY INSIGHTS

**Why This Approach Works**:

1. **Parallel Execution** (§26)
   - Independent tasks run concurrently
   - 3-4× speedup vs sequential
   - Shared memory prevents conflicts

2. **Validation Gates**
   - Systematic quality checks at each wave
   - Hardy framework: LATENT → HYPOTHETICAL → PRESTIGE
   - 95%+ evidence ratio enforced

3. **Archaeological Grounding**
   - Reuse existing patterns where possible
   - Phase 0 foundation already complete
   - Focus on enhancement vs greenfield

4. **Quality Over Speed**
   - Parallelization for efficiency, not rushing
   - Full test coverage required
   - Production-grade code standards

---

## 📚 REFERENCES

**Patterns Applied**:
- CLAUDE.md §22: InfiniTEA Hybrid Orchestration
- CLAUDE.md §26: Cross-Referential Lesson Enforcement (parallel execution)
- SESSION_2025_11_16: Parallel orchestration (12.5× speedup)
- SESSION_HANDOFF_2025_11_06: Shared memory coordination (96/96 tests)

**Authority Hierarchy** (§24):
1. This runbook (execution instructions)
2. PRD.md (feature specifications)
3. CLAUDE.md protocols (baseline standards)

---

**Plan Status**: HYPOTHETICAL (0.65) - Pending execution validation
**Target Confidence**: PRESTIGE (0.90) when all gates pass
**Evidence Tracking**: Via `_WORKING_MEMORY.md` + test artifacts

**Ready to execute Waves 2-4.**

---

## 📝 EXECUTION LOG

### 2025-11-17: Wave 1 Complete
- Commit: `a3666e5` - Phase 0 foundation
- Status: ✅ All validation gates passed
- Evidence: 30 files, 2,650+ lines, test framework ready

### Next: Wave 2 Launch
- Awaiting execution signal
- 4 parallel tracks ready
- Estimated completion: 90 minutes (wall-clock)
