# User Guide

Step-by-step instructions for using the Growth Parameters Calculator.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Workflow](#basic-workflow)
- [Detailed Instructions](#detailed-instructions)
- [Understanding Results](#understanding-results)
- [Using Growth Charts](#using-growth-charts)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Application

**Online**: Visit [https://growth-parameters-calculator.onrender.com](https://growth-parameters-calculator.onrender.com)

**Local Installation**:
```bash
source venv/bin/activate
python app.py
# Navigate to http://localhost:8080
```

### First Time Setup

1. **Read the Disclaimer**: The warning banner at the top explains the tool is for educational purposes only
2. **Dismiss Disclaimer** (optional): Click "Dismiss" to hide the banner for this session
3. **Choose Mode**: Toggle between Basic and Advanced mode in the top-right
   - **Basic Mode**: Simplified interface for quick assessments
   - **Advanced Mode**: Full feature set with all options

## Basic Workflow

### Simple Calculation (3 Steps)

1. **Enter Patient Details**
   - Select sex (male/female)
   - Enter date of birth
   - Enter measurement date (defaults to today)

2. **Enter Measurements**
   - Enter at least one: weight, height, or OFC
   - Optionally enter parental heights

3. **Calculate**
   - Click "Calculate" button
   - View results below the form

### Viewing Charts (2 Steps)

1. **After calculating**, click "Show Growth Charts" button
2. **Switch tabs** to view different chart types (Height, Weight, BMI, OFC)

## Detailed Instructions

### Step 1: Patient Demographics

#### Sex Selection
- **Required field**
- Click radio button for Male or Female
- **Note**: Turner syndrome reference only available for females

#### Date of Birth
- **Required field**
- Click the date picker or type date in YYYY-MM-DD format
- Must be in the past
- Example: 2018-05-15

#### Measurement Date
- **Required field**
- Defaults to today's date
- Can be changed if measurements were taken on a different date
- Must be after date of birth

### Step 2: Growth Reference (Advanced Mode Only)

Choose the appropriate growth reference:

- **UK-WHO (Standard)**: Default for general UK population
- **CDC (US)**: For US population
- **Turner Syndrome**: For girls with Turner syndrome (female only)
- **Trisomy 21**: For children with Down syndrome

**In Basic Mode**: UK-WHO is automatically selected

### Step 3: Current Measurements

Enter at least one of the following:

#### Weight
- **Units**: Kilograms (kg)
- **Range**: 0.1 - 300 kg
- **Precision**: Two decimal places (e.g., 12.35)
- **Example**: A child weighing 25 kg, enter "25" or "25.00"

#### Height
- **Units**: Centimeters (cm)
- **Range**: 10 - 250 cm
- **Precision**: One decimal place (e.g., 125.5)
- **Example**: A child measuring 125.5 cm, enter "125.5"

#### Head Circumference (OFC)
- **Units**: Centimeters (cm)
- **Range**: 10 - 100 cm
- **Precision**: One decimal place (e.g., 48.5)
- **Example**: Head circumference of 48.5 cm, enter "48.5"

**Note**:
- BMI automatically calculated if both weight and height provided
- BSA automatically calculated from weight alone (cBNF) or weight + height (Boyd)

### Step 4: Gestational Age (Advanced Mode Only)

For preterm babies only:

#### When to Enter
- Baby born before 37 weeks gestation
- Currently within correction period:
  - 32-36 weeks: Until age 1 year
  - <32 weeks: Until age 2 years

#### How to Enter
- **Weeks**: Enter 22-44
- **Days**: Enter 0-6 (optional)
- **Example**: Baby born at 34 weeks + 3 days
  - Weeks: 34
  - Days: 3

#### What Happens
- System calculates both chronological and corrected age
- Both points plotted on charts
- Corrected age shown as cross (X), chronological as circle
- Dotted line connects the two points

### Step 5: Previous Measurements (Advanced Mode Only)

For height velocity calculation:

#### Previous Height
- **Units**: Centimeters (cm)
- **When**: Previous measurement from at least 4 months ago
- **Example**: Previous height of 120 cm, enter "120"

#### Previous Date
- **Format**: YYYY-MM-DD
- **Requirement**: Must be at least 4 months (122 days) before current measurement date
- **Must be**: After birth date but before current measurement date

**Result**: Annualized height velocity in cm/year

### Step 6: Parental Heights

For mid-parental height prediction:

#### Maternal Height
1. **Choose Units**: Click "cm" or "ft/in" radio button
2. **Enter Height**:
   - If cm: Enter directly (e.g., 165)
   - If ft/in: Enter feet and inches separately (e.g., 5 ft 5 in)

#### Paternal Height
1. **Choose Units**: Click "cm" or "ft/in" radio button (independent of maternal)
2. **Enter Height**:
   - If cm: Enter directly (e.g., 178)
   - If ft/in: Enter feet and inches separately (e.g., 5 ft 10 in)

**Note**:
- Each parent's height can use different units
- Heights automatically converted to cm for calculation
- Switching units clears the input for that parent

### Step 7: Calculate

1. **Click "Calculate" button**
2. **Wait**: Button shows "Calculating..." briefly
3. **Review**: Results appear below the form

**If Errors Occur**:
- Read error message carefully
- Check all required fields are filled
- Verify measurements are within valid ranges
- Ensure dates are logical (birth before measurement)

## Understanding Results

### Age Display

```
5y 3m 12d
(5.28 years)
```

- **Top line**: Calendar age (years, months, days)
- **Bottom line**: Decimal years (used in calculations)

### Measurement Results

Each measurement shows:

```
Weight: 25.5 kg
Centile: 50.2%
SDS: 0.03
```

- **Value**: Measurement with units
- **Centile**: Percentage of population below this value
- **SDS**: Standard deviations from population mean

#### Interpreting Centiles
- **50th centile**: Exactly average
- **75th centile**: Above average (taller/heavier than 75% of peers)
- **25th centile**: Below average (taller/heavier than 25% of peers)
- **98th centile**: Very high (taller/heavier than 98% of peers)
- **2nd centile**: Very low (taller/heavier than 2% of peers)

#### Interpreting SDS
- **0**: Exactly average
- **+1**: One standard deviation above average
- **-1**: One standard deviation below average
- **±2**: Approximately 2nd/98th centile
- **±3**: Approximately 0.1st/99.9th centile

### Validation Warnings

If you see:
```
⚠️ Advisory Warnings:
• Height SDS beyond ±4
```

**What it means**:
- Measurement is extreme but not impossible
- Calculation has proceeded
- You should verify the measurement
- Consider remeasuring to confirm

**Action**: Double-check the measurement before using clinically

### Height Velocity

```
Height Velocity: 6.5 cm/year
```

- Annualized growth rate
- Requires two height measurements
- Minimum 4-month interval
- Typical ranges vary by age and sex

### Body Surface Area

```
Body Surface Area (Boyd): 0.95 m²
```

or

```
Body Surface Area (cBNF): 0.95 m²
```

- **Boyd**: Used when both weight and height available (more accurate)
- **cBNF**: Used when only weight available (estimated)
- Used for drug dosing and GH calculations

### GH Dose Calculator

```
GH Dose Calculator
[−] 0.7 [+] mg/day
= 7.0 mg/m²/week
= 27.5 mcg/kg/day
```

- **Top line**: Daily dose (adjustable with +/− buttons)
- **Middle line**: Weekly dose per square meter BSA
- **Bottom line**: Daily dose per kilogram weight

**To Adjust**:
1. Click [+] to increase dose
2. Click [−] to decrease dose
3. Watch real-time updates of equivalents

### Mid-Parental Height

```
Mid-Parental Height: 172.0 cm
Centile: 45.3%
Target Range: 164.0 - 180.0 cm
```

- **MPH**: Predicted adult height based on parents
- **Centile**: Where MPH falls on growth curve
- **Target Range**: Expected adult height range (±8.5 cm girls, ±10 cm boys)

## Using Growth Charts

### Opening Charts

1. **After calculating**, scroll to results section
2. **Click "Show Growth Charts"** button
3. **Charts section opens** with first available chart

### Chart Layout

- **Title**: Shows measurement type and reference (e.g., "Height (UK-WHO)")
- **Tabs**: Height, Weight, BMI, OFC (enabled/disabled based on data provided)
- **Age Range Selector**: Choose different age ranges
- **Chart**: Centile curves with patient data overlay
- **Close Button**: Returns to results view

### Reading the Chart

#### Centile Lines
- **Solid lines**: Main centiles (2nd, 25th, 50th, 75th, 98th)
- **Dotted lines**: Extreme centiles (0.4th, 9th, 91st, 99.6th)
- **Heavy line**: 50th centile (median)
- **Color**: Blue for boys, pink for girls

#### Patient Points
- **Filled circle**: Current measurement at chronological age
- **Cross (X)**: Corrected age measurement (if gestation correction applied)
- **Orange circle**: Previous measurement (if provided)
- **Dotted line**: Connects chronological and corrected age points

#### Tooltips
Hover over any patient point to see:
- Age (decimal years)
- Measurement value
- Centile percentage
- SDS score

### Age Range Selector

Different ranges available by chart type:

**Height/Weight**:
- 0-2 years (default for children ≤2 years)
- 0-4 years
- 0-18 years
- 8-20 years

**BMI**:
- 0-4 years
- 2-18 years

**OFC**:
- 0-2 years (default)
- 0-18 years

**To Change Range**:
1. Click radio button for desired range
2. Chart automatically reloads

### Mid-Parental Height on Charts

On height charts only (when parental heights provided):

- **Vertical line**: Shows target range
- **Horizontal bar**: Mid-parental height value
- **Color**: Contrasting color (green for boys, magenta for girls)
- **Position**: At age 18 (for 0-18 charts) or age 20 (for 8-20 charts)

### Closing Charts

Click **"Close Charts"** button to return to results view

## Advanced Features

### Basic vs Advanced Mode Toggle

**Location**: Top-right corner next to title

**To Switch**:
1. Click the toggle switch
2. Interface updates immediately
3. Form data preserved during switch

**Basic Mode Shows**:
- Essential inputs only
- UK-WHO reference only
- Core calculations
- Simplified interface

**Advanced Mode Shows**:
- All inputs
- All growth references
- All features
- Full interface

### Form Auto-Save

Your form data is automatically saved as you type:

- **Auto-save**: Triggered after 1 second of inactivity
- **Storage**: Browser localStorage (local only, not sent to server)
- **Restoration**: Form repopulated on page reload
- **Cleared**: Automatically after successful calculation
- **Manual Clear**: Click "Reset" button

**Note**: Data persists even if you close the browser

### Reset Function

**Reset Button**: Clears all form inputs

**What it does**:
- Clears all form fields
- Hides results and charts
- Resets to default state
- Clears saved form data
- Sets measurement date to today

**When to use**:
- Starting new patient calculation
- Clearing incorrect data
- Starting fresh

## Tips and Best Practices

### Measurement Tips

1. **Accuracy is Critical**
   - Use calibrated equipment
   - Take multiple measurements if uncertain
   - Record measurements immediately
   - Check for warnings in results

2. **Units Matter**
   - Weight: Always in kilograms
   - Height: Always in centimeters
   - Double-check unit conversion if needed

3. **Date Precision**
   - Use exact dates when available
   - Measurement date defaults to today
   - Ensure dates are in correct order

### Interpreting Results

1. **Centiles vs SDS**
   - Centiles easier to understand for parents
   - SDS more precise for clinical use
   - Both show the same information differently

2. **Context is Key**
   - Single measurement is a snapshot
   - Trend over time is more important
   - Compare to previous measurements
   - Consider clinical context

3. **Warnings**
   - Take seriously but don't panic
   - Verify measurement first
   - Consider remeasuring
   - Consult clinical guidelines

### Chart Usage

1. **Choose Appropriate Range**
   - Use 0-2 for infants/toddlers
   - Use 0-18 for general assessment
   - Use 8-20 for adolescents

2. **Track Growth Pattern**
   - Look at trajectory, not just position
   - Crossing centiles may indicate issue
   - Consistent tracking along centile is normal

3. **Use Tooltips**
   - Hover for exact values
   - Check both centile and SDS
   - Compare current to previous

### Workflow Efficiency

1. **Use Auto-Save**
   - Don't worry about losing data
   - Refresh safe after 1 second
   - Data persists across sessions

2. **Keyboard Navigation**
   - Tab through fields efficiently
   - Enter submits form
   - Arrow keys in date pickers

3. **Mobile Usage**
   - Install as PWA for app-like experience
   - Works offline after first load
   - Touch-optimized interface

## Troubleshooting

### Common Errors

#### "At least one measurement (weight, height, or OFC) is required"
- **Cause**: No measurements entered
- **Solution**: Enter at least weight, height, or OFC

#### "Birth date must be before measurement date"
- **Cause**: Dates in wrong order
- **Solution**: Check both dates, ensure birth date is earlier

#### "Weight must be between 0.1 and 300 kg"
- **Cause**: Weight outside valid range
- **Solution**: Check units (kg not lbs) and value

#### "Height velocity requires at least 4 months between measurements"
- **Cause**: Previous measurement too recent
- **Solution**: Use measurements from at least 4 months apart

#### "Height SDS (±8.5) exceeds acceptable range"
- **Cause**: Measurement extremely unlikely
- **Solution**: Verify measurement accuracy, check for entry error

### Chart Issues

#### "No chart data available for this combination"
- **Cause**: Reference doesn't support this measurement/sex combination
- **Solution**: Choose different reference or check sex selection

#### Charts Not Loading
- **Cause**: Network issue or browser problem
- **Solution**: Refresh page, check internet connection

#### Tabs Disabled
- **Cause**: Measurements not provided
- **Solution**: Provide required measurements and recalculate

### Performance Issues

#### Slow Calculations
- **Cause**: Server load or network latency
- **Solution**: Wait for loading indicator, try again if timeout

#### Form Not Saving
- **Cause**: Browser localStorage disabled
- **Solution**: Enable cookies/localStorage in browser settings

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation**: Review this guide and [FEATURES.md](FEATURES.md)
2. **Browser Console**: Check for JavaScript errors (F12 → Console)
3. **GitHub Issues**: Report bugs at [Issues](https://github.com/gm5dna/growth-parameters-calculator/issues)
4. **Discussions**: Ask questions at [Discussions](https://github.com/gm5dna/growth-parameters-calculator/discussions)

Remember: This tool is for educational purposes only. Always verify calculations independently before clinical use.
