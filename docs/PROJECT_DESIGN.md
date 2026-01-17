# Growth Parameters Calculator - Project Design Document

> **Living Document** - Last updated: 2026-01-17
> Update this document as design decisions evolve.

---

## 1. Project Vision

### Purpose
A mobile-compatible web application for calculating pediatric growth parameters using the validated rcpchgrowth library from the Royal College of Paediatrics and Child Health (RCPCH).

### Target Users
- Healthcare professionals (pediatricians, nurses, GPs)
- Researchers working with growth data
- Medical students learning about growth assessment
- Parents (with appropriate disclaimers about clinical interpretation)

### Non-Goals
- **NOT** for clinical decision-making (educational/research tool only)
- **NOT** storing patient data persistently
- **NOT** replacing professional medical judgment

---

## 2. Design Principles

### 2.1 Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Stateless** | No database, no sessions, no PHI retention |
| **Mobile-first** | Responsive design, touch-friendly, offline-capable |
| **Fail-fast** | Validate early, return clear error messages |
| **Separation of concerns** | Modular architecture with single-responsibility modules |
| **Clinical accuracy** | Use RCPCH-validated rcpchgrowth library exclusively |

### 2.2 Security Principles
- No persistent storage of health data
- Client-side localStorage for convenience only (form state)
- Rate limiting to prevent abuse
- Input validation at both client and server

---

## 3. Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (SPA)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ index.html  │  │ script.js   │  │ Chart.js visualizations│
│  │ (template)  │  │ (1296 lines)│  │ (centile curves)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                         ↓ JSON API                           │
├─────────────────────────────────────────────────────────────┤
│                        Backend (Flask)                       │
│  ┌─────────┐  ┌────────────┐  ┌──────────────┐  ┌────────┐  │
│  │ app.py  │→ │validation.py│→ │calculations.py│→│models.py│ │
│  │ (routes)│  │ (input)    │  │ (business)   │  │(rcpch) │  │
│  └─────────┘  └────────────┘  └──────────────┘  └────────┘  │
│        ↓                                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              rcpchgrowth library (RCPCH)                │  │
│  │  - UK-WHO, CDC, Turner Syndrome, Trisomy 21 references │  │
│  │  - SDS/centile calculations                            │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
User Input → Client Validation → POST /calculate → Server Validation
          → Age Calculation → Gestation Correction Check
          → rcpchgrowth Measurement Creation → SDS/Centile Extraction
          → Additional Calculations (BSA, velocity, MPH, GH dose)
          → JSON Response → Frontend Rendering → Chart Update
```

### 3.3 Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `app.py` | Routing, orchestration, rate limiting | Routes, measurement creation |
| `constants.py` | Configuration, thresholds | Age limits, SDS bounds, error codes |
| `validation.py` | Input validation | `validate_date()`, `validate_weight()`, etc. |
| `calculations.py` | Business logic | `calculate_age_in_years()`, `calculate_bsa()`, etc. |
| `models.py` | rcpchgrowth interface | `create_measurement()`, `extract_measurement_result()` |
| `utils.py` | Helpers | `norm_cdf()`, `calculate_mid_parental_height()` |

---

## 4. Feature Specifications

### 4.1 Core Calculations

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Age** | Decimal years + calendar (y/m/d) | `calculate_age_in_years()` using relativedelta |
| **Weight SDS/centile** | Z-score and percentile | rcpchgrowth Measurement |
| **Height SDS/centile** | Z-score and percentile | rcpchgrowth Measurement |
| **BMI** | Calculated + SDS/centile | rcpchgrowth Measurement |
| **Head circumference** | OFC SDS/centile | rcpchgrowth Measurement |

### 4.2 Advanced Calculations

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Gestation correction** | Adjusted age for preterm | `calculate_corrected_age()` |
| **Height velocity** | Annualized growth rate | `calculate_height_velocity()` (min 4 months) |
| **Mid-parental height** | Target height from parents | `calculate_mid_parental_height()` with ±8.5cm range |
| **BSA** | Body surface area | Boyd formula (default) or cBNF lookup |
| **GH dose** | Growth hormone dosing | Standard 7 mg/m²/week |

### 4.3 Growth References

| Reference | Population | Use Case |
|-----------|------------|----------|
| UK-WHO | General UK population | Default for UK patients |
| CDC | US population | US patients |
| Turner Syndrome | Turner syndrome patients | Specialized reference |
| Trisomy 21 | Down syndrome patients | Specialized reference |

### 4.4 Validation Rules

| Field | Rules |
|-------|-------|
| Birth date | Valid format, not future, age 0-25 years |
| Measurement date | Valid format, after birth date |
| Weight | 0.1-300 kg |
| Height | 10-250 cm |
| OFC | 10-100 cm |
| Gestation | 22-44 weeks, 0-6 days |
| SDS | Warning at ±4, hard limit at ±8 (BMI: ±15) |

---

## 5. API Reference

### POST /calculate

**Request:**
```json
{
  "birth_date": "2020-01-15",
  "measurement_date": "2024-01-15",
  "sex": "male",
  "reference": "uk-who",
  "weight": 16.5,
  "height": 104.2,
  "ofc": 51.0,
  "gestation_weeks": 34,
  "gestation_days": 3,
  "previous_height": 98.5,
  "previous_date": "2023-07-15",
  "maternal_height": 165,
  "paternal_height": 178
}
```

**Response (success):**
```json
{
  "success": true,
  "results": {
    "age_years": 4.0,
    "age_calendar": {"years": 4, "months": 0, "days": 0},
    "weight": {"value": 16.5, "centile": 50.0, "sds": 0.0},
    "height": {"value": 104.2, "centile": 55.0, "sds": 0.12},
    "bmi": {"value": 15.2, "centile": 45.0, "sds": -0.13},
    "ofc": {"value": 51.0, "centile": 60.0, "sds": 0.25},
    "gestation_correction_applied": false,
    "height_velocity": {"value": 11.4, "message": "..."},
    "bsa": 0.68,
    "bsa_method": "Boyd",
    "mid_parental_height": {...},
    "gh_dose": {...},
    "validation_messages": []
  }
}
```

### POST /chart-data

**Request:**
```json
{
  "reference": "uk-who",
  "measurement_method": "height",
  "sex": "male"
}
```

**Response:**
```json
{
  "success": true,
  "centiles": [
    {"centile": 0.4, "data": [{"x": 0, "y": 46.1}, ...]},
    {"centile": 2, "data": [...]},
    ...
  ]
}
```

---

## 6. UI/UX Design

### 6.1 Layout Modes

| Mode | Features Shown |
|------|---------------|
| **Basic** | Birth date, measurement date, sex, reference, weight, height, OFC |
| **Advanced** | + Gestation, previous height/date, parental heights |

### 6.2 Chart Types
- Height-for-age
- Weight-for-age
- BMI-for-age
- Head circumference-for-age

### 6.3 Centile Lines Displayed
0.4th, 2nd, 9th, 25th, 50th, 75th, 91st, 98th, 99.6th

---

## 7. Testing Strategy

### 7.1 Test Categories

| Category | Location | Coverage |
|----------|----------|----------|
| Unit tests | `tests/test_calculations.py` | Age, BSA, velocity, GH dose |
| Validation tests | `tests/test_validation.py` | All input validation |

### 7.2 Key Test Scenarios

- Age calculation across leap years
- Preterm gestation correction logic
- BSA formula accuracy (Boyd and cBNF)
- Edge cases for validation (boundary values)
- Error code consistency

---

## 8. Deployment

### 8.1 Current Setup
- **Platform:** Render.com
- **Server:** Gunicorn with 4 workers
- **URL:** https://growth-parameters-calculator.onrender.com

### 8.2 Environment Variables
- `PORT` - Server port (default: 8080)
- Rate limiter storage (memory:// for dev, redis:// for prod)

---

## 9. Known Limitations

| Limitation | Reason | Future Consideration |
|------------|--------|---------------------|
| No data persistence | Privacy/compliance by design | Could add optional export |
| UK-WHO as only default reference | Simplicity | Could detect user locale |
| Single measurement point on charts | MVP scope | Could add measurement history |
| No multi-language support | MVP scope | Could add i18n |

---

## 10. Future Considerations

### Potential Enhancements
- [ ] Export results as PDF report
- [ ] Multiple measurement history on charts
- [ ] Additional growth references
- [ ] Internationalization (i18n)
- [ ] Specialized calculators (bone age, predicted adult height)

### Technical Debt
- None currently identified

---

## 11. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-17 | Document created | Establish project context for AI assistance |
| Prior | Modular architecture | Separation of concerns, testability |
| Prior | No database | Privacy compliance, simplicity |
| Prior | rcpchgrowth library | RCPCH-validated, authoritative |
| Prior | Mobile-first PWA | Target user accessibility |

---

## 12. References

- [RCPCH Growth Charts](https://www.rcpch.ac.uk/resources/uk-who-growth-charts)
- [rcpchgrowth Python library](https://pypi.org/project/rcpchgrowth/)
- [UK-WHO Growth Standards](https://www.who.int/tools/child-growth-standards)

---

*This document should be updated whenever significant design decisions are made or the project direction changes.*
