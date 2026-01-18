# Copy Results Feature - Usage Guide

## Overview

The Copy Results feature allows users to copy calculation results to their clipboard with a single click, formatted for easy pasting into medical records, notes, or sharing with colleagues.

## How to Use

### Basic Usage

1. Complete a calculation (enter patient data and click "Calculate")
2. When results appear, click the **"Copy"** button in the results header
3. A green success toast will appear: "✓ Results copied to clipboard"
4. Paste the results anywhere using Ctrl+V (Windows/Linux) or Cmd+V (Mac)

### Keyboard Shortcut

When results are visible:
- Press **Ctrl+C** (Windows/Linux) or **Cmd+C** (Mac) to copy results
- This only works when no text is selected (to avoid interfering with normal text copying)

## Output Format

Results are copied in a professional clinical format:

```
Growth Parameters - 17/01/2026

Sex: Male
Age: 6y 0m 16d (6.04 years)

DOB: 01/01/2020
Reference: UK-WHO

MEASUREMENTS:
Weight      20 kg          (36.77%, SDS: -0.34)
Height      120 cm         (78.2%, SDS: 0.78)
BMI         13.9 kg/m²     (7.54%, SDS: -1.44)
OFC         51 cm          (7.72%, SDS: -1.42)

Height Velocity:  1.2 cm/year
BSA (Boyd):       0.82 m²
GH Dose:          0.80 mg/day (6.8 mg/m²/week, 40 mcg/kg/day)

Mid-Parental Height: 178 cm (53.4%)
Target Range: 167.9-187.5 cm

WARNINGS:
• Height below 0.4th centile (SDS: -2.7)
```

## What Gets Copied

The copy function includes:
- **Patient Info**: Sex, age, date of birth
- **Reference Dataset**: UK-WHO, Turner, Trisomy 21, or CDC
- **Measurements**: All entered measurements with centiles and SDS values
- **Additional Parameters**:
  - Height velocity (if previous measurement provided)
  - Body Surface Area (Boyd or cBNF method)
  - Growth hormone dose (if calculated)
  - Mid-parental height with target range
- **Warnings**: Any validation warnings or alerts
- **Metadata**: Calculation date and source link

## Mobile Support

The copy feature works on:
- ✅ iOS Safari (iPad/iPhone)
- ✅ Android Chrome
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)

On mobile devices:
- The Copy button appears full-width for easy tapping
- Touch the button to copy
- Use your device's paste function to insert the results

## Browser Compatibility

### Modern Browsers (Recommended)
Uses the Clipboard API for secure, modern clipboard access:
- Chrome 63+
- Firefox 53+
- Safari 13.1+
- Edge 79+

### Older Browsers
Automatically falls back to `document.execCommand('copy')` for compatibility with:
- Internet Explorer 11
- Older versions of Firefox/Chrome

## Troubleshooting

### "Failed to copy results" Error

If you see an error toast, try these solutions:

1. **Check Browser Permissions**
   - Some browsers require clipboard permission
   - Click "Allow" if prompted

2. **HTTPS Required**
   - Modern clipboard API requires HTTPS (secure connection)
   - The app is deployed on HTTPS by default

3. **Manual Copy Fallback**
   - Select all text in the results section
   - Press Ctrl+C or Cmd+C manually
   - Or right-click and choose "Copy"

### Safari Private Browsing

Safari's private browsing mode may block clipboard access:
- Try using regular (non-private) mode
- Or use manual text selection and copy

## Technical Details

### Data Extraction

The copy feature intelligently extracts all visible results from the DOM, including:
- Results that are currently displayed
- Measurements in Basic or Advanced mode
- Optional parameters (only if calculated)

### Format

Results are formatted as:
- **Plain text** - Easy to paste into any application
- **Line-aligned** - Readable structure with proper spacing
- **Professional** - Suitable for medical documentation
- **Complete** - Includes all relevant calculation data

### Privacy

- **No server communication** - Copying happens entirely in your browser
- **Local only** - Results are not sent to any server
- **No storage** - Clipboard data is not permanently stored
- **User-controlled** - You decide when to copy and where to paste

## Future Enhancements

Potential improvements being considered:
- Multiple format options (Compact, Markdown, JSON)
- Format selector dropdown
- Copy individual measurements
- Include chart images
- Custom templates

## Support

For issues or feature requests, please visit:
https://github.com/gm5dna/growth-parameters-calculator/issues

---

**Last Updated:** January 17, 2026
