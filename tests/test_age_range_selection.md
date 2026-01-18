# Age Range Selection Logic - Test Cases

This document describes the test scenarios for the intelligent age range selection feature.

## Logic Overview

The system automatically selects the most appropriate age range for growth charts based on:
1. The child's age
2. Available measurements (particularly mid-parental height for height charts)

## Test Scenarios

### Height Charts

| Age | Has MPH | Expected Range | Rationale |
|-----|---------|---------------|-----------|
| 0.5y | No | 0-2 years | Infant - detailed view most relevant |
| 1.5y | Yes | 0-2 years | Infant - detailed view regardless of MPH |
| 2.5y | No | 0-4 years | Toddler - shows growth from birth |
| 3.5y | Yes | 0-4 years | Toddler - shows growth trajectory |
| 5y | No | 0-18 years | Child - full context without MPH |
| 5y | Yes | 2-18 years | Child - focused range with MPH prediction |
| 10y | No | 0-18 years | Older child - full range without MPH |
| 10y | Yes | 2-18 years | Older child - clinical range with MPH |

### Weight Charts

| Age | Expected Range | Rationale |
|-----|---------------|-----------|
| 0.5y | 0-2 years | Infant - most detailed view |
| 1.5y | 0-2 years | Infant - detailed monitoring |
| 2.5y | 0-4 years | Toddler - transition period |
| 3.5y | 0-4 years | Toddler - shows pattern from birth |
| 5y | 0-18 years | Child - full range for context |
| 10y | 0-18 years | Older child - full growth pattern |

### BMI Charts

| Age | Expected Range | Rationale |
|-----|---------------|-----------|
| 1y | 0-4 years | Infant - BMI less meaningful but shows pattern |
| 2.5y | 0-4 years | Toddler - early BMI tracking |
| 5y | 2-18 years | Child - most clinically relevant (default) |
| 8y | 2-18 years | Older child - standard clinical range |
| 12y | 0-18 years | Adolescent - full pattern for puberty context |
| 16y | 0-18 years | Adolescent - comprehensive view |

### OFC Charts

| Age | Expected Range | Rationale |
|-----|---------------|-----------|
| 0.5y | 0-2 years | Infant - most detailed and relevant |
| 1.5y | 0-2 years | Infant - primary age for OFC monitoring |
| 2.5y | 0-18 years | Toddler - if still measuring, show full context |
| 5y | 0-18 years | Child - uncommon but show full range |

## Manual Testing Procedure

### Test 1: Infant with All Measurements

**Input:**
- Age: 6 months
- Weight: 8 kg
- Height: 68 cm
- OFC: 43 cm

**Expected Behavior:**
1. Click "Show Charts"
2. Height chart should default to **0-2 years**
3. Switch to Weight tab → should show **0-2 years**
4. Switch to BMI tab → should show **0-4 years**
5. Switch to OFC tab → should show **0-2 years**

### Test 2: Toddler (Age 3)

**Input:**
- Age: 3 years
- Weight: 14 kg
- Height: 95 cm

**Expected Behavior:**
1. Height chart → **0-4 years**
2. Weight chart → **0-4 years**
3. BMI chart → **0-4 years**

### Test 3: School Age Child with MPH (Age 7)

**Input:**
- Age: 7 years
- Weight: 24 kg
- Height: 122 cm
- Maternal height: 165 cm
- Paternal height: 178 cm

**Expected Behavior:**
1. Height chart → **2-18 years** (because MPH available)
2. Weight chart → **0-18 years**
3. BMI chart → **2-18 years**
4. MPH line should be visible on height chart

### Test 4: School Age Child without MPH (Age 7)

**Input:**
- Age: 7 years
- Weight: 24 kg
- Height: 122 cm
- No parental heights

**Expected Behavior:**
1. Height chart → **0-18 years** (no MPH, show full range)
2. Weight chart → **0-18 years**
3. BMI chart → **2-18 years**

### Test 5: Adolescent (Age 14)

**Input:**
- Age: 14 years
- Weight: 52 kg
- Height: 162 cm

**Expected Behavior:**
1. Height chart → **0-18 years** (or 2-18 if MPH available)
2. Weight chart → **0-18 years**
3. BMI chart → **0-18 years** (shows puberty context)

### Test 6: Preterm Infant (Corrected Age 3 months)

**Input:**
- Birth date: 6 months ago
- Gestation: 30 weeks
- Corrected age: ~3 months
- Measurements at corrected age

**Expected Behavior:**
1. Uses corrected age for range selection
2. All charts → **0-2 years**

## Edge Cases

### No Age Data
- **Behavior:** Fallback to first available age range option
- **Reason:** Cannot auto-select without age information

### Invalid Age Range
- **Behavior:** Fallback to first available option for that measurement
- **Reason:** Graceful degradation if calculated range doesn't exist

### User Manual Override
- **Behavior:** User can always manually select different age range
- **Reason:** Clinical judgment may require different view
- **Persistence:** Manual selection persists until chart refresh

## Implementation Notes

### selectOptimalAgeRange() Function

**Location:** `static/script.js`

**Parameters:**
- `measurement` (string): 'height', 'weight', 'bmi', or 'ofc'

**Returns:**
- (string): Age range value like '0-2', '2-18', etc.

**Data Dependencies:**
- `calculationResults.age_years`: Decimal age of child
- `calculationResults.mid_parental_height`: Presence indicates MPH available

### When Selection Occurs

1. **Initial chart load:** When "Show Charts" button clicked
2. **Tab switching:** When user clicks different chart tab
3. **NOT on manual selection:** User manual changes are respected

## Browser Compatibility

The logic uses:
- Optional chaining (`?.`) - requires modern browsers
- Arrow functions - ES6+
- QuerySelector API - widely supported

Tested on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- iOS Safari (13+)

## Accessibility

- Radio buttons remain keyboard navigable
- Screen readers announce selected age range
- Visual indication of selected range
- Manual override always available
