# Growth Parameters Calculator

**⚠️ DISCLAIMER: This is an experimental web application created using Claude AI. It should NOT be used for clinical decision-making. All calculations must be verified independently before any clinical use. This tool is for educational and research purposes only.**

A mobile-compatible web application for calculating paediatric growth parameters using the rcpchgrowth library from the Royal College of Paediatrics and Child Health.

## Development Note

This application was "vibe-coded" using Claude AI (Anthropic) as an experimental project to explore rapid application development for paediatric tools. Whilst the underlying calculations use the validated rcpchgrowth library, the application itself has not been clinically validated or formally tested.

## Features

The application calculates the following parameters:

- **Age** (in years)
- **Weight** Centile / SDS
- **Height** Centile / SDS
- **BMI** / BMI Centile / BMI SDS
- **Height Velocity** (yearly derived, requires previous height measurement)
- **Body Surface Area** (using Boyd formula)
- **Growth Hormone Doses** (in mg/day for 5, 7, and 10 mg/m²/week dose options)
- **Mid-Parental Height** with centile and target range (requires parental heights)

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

Or use the provided run script:
```bash
./run.sh
```

## Usage

### Required Inputs
1. Select the patient's sex (male/female)
2. Enter the date of birth
3. Enter the current measurement date
4. Enter weight (kg)
5. Enter height (cm)

### Optional Inputs
6. **Previous Height Data**: Enter previous measurement date and height for height velocity calculation
7. **Parental Heights**: Enter maternal and paternal heights (cm) for mid-parental height and target range calculation

### Results
Click "Calculate" to see:
- Age, weight, height, and BMI with centiles and SDS values
- Height velocity (if previous data provided)
- Body Surface Area (Boyd formula)
- GH doses in mg/day for three standard dose options (5, 7, and 10 mg/m²/week)
- Mid-parental height with centile and target range (if parental heights provided)

## Technology Stack

- **Backend**: Flask (Python)
- **Growth Calculations**: rcpchgrowth library
- **Frontend**: HTML5, CSS3, JavaScript
- **Responsive Design**: Mobile-first approach

## Growth References

The application supports three growth references:
- **UK-WHO (Standard)**: Standard growth charts for the general population
- **Turner Syndrome**: Syndrome-specific growth charts
- **Trisomy 21 (Down Syndrome)**: Syndrome-specific growth charts

## Notes

- The application uses UK-WHO growth charts via the rcpchgrowth library
- All calculations are performed server-side
- The interface is optimised for both mobile and desktop devices
- Includes progressive web app (PWA) support - can be added to home screen on mobile devices

## Disclaimer (Important)

This is an experimental, AI-generated tool created for educational purposes. It has not undergone clinical validation or testing. **Do not use this application for clinical decision-making.** Always verify calculations independently and use established clinical tools for patient care.
