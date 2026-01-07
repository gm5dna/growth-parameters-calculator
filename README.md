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
- **Body Surface Area** - Calculated using:
  - **Boyd formula** when both weight and height are available (more accurate)
  - **cBNF lookup table** when only weight is available (estimated from weight alone)
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

The application supports four validated growth references:

- **UK-WHO (Standard)**: Combined UK90 and WHO growth charts - standard reference for the general UK paediatric population
- **CDC (US)**: Centers for Disease Control and Prevention growth charts - standard reference for the US paediatric population
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
- **Reference-specific** - Charts match the selected growth reference (UK-WHO, CDC, Turner, Trisomy 21)

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
4. **Growth Reference** - UK-WHO (Standard), CDC (US), Turner Syndrome, or Trisomy 21
5. **At least one measurement** - Weight, height, or OFC (see below)

### Measurements

**At least one of the following measurements is required:**

- **Weight** - Current weight in kg
- **Height** - Current height in cm
- **OFC (Head Circumference)** - Occipitofrontal circumference in cm

**Notes:**
- The calculator will perform calculations and display results only for the measurements provided
- BMI calculation requires both weight and height
- Body Surface Area (BSA) can be calculated from:
  - Both weight and height (using Boyd formula - more accurate)
  - Weight alone (using cBNF lookup table - estimated)
- GH dose calculator requires BSA (and therefore at least weight)
- Growth charts will only show tabs for measurements that were provided

### Optional Inputs

**Previous Height Data** (for height velocity):
- Previous measurement date
- Previous height in cm
- *Note: Requires minimum 4-month interval between measurements*

**Parental Heights** (for mid-parental height):
- Maternal height
- Paternal height
- Can be entered in cm or feet/inches

### Results

The application displays:
- **Age**: Calendar format (e.g., "5y 3m 12d") with decimal years in parentheses
- **Measurements Provided**: Only the measurements that were entered will be displayed with their centiles and SDS values:
  - Weight (kg) - if provided
  - Height (cm) - if provided
  - BMI (kg/m²) - if both weight and height provided
  - OFC / Head circumference (cm) - if provided
- **Validation Warnings**: Advisory alerts for extreme SDS values (>±4) encouraging measurement verification
- **Height Velocity**: Annualised growth rate (cm/year) if height and previous height data provided
- **Body Surface Area**:
  - Calculated using **Boyd formula** if both weight and height provided (displayed as "BSA (Boyd)")
  - Calculated using **cBNF lookup table** if only weight provided (displayed as "BSA (cBNF)")
  - See [Body Surface Area Calculation Methods](#body-surface-area-calculation-methods) for details
- **GH Dose Calculator**: Interactive dose adjuster starting at 7 mg/m²/week (requires BSA, which needs at least weight)
- **Mid-Parental Height**: Target height with centile and expected adult height range (if parental heights provided)

### Viewing Growth Charts

After calculating growth parameters:

1. Click the **"Show Growth Charts"** button below the results
2. Charts section opens with the first available chart displayed
3. Click tabs to switch between **Height**, **Weight**, **BMI**, and **OFC** charts
4. **Centile lines** are color-coded: blue for boys, pink for girls
5. **50th centile** is shown with a heavier line weight
6. **Extreme centiles** (0.4th, 9th, 91st, 99.6th) are shown as dotted lines
7. Hover over **patient measurements** (small dots) to see detailed tooltips
8. Click **"Close Charts"** to collapse back to results view

**Note**: Chart tabs will only be enabled for measurements that were provided:
- **Height tab**: Enabled only if height was provided
- **Weight tab**: Enabled only if weight was provided
- **BMI tab**: Enabled only if both height and weight were provided
- **OFC tab**: Enabled only if head circumference was provided

## Body Surface Area Calculation Methods

The application uses two methods for calculating Body Surface Area (BSA) depending on available measurements:

### Boyd Formula (Preferred)

**Used when**: Both weight and height are available

The Boyd formula is more accurate as it incorporates both weight and height:

```
BSA = 0.0003207 × (height_cm^0.3) × (weight_g^(0.7285 - (0.0188 × log10(weight_g))))
```

This is the preferred method and provides the most accurate BSA estimation for children.

**Display**: Results show as "BSA (Boyd)"

### cBNF Lookup Table (Fallback)

**Used when**: Only weight is available (no height measurement)

When height is not provided, the application uses lookup tables from the British National Formulary for Children (BNFc). These tables estimate BSA from weight alone using pre-calculated values based on the Boyd equation.

**Source**: Adapted from Sharkey I et al., *British Journal of Cancer* 2001; 85 (1): 23–28, © 2001 Macmillan Publishers Ltd

**Coverage**:
- Weights from 1 kg to 90 kg with specific data points
- Linear interpolation between table values
- Linear extrapolation for weights outside the table range

**Display**: Results show as "BSA (cBNF)"

**Note**: While the cBNF method is convenient when height is unavailable, the Boyd formula with both weight and height is more accurate and should be used whenever possible.

### Clinical Applications

Both BSA calculations are used for:
- Growth hormone (GH) dose calculations (mg/m²/week)
- Drug dosing that requires BSA
- Physiological assessments

The GH dose calculator will work with either method but will be more accurate when based on the Boyd formula.

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
