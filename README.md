# Growth Parameters Calculator

**🌐 Live App: [https://growth-parameters-calculator.onrender.com](https://growth-parameters-calculator.onrender.com)**

**⚠️ DISCLAIMER: This is an experimental web application created using Claude AI. It should NOT be used for clinical decision-making. All calculations must be verified independently before any clinical use. This tool is for educational and research purposes only.**

A mobile-compatible web application for calculating paediatric growth parameters using the [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/) from the Royal College of Paediatrics and Child Health.

This application was "vibe-coded" using Claude AI (Anthropic) as an experimental project to explore rapid application development for paediatric tools. Whilst the underlying calculations use the validated [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/), the application itself has not been clinically validated or formally tested.

## Features

### Core Calculations

- **Age** - Calendar age (years, months, days) and decimal years from date of birth
- **Weight** - Centile and SDS (z-score) using selected growth reference
- **Height** - Centile and SDS (z-score) using selected growth reference
- **BMI** - Body Mass Index with centile and SDS
- **OFC** - Occipitofrontal circumference (head circumference) with centile and SDS
- **Height Velocity** - Annualised growth rate (requires minimum 4-month interval between measurements)
- **Body Surface Area** - Calculated using Boyd formula
- **Mid-Parental Height** - Target height with centile and expected adult height range (requires parental heights)

### Data Quality and Safety Features

- **SDS Validation** - Automatic validation of measurement accuracy:
  - **Advisory warnings** at ±4 SDS for height, weight, BMI, and OFC - calculation proceeds with prominent warning
  - **Hard cut-offs** rejecting calculations:
    - ±8 SDS for height, weight, and OFC
    - ±15 SDS for BMI (higher threshold accommodates clinical conditions like severe obesity or anorexia nervosa)
  - Encourages users to verify measurements and consider remeasuring when values are extreme

### Interactive GH Dose Calculator

- Initial dose calculated for 7 mg/m²/week based on patient's BSA
- Adjustable dose with intelligent increment sizing:
  - **0.025 mg** increments for doses 0-0.5 mg
  - **0.05 mg** increments for doses 0.5-1.5 mg
  - **0.1 mg** increments for doses above 1.5 mg
- Real-time recalculation of mg/m²/week and mcg/kg/day equivalents

### Growth References

The application supports three validated growth references:

- **UK-WHO (Standard)**: Combined UK90 and WHO growth charts - standard reference for the general UK paediatric population
- **Turner Syndrome**: Syndrome-specific growth charts for girls with Turner syndrome
- **Trisomy 21 (Down Syndrome)**: Syndrome-specific growth charts for children with Down syndrome

All growth references are provided by the Royal College of Paediatrics and Child Health (RCPCH) via the [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/).

### Interactive Growth Charts

- **Visual centile charts** for height, weight, BMI, and head circumference (OFC)
- **Centile curves** from 0.4th to 99.6th percentile (solid lines for 2nd, 25th, 50th, 75th, 98th; dotted for 0.4th, 9th, 91st, 99.6th)
- **Sex-specific colours** - Blue for boys, pink for girls
- **Patient data overlay** - Current and previous measurements plotted as small dots
- **Tabbed interface** - Easy switching between different measurement types
- **Extended x-axis** - Starts at -2 weeks
- **Hover tooltips** - Interactive details on patient measurements only
- **Fully responsive** - Optimized viewing on mobile, tablet, and desktop devices
- **Powered by Chart.js** - Smooth, interactive charts
- **Reference-specific** - Charts match the selected growth reference (UK-WHO, Turner, Trisomy 21)

### User Interface

- **Responsive Design** - Optimised layouts for mobile, tablet, and desktop
- **Progressive Web App** - Can be installed on mobile devices and used like a native app
- **Parental Height Units** - Toggle between cm and feet/inches for parental heights
- **Clear Error Messages** - Informative feedback for validation issues and calculation requirements

## Usage

### Required Inputs
1. **Sex** - Select male or female
2. **Date of Birth** - Patient's date of birth
3. **Measurement Date** - Date of current measurements (defaults to today)
4. **Weight** - Current weight in kg
5. **Height** - Current height in cm
6. **Growth Reference** - UK-WHO (Standard), Turner Syndrome, or Trisomy 21

### Optional Inputs

**Previous Height Data** (for height velocity):
- Previous measurement date
- Previous height in cm
- *Note: Requires minimum 4-month interval between measurements*

**Parental Heights** (for mid-parental height):
- Maternal height
- Paternal height
- Can be entered in cm or feet/inches

**Head Circumference**:
- OFC (Occipitofrontal Circumference) in cm

### Results

The application displays:
- **Age**: Calendar format (e.g., "5y 3m 12d") with decimal years in parentheses
- **Basic Parameters**: Weight, height, and BMI with centiles and SDS values
- **Validation Warnings**: Advisory alerts for extreme SDS values (>±4) encouraging measurement verification
- **Height Velocity**: Annualised growth rate (cm/year) if previous height data provided
- **Body Surface Area**: Calculated using Boyd formula
- **GH Dose Calculator**: Interactive dose adjuster starting at 7 mg/m²/week with variable increment sizing, showing both mg/m²/week and mcg/kg/day
- **Mid-Parental Height**: Target height with centile and expected adult height range
- **OFC**: Head circumference centile and SDS if provided

### Viewing Growth Charts

After calculating growth parameters:

1. Click the **"Show Growth Charts"** button below the results
2. Charts section opens with the height chart displayed by default
3. Click tabs to switch between **Height**, **Weight**, **BMI**, and **OFC** charts
4. **Centile lines** are color-coded: blue for boys, pink for girls
5. **50th centile** is shown with a heavier line weight
6. **Extreme centiles** (0.4th, 9th, 91st, 99.6th) are shown as dotted lines
7. Hover over **patient measurements** (small dots) to see detailed tooltips
8. Click **"Close Charts"** to collapse back to results view

**Note**: The OFC tab will be disabled if head circumference was not provided in the calculation.

## Technology Stack

- **Backend**: Flask 3.0.0 (Python web framework)
- **Growth Calculations**: [rcpchgrowth](https://growth.rcpch.ac.uk/developer/rcpchgrowth/) 4.3.8 (RCPCH validated library)
- **Frontend**: HTML5, CSS3, vanilla JavaScript
- **Deployment**: Gunicorn WSGI server
- **Design**: Mobile-first responsive approach with CSS Grid

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

## Open Source

Full source code available on [GitHub](https://github.com/gm5dna/growth-parameters-calculator).
