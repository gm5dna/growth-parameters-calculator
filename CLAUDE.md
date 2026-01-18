# CLAUDE.md - Quick Reference

> **For detailed context:** See `PROJECT.md`
> This file contains only essentials for AI assistance.

## Quick Start

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt              # Production
pip install -r requirements-dev.txt          # Dev/test only

# Run
python app.py                                # Dev :8080

# Test & Deploy
pytest                                       # Test first
git add . && git commit -m "msg" && git push # Auto-deploys
```

## Stack

**Backend:** Flask 3.0.0 + Python 3.12.8 (greenlet requirement)
**Frontend:** Vanilla JS + Chart.js + Material Symbols
**Growth:** rcpchgrowth (RCPCH library)
**Deploy:** https://growth-parameters-calculator.onrender.com
**Docs:** https://gm5dna.github.io/growth-parameters-calculator/

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Routes & orchestration | 900 |
| `static/script.js` | Frontend logic | 970 |
| `constants.py` | Config & thresholds | - |
| `validation.py` | Input validation | - |
| `calculations.py` | Business logic | - |
| `models.py` | rcpchgrowth wrapper | - |
| `utils.py` | Helpers (MPH, etc) | - |
| `pdf_utils.py` | PDF generation | - |

## API

- `GET /` → SPA
- `POST /calculate` → Growth calculations
- `POST /chart-data` → Centile curves
- `POST /export-pdf` → PDF report
- `GET /generate-demo-data` → Demo data

## Key Patterns

- **Validation:** Client (feedback) + Server (authoritative)
- **Errors:** `ValidationError` with codes (ERR_001-010)
- **Responses:** `format_success_response()` / `format_error_response()`
- **Measurements:** `create_measurement()` factory
- **Growth data:** All via `rcpchgrowth.Measurement`

## Critical Rules

1. **Python 3.12.8 only** (runtime.txt) - greenlet compatibility
2. **No testing deps in requirements.txt** - production only
3. **Test before commit** - `pytest` must pass
4. **No database** - stateless by design
5. **rcpchgrowth only** - for growth calculations

## Recent Work (Jan 18, 2026)

- ✅ Collapsible sections (prev measurements, bone age)
- ✅ Demo mode with realistic data generation
- ✅ CSV import/export for previous measurements
- 🐛 Fixed: CSS conflicts, demo mode parameter bug

## Current Status

- All 46 tests passing
- Demo mode bug fixed (awaiting deployment)
- Collapsible sections working correctly

## See Also

- **Full context:** `PROJECT.md`
- **User guide:** `docs/index.html`
- **Dev docs:** `documentation/` (technical details)
