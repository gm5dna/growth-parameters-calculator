# CLAUDE.md - Growth Parameters Calculator

## Quick Reference

**What:** Pediatric growth calculator using RCPCH's rcpchgrowth library
**Stack:** Flask 3.0.0 + Vanilla JS SPA + Chart.js + Material Design Icons
**Deploy:** https://growth-parameters-calculator.onrender.com
**Python:** 3.12.8 (specified in runtime.txt for Render)
**Dev Docs:** See `documentation/` folder - technical guides
**User Docs:** See `docs/` folder - GitHub Pages site at https://gm5dna.github.io/growth-parameters-calculator/

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt              # Production dependencies
pip install -r requirements-dev.txt          # Testing dependencies (dev only)

# Run
python app.py                         # Dev server :8080
gunicorn --bind 0.0.0.0:8080 app:app  # Production

# Test
pytest                                # All tests
pytest -v                             # Verbose
pytest --cov=. --cov-report=html      # With coverage
```

## Project Structure

```
app.py                # Flask routes, orchestration
constants.py          # Config, thresholds, error codes
validation.py         # Input validation (ValidationError)
calculations.py       # Age, BSA, velocity, GH dose
models.py             # rcpchgrowth Measurement factory
utils.py              # MPH, centile data, responses
pdf_utils.py          # PDF generation (ReportLab)
requirements.txt      # Production dependencies (Render uses this)
requirements-dev.txt  # Development/testing dependencies
runtime.txt           # Python version for Render (3.12.8)

static/
  script.js           # Frontend logic, Chart.js, dark mode
  validation.js       # Client validation
  style.css           # Responsive styles, theme system
  clipboard.js        # Copy to clipboard functionality
templates/
  index.html          # SPA shell with Material Icons
tests/                # pytest test suite
docs/                 # User documentation (GitHub Pages)
documentation/        # Developer documentation & guides
```

## Key Patterns

- **Validation:** Client-side (feedback) + server-side (authoritative)
- **Errors:** `ValidationError` with codes (ERR_001-010)
- **Responses:** `format_success_response()` / `format_error_response()`
- **Measurements:** `create_measurement()` factory in models.py
- **Growth data:** All SDS/centile via `rcpchgrowth.Measurement`

## API Endpoints

- `GET /` - Serves SPA
- `POST /calculate` - Main calculation (JSON in/out)
- `POST /chart-data` - Centile curve data
- `POST /export-pdf` - PDF report generation

## Important Constants

- SDS limits: warning ±4, hard ±8 (BMI: ±15)
- Preterm threshold: 37 weeks
- Correction ages: 1yr (moderate preterm), 2yr (extreme <32wk)
- GH dose standard: 7 mg/m²/week

## Deployment (Render)

**Auto-deploy:** Pushes to `main` trigger automatic Render deployment

**Key Files:**
- `runtime.txt` - Pins Python to 3.12.8 (required: greenlet doesn't support 3.14)
- `requirements.txt` - Production dependencies only (no testing tools)
- `requirements-dev.txt` - Testing dependencies (playwright, pytest) - NOT deployed

**Why Python 3.12?**
Playwright requires greenlet, which doesn't yet support Python 3.14's internal API changes.
By separating testing dependencies and pinning Python to 3.12.8, we avoid build failures.

**Troubleshooting:**
- If greenlet errors appear: Check runtime.txt exists and specifies Python 3.12.x
- If deployment fails: Ensure testing deps (playwright/pytest) are NOT in requirements.txt
- Check Render logs for specific build/runtime errors

## Development Workflow

**After completing tasks:** Test with `pytest`, then commit and push changes.

```bash
pytest                                # Test first
git add .                             # Stage changes
git commit -m "Descriptive message"   # Commit
git push origin main                  # Push (triggers Render deployment)
```

**Commit when:** Feature complete, refactoring done, docs updated
**Don't commit:** Broken code, debug statements, commented code

**Note:** Only production code needs testing before commit. Testing dependencies
are in requirements-dev.txt and won't affect Render deployments.

## Completed Features

- ✅ Dark mode with system detection (Material Design icons)
- ✅ PDF export with charts
- ✅ Copy results to clipboard (clinical formatting)
- ✅ Mobile responsive design
- ✅ Growth chart visualization (Chart.js)
- ✅ PWA offline support
- ✅ Render deployment optimized (Python 3.12.8, split dependencies)
- ✅ Percentage median BMI (advanced mode - malnutrition assessment)
- ✅ Intelligent age range selection (auto-selects optimal chart range based on age and measurements)
- ✅ User documentation site (GitHub Pages)

## Next Priority Features

See `documentation/feature-plans/` for detailed roadmaps. Top candidates:
- Keyboard shortcuts (Ctrl+Enter to calculate)
- Recent calculations history
- Chart download (PNG/SVG)
- Trajectory tracking (multiple measurements)
