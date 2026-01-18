# Growth Parameters Calculator - Project Reference

> **Central project documentation** - Updated 2026-01-18
> This is the single source of truth for project context, design decisions, and development status.

## Project Overview

**Purpose:** Pediatric growth calculator using RCPCH's validated rcpchgrowth library
**Stack:** Flask 3.0.0 + Vanilla JS + Chart.js + Material Design Icons
**Deploy:** https://growth-parameters-calculator.onrender.com
**Docs:** https://gm5dna.github.io/growth-parameters-calculator/
**Python:** 3.12.8 (greenlet compatibility requirement)

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask 3.0.0, Python 3.12.8 | API server, orchestration |
| **Growth Library** | rcpchgrowth | RCPCH-validated calculations |
| **Frontend** | Vanilla JavaScript | SPA, no framework overhead |
| **Charts** | Chart.js | Interactive centile curves |
| **PDF** | ReportLab | Server-side PDF generation |
| **Icons** | Material Symbols | Modern, accessible icons |
| **Deploy** | Render.com | Auto-deploy from git push |
| **Testing** | pytest + Jest | Backend (177) + Frontend (94) tests |

## File Structure

```
app.py                # Flask routes & orchestration (900 lines)
constants.py          # Config, thresholds, error codes
validation.py         # Input validation + ValidationError
calculations.py       # Age, BSA, velocity, GH dose
models.py             # rcpchgrowth Measurement factory
utils.py              # MPH, centile helpers
pdf_utils.py          # PDF report generation
requirements.txt      # Production deps (Render)
requirements-dev.txt  # Dev/test deps (local only)
runtime.txt           # Python 3.12.8 for Render
package.json          # Jest configuration for frontend tests
static/script.js      # Frontend logic (970 lines)
static/style.css      # Responsive CSS + dark mode
static/validation.js  # Client-side validation (207 lines)
static/clipboard.js   # Clipboard formatting (370 lines)
templates/index.html  # SPA shell
tests/                # pytest + Jest comprehensive test suite
├── conftest.py       # pytest fixtures (live_server, etc)
├── test_*.py         # Backend tests (177 tests)
├── js/               # Frontend Jest tests (94 tests)
└── helpers/          # Test data generators & assertions
docs/                 # GitHub Pages user guide
documentation/        # Technical documentation
├── TESTING.md        # Testing guide
└── TESTING_GUIDELINES.md  # Test conventions
```

## Design Principles

1. **Stateless** - No database, no PHI retention
2. **Mobile-first** - Responsive, touch-friendly, PWA
3. **Clinical accuracy** - RCPCH library exclusively
4. **Fail-fast** - Early validation, clear errors
5. **Modular** - Single-responsibility modules

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Python 3.12.8** | greenlet (Playwright dep) doesn't support 3.14 yet |
| **No database** | Privacy by design, simplicity |
| **Split requirements** | Keep testing deps out of production build |
| **rcpchgrowth library** | RCPCH-validated, authoritative |
| **Vanilla JS** | No framework overhead, faster load |
| **Server-side PDF** | Quality control, chart rendering |
| **Material Symbols** | Modern icons, variable font |

## API Endpoints

- `GET /` - SPA
- `POST /calculate` - Main growth calculations
- `POST /chart-data` - Centile curve data for charts
- `POST /export-pdf` - PDF report generation

## Validation Rules

- **Birth date:** Valid, not future, age 0-25 years
- **Measurement date:** Valid, after birth date
- **Weight:** 0.1-300 kg
- **Height:** 10-250 cm
- **OFC:** 10-100 cm
- **Gestation:** 22-44 weeks, 0-6 days
- **SDS limits:** Warning ±4, hard limit ±8 (BMI: ±15)

## Completed Features

### Core Features
- ✅ Age calculation (decimal + calendar years/months/days)
- ✅ Weight, height, BMI, OFC with SDS/centiles
- ✅ Multiple growth references (UK-WHO, CDC, Turner, Trisomy-21)
- ✅ Interactive growth charts (Chart.js)
- ✅ Gestational age correction for preterm
- ✅ Mid-parental height calculation
- ✅ Height velocity (minimum 4-month interval)
- ✅ BSA calculation (Boyd formula + cBNF lookup)
- ✅ GH dose calculator

### UX Features
- ✅ Dark mode (system detection + manual toggle)
- ✅ Mobile responsive design
- ✅ PWA offline support
- ✅ Auto-save form state (localStorage)
- ✅ PDF export with charts
- ✅ Chart download (PNG export)
- ✅ Copy results to clipboard (clinical formatting)

### Advanced Features (Jan 2026)
- ✅ Percentage median BMI (malnutrition assessment)
- ✅ Intelligent age range selection (optimizes chart display)
- ✅ Multiple previous measurements with CSV import/export
- ✅ Growth trajectory tracking (previous measurements plotted on charts)
- ✅ Bone age assessment (Greulich-Pyle, TW3)
- ✅ Collapsible sections (progressive disclosure)

## Current Sprint (Jan 18, 2026)

**Status:** Testing infrastructure complete ✅
- ✅ Fixed collapsible sections CSS conflicts
- ✅ Improved CSV button layout
- ✅ Reorganized documentation structure
- ✅ Removed demo mode feature (unstable)
- ✅ **Comprehensive testing infrastructure implemented** (4-phase plan complete)
  - 177 backend tests (pytest) covering endpoints, models, utils, workflows, error paths
  - 94 frontend tests (Jest) covering validation, clipboard, script functions
  - Live server fixture for E2E testing
  - Test data generators and custom assertions
  - Complete documentation (TESTING.md + TESTING_GUIDELINES.md)
  - 97% test pass rate, coverage increased from 15% to 31%

## Feature Backlog

### High Priority (Quick Wins)
- [ ] **Keyboard Shortcuts** - Ctrl+Enter to calculate, Ctrl+R to reset

### Medium Priority (Clinical Features)
- [ ] **Centile Band Interpretation** - "Between 25th-50th centile" text
- [ ] **Weight Target Calculator** - Calculate weight for target BMI centile
- [ ] **Parental OFC Plotting** - For familial macrocephaly assessment
- [ ] **Event Annotations** - Tag measurements with clinical notes

### Low Priority (Future Enhancements)
- [ ] **Predicted Adult Height** - Bayley-Pinneau, Khamis-Roche methods
- [ ] **Privacy Mode** - No localStorage/ephemeral session
- [ ] **Puberty Staging** - Tanner stage selector
- [ ] **Multi-language Support** - i18n
- [ ] **Syndrome-Specific Charts** - Noonan, Achondroplasia, etc.
- [ ] **FHIR/HL7 Integration** - EHR interoperability (see documentation/FHIR_INTEGRATION.md)

## Testing

**Coverage:** 271 tests (177 backend + 94 frontend), 97% pass rate, 31% overall coverage (85%+ on tested files)

```bash
# Backend tests
pytest                    # All backend tests
pytest -v                 # Verbose output
pytest --cov=.            # With coverage report
pytest -k "test_name"     # Run specific test

# Frontend tests
npm test                  # All frontend tests
npm run test:watch        # Watch mode
npm run test:coverage     # With coverage report

# Full test suite
pytest && npm test        # Run all tests
```

**Test Infrastructure:**
- **Backend:** pytest with comprehensive fixtures (live_server, test_data generators)
- **Frontend:** Jest with jsdom for JavaScript unit testing
- **Integration:** Complete workflow tests (calculate → PDF)
- **Error Paths:** Boundary conditions, malformed input, edge cases
- **Accessibility:** WCAG 2.1 AA compliance testing

**Key test areas:**
- **Endpoints:** `/calculate`, `/chart-data`, `/export-pdf` (35+ tests)
- **Models:** Measurement creation, SDS validation (30+ tests)
- **Utils:** Chart data, MPH calculations (23+ tests)
- **Validation:** Client-side form validation (30+ tests)
- **Clipboard:** Text formatting for clinical notes (25+ tests)
- **Workflows:** End-to-end user scenarios (20+ tests)
- **Error handling:** Boundary values, malformed requests (50+ tests)

## Deployment

**Platform:** Render.com
**Method:** Auto-deploy on push to `main`
**URL:** https://growth-parameters-calculator.onrender.com
**Monitoring:** Can use `render` CLI for logs

**Deployment checklist:**
1. Run tests locally: `pytest`
2. Commit with descriptive message
3. Push to main: `git push origin main`
4. Render auto-deploys (monitor via Render dashboard)

## Development Workflow

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
npm install                      # Install Jest and frontend test deps

# Development
python app.py                    # Dev server on :8080

# Testing
pytest -v                        # Run backend tests
npm test                         # Run frontend tests
pytest --cov=. --cov-report=html # Backend coverage report
npm run test:coverage            # Frontend coverage report

# Deployment (tests must pass first!)
pytest && npm test               # Run all tests
git add .
git commit -m "Descriptive message"
git push origin main             # Triggers auto-deploy
```

## Important Constants

```python
# Age limits
MIN_AGE_YEARS = 0.0
MAX_AGE_YEARS = 25.0

# SDS thresholds
SDS_WARNING_THRESHOLD = 4.0
SDS_HARD_LIMIT = 8.0
BMI_SDS_HARD_LIMIT = 15.0

# Preterm correction
PRETERM_THRESHOLD_WEEKS = 37
MODERATE_PRETERM_CORRECTION_UNTIL_YEARS = 1.0
EXTREME_PRETERM_THRESHOLD_WEEKS = 32
EXTREME_PRETERM_CORRECTION_UNTIL_YEARS = 2.0

# GH dosing
STANDARD_GH_DOSE_MG_M2_WEEK = 7.0

# Height velocity
HEIGHT_VELOCITY_MIN_INTERVAL_MONTHS = 4
```

## External Resources

- [rcpchgrowth docs](https://growth.rcpch.ac.uk/developer/rcpchgrowth/)
- [RCPCH Growth Charts](https://www.rcpch.ac.uk/resources/uk-who-growth-charts)
- [Flask docs](https://flask.palletsprojects.com/)
- [Chart.js docs](https://www.chartjs.org/docs/)

## License & Attribution

**Created by:** Stuart ([@gm5dna](https://github.com/gm5dna))
**Powered by:** [rcpchgrowth](https://growth.rcpch.ac.uk/) from RCPCH
**License:** See repository

---

**⚠️ Disclaimer:** Educational and research tool only. NOT for clinical decision-making.
All calculations must be verified independently before any clinical use.
