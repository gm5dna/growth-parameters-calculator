# Growth Parameters Calculator

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask Version](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-Open%20Source-brightgreen.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)

**🌐 Live App: [https://growth-parameters-calculator.onrender.com](https://growth-parameters-calculator.onrender.com)**

**⚠️ DISCLAIMER: This is an experimental web application. It should NOT be used for clinical decision-making. All calculations must be verified independently before any clinical use. This tool is for educational and research purposes only.**

A mobile-compatible web application for calculating paediatric growth parameters using the validated [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/) from the Royal College of Paediatrics and Child Health (RCPCH).

## Features

- 📊 **Growth Measurements** - Weight, height, BMI, and head circumference with centiles and SDS scores
- 📈 **Interactive Growth Charts** - Visual centile charts with patient data overlay
- 🔄 **Height Velocity** - Annualised growth rate calculation
- 💉 **GH Dose Calculator** - Interactive growth hormone dosing tool
- 📏 **Mid-Parental Height** - Target height prediction with ranges
- 🌍 **Multiple References** - UK-WHO, CDC, Turner syndrome, and Trisomy 21 charts
- 📱 **Mobile-First Design** - Responsive layout, works as Progressive Web App
- 🎯 **Data Quality Checks** - Automatic SDS validation with warnings

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gm5dna/growth-parameters-calculator.git
cd growth-parameters-calculator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py

# Open browser to http://localhost:8080
```

Or use the convenience script:
```bash
./run.sh
```

## Usage

### Required Inputs
1. **Sex** - Male or female
2. **Date of Birth** - Patient's date of birth
3. **Measurement Date** - Date of measurements (defaults to today)
4. **At least one measurement** - Weight (kg), height (cm), or OFC (cm)

### Optional Inputs
- **Previous Height Data** - For height velocity (requires 4-month minimum interval)
- **Parental Heights** - For mid-parental height prediction (cm or ft/in)
- **Gestation at Birth** - For preterm correction (weeks + days)
- **Growth Reference** - UK-WHO (default), CDC, Turner syndrome, or Trisomy 21

### Results
The calculator displays:
- Age (calendar and decimal years)
- Growth measurements with centiles and SDS
- Advisory warnings for extreme values
- Height velocity (if previous data provided)
- Body Surface Area (Boyd or cBNF method)
- GH dose calculator with real-time adjustments
- Mid-parental height with target range
- Interactive growth charts

## Documentation

Detailed documentation is available in the [`docs/`](./docs) folder:

- **[Features Guide](./docs/FEATURES.md)** - Comprehensive feature documentation
- **[User Guide](./docs/USER_GUIDE.md)** - Step-by-step usage instructions
- **[Technical Documentation](./docs/TECHNICAL.md)** - Architecture and implementation details
- **[API Reference](./docs/API.md)** - API endpoints and data formats
- **[Development Guide](./docs/DEVELOPMENT.md)** - Contributing and development setup

## Technology Stack

- **Backend**: Flask 3.0.0, Python 3.8+
- **Growth Calculations**: rcpchgrowth 4.3.8 (RCPCH validated library)
- **Frontend**: HTML5, CSS3, vanilla JavaScript
- **Charts**: Chart.js 4.4.1
- **Testing**: pytest 7.4.3
- **Deployment**: Gunicorn, Render.com

## Architecture

The application uses a modular architecture for maintainability:

```
growth-parameters-calculator/
├── app.py                 # Flask application & routes
├── constants.py           # Configuration & error codes
├── validation.py          # Input validation
├── calculations.py        # Growth calculations
├── models.py              # Measurement models
├── utils.py               # Helper functions
├── static/                # Frontend assets
│   ├── script.js         # Main JavaScript
│   ├── validation.js     # Client-side validation
│   └── style.css         # Styles
├── templates/             # HTML templates
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_calculations.py
```

## License

This project is open source. The underlying growth calculations are provided by the RCPCH rcpchgrowth library.

## Acknowledgements

- **RCPCH** - For the validated [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/)
- **Claude AI** (Anthropic) - For rapid application development assistance
- **Chart.js** - For interactive charting capabilities

## Disclaimer

This application is for **educational and research purposes only**. It has not been clinically validated or formally tested for medical use. All calculations should be independently verified before any clinical application. The developers accept no liability for clinical decisions made using this tool.

---

**Created by**: Stuart ([@gm5dna](https://github.com/gm5dna))
**Powered by**: [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/) from RCPCH
