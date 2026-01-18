# Features Backlog - rcpchgrowth Library Capabilities

This document tracks available features from the rcpchgrowth library that could be implemented in the Growth Parameters Calculator.

**Last Updated:** 2026-01-18

---

## Quick Wins (1-2 hours each) ⚡

### 1. Percentage Median BMI ⭐⭐⭐
**Status:** ✅ COMPLETED (2026-01-18)
**Priority:** HIGH
**Clinical Value:** Critical for malnutrition assessment

Shows BMI as percentage of median (e.g., "85% of median BMI"). More intuitive than centiles for nutritional assessment.

```python
rcpchgrowth.percentage_median_bmi(reference, age, actual_bmi, sex)
```

**Implementation:**
- ✅ Added to BMI result card (advanced mode only)
- ✅ Displayed alongside existing centile/SDS
- ✅ Clinical interpretation documented in code comments
- ✅ Comprehensive test suite (9 tests)
- ✅ Works with all references (UK-WHO, CDC, Turner, Trisomy-21)

**Clinical Interpretation Ranges:**
- <70% = Severe malnutrition
- 70-80% = Moderate malnutrition
- 80-90% = Mild malnutrition
- 90-110% = Normal nutritional status
- >120% = Overweight/obesity

**Files Modified:**
- `utils.py` - Added `calculate_percentage_median_bmi()`
- `app.py` - Calculate and return percentage median BMI
- `templates/index.html` - Added display element (advanced-only)
- `static/script.js` - Populate percentage median value
- `tests/test_percentage_median_bmi.py` - Comprehensive test coverage

---

### 2. CDC Reference Support ⭐⭐⭐
**Status:** 🔴 Not Started
**Priority:** HIGH
**Clinical Value:** US market expansion, extended BMI for obesity

Enable CDC reference that's already in the UI dropdown. Includes extended BMI calculations for severe obesity (>95th centile).

**Implementation:**
- Already in dropdown, just needs backend support
- Test with rcpchgrowth CDC reference
- Add CDC-specific centile formats (85th centile option)
- Document differences vs UK-WHO

---

### 3. Centile Band Interpretation ⭐⭐
**Status:** 🔴 Not Started
**Priority:** MEDIUM
**Clinical Value:** Better clinical communication

Returns interpretive text like "between 25th-50th centile" instead of exact "37th centile".

```python
rcpchgrowth.centile_band_for_centile(centile)
```

**Implementation:**
- Add below centile numbers in results
- Apply to all measurements (height, weight, BMI, OFC)
- Optional user preference to show/hide exact centiles

---

### 4. Weight Target Calculator ⭐⭐
**Status:** 🔴 Not Started
**Priority:** MEDIUM
**Clinical Value:** Weight management goals

Calculate target weight for desired BMI centile.

```python
rcpchgrowth.weight_for_bmi_height(height, bmi)
```

**Implementation:**
- Add interactive widget to BMI card
- "Weight for 50th centile BMI: X.X kg"
- Allow user to select target centile (25th, 50th, 75th)
- Show weight difference from current

---

### 5. Library Age Functions ⭐
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** Code quality, standardization

Replace custom age calculations with library functions:
- `corrected_gestational_age()` - formatted string output
- `estimated_date_delivery()` - calculate EDD from birth + gestation
- `comment_prematurity_correction()` - explanatory text for users
- `chronological_calendar_age()` - formatted age with context

**Implementation:**
- Refactor calculations.py
- Use library functions for consistency
- Add EDD display for preterm babies
- Add correction explanation text

---

## Major Features (8+ hours each) 🚀

### 6. Bone Age Assessment 🩻
**Status:** 🔴 Not Started
**Priority:** HIGH
**Clinical Value:** Significant clinical diagnostic tool

Complete bone age system with predicted adult height.

**Available Methods:**
- Greulich-Pyle (most common)
- Tanner-Whitehouse II/III
- Fels
- BoneXpert (automated)

**Height Prediction Methods:**
- Bayley-Pinneau
- Roche-Wainer-Thissen

**Implementation:**
- Add bone age input field (years)
- Add method selection dropdown
- Calculate bone age centile/SDS
- Add predicted adult height calculation
- Display in advanced mode results section
- Add to PDF export

**UI Changes:**
- New form section: "Bone Age Assessment (Optional)"
- New result card: "Bone Age" with centile/SDS
- New result card: "Predicted Adult Height" with method

---

### 7. Serial Measurements & Trajectory Tracking 📈
**Status:** 🔴 Not Started (Experimental feature)
**Priority:** HIGH
**Clinical Value:** Growth monitoring over time

Track multiple measurements, calculate velocity/acceleration, visualize trends.

**Available Functions:**
```python
rcpchgrowth.dynamic_growth.velocity(measurements_list)
rcpchgrowth.dynamic_growth.acceleration(measurements_list)
rcpchgrowth.dynamic_growth.conditional_weight_gain(measurements_list)
```

**Implementation:**
- Add local storage/session for measurement history
- "Save measurement" button
- History view with measurement list
- Delete/edit measurements
- Chart overlay showing all historical points
- Velocity calculations using library functions
- Acceleration detection (requires ≥3 measurements)
- Export history to CSV/JSON

**Note:** These functions are marked experimental in rcpchgrowth. Requires thorough testing.

---

### 8. Thrive Lines 📉
**Status:** 🔴 Not Started (Experimental feature)
**Priority:** MEDIUM
**Clinical Value:** Failure to thrive monitoring

Generate expected growth trajectories from current measurement.

```python
rcpchgrowth.create_thrive_lines()
```

**Implementation:**
- Add thrive line toggle to charts
- Display expected trajectory as dashed line
- Show deviation from expected path
- Requires serial measurements feature

**Note:** Experimental - needs clinical validation before use.

---

## Additional References 🌍

### 9. Trisomy-21-AAP Reference
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** US Down syndrome population

American Academy of Pediatrics 2015 updated charts for Down syndrome.

**Implementation:**
- Add to reference dropdown
- Test with rcpchgrowth 'trisomy-21-aap' reference
- Document differences vs UK Trisomy-21 charts
- Provide guidance on which to use

---

### 10. Standalone WHO Reference
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** International users

WHO reference without UK90 components.

**Implementation:**
- Add 'who' to reference dropdown
- Document age ranges (0-5 years)
- Clarify difference from 'uk-who'

---

### 11. UK-WHO Sub-references
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** Advanced users, research

Expose individual components of UK-WHO composite reference:
- `uk90_preterm`
- `uk_who_infant`
- `uk_who_child`
- `uk90_child`

**Implementation:**
- Advanced mode dropdown option
- Documentation on when each applies
- Chart selection logic

---

## User Experience Enhancements 🎨

### 12. Event Annotations
**Status:** 🔴 Not Started
**Priority:** MEDIUM
**Clinical Value:** Clinical context for measurements

Tag measurements with clinical events (GH start, surgery, puberty, etc.)

**Implementation:**
- Event input field in form
- Pass to rcpchgrowth via `events_text` parameter
- Display events on charts as markers
- Show in PDF reports
- Event history in serial measurements

**Use Cases:**
- "Growth hormone therapy started"
- "Thyroid treatment commenced"
- "Surgery"
- "Puberty onset"

---

### 13. Alternative Centile Formats
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** User preference, regional differences

User-selectable centile display formats:
- **Cole nine-centiles** (current): 0.4, 2, 9, 25, 50, 75, 91, 98, 99.6
- **Three-percent**: 3, 10, 25, 50, 75, 90, 97
- **Five-percent**: 5, 10, 25, 50, 75, 90, 95
- **Eighty-five-percent**: For CDC extended BMI
- **Extended-WHO**: WHO-specific format

**Implementation:**
- Settings panel
- Save preference to localStorage
- Update chart display
- Update result displays

---

### 14. Demo Mode 🎭
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** Testing, training, demonstrations

Generate synthetic patient data for demos and testing.

```python
rcpchgrowth.generate_fictional_child_data()
```

**Implementation:**
- "Load Demo Data" button
- Generate realistic measurement series
- Configurable parameters (age range, SDS drift, noise)
- Useful for screenshots, videos, training
- Multiple demo scenarios (normal, FTT, catch-up growth)

---

## Advanced Calculations 🧮

### 15. Expected Height from MPH
**Status:** 🔴 Not Started
**Priority:** MEDIUM
**Clinical Value:** Enhanced MPH interpretation

Compare child's actual height SDS to expected SDS from mid-parental height.

```python
rcpchgrowth.expected_height_z_from_mid_parental_height_z()
```

**Implementation:**
- Add to MPH result card
- Show expected vs actual comparison
- Indicate if within expected range
- Clinical interpretation text

---

### 16. SDS/Centile Conversion Tools
**Status:** 🔴 Not Started
**Priority:** LOW
**Clinical Value:** Educational, research

Bidirectional SDS ↔ centile conversion tools.

```python
rcpchgrowth.sds_for_centile(centile)
rcpchgrowth.rounded_sds_for_centile(centile)
```

**Implementation:**
- Utility panel or separate page
- Input centile → get SDS
- Input SDS → get centile
- Educational tool for clinicians

---

## Implementation Priority Matrix

### Completed ✅
1. Percentage Median BMI (2026-01-18)

### Immediate (Next Sprint)
2. CDC Reference Support
3. Weight Target Calculator
4. Centile Band Interpretation

### Short Term (1-2 months)
5. Bone Age Assessment
6. Event Annotations
7. Library Age Functions

### Medium Term (3-6 months)
7. Serial Measurements & Trajectory Tracking
8. Expected Height from MPH
9. Library Age Functions

### Long Term (6+ months)
10. Thrive Lines (experimental - needs validation)
11. Alternative Centile Formats
12. Additional References (AAP, WHO standalone)

### Nice to Have (As Time Permits)
13. Demo Mode
14. SDS/Centile Conversion Tools
15. UK-WHO Sub-references

---

## Clinical Value Legend

⭐⭐⭐ = Critical clinical feature, widely used
⭐⭐ = Valuable clinical feature, good utility
⭐ = Nice to have, niche use case

---

## Feature Status

- ✅ Completed
- 🟢 In Progress
- 🟡 Planned
- 🔴 Not Started
- ⚠️ Experimental (needs validation)

---

## Notes

**Experimental Features:**
Thrive lines, velocity/acceleration functions are marked experimental in rcpchgrowth. Require thorough clinical validation before production use.

**Testing Requirements:**
All new features must include:
- Unit tests in tests/
- Manual testing with edge cases
- Documentation in docs/
- Update to CLAUDE.md

**Clinical Safety:**
Features that affect clinical decisions must include:
- Appropriate disclaimers
- Reference to validation studies
- Clear limitations

---

## References

- [RCPCH Digital Growth Charts - Python Library](https://growth.rcpch.ac.uk/products/python-library/)
- [rcpchgrowth GitHub Repository](https://github.com/rcpch/rcpchgrowth-python)
- [Clinical Reference Documentation](https://growth.rcpch.ac.uk/clinician/growth-references/)
