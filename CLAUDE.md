# CLAUDE.md - Growth Parameters Calculator

## Quick Reference

**What:** Pediatric growth calculator using RCPCH's rcpchgrowth library
**Stack:** Flask 3.0.0 + Vanilla JS SPA + Chart.js
**Deploy:** https://growth-parameters-calculator.onrender.com
**Docs:** See `docs/` folder - comprehensive guides in `docs/README.md`

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

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
app.py          # Flask routes, orchestration
constants.py    # Config, thresholds, error codes
validation.py   # Input validation (ValidationError)
calculations.py # Age, BSA, velocity, GH dose
models.py       # rcpchgrowth Measurement factory
utils.py        # MPH, centile data, responses
pdf_utils.py    # PDF generation (ReportLab)

static/
  script.js     # Frontend logic, Chart.js, dark mode
  validation.js # Client validation
  style.css     # Responsive styles, theme system
templates/
  index.html    # SPA shell
tests/          # pytest test suite
docs/           # Full documentation
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

## Development Workflow

**After completing tasks:** Test with `pytest`, then commit and push changes.

```bash
pytest                                # Test first
git add .                             # Stage changes
git commit -m "Descriptive message"   # Commit
git push origin main                  # Push
```

**Commit when:** Feature complete, refactoring done, docs updated
**Don't commit:** Broken code, debug statements, commented code

## Completed Features

- ✅ Dark mode with system detection
- ✅ PDF export with charts
- ✅ Copy results to clipboard
- ✅ Mobile responsive design
- ✅ Growth chart visualization
- ✅ PWA offline support

## Next Priority Features

See `docs/feature-plans/` for detailed roadmaps. Top candidates:
- Keyboard shortcuts (Ctrl+Enter to calculate)
- Recent calculations history
- Chart download (PNG/SVG)
- Trajectory tracking (multiple measurements)
