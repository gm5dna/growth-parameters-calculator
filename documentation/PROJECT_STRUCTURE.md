# Project Structure

Clean, organized structure for the Growth Parameters Calculator.

```
growth-parameters-calculator/
│
├── README.md                      # Main project overview
├── SETUP.md                       # Quick setup guide
├── PROJECT_STRUCTURE.md           # This file
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Test configuration
├── run.sh                         # Startup script
│
├── app.py                         # Main Flask application
├── constants.py                   # Configuration constants
├── validation.py                  # Input validation
├── calculations.py                # Growth calculations
├── models.py                      # Data models
├── utils.py                       # Helper functions
│
├── docs/                          # 📚 Documentation
│   ├── README.md                  # Documentation index
│   ├── USER_GUIDE.md              # Step-by-step user guide
│   ├── FEATURES.md                # Feature documentation
│   ├── TECHNICAL.md               # Technical architecture
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── IMPROVEMENTS_SUMMARY.md    # Recent improvements
│   └── IMPROVEMENTS_COMPLETED.md  # Detailed improvement log
│
├── static/                        # 🎨 Frontend assets
│   ├── script.js                  # Main JavaScript
│   ├── validation.js              # Client-side validation
│   ├── style.css                  # Styles (mobile-first)
│   ├── favicon.svg                # App icon
│   ├── favicon-32x32.png          # Favicon
│   ├── apple-touch-icon.png       # iOS icon
│   ├── android-chrome-*.png       # Android icons
│   └── site.webmanifest           # PWA manifest
│
├── templates/                     # 📄 HTML templates
│   └── index.html                 # Main application page
│
├── tests/                         # 🧪 Unit tests
│   ├── __init__.py               # Test package init
│   ├── test_calculations.py      # Calculation tests
│   └── test_validation.py        # Validation tests
│
└── venv/                          # 🐍 Virtual environment (gitignored)
```

## File Descriptions

### Root Level

#### Configuration Files
- **README.md** - Main project documentation with quick start guide
- **SETUP.md** - Detailed setup and troubleshooting instructions
- **PROJECT_STRUCTURE.md** - This file, project organization reference
- **.gitignore** - Files and folders excluded from version control
- **requirements.txt** - Python package dependencies
- **pytest.ini** - pytest configuration for running tests
- **run.sh** - Convenience script to start the application

#### Backend Python Modules
- **app.py** (main) - Flask application with routes, rate limiting (optional)
- **constants.py** - Magic numbers, thresholds, error codes
- **validation.py** - Input validation with ValidationError exception
- **calculations.py** - Age, BSA, height velocity, GH dose calculations
- **models.py** - Measurement creation and SDS validation
- **utils.py** - Mid-parental height and chart data utilities

### Documentation (`docs/`)

Comprehensive documentation for users and developers:

- **README.md** - Documentation index and navigation
- **USER_GUIDE.md** (~700 lines) - Complete usage instructions
- **FEATURES.md** (~600 lines) - Detailed feature descriptions
- **TECHNICAL.md** (~800 lines) - Architecture and implementation
- **DEPLOYMENT.md** - Production deployment guide
- **IMPROVEMENTS_SUMMARY.md** - Recent code improvements summary
- **IMPROVEMENTS_COMPLETED.md** - Detailed improvement tracking

### Frontend Assets (`static/`)

#### JavaScript
- **script.js** (~1270 lines) - Main application logic, chart rendering
- **validation.js** (~240 lines) - Client-side validation, localStorage

#### Styles
- **style.css** - Mobile-first responsive design with CSS Grid

#### Icons & PWA
- **favicon.svg** - Vector app icon
- **favicon-32x32.png** - Browser favicon
- **apple-touch-icon.png** - iOS home screen icon
- **android-chrome-192x192.png** - Android icon (192×192)
- **android-chrome-512x512.png** - Android icon (512×512)
- **site.webmanifest** - PWA manifest (installable app)

### Templates (`templates/`)

- **index.html** (~405 lines) - Single-page application HTML

### Tests (`tests/`)

Unit tests with pytest:

- **__init__.py** - Test package initialization
- **test_calculations.py** (~280 lines) - Age, BSA, height velocity tests
- **test_validation.py** (~260 lines) - Input validation tests

## Code Organization

### Backend Architecture

```
Request → app.py (routes)
           ↓
       validation.py (validate inputs)
           ↓
       calculations.py (compute results)
           ↓
       models.py (create measurements, validate SDS)
           ↓
       utils.py (helper functions)
           ↓
       Response (JSON)
```

### Frontend Architecture

```
index.html (structure)
    ↓
validation.js (client validation, localStorage)
    ↓
script.js (form handling, results display)
    ↓
Chart.js (growth charts)
```

### Module Dependencies

```
app.py
├── Flask (web framework)
├── constants (configuration)
├── validation (input checking)
├── calculations (growth math)
├── models (measurements)
├── utils (helpers)
└── rcpchgrowth (RCPCH library)

script.js
├── validation.js (client validation)
└── Chart.js (charting library)
```

## Key Features by File

### app.py
- Route handlers (`/`, `/calculate`, `/chart-data`)
- Optional rate limiting (Flask-Limiter)
- Error handling
- JSON API responses

### constants.py
- Age calculation constants
- Gestation thresholds
- SDS limits
- Validation ranges
- Error codes

### validation.py
- ValidationError exception
- Date validation
- Measurement range checking
- Gestation validation
- Error code assignment

### calculations.py
- Age calculation (decimal and calendar)
- Gestation correction logic
- BSA calculation (Boyd and cBNF)
- Height velocity
- GH dose calculation

### models.py
- Measurement object creation
- SDS validation (hard and soft limits)
- Gestation-aware measurements

### utils.py
- Mid-parental height calculation
- Chart data fetching
- Target range computation

### script.js
- Form submission handling
- Results display
- Chart rendering (Chart.js)
- Basic/Advanced mode toggle
- Auto-save functionality

### validation.js
- Client-side validation rules
- localStorage save/restore
- Debounced auto-save
- Form state management

### style.css
- Mobile-first responsive design
- CSS Grid layouts
- Advanced mode visibility
- Chart styling

## Development Workflow

### Starting Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
./run.sh

# Open browser
open http://localhost:8080
```

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_calculations.py
```

### Code Style

- **Python**: PEP 8 compliant
- **JavaScript**: ES6+ with async/await
- **CSS**: Mobile-first, semantic naming
- **HTML**: Semantic elements, ARIA labels

## File Size Reference

### Backend
- app.py: ~22 KB (refactored from 29 KB)
- calculations.py: ~9 KB
- validation.py: ~6 KB
- models.py: ~4 KB
- utils.py: ~4 KB
- constants.py: ~1.4 KB

### Frontend
- script.js: ~60 KB (chart rendering)
- validation.js: ~7 KB
- style.css: ~20 KB
- index.html: ~18 KB

### Documentation
- TECHNICAL.md: ~42 KB
- USER_GUIDE.md: ~40 KB
- FEATURES.md: ~38 KB
- IMPROVEMENTS_SUMMARY.md: ~35 KB

### Tests
- test_calculations.py: ~12 KB
- test_validation.py: ~11 KB

## Ignored Files/Folders

These are excluded from version control (see `.gitignore`):

- `venv/` - Virtual environment
- `__pycache__/` - Python bytecode
- `.DS_Store` - macOS metadata
- `.claude/` - Claude Code artifacts
- `.pytest_cache/` - Test cache
- `htmlcov/` - Coverage reports
- `*.backup` - Backup files
- `*.log` - Log files

## Clean State

The project is now in a clean, organized state:

✅ No backup files (app.py.backup removed)
✅ No cache directories (__pycache__ removed)
✅ No OS metadata (.DS_Store removed)
✅ Comprehensive .gitignore
✅ Documentation organized in docs/
✅ Clear separation of concerns
✅ Ready for development or deployment

## Next Steps

1. **Development**: Run `./run.sh` to start the app
2. **Testing**: Run `pytest` to verify all tests pass
3. **Documentation**: Read `docs/README.md` for detailed guides
4. **Deployment**: Follow `docs/DEPLOYMENT.md` for production setup

---

**Last Updated**: January 2026
**Version**: Post-improvements (modular architecture)
