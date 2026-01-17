# CLAUDE.md - Growth Parameters Calculator

## Quick Reference

**What:** Pediatric growth parameter calculator using RCPCH's rcpchgrowth library
**Stack:** Flask 3.0.0 + Vanilla JS SPA + Chart.js
**Deploy:** Render.com (https://growth-parameters-calculator.onrender.com)

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Run
python app.py                    # Dev server on :8080
gunicorn --bind 0.0.0.0:8080 app:app  # Production

# Test
pytest                           # All tests
pytest -v                        # Verbose
pytest --cov=. --cov-report=html # With coverage
```

## Project Structure

```
app.py          # Flask routes, main orchestration
constants.py    # Config values, thresholds, error codes
validation.py   # Input validation (ValidationError class)
calculations.py # Age, BSA, height velocity, GH dose
models.py       # rcpchgrowth Measurement factory
utils.py        # MPH, centile data, response formatting
pdf_utils.py    # PDF report generation (ReportLab)

static/
  script.js     # Frontend logic, Chart.js integration, dark mode
  validation.js # Client-side validation
  style.css     # Mobile-first responsive styles, theme system
templates/
  index.html    # SPA shell
tests/
  test_calculations.py, test_validation.py, test_pdf_export.py
  test_copy_feature.py, test_responsive.py
docs/
  README.md, FEATURES.md, USER_GUIDE.md, TECHNICAL.md
  feature-plans/, test-reports/
```

## Key Patterns

- **Validation:** Client-side (immediate feedback) + server-side (authoritative)
- **Error handling:** `ValidationError` exception with error codes (ERR_001-010)
- **Responses:** `format_success_response()` / `format_error_response()` in utils.py
- **Measurements:** Created via `create_measurement()` factory in models.py
- **Growth data:** All SDS/centile calculations via `rcpchgrowth.Measurement`

## Development Workflow

### Git Commit Best Practices

**IMPORTANT:** After completing and testing any todo/goal/task, you MUST:

1. **Test thoroughly** - Run relevant tests (`pytest`) to ensure nothing is broken
2. **Commit changes** - Create a meaningful commit with descriptive message
3. **Push to remote** - Push commits to keep remote repository in sync

```bash
# Example workflow after completing a feature
pytest                                    # Test first
git add .                                 # Stage all changes
git commit -m "Add dark mode feature"     # Commit with clear message
git push origin main                      # Push to remote
```

**Commit Message Guidelines:**
- Use imperative mood ("Add feature" not "Added feature")
- Be specific and descriptive
- Reference issue numbers if applicable
- Keep first line under 50 characters
- Add detailed description if needed

**When to Commit:**
- ✅ After completing a feature/fix and tests pass
- ✅ After significant refactoring
- ✅ After updating documentation
- ✅ Before starting a new major task
- ❌ Don't commit broken/untested code
- ❌ Don't commit commented-out code or debug statements

## API Endpoints

- `GET /` - Serves SPA
- `POST /calculate` - Main calculation (JSON in/out)
- `POST /chart-data` - Centile curve data for charts
- `POST /export-pdf` - Generate PDF report from calculation results

## Important Constants (constants.py)

- SDS limits: warning ±4, hard ±8 (BMI: ±15)
- Preterm threshold: 37 weeks
- Correction ages: 1yr (moderate preterm), 2yr (extreme preterm <32wk)
- GH dose standard: 7 mg/m²/week

## Testing Notes

- Tests in `tests/` directory
- Use pytest fixtures for common test data
- Coverage reports in `htmlcov/`

## Documentation

Full docs in `docs/` folder - see `docs/README.md` for index.

## Future Improvements Backlog

### 🎨 User Experience - Quick Wins
1. ~~Dark mode theme with system preference detection~~ ✅ **COMPLETED**
2. Keyboard shortcuts (Ctrl+Enter to calculate, Ctrl+R to reset)
3. Undo/redo functionality for form changes
4. **Recent calculations history** (last 5-10 in sidebar)
5. ~~Copy results to clipboard button~~ ✅ **COMPLETED**
6. Patient session management (save/switch between patients)
7. Guided tour/onboarding for new users
8. Comparison view (current vs previous visit)
9. Customizable units (imperial/metric toggle)

### 📊 Data & Analytics
10. ~~Export to PDF/CSV/print-friendly view~~ ✅ **COMPLETED** (PDF export)
11. Screenshot/image export for charts
12. Growth trajectory tracking (multiple measurements over time)
13. Data import from CSV/EMR systems
14. Statistics dashboard with usage analytics

### 📈 Chart Enhancements
15. Chart annotations (add notes to points)
16. Chart download options (PNG, SVG, PDF)
17. Growth velocity charts with centiles
18. Multi-patient comparison charts
19. Custom chart ranges with zoom/pan
20. 3D growth charts (height vs weight vs age)

### 🔬 Clinical Features
21. Bone age integration (Greulich-Pyle/TW3)
22. Puberty staging (Tanner) selector
23. Predicted adult height (Bayley-Pinneau, Khamis-Roche)
24. BMI categories with WHO classifications
25. Red flag alerts (growth faltering detection)
26. Syndrome-specific charts (Noonan, Achondroplasia, Prader-Willi)
27. Nutritional calculations (caloric/protein requirements)
28. Lab integration (IGF-1, IGFBP-3, thyroid)

### 🌍 Accessibility & Localization
29. Screen reader optimization
30. High contrast mode (WCAG AAA)
31. Multi-language support (Spanish, French, Mandarin)
32. Voice input for measurements

### 💾 Data Management
33. Offline mode improvements with sync
34. Cloud sync with encryption
35. FHIR API integration
36. Database backend (PostgreSQL)

### 🧪 Testing & Quality
37. E2E testing (Cypress/Playwright)
38. Performance monitoring (RUM, Sentry)
39. A/B testing framework
40. Automated accessibility testing

### 🔒 Security & Privacy
41. Privacy mode (no localStorage/ephemeral)
42. Data encryption for localStorage
43. Audit logging
44. Enhanced rate limiting

### 🎓 Education & Documentation
45. Contextual help with tooltips
46. Video tutorials
47. FAQ section
48. Interactive examples with sample patients
49. Clinical guidelines integration

### 🚀 Performance & Technical
50. Code splitting and lazy loading
51. Image optimization (WebP)
52. Service worker improvements
53. GraphQL API
54. WebSocket real-time updates
55. Micro-frontend architecture

**Top Priority Items:**
- #10: Export to PDF (high clinical value)
- #1: Dark mode (UX improvement)
- #12: Growth trajectory tracking (core clinical value)
- #5: Copy results to clipboard
- #4: Recent calculations history
- #16: Chart download options
- #24: BMI categories
- #2: Keyboard shortcuts
- #41: Privacy mode
- #37: E2E testing
