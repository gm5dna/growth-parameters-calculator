# Features Guide

Comprehensive documentation of all features in the Growth Parameters Calculator.

## Table of Contents

- [Core Calculations](#core-calculations)
- [Interactive Growth Charts](#interactive-growth-charts)
- [Growth References](#growth-references)
- [Data Quality and Safety](#data-quality-and-safety)
- [GH Dose Calculator](#gh-dose-calculator)
- [Gestational Age Correction](#gestational-age-correction)
- [Body Surface Area Methods](#body-surface-area-methods)
- [User Interface Features](#user-interface-features)

## Core Calculations

### Age Calculation
- **Calendar Age**: Years, months, and days (e.g., "5y 3m 12d")
- **Decimal Years**: Precise age calculation using 365.25 days/year
- Automatically calculated from date of birth and measurement date

### Growth Measurements

All measurements include:
- **Centile**: Percentage of population below this value
- **SDS (Z-Score)**: Standard deviation score from population mean

#### Weight
- Input: Kilograms (kg)
- Range: 0.1 - 300 kg
- Calculates centile and SDS using selected growth reference

#### Height
- Input: Centimeters (cm)
- Range: 10 - 250 cm
- Calculates centile and SDS using selected growth reference

#### BMI (Body Mass Index)
- Requires: Both weight and height
- Formula: weight(kg) / (height(m))²
- Calculates age-adjusted centile and SDS

#### OFC (Occipitofrontal Circumference)
- Input: Centimeters (cm)
- Range: 10 - 100 cm
- Head circumference measurement
- Calculates centile and SDS using selected growth reference

### Height Velocity

Calculates annualized growth rate from two height measurements.

**Requirements**:
- Current height and date
- Previous height and date
- Minimum 4-month interval between measurements

**Output**:
- Growth rate in cm/year
- Validation message if interval too short

**Calculation**:
```
velocity = (height_diff / days_between) × 365.25
```

### Mid-Parental Height

Predicts target adult height based on parental heights.

**Requirements**:
- Maternal height (cm or ft/in)
- Paternal height (cm or ft/in)
- Child's sex

**Output**:
- Mid-parental height (cm)
- Centile of mid-parental height
- Target range (±8.5 cm for girls, ±10 cm for boys)
- Evaluated at age 18 for 0-18 year charts, age 20 for 8-20 year charts

**Calculation**:
- For girls: (maternal_height + paternal_height - 13) / 2
- For boys: (maternal_height + paternal_height + 13) / 2

## Interactive Growth Charts

### Chart Features

- **Chart Types**: Height, weight, BMI, and OFC
- **Centile Curves**: 0.4th, 2nd, 9th, 25th, 50th, 75th, 91st, 98th, 99.6th
- **Age Ranges**:
  - Height/Weight: 0-2, 0-4, 0-18, 8-20 years
  - BMI: 0-4, 2-18 years
  - OFC: 0-2, 0-18 years
- **Auto-defaulting**: For children ≤2 years, defaults to 0-2 year range

### Visual Elements

- **Sex-Specific Colors**:
  - Blue for boys
  - Pink for girls
- **Line Styles**:
  - Solid lines: 2nd, 25th, 50th, 75th, 98th centiles
  - Dotted lines: 0.4th, 9th, 91st, 99.6th centiles
  - Heavy line: 50th centile (median)

### Patient Data Overlay

- **Current Measurement**: Filled circle
- **Corrected Age Measurement**: Cross (X shape) if gestation correction applied
- **Previous Measurement**: Orange filled circle
- **Correction Line**: Dotted line connecting chronological and corrected age points

### Enhanced Tooltips

Hover over patient measurements to see:
- Age at measurement (decimal years)
- Measurement value with units
- Centile percentage
- SDS (Standard Deviation Score)

Available for:
- Current measurements
- Corrected age measurements
- Previous measurements
- Mid-parental height markers

### Dynamic Features

- **Responsive Axis**: Automatically adjusts to data range
- **Integer Tick Marks**: One-year intervals for clarity
- **Tabbed Interface**: Easy switching between measurement types
- **Disabled Tabs**: Tabs disabled for measurements not provided
- **Mobile Optimized**: Touch-friendly, responsive design

## Growth References

### UK-WHO (Standard)

Combined UK90 and WHO growth charts.

**Population**: General UK paediatric population
**Age Ranges**:
- 0-4 years: WHO standards
- 4-18 years: UK90 references
**Source**: RCPCH

### CDC (US)

Centers for Disease Control and Prevention growth charts.

**Population**: General US paediatric population
**Age Range**: 0-20 years
**Source**: CDC/NCHS, revised 2000

### Turner Syndrome

Syndrome-specific growth charts for girls with Turner syndrome.

**Population**: Girls with Turner syndrome
**Sex**: Female only (male option disabled)
**Age Range**: 0-20 years
**Source**: RCPCH/Turner syndrome-specific data

### Trisomy 21 (Down Syndrome)

Syndrome-specific growth charts for children with Down syndrome.

**Population**: Children with Trisomy 21
**Sex**: Both male and female
**Age Range**: 0-18 years
**Source**: RCPCH/Down syndrome-specific data

## Data Quality and Safety

### SDS Validation

Automatic validation of measurement accuracy with three levels:

#### Normal Range (±4 SDS)
- Calculations proceed without warnings
- Typical clinical measurements

#### Advisory Warnings (±4 to ±8 SDS for height/weight/OFC)
- Calculation proceeds with prominent warning
- Encourages measurement verification
- Message: "⚠️ Advisory Warnings: [Measurement] SDS beyond ±4"
- User should consider remeasuring

#### Hard Cut-offs (Rejected)
- **Height, Weight, OFC**: ±8 SDS
- **BMI**: ±15 SDS (higher threshold for clinical conditions)
- Calculation rejected with error message
- Prevents processing of likely erroneous data

### Input Validation

#### Date Validation
- Birth date must be in the past
- Measurement date cannot be in the future
- Measurement date must be after birth date

#### Measurement Ranges
- **Weight**: 0.1 - 300 kg
- **Height**: 10 - 250 cm
- **OFC**: 10 - 100 cm
- **Gestation**: 22-44 weeks + 0-6 days

#### Previous Measurement Validation
- Previous date must be before current measurement date
- Minimum 4-month interval for height velocity

## GH Dose Calculator

Interactive growth hormone dosing tool.

### Features

- **Initial Dose**: Calculated for 7 mg/m²/week
- **Based on BSA**: Uses patient's body surface area
- **Adjustable Dose**: Plus/minus buttons for dose modification
- **Real-time Conversion**: Instant recalculation of equivalents

### Intelligent Increment Sizing

Variable increments based on dose level:
- **0-0.5 mg**: 0.025 mg increments (fine control)
- **0.5-1.5 mg**: 0.05 mg increments (medium control)
- **>1.5 mg**: 0.1 mg increments (coarse control)

### Display Formats

Shows dose in three formats simultaneously:
1. **mg/day**: Daily dose in milligrams
2. **mg/m²/week**: Weekly dose per square meter BSA
3. **mcg/kg/day**: Daily dose per kilogram weight

### Requirements

- Body Surface Area (BSA) must be calculable
- Requires at least weight measurement
- More accurate with both weight and height

## Gestational Age Correction

Automatic age correction for preterm infants.

### Eligibility Criteria

Correction applied when ALL conditions met:
- Gestation at birth < 37 weeks
- Age-dependent thresholds:
  - **32-36 weeks**: Correct until age 1 year
  - **<32 weeks**: Correct until age 2 years

### Correction Method

1. Calculate expected due date (40 weeks gestation)
2. Determine days premature
3. Adjust age by adding days to due date
4. Use corrected age for growth calculations

### Visual Representation

On growth charts:
- **Chronological age**: Filled circle
- **Corrected age**: Cross (X shape)
- **Connection**: Dotted line between points
- **Separate tooltips**: Both points show full data

### When Not to Correct

- Term babies (≥37 weeks)
- Preterm babies beyond correction age threshold
- No gestation data provided

## Body Surface Area Methods

### Boyd Formula (Preferred)

**Used when**: Both weight and height available

**Formula**:
```
BSA = 0.0003207 × (height_cm^0.3) × (weight_g^(0.7285 - (0.0188 × log10(weight_g))))
```

**Accuracy**: Most accurate method for children
**Display**: Label shows "Body Surface Area (Boyd)"
**Units**: m² (square meters)

### cBNF Lookup Table (Fallback)

**Used when**: Only weight available (no height)

**Source**: British National Formulary for Children (BNFc)
**Reference**: Sharkey I et al., *Br J Cancer* 2001; 85(1):23-28
**Method**:
- Lookup table with interpolation
- Weight range: 1-90 kg with specific points
- Linear interpolation between values
- Linear extrapolation outside range

**Display**: Label shows "Body Surface Area (cBNF)"
**Accuracy**: Less accurate than Boyd, but useful when height unavailable

### Clinical Applications

BSA used for:
- Growth hormone dose calculations
- Drug dosing requiring BSA
- Physiological assessments
- Metabolic calculations

## User Interface Features

### Responsive Design

- **Mobile-First**: Optimized for smartphones
- **Tablet Support**: Adapted layouts for medium screens
- **Desktop**: Full-featured interface with optimal spacing
- **Touch-Friendly**: Large tap targets, gesture support

### Progressive Web App (PWA)

- **Installable**: Add to home screen on mobile devices
- **Offline Capable**: Core functionality works offline
- **App-Like**: Launches like a native app
- **Auto-Updates**: New versions load automatically

### Basic vs Advanced Mode

Toggle between simplified and full-featured interfaces.

**Basic Mode**:
- UK-WHO reference (fixed)
- Core inputs: DOB, measurement date, weight, height, OFC, parental heights
- Core calculations: Age, weight, height, OFC, BMI, MPH, target range
- Growth charts
- Simplified interface for quick assessments

**Advanced Mode**:
- All growth references (UK-WHO, CDC, Turner, Trisomy 21)
- All inputs including:
  - Gestation at birth
  - Previous height measurements
  - Height velocity
  - GH dose calculator
- Full feature set
- Comprehensive interface for detailed assessments

### Parental Height Units

Flexible input for international users:
- **Centimeters (cm)**: Metric input
- **Feet and Inches (ft/in)**: Imperial input
- **Independent**: Each parent can use different units
- **Auto-conversion**: Converts to cm for calculations

### Form Persistence

Automatic save/restore functionality:
- **Auto-save**: Form data saved to browser localStorage
- **Debounced**: 1-second delay to prevent excessive writes
- **Restore on Load**: Form repopulated on page reload
- **Clear on Success**: Saved data removed after successful calculation
- **Includes Mode**: Basic/Advanced mode state preserved

### Loading States

Visual feedback during calculations:
- **Button State**: "Calculate" → "Calculating..."
- **Button Disabled**: Prevents multiple submissions
- **Cursor**: Changes to wait cursor
- **Automatic Reset**: Restores on completion or error

### Accessibility Features

- **ARIA Labels**: All form inputs properly labeled
- **Screen Reader Support**: Semantic HTML structure
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Management**: Logical tab order
- **Error Announcements**: Clear validation messages

### Error Handling

- **Client-Side Validation**: Immediate feedback on invalid inputs
- **Server-Side Validation**: Robust backend validation
- **Clear Messages**: Descriptive error text
- **Error Codes**: Standardized codes for debugging
- **Rate Limiting**: Protection against abuse (30/min)

### Chart Interactions

- **Show/Hide**: Collapsible charts section
- **Tab Switching**: Instant chart type changes
- **Smooth Scrolling**: Auto-scroll to relevant sections
- **Hover Tooltips**: Detailed data on mouse over
- **Memory Management**: Charts properly destroyed on close
- **Loading Indicators**: Spinner during chart data fetch
