# Technical Documentation

Architecture, implementation details, and technical specifications for the Growth Parameters Calculator.

## Table of Contents

- [System Architecture](#system-architecture)
- [Backend Implementation](#backend-implementation)
- [Frontend Implementation](#frontend-implementation)
- [Data Flow](#data-flow)
- [Security](#security)
- [Performance](#performance)
- [Deployment](#deployment)

## System Architecture

### Overview

The Growth Parameters Calculator uses a modern, modular architecture:

```
┌─────────────────┐
│   Browser/PWA   │
│  (JavaScript)   │
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────┐
│  Flask Server   │
│  (Python 3.8+)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  rcpchgrowth    │
│    Library      │
└─────────────────┘
```

### Component Architecture

```
growth-parameters-calculator/
├── app.py                      # Flask application & routing
├── constants.py                # Configuration & constants
├── validation.py               # Input validation layer
├── calculations.py             # Growth calculation logic
├── models.py                   # Data models & SDS validation
├── utils.py                    # Utility functions
├── requirements.txt            # Python dependencies
├── static/
│   ├── script.js              # Main application logic
│   ├── validation.js          # Client-side validation
│   ├── style.css              # Styles (mobile-first)
│   ├── favicon.svg            # App icon
│   └── site.webmanifest       # PWA manifest
├── templates/
│   └── index.html             # Single-page application
├── tests/
│   ├── test_calculations.py   # Calculation unit tests
│   ├── test_validation.py     # Validation unit tests
│   └── pytest.ini             # Test configuration
└── docs/                       # Documentation
```

### Design Principles

1. **Modular Architecture**: Separation of concerns across focused modules
2. **Single Responsibility**: Each module has one clear purpose
3. **DRY (Don't Repeat Yourself)**: Shared logic extracted to utilities
4. **Fail Fast**: Validation at entry points prevents propagation of bad data
5. **Mobile-First**: Progressive enhancement from mobile to desktop
6. **Offline-Capable**: PWA features enable offline functionality

## Backend Implementation

### Flask Application (app.py)

Main application file with route handlers.

#### Routes

```python
@app.route('/')
def index():
    """Serves the main application page"""

@app.route('/calculate', methods=['POST'])
@limiter.limit("30 per minute")
def calculate():
    """Main calculation endpoint with rate limiting"""

@app.route('/chart-data', methods=['POST'])
def chart_data():
    """Fetches centile chart data for specified parameters"""
```

#### Rate Limiting

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

- **Global**: 200 requests/day, 50 requests/hour
- **Calculate endpoint**: 30 requests/minute
- **Storage**: In-memory (upgrade to Redis for production)

### Constants Module (constants.py)

Centralized configuration and magic numbers.

```python
# Age calculation
DAYS_PER_YEAR = 365.25
MONTHS_PER_YEAR = 12.0
DAYS_PER_WEEK = 7.0

# Gestation thresholds
PRETERM_THRESHOLD_WEEKS = 37
MODERATE_PRETERM_THRESHOLD_WEEKS = 32
CORRECTION_AGE_THRESHOLD_MODERATE = 1.0
CORRECTION_AGE_THRESHOLD_EXTREME = 2.0

# SDS validation
SDS_HARD_LIMIT = 8.0
SDS_WARNING_LIMIT = 4.0
BMI_SDS_HARD_LIMIT = 15.0

# Validation ranges
MIN_WEIGHT_KG = 0.1
MAX_WEIGHT_KG = 300.0
MIN_HEIGHT_CM = 10.0
MAX_HEIGHT_CM = 250.0
MIN_OFC_CM = 10.0
MAX_OFC_CM = 100.0

# Error codes
class ErrorCodes:
    INVALID_DATE_FORMAT = "ERR_001"
    INVALID_DATE_RANGE = "ERR_002"
    MISSING_MEASUREMENT = "ERR_003"
    INVALID_WEIGHT = "ERR_004"
    INVALID_HEIGHT = "ERR_005"
    INVALID_OFC = "ERR_006"
    INVALID_GESTATION = "ERR_007"
    SDS_OUT_OF_RANGE = "ERR_008"
```

### Validation Module (validation.py)

Input validation with standardized error handling.

```python
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, code):
        self.message = message
        self.code = code

def validate_date(date_string, field_name):
    """Validate date format and range"""
    # Check format
    # Prevent future dates
    # Return parsed date object

def validate_date_range(birth_date, measurement_date):
    """Ensure measurement after birth"""

def validate_weight(weight):
    """Validate weight within acceptable range"""

def validate_height(height):
    """Validate height within acceptable range"""

def validate_ofc(ofc):
    """Validate OFC within acceptable range"""

def validate_gestation(weeks, days):
    """Validate gestation weeks and days"""
```

### Calculations Module (calculations.py)

Core growth calculation functions.

```python
def calculate_age_in_years(birth_date, measurement_date):
    """
    Calculate decimal years and calendar age
    Returns: (decimal_years, calendar_age_dict)
    """
    delta = relativedelta(measurement_date, birth_date)
    decimal_years = years + (months / MONTHS_PER_YEAR) + (days / DAYS_PER_YEAR)
    return decimal_years, calendar_age

def should_apply_gestation_correction(gestation_weeks, gestation_days, chronological_age_years):
    """
    Determine if gestational correction should be applied
    Rules:
    - <37 weeks gestation required
    - 32-36 weeks: correct until 1 year
    - <32 weeks: correct until 2 years
    """

def calculate_corrected_age(birth_date, measurement_date, gestation_weeks, gestation_days):
    """
    Calculate age corrected for prematurity
    Method: Adjust birth date to expected due date (40 weeks)
    """

def calculate_boyd_bsa(weight_kg, height_cm):
    """
    Boyd formula for BSA
    BSA = 0.0003207 × (height^0.3) × (weight_g^(0.7285 - (0.0188 × log10(weight_g))))
    """

def calculate_cbnf_bsa(weight_kg):
    """
    cBNF lookup table with interpolation
    Fallback when height not available
    """

def calculate_height_velocity(current_height, previous_height, current_date, previous_date):
    """
    Annualized growth rate
    Requires minimum 4-month interval
    Returns: {'value': cm/year, 'message': optional_warning}
    """

def calculate_gh_dose(bsa, weight_kg):
    """
    GH dose calculation for 7 mg/m²/week
    Returns: {'mg_per_day', 'mg_m2_week', 'mcg_kg_day'}
    """
```

### Models Module (models.py)

Measurement creation and SDS validation.

```python
def create_measurement(sex, birth_date, observation_date, measurement_method,
                      observation_value, reference, gestation_weeks=None, gestation_days=None):
    """
    Create rcpchgrowth Measurement object
    Handles both term and preterm babies
    """

def validate_measurement_sds(measurement_data, measurement_type):
    """
    Validate SDS within acceptable limits
    - Hard limit: ±8 SDS (±15 for BMI)
    - Soft limit: ±4 SDS (warning)
    Returns: (is_valid, warnings_list)
    """
```

### Utils Module (utils.py)

Helper functions for common operations.

```python
def calculate_mid_parental_height(maternal_height, paternal_height, sex):
    """
    Calculate MPH with target range
    Returns: {'mph': cm, 'centile': %, 'lower': cm, 'upper': cm}
    """

def get_chart_data(reference, measurement_method, sex, min_age=0, max_age=20):
    """
    Fetch centile curve data from rcpchgrowth
    Returns: Array of centile curves with data points
    """
```

### Dependencies

```
Flask==3.0.0                    # Web framework
rcpchgrowth==4.3.8             # Growth calculations
python-dateutil==2.8.2         # Date manipulation
gunicorn==21.2.0               # WSGI server
Flask-Limiter==3.5.0           # Rate limiting
pytest==7.4.3                  # Testing framework
scipy==1.11.4                  # Scientific computing (rcpchgrowth dependency)
```

## Frontend Implementation

### Architecture

Single-page application (SPA) with vanilla JavaScript.

```
┌──────────────────────┐
│    index.html        │
│  (Structure & UI)    │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌─────────┐
│ script │   │validation│
│  .js   │   │  .js    │
└────────┘   └─────────┘
    │
    ▼
┌──────────────────┐
│   Chart.js       │
│  (Visualization) │
└──────────────────┘
```

### Main JavaScript (script.js)

#### State Management

```javascript
let isAdvancedMode = false;
let calculationResults = null;
let currentChartInstance = null;
let isLoadingChart = false;
let currentPatientData = {
    sex: null,
    reference: null,
    age: null,
    measurements: {...},
    previousMeasurements: {...}
};
```

#### Event Handlers

```javascript
// Mode toggle
document.getElementById('modeToggle').addEventListener('change', ...)

// Form submission
document.getElementById('growthForm').addEventListener('submit', async (e) => {
    // Validate inputs
    // Show loading state
    // POST to /calculate
    // Display results
    // Clear saved state
})

// Chart interactions
document.getElementById('showChartsBtn').addEventListener('click', ...)
document.querySelectorAll('.chart-tab').forEach(tab => {
    tab.addEventListener('click', ...)
})
```

#### Form Submission Flow

```javascript
async function handleSubmit(e) {
    e.preventDefault();

    // 1. Collect form data
    const formData = collectFormData();

    // 2. Client-side validation
    const errors = validateFormInputs(formData);
    if (errors.length > 0) {
        showError(errors.join('; '));
        return;
    }

    // 3. Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    // 4. POST to server
    const response = await fetch('/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    });

    // 5. Handle response
    const data = await response.json();
    if (data.success) {
        displayResults(data.results);
        clearSavedFormState();
    } else {
        showError(data.error);
    }

    // 6. Reset loading state
    submitBtn.disabled = false;
    submitBtn.textContent = 'Calculate';
}
```

### Validation JavaScript (validation.js)

Client-side validation matching backend rules.

```javascript
// Validation constants
const VALIDATION = {
    WEIGHT: { min: 0.1, max: 300 },
    HEIGHT: { min: 10, max: 250 },
    OFC: { min: 10, max: 100 },
    GESTATION: { weeks: {min: 22, max: 44}, days: {min: 0, max: 6} }
};

function validateFormInputs(formData) {
    const errors = [];

    // Date validation
    // Measurement range validation
    // Logic validation

    return errors;
}

// localStorage persistence
function saveFormState() {
    const formData = {...};
    localStorage.setItem('growthCalcForm', JSON.stringify(formData));
}

function restoreFormState() {
    const saved = localStorage.getItem('growthCalcForm');
    if (saved) {
        const formData = JSON.parse(saved);
        // Populate form fields
    }
}

// Debounced auto-save
const debouncedSave = debounce(saveFormState, 1000);
```

### Chart Rendering

Uses Chart.js for interactive visualizations.

```javascript
function renderGrowthChart(canvas, centiles, patientData, measurementMethod) {
    const datasets = [];

    // 1. Add centile curves
    centiles.forEach(centile => {
        datasets.push({
            label: `${centile.centile}th centile`,
            data: centile.data,
            borderColor: centileColor,
            borderWidth: isMedian ? 2 : 1.5,
            borderDash: isDotted ? [5, 5] : [],
            ...
        });
    });

    // 2. Add patient measurements
    datasets.push({
        label: 'Current Measurement',
        data: currentPoints,
        backgroundColor: centileColor,
        pointRadius: 5,
        ...
    });

    // 3. Add corrected age if applicable
    if (correctedPoints.length > 0) {
        datasets.push({
            label: 'Corrected Age',
            data: correctedPoints,
            pointStyle: 'cross',
            ...
        });
    }

    // 4. Configure Chart.js
    return new Chart(canvas, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            plugins: {
                tooltip: {...},
                legend: {...}
            },
            scales: {...}
        }
    });
}
```

### CSS Architecture

Mobile-first responsive design using CSS Grid and Flexbox.

```css
/* Mobile-first base styles */
.container {
    max-width: 100%;
    padding: 15px;
}

/* Tablet breakpoint */
@media (min-width: 768px) {
    .container {
        max-width: 800px;
        padding: 20px;
    }
}

/* Desktop breakpoint */
@media (min-width: 1200px) {
    .container {
        max-width: 1000px;
    }
}

/* CSS Grid for form layout */
.form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
}

@media (min-width: 768px) {
    .form-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

## Data Flow

### Calculation Request Flow

```
1. User Input
   └─> Browser Form

2. Client-Side Validation
   └─> validation.js
       └─> If invalid: Show error, stop
       └─> If valid: Continue

3. HTTP POST Request
   └─> JSON payload to /calculate

4. Server-Side Validation
   └─> validation.py
       └─> If invalid: Return 400 error
       └─> If valid: Continue

5. Calculation
   └─> calculations.py
   └─> models.py
   └─> rcpchgrowth library

6. SDS Validation
   └─> models.py
       └─> If extreme: Return warnings
       └─> If impossible: Return error

7. JSON Response
   └─> Results object

8. Client-Side Rendering
   └─> script.js
   └─> Display results
   └─> Enable chart viewing
```

### Chart Data Flow

```
1. Click "Show Charts"
   └─> Enable chart tabs

2. Select Chart Type
   └─> Active tab changes

3. HTTP POST Request
   └─> JSON payload to /chart-data
   └─> Parameters: reference, measurement_method, sex

4. Server Fetches Data
   └─> utils.py::get_chart_data()
   └─> rcpchgrowth.create_chart()

5. JSON Response
   └─> Centile curves array

6. Client-Side Rendering
   └─> script.js::renderGrowthChart()
   └─> Chart.js creates visualization
```

## Security

### Input Validation

**Defense in Depth**: Validation at multiple layers

1. **Client-Side (JavaScript)**
   - Immediate feedback
   - Range checking
   - Date logic validation
   - Reduces server load

2. **Server-Side (Python)**
   - Authoritative validation
   - Cannot be bypassed
   - Error codes for debugging
   - Comprehensive checks

### Rate Limiting

**Flask-Limiter** configuration:
- Prevents abuse
- Protects against DoS
- Per-IP tracking
- Configurable limits

```python
@limiter.limit("30 per minute")
def calculate():
    ...
```

### Data Handling

**No Persistent Storage**:
- Calculations processed in-memory
- No database of patient data
- No PHI (Protected Health Information) stored
- Compliant with data protection

**localStorage**:
- Client-side only
- Never sent to server
- User can clear anytime
- No sensitive data stored

### HTTPS

**Production Requirements**:
- All connections over HTTPS
- TLS 1.2+ required
- Secure headers
- HSTS enabled

## Performance

### Backend Optimization

1. **Modular Architecture**
   - Fast imports
   - Minimal startup time
   - Efficient memory use

2. **Rate Limiting**
   - Prevents overload
   - Fair resource allocation

3. **No Database**
   - Eliminates query latency
   - Stateless design
   - Horizontal scaling possible

### Frontend Optimization

1. **Minimal Dependencies**
   - Vanilla JavaScript (no framework overhead)
   - Single CSS file
   - Chart.js only library

2. **Progressive Enhancement**
   - Core functionality loads first
   - Charts load on demand
   - Lazy loading for images

3. **Resource Management**
   - Chart instances destroyed when closed
   - Event listeners properly removed
   - Memory leaks prevented

4. **Caching**
   - Static assets cached
   - Service Worker for offline
   - Browser caching headers

### PWA Features

**Service Worker**:
```javascript
// Cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('growth-calc-v1').then((cache) => {
            return cache.addAll([
                '/',
                '/static/style.css',
                '/static/script.js',
                '/static/validation.js'
            ]);
        })
    );
});
```

**Manifest**:
```json
{
    "name": "Growth Parameters Calculator",
    "short_name": "Growth Calc",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#667eea",
    "theme_color": "#667eea"
}
```

## Deployment

### Production Setup

#### Environment Variables

```bash
FLASK_ENV=production
FLASK_DEBUG=0
PORT=8080
```

#### Gunicorn Configuration

```bash
gunicorn --bind 0.0.0.0:8080 \
         --workers 4 \
         --timeout 60 \
         --access-logfile - \
         --error-logfile - \
         app:app
```

**Worker Count**: 4 workers (adjust based on CPU cores)
**Timeout**: 60 seconds for calculations

#### Rate Limiter Storage

**Development**: In-memory
```python
storage_uri="memory://"
```

**Production**: Redis
```python
storage_uri="redis://localhost:6379"
```

### Render.com Deployment

**render.yaml**:
```yaml
services:
  - type: web
    name: growth-parameters-calculator
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Health Monitoring

**Endpoints**:
- `/`: Homepage (health check)
- `/calculate`: POST endpoint (functional check)

**Monitoring**:
- Response times
- Error rates
- Rate limit hits
- Memory usage

### Backup and Recovery

**Code**: GitHub repository
**No Database**: No data backup required
**Configuration**: Environment variables only

### Scaling

**Horizontal Scaling**:
- Stateless design
- No session storage
- Load balancer compatible
- Multiple instances possible

**Vertical Scaling**:
- Increase worker count
- More CPU cores
- Additional memory
