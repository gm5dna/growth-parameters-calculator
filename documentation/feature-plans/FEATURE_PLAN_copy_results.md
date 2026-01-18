# Feature Plan: Copy Results to Clipboard

**Feature ID:** #5
**Priority:** High (Top 5)
**Estimated Effort:** 4-6 hours
**Status:** Planning

## Overview

Add a "Copy Results" button that copies calculation results to the clipboard in a formatted, EMR-ready format. This enables clinicians to quickly paste results into electronic medical records, notes, or share with colleagues.

## User Stories

1. **As a clinician**, I want to copy results with one click so I can paste them into my EMR system
2. **As a user**, I want results formatted professionally for clinical documentation
3. **As a user**, I want visual confirmation that copying succeeded
4. **As a mobile user**, I want clipboard copying to work on iOS/Android
5. **As a user**, I want to choose between different copy formats (plain text, markdown, structured)

## Requirements

### Functional Requirements
- [x] Copy button visible when results are displayed
- [x] Copy all visible results (age, measurements, centiles, SDS, MPH, etc.)
- [x] Format results for clinical documentation (professional, scannable)
- [x] Toast/snackbar notification on successful copy
- [x] Error handling if clipboard access fails
- [x] Support multiple output formats (selectable)
- [x] Include calculation metadata (date, reference, mode)
- [x] Omit empty/null results gracefully
- [x] Keyboard shortcut (Ctrl+C / Cmd+C when results visible)

### Non-Functional Requirements
- [x] Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- [x] Mobile support (iOS Safari, Android Chrome)
- [x] Clipboard API with fallback for older browsers
- [x] Copy operation completes in <100ms
- [x] Accessible (screen reader friendly, keyboard accessible)
- [x] No external dependencies

## Design

### Copy Formats

#### Option 1: Clinical Plain Text (Default, Recommended)
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

Height Velocity:  1.2 cm/year (interval: 6 months)
BSA (Boyd):       0.82 m²
GH Dose:          0.80 mg/day (6.8 mg/m²/week, 40 mcg/kg/day)

Mid-Parental Height: 178 cm (53.4%)
Target Range: 167.9-187.5 cm

WARNINGS:
• Height velocity below expected for age
```

#### Option 2: Compact Format
```
Male 3.0y | W: 15kg (50%ile) H: 90cm (25%ile) BMI: 18.5 (75%ile) | MPH: 175cm (50%ile) | UK-WHO | 17/01/26
```

#### Option 3: Markdown (for documentation)
```markdown
## Growth Parameters Assessment

**Date:** 17/01/2026
**Patient:** Male, 3.0 years (DOB: 01/01/2020)
**Reference:** UK-WHO

### Measurements

| Parameter | Value | Centile | SDS |
|-----------|-------|---------|-----|
| Weight | 15.0 kg | 50th | 0.0 |
| Height | 90.0 cm | 25th | -0.67 |
| BMI | 18.5 kg/m² | 75th | +0.67 |

### Additional Parameters

- **Height Velocity:** 6.5 cm/year
- **BSA (Boyd):** 0.63 m²
- **Mid-Parental Height:** 175 cm (50th centile, range: 168-182 cm)
```

#### Option 4: Structured JSON (for integration)
```json
{
  "date": "2026-01-17",
  "patient": {
    "sex": "male",
    "ageYears": 3.0,
    "dateOfBirth": "2020-01-01"
  },
  "reference": "uk-who",
  "measurements": {
    "weight": {"value": 15.0, "unit": "kg", "centile": 50, "sds": 0.0},
    "height": {"value": 90.0, "unit": "cm", "centile": 25, "sds": -0.67},
    "bmi": {"value": 18.5, "unit": "kg/m²", "centile": 75, "sds": 0.67}
  },
  "additional": {
    "heightVelocity": {"value": 6.5, "unit": "cm/year"},
    "bsa": {"value": 0.63, "unit": "m²", "method": "Boyd"},
    "midParentalHeight": {"value": 175, "unit": "cm", "centile": 50}
  }
}
```

### Recommended Approach

**Primary (Default):** Clinical Plain Text (Option 1)
- Most universally useful
- EMR-ready format
- Professional appearance
- Easy to read/scan

**Alternative Formats:** Add dropdown menu for power users
- Format selector next to copy button
- Saves preference to localStorage
- Options: Plain Text, Compact, Markdown, JSON

### UI Design

#### Copy Button Placement

**Option A: In Results Header (Recommended)**
```
┌─────────────────────────────────────────┐
│ Results               [Copy] [📋▼]      │
├─────────────────────────────────────────┤
│ Reference: UK-WHO                        │
│ ...                                      │
```

**Option B: Floating Action Button**
- Fixed bottom-right corner
- Always visible when results shown
- Better for long result sets

**Recommended:** Start with **Option A** (cleaner, less intrusive)

#### Toast Notification

```
╔═══════════════════════════════╗
║ ✓ Results copied to clipboard ║
╚═══════════════════════════════╝
```

- Appears at top-center
- Auto-dismisses after 3 seconds
- Slide-in animation
- Green background (#4CAF50)
- White text

## Implementation Plan

### Phase 1: Core Clipboard Functionality (1-2 hours)

**Create new file: `static/clipboard.js`**

```javascript
/**
 * Clipboard Manager for Growth Calculator
 * Handles copying results in multiple formats
 */

class ClipboardManager {
  constructor() {
    this.formats = {
      'plain': this.formatPlainText.bind(this),
      'compact': this.formatCompact.bind(this),
      'markdown': this.formatMarkdown.bind(this),
      'json': this.formatJSON.bind(this)
    };

    this.currentFormat = localStorage.getItem('copyFormat') || 'plain';
  }

  /**
   * Main copy function - handles browser compatibility
   */
  async copy(data, format = this.currentFormat) {
    try {
      const text = this.formats[format](data);

      // Modern Clipboard API (preferred)
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return { success: true, text };
      }

      // Fallback for older browsers
      return this.fallbackCopy(text);

    } catch (error) {
      console.error('Copy failed:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Fallback copy method using execCommand
   */
  fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return { success, text };
    } catch (error) {
      document.body.removeChild(textarea);
      return { success: false, error: error.message };
    }
  }

  /**
   * Format: Clinical Plain Text
   */
  formatPlainText(data) {
    const lines = [];
    const today = new Date().toLocaleDateString('en-GB');

    // Header
    lines.push('Growth Parameters - ' + today);
    lines.push('');

    // Patient info
    lines.push(`Patient: ${this.capitalize(data.sex)}, ${data.age}`);
    if (data.dateOfBirth) {
      lines.push(`DOB: ${this.formatDate(data.dateOfBirth)}`);
    }
    lines.push(`Reference: ${this.formatReference(data.reference)}`);
    lines.push('');

    // Measurements
    lines.push('MEASUREMENTS:');

    if (data.weight) {
      lines.push(this.formatMeasurement('Weight', data.weight.value, 'kg',
                                        data.weight.centile, data.weight.sds));
    }

    if (data.height) {
      lines.push(this.formatMeasurement('Height', data.height.value, 'cm',
                                        data.height.centile, data.height.sds));
    }

    if (data.bmi) {
      lines.push(this.formatMeasurement('BMI', data.bmi.value, 'kg/m²',
                                        data.bmi.centile, data.bmi.sds));
    }

    if (data.ofc) {
      lines.push(this.formatMeasurement('OFC', data.ofc.value, 'cm',
                                        data.ofc.centile, data.ofc.sds));
    } else {
      lines.push('OFC:        Not measured');
    }

    // Additional parameters
    if (data.heightVelocity || data.bsa || data.mph) {
      lines.push('');
      lines.push('ADDITIONAL:');

      if (data.heightVelocity) {
        lines.push(`Height Velocity:  ${data.heightVelocity.value} cm/year`);
        if (data.heightVelocity.interval) {
          lines.push(`  (interval: ${data.heightVelocity.interval})`);
        }
      }

      if (data.bsa) {
        lines.push(`BSA (${data.bsa.method}):  ${data.bsa.value} m²`);
      }

      if (data.ghDose) {
        lines.push(`GH Dose:  ${data.ghDose.mgPerDay} mg/day`);
        lines.push(`  (${data.ghDose.mgM2Week} mg/m²/week, ${data.ghDose.mcgKgDay} mcg/kg/day)`);
      }

      if (data.mph) {
        lines.push(`Mid-Parental Height: ${data.mph.value} cm (${data.mph.centile})`);
        lines.push(`  Target Range: ${data.mph.rangeMin}-${data.mph.rangeMax} cm`);
      }
    }

    // Warnings
    if (data.warnings && data.warnings.length > 0) {
      lines.push('');
      lines.push('WARNINGS:');
      data.warnings.forEach(warning => {
        lines.push(`• ${warning}`);
      });
    }

    // Footer
    lines.push('');
    lines.push('---');
    lines.push('Generated by Growth Parameters Calculator');
    lines.push('https://growth-parameters-calculator.onrender.com');

    return lines.join('\n');
  }

  /**
   * Format: Compact one-liner
   */
  formatCompact(data) {
    const parts = [];
    const date = new Date().toLocaleDateString('en-GB').slice(0, 8); // DD/MM/YY

    parts.push(`${this.capitalize(data.sex)} ${data.age}`);

    if (data.weight) {
      parts.push(`W: ${data.weight.value}kg (${data.weight.centile}%ile)`);
    }

    if (data.height) {
      parts.push(`H: ${data.height.value}cm (${data.height.centile}%ile)`);
    }

    if (data.bmi) {
      parts.push(`BMI: ${data.bmi.value} (${data.bmi.centile}%ile)`);
    }

    if (data.mph) {
      parts.push(`MPH: ${data.mph.value}cm (${data.mph.centile})`);
    }

    parts.push(this.formatReference(data.reference));
    parts.push(date);

    return parts.join(' | ');
  }

  /**
   * Format: Markdown
   */
  formatMarkdown(data) {
    const lines = [];
    const today = new Date().toLocaleDateString('en-GB');

    lines.push('## Growth Parameters Assessment');
    lines.push('');
    lines.push(`**Date:** ${today}  `);
    lines.push(`**Patient:** ${this.capitalize(data.sex)}, ${data.age}  `);
    lines.push(`**Reference:** ${this.formatReference(data.reference)}`);
    lines.push('');

    // Table
    lines.push('### Measurements');
    lines.push('');
    lines.push('| Parameter | Value | Centile | SDS |');
    lines.push('|-----------|-------|---------|-----|');

    if (data.weight) {
      lines.push(`| Weight | ${data.weight.value} kg | ${data.weight.centile} | ${data.weight.sds} |`);
    }

    if (data.height) {
      lines.push(`| Height | ${data.height.value} cm | ${data.height.centile} | ${data.height.sds} |`);
    }

    if (data.bmi) {
      lines.push(`| BMI | ${data.bmi.value} kg/m² | ${data.bmi.centile} | ${data.bmi.sds} |`);
    }

    if (data.ofc) {
      lines.push(`| OFC | ${data.ofc.value} cm | ${data.ofc.centile} | ${data.ofc.sds} |`);
    }

    // Additional
    if (data.heightVelocity || data.bsa || data.mph) {
      lines.push('');
      lines.push('### Additional Parameters');
      lines.push('');

      if (data.heightVelocity) {
        lines.push(`- **Height Velocity:** ${data.heightVelocity.value} cm/year`);
      }

      if (data.bsa) {
        lines.push(`- **BSA (${data.bsa.method}):** ${data.bsa.value} m²`);
      }

      if (data.mph) {
        lines.push(`- **Mid-Parental Height:** ${data.mph.value} cm (${data.mph.centile}, range: ${data.mph.rangeMin}-${data.mph.rangeMax} cm)`);
      }
    }

    return lines.join('\n');
  }

  /**
   * Format: JSON
   */
  formatJSON(data) {
    return JSON.stringify(data, null, 2);
  }

  // Helper methods
  formatMeasurement(label, value, unit, centile, sds) {
    const paddedLabel = label.padEnd(12);
    const valueStr = `${value} ${unit}`.padEnd(15);
    const centileStr = centile ? `(${centile}, SDS: ${sds})` : '';
    return `${paddedLabel}${valueStr}${centileStr}`;
  }

  formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-GB');
  }

  formatReference(ref) {
    const refs = {
      'uk-who': 'UK-WHO',
      'turners-syndrome': 'Turner Syndrome',
      'trisomy-21': 'Trisomy 21',
      'cdc': 'CDC (US)'
    };
    return refs[ref] || ref;
  }

  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  setFormat(format) {
    if (this.formats[format]) {
      this.currentFormat = format;
      localStorage.setItem('copyFormat', format);
    }
  }

  getFormat() {
    return this.currentFormat;
  }
}

// Export singleton instance
const clipboardManager = new ClipboardManager();
```

### Phase 2: UI Components (1-2 hours)

**HTML Changes (templates/index.html):**

```html
<!-- In results section header -->
<div class="results-header">
  <h2>Results</h2>
  <div class="results-actions">
    <button id="copyResultsBtn" class="btn-copy" title="Copy results to clipboard" aria-label="Copy results to clipboard">
      <span class="icon">📋</span>
      <span class="text">Copy</span>
    </button>

    <!-- Optional: Format selector dropdown -->
    <div class="copy-format-selector" style="display: none;">
      <select id="copyFormat" aria-label="Copy format">
        <option value="plain" selected>Plain Text</option>
        <option value="compact">Compact</option>
        <option value="markdown">Markdown</option>
        <option value="json">JSON</option>
      </select>
    </div>
  </div>
</div>

<!-- Toast notification -->
<div id="copyToast" class="toast" role="status" aria-live="polite" aria-atomic="true">
  <span class="toast-icon">✓</span>
  <span class="toast-message">Results copied to clipboard</span>
</div>
```

**CSS (static/style.css):**

```css
/* Results header with actions */
.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.results-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

/* Copy button */
.btn-copy {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-copy:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-copy:active {
    transform: translateY(0);
}

.btn-copy .icon {
    font-size: 16px;
}

/* Format selector */
.copy-format-selector select {
    padding: 8px 12px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 13px;
    background: white;
    cursor: pointer;
}

/* Toast notification */
.toast {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(-100px);
    background: #4CAF50;
    color: white;
    padding: 14px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 500;
    z-index: 2000;
    opacity: 0;
    transition: all 0.3s ease;
}

.toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}

.toast-icon {
    font-size: 18px;
    font-weight: bold;
}

/* Error toast variant */
.toast.error {
    background: #f44336;
}

/* Mobile responsive */
@media (max-width: 600px) {
    .results-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .results-actions {
        width: 100%;
        flex-direction: column;
    }

    .btn-copy {
        width: 100%;
        justify-content: center;
    }
}
```

### Phase 3: Integration (1-2 hours)

**JavaScript Integration (static/script.js):**

```javascript
// Copy button event listener
document.getElementById('copyResultsBtn')?.addEventListener('click', async () => {
  const data = extractResultsData();
  const format = document.getElementById('copyFormat')?.value || 'plain';

  const result = await clipboardManager.copy(data, format);

  if (result.success) {
    showToast('Results copied to clipboard', 'success');

    // Analytics (if implemented)
    trackEvent('copy_results', { format });
  } else {
    showToast('Failed to copy results', 'error');
    console.error('Copy failed:', result.error);
  }
});

// Format selector
document.getElementById('copyFormat')?.addEventListener('change', (e) => {
  clipboardManager.setFormat(e.target.value);
});

// Keyboard shortcut: Ctrl/Cmd + C
document.addEventListener('keydown', (e) => {
  // Only trigger if results are visible and Ctrl/Cmd+C
  if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
    const resultsVisible = document.getElementById('results').classList.contains('show');
    const noTextSelected = window.getSelection().toString().length === 0;

    if (resultsVisible && noTextSelected) {
      e.preventDefault();
      document.getElementById('copyResultsBtn').click();
    }
  }
});

/**
 * Extract all results data from DOM
 */
function extractResultsData() {
  return {
    sex: document.querySelector('input[name="sex"]:checked')?.value,
    age: document.getElementById('age')?.textContent,
    dateOfBirth: document.getElementById('birth_date')?.value,
    measurementDate: document.getElementById('measurement_date')?.value,
    reference: document.getElementById('reference')?.value,

    weight: extractMeasurement('weight'),
    height: extractMeasurement('height'),
    bmi: extractMeasurement('bmi'),
    ofc: extractMeasurement('ofc'),

    heightVelocity: extractHeightVelocity(),
    bsa: extractBSA(),
    ghDose: extractGHDose(),
    mph: extractMPH(),

    warnings: extractWarnings()
  };
}

function extractMeasurement(type) {
  const valueEl = document.getElementById(`${type}-value`);
  if (!valueEl || !valueEl.textContent) return null;

  return {
    value: parseFloat(valueEl.textContent),
    centile: document.getElementById(`${type}-centile`)?.textContent,
    sds: document.getElementById(`${type}-sds`)?.textContent
  };
}

function extractHeightVelocity() {
  const el = document.getElementById('height-velocity');
  if (!el || !el.textContent) return null;

  return {
    value: parseFloat(el.textContent),
    interval: document.getElementById('height-velocity-message')?.textContent
  };
}

function extractBSA() {
  const el = document.getElementById('bsa');
  if (!el || !el.textContent) return null;

  return {
    value: parseFloat(el.textContent),
    method: document.getElementById('bsa-label')?.textContent.includes('cBNF') ? 'cBNF' : 'Boyd'
  };
}

function extractGHDose() {
  const el = document.getElementById('gh-dose-input');
  if (!el || !el.value || parseFloat(el.value) === 0) return null;

  return {
    mgPerDay: el.value,
    mgM2Week: document.getElementById('gh-dose-mg-m2-week')?.textContent,
    mcgKgDay: document.getElementById('gh-dose-mcg-kg-day')?.textContent
  };
}

function extractMPH() {
  const el = document.getElementById('mph-value');
  if (!el || !el.textContent) return null;

  const rangeText = document.getElementById('mph-range')?.textContent || '';
  const [rangeMin, rangeMax] = rangeText.split('-').map(s => parseFloat(s));

  return {
    value: parseFloat(el.textContent),
    centile: document.getElementById('mph-centile')?.textContent,
    rangeMin,
    rangeMax
  };
}

function extractWarnings() {
  const warningsEl = document.getElementById('validation-warnings');
  if (!warningsEl || !warningsEl.classList.contains('show')) return [];

  const warnings = [];
  warningsEl.querySelectorAll('li').forEach(li => {
    warnings.push(li.textContent.trim());
  });
  return warnings;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
  const toast = document.getElementById('copyToast');
  const messageEl = toast.querySelector('.toast-message');

  messageEl.textContent = message;
  toast.classList.remove('success', 'error');
  toast.classList.add(type);
  toast.classList.add('show');

  // Auto-hide after 3 seconds
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}
```

### Phase 4: Testing (1 hour)

**Manual Testing Checklist:**
- [ ] Copy button appears when results displayed
- [ ] Copy button hidden when no results
- [ ] Click copy button → toast notification appears
- [ ] Toast auto-dismisses after 3 seconds
- [ ] Clipboard contains formatted results
- [ ] Paste into text editor shows proper formatting
- [ ] All measurements included (weight, height, BMI, OFC)
- [ ] Additional params included (BSA, MPH, HV, GH dose)
- [ ] Warnings included if present
- [ ] Optional fields handled gracefully (missing OFC, etc.)
- [ ] Keyboard shortcut (Ctrl/Cmd+C) works when results visible
- [ ] Keyboard shortcut doesn't interfere with text selection
- [ ] Format selector changes output format
- [ ] Selected format persists after page reload
- [ ] Works on Chrome, Firefox, Safari, Edge
- [ ] Works on mobile iOS Safari
- [ ] Works on mobile Android Chrome
- [ ] Fallback works on older browsers
- [ ] Error toast shows if copy fails
- [ ] Mobile responsive (button full-width on small screens)

**Browser Compatibility Testing:**
```javascript
// Test script for various browsers
async function testClipboard() {
  console.log('Testing clipboard functionality...');

  // Test modern API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    console.log('✓ Modern Clipboard API available');
  } else {
    console.log('⚠ Falling back to execCommand');
  }

  // Test copy
  const testData = {
    sex: 'male',
    age: '3.0 years',
    weight: { value: 15, centile: '50th', sds: '0.0' }
  };

  const result = await clipboardManager.copy(testData);

  if (result.success) {
    console.log('✓ Copy successful');
    console.log('Copied text:', result.text);
  } else {
    console.log('✗ Copy failed:', result.error);
  }
}
```

## Edge Cases & Error Handling

1. **Clipboard API Not Available**
   - Fall back to execCommand
   - Show warning if both fail
   - Provide manual copy option (select + Ctrl+C)

2. **Partial Results**
   - Handle missing measurements gracefully
   - Skip null/undefined values
   - Don't show "undefined" in output

3. **Permissions Denied**
   - Safari sometimes blocks clipboard access
   - Show clear error message
   - Suggest manual copy

4. **Mobile Keyboard Shortcuts**
   - Don't register Cmd+C on mobile (no keyboard)
   - Rely on button tap only

5. **Very Long Results**
   - Ensure all data fits in clipboard
   - Test with maximum data (all fields filled)

6. **Special Characters**
   - Escape special chars in JSON format
   - Handle unicode properly (centile symbols)

## Accessibility

- [x] Button has clear aria-label
- [x] Toast has role="status" and aria-live="polite"
- [x] Keyboard shortcut documented
- [x] Focus management (button receives focus after copy)
- [x] Screen reader announces success/failure
- [x] Color contrast sufficient (toast background)
- [x] Works without mouse (keyboard only)

## Future Enhancements (Post-MVP)

1. **Copy Individual Measurements**
   - Small copy icon next to each result item
   - Copy just weight, or just BMI, etc.

2. **Custom Templates**
   - User-defined copy formats
   - Template editor
   - Save multiple templates

3. **Email/Share Integration**
   - Email results button
   - Generate shareable link
   - QR code for mobile transfer

4. **Copy Chart Image**
   - Include chart screenshot in clipboard
   - Rich text clipboard with embedded image

5. **Auto-paste to EMR**
   - Integration with common EMR systems
   - Chrome extension for auto-paste

## Success Metrics

- 40%+ of users use copy feature at least once
- <1% clipboard errors (after fallback)
- Average 2-3 copies per session
- Positive user feedback on format
- Reduced time to documentation

## Timeline

- **Hour 1-2**: Implement ClipboardManager class + formats
- **Hour 3**: Add UI components (HTML/CSS)
- **Hour 4**: JavaScript integration + event handlers
- **Hour 5**: Testing on multiple browsers/devices
- **Hour 6**: Bug fixes + documentation

## Dependencies

- None (uses native browser APIs)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Safari clipboard blocked | High | Fallback + clear instructions |
| Old browser support | Medium | execCommand fallback |
| Mobile keyboard conflicts | Low | Button-only on mobile |
| Format not EMR-compatible | Medium | Offer multiple formats, get user feedback |

---

**Next Steps:**
1. Review and approve plan
2. Implement ClipboardManager class
3. Add UI components
4. Test across browsers
5. Gather user feedback on format
