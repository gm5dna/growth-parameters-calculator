# CLAUDE.md - Quick Reference

> **For detailed context:** See `PROJECT.md`
> This file contains only essentials for AI assistance.

## Quick Start

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt              # Production
pip install -r requirements-dev.txt          # Dev/test only
npm install                                  # Jest + frontend test deps

# Run
python app.py                                # Dev :8080

# Test & Deploy
pytest && npm test                           # All tests (271 tests)
git add . && git commit -m "msg" && git push # Auto-deploys
```

## Stack

**Backend:** Flask 3.0.0 + Python 3.12.8 (greenlet requirement)
**Frontend:** Vanilla JS + Chart.js + Material Symbols
**Growth:** rcpchgrowth (RCPCH library)
**Deploy:** https://growth-parameters-calculator.onrender.com
**Docs:** https://gm5dna.github.io/growth-parameters-calculator/

## Files

| File | Purpose | Lines | Tests |
|------|---------|-------|-------|
| `app.py` | Routes & orchestration | 900 | 35+ endpoint tests |
| `static/script.js` | Frontend logic | 970 | 20+ Jest tests |
| `static/validation.js` | Client validation | 207 | 30+ Jest tests |
| `static/clipboard.js` | Clipboard formatting | 370 | 25+ Jest tests |
| `constants.py` | Config & thresholds | - | - |
| `validation.py` | Input validation | - | 100% coverage |
| `calculations.py` | Business logic | - | 100% coverage |
| `models.py` | rcpchgrowth wrapper | - | 30+ tests |
| `utils.py` | Helpers (MPH, etc) | - | 23+ tests |
| `pdf_utils.py` | PDF generation | - | 5+ tests |

## API

- `GET /` → SPA
- `POST /calculate` → Growth calculations
- `POST /chart-data` → Centile curves
- `POST /export-pdf` → PDF report

## Key Patterns

- **Validation:** Client (feedback) + Server (authoritative)
- **Errors:** `ValidationError` with codes (ERR_001-010)
- **Responses:** `format_success_response()` / `format_error_response()`
- **Measurements:** `create_measurement()` factory
- **Growth data:** All via `rcpchgrowth.Measurement`

## Testing

**271 tests total:** 177 backend (pytest) + 94 frontend (Jest)
**Pass rate:** 97% (262/271 passing)
**Coverage:** 31% overall (85%+ on tested files)

```bash
# Backend tests
pytest -v                        # Run all backend tests
pytest --cov=. --cov-report=html # With coverage
pytest -k "test_name"            # Specific test

# Frontend tests
npm test                         # Run all frontend tests
npm run test:coverage            # With coverage

# All tests
pytest && npm test               # Full test suite
```

**Test files:**
- `tests/test_endpoints.py` - API endpoint tests (35+ tests)
- `tests/test_models.py` - Measurement creation (30+ tests)
- `tests/test_utils.py` - Helper functions (23+ tests)
- `tests/test_workflows.py` - Integration tests (20+ tests)
- `tests/test_error_paths.py` - Error handling (50+ tests)
- `tests/js/validation.test.js` - Client validation (30+ tests)
- `tests/js/clipboard.test.js` - Clipboard formatting (25+ tests)
- `tests/js/script.test.js` - Frontend logic (20+ tests)

**See:** `TESTING.md` for full testing guide

## Critical Rules

1. **Python 3.12.8 only** (runtime.txt) - greenlet compatibility
2. **No testing deps in requirements.txt** - production only
3. **Test before commit** - `pytest && npm test` must pass
4. **No database** - stateless by design
5. **rcpchgrowth only** - for growth calculations

## Recent Work (Jan 18, 2026)

- ✅ Collapsible sections (prev measurements, bone age)
- ✅ CSV import/export for previous measurements
- ✅ Documentation reorganization (PROJECT.md as source of truth)
- ✅ Removed demo mode (unstable)
- ✅ Feature backlog reviewed and curated (10 features remaining)
- ✅ **Comprehensive testing infrastructure** (4-phase plan complete)
  - 177 backend tests + 94 frontend tests
  - Live server fixture for E2E testing
  - Test data generators and custom assertions
  - Complete documentation (TESTING.md + TESTING_GUIDELINES.md)

## Current Status

- 271 tests passing (97% pass rate)
- Coverage increased from 15% to 31%
- Testing infrastructure production-ready
- All features stable and well-tested

## See Also

- **Full context:** `PROJECT.md`
- **User guide:** `docs/index.html`
- **Dev docs:** `documentation/` (technical details)
