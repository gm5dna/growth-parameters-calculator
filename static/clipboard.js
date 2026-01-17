/**
 * Clipboard Manager for Growth Parameters Calculator
 * Handles copying results in multiple formats with browser compatibility
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
   * @param {Object} data - Results data to copy
   * @param {string} format - Output format (plain, compact, markdown, json)
   * @returns {Promise<Object>} Result object with success status
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
   * Fallback copy method using execCommand (for older browsers)
   * @param {string} text - Text to copy
   * @returns {Object} Result object
   */
  fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.top = '0';
    textarea.style.left = '0';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';
    document.body.appendChild(textarea);

    textarea.focus();
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
   * Format: Clinical Plain Text (Default)
   * Professional format ready for EMR documentation
   */
  formatPlainText(data) {
    const lines = [];
    const today = new Date().toLocaleDateString('en-GB');

    // Header
    lines.push('Growth Parameters - ' + today);
    lines.push('');

    // Sex
    if (data.sex) {
      lines.push(`Sex: ${this.capitalize(data.sex)}`);
    }

    // Age - ensure space before parenthesis
    if (data.age) {
      const ageFormatted = data.age.replace(/\(/g, ' (').replace(/\s+\(/g, ' (');
      lines.push(`Age: ${ageFormatted}`);
    }

    lines.push('');

    // DOB and Reference
    if (data.dateOfBirth) {
      lines.push(`DOB: ${this.formatDate(data.dateOfBirth)}`);
    }
    if (data.reference) {
      lines.push(`Reference: ${this.formatReference(data.reference)}`);
    }
    lines.push('');

    // Measurements
    lines.push('MEASUREMENTS:');

    if (data.weight) {
      lines.push(this.formatMeasurementNew('Weight', data.weight.value, 'kg',
                                           data.weight.centile, data.weight.sds));
    }

    if (data.height) {
      lines.push(this.formatMeasurementNew('Height', data.height.value, 'cm',
                                           data.height.centile, data.height.sds));
    }

    if (data.bmi) {
      lines.push(this.formatMeasurementNew('BMI', data.bmi.value, 'kg/m²',
                                           data.bmi.centile, data.bmi.sds));
    }

    if (data.ofc) {
      lines.push(this.formatMeasurementNew('OFC', data.ofc.value, 'cm',
                                           data.ofc.centile, data.ofc.sds));
    }

    // Additional parameters (no section header)
    const hasAdditional = data.heightVelocity || data.bsa || data.ghDose || data.mph;
    if (hasAdditional) {
      lines.push('');

      if (data.heightVelocity) {
        let hvLine = `Height Velocity:  ${data.heightVelocity.value} cm/year`;
        if (data.heightVelocity.interval) {
          hvLine += ` (${data.heightVelocity.interval})`;
        }
        lines.push(hvLine);
      }

      if (data.bsa) {
        lines.push(`BSA (${data.bsa.method}):       ${data.bsa.value} m²`);
      }

      if (data.ghDose) {
        // Format mcg/kg/day to remove trailing zeros
        const mcgKgDay = parseFloat(data.ghDose.mcgKgDay);
        const mcgKgDayFormatted = Number.isInteger(mcgKgDay) ? mcgKgDay.toString() : mcgKgDay.toFixed(1).replace(/\.0$/, '');

        // Format mg/day - remove unnecessary trailing zeros but keep 2 decimal places minimum
        const mgPerDay = parseFloat(data.ghDose.mgPerDay);
        const mgPerDayFormatted = mgPerDay.toFixed(2).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');

        lines.push(`GH Dose:          ${mgPerDayFormatted} mg/day (${data.ghDose.mgM2Week} mg/m²/week, ${mcgKgDayFormatted} mcg/kg/day)`);
      }

      if (data.mph) {
        // Extract percentage from centile (e.g., "50th centile" -> "50%")
        const centilePercent = this.extractPercentage(data.mph.centile);
        lines.push('');
        lines.push(`Mid-Parental Height: ${data.mph.value} cm (${centilePercent})`);
        if (data.mph.rangeMin && data.mph.rangeMax) {
          lines.push(`Target Range: ${data.mph.rangeMin}-${data.mph.rangeMax} cm`);
        }
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

    return lines.join('\n');
  }

  /**
   * Format: Compact one-liner
   * Quick summary for brief notes
   */
  formatCompact(data) {
    const parts = [];
    const date = new Date().toLocaleDateString('en-GB').slice(0, 8); // DD/MM/YY

    if (data.sex && data.age) {
      parts.push(`${this.capitalize(data.sex)} ${data.age}`);
    }

    if (data.weight) {
      parts.push(`W: ${data.weight.value}kg (${data.weight.centile})`);
    }

    if (data.height) {
      parts.push(`H: ${data.height.value}cm (${data.height.centile})`);
    }

    if (data.bmi) {
      parts.push(`BMI: ${data.bmi.value} (${data.bmi.centile})`);
    }

    if (data.mph) {
      parts.push(`MPH: ${data.mph.value}cm (${data.mph.centile})`);
    }

    if (data.reference) {
      parts.push(this.formatReference(data.reference));
    }

    parts.push(date);

    return parts.join(' | ');
  }

  /**
   * Format: Markdown
   * For documentation with formatted tables
   */
  formatMarkdown(data) {
    const lines = [];
    const today = new Date().toLocaleDateString('en-GB');

    lines.push('## Growth Parameters Assessment');
    lines.push('');
    lines.push(`**Date:** ${today}  `);

    if (data.sex && data.age) {
      lines.push(`**Patient:** ${this.capitalize(data.sex)}, ${data.age}  `);
    }

    if (data.reference) {
      lines.push(`**Reference:** ${this.formatReference(data.reference)}`);
    }

    lines.push('');

    // Measurements table
    const hasMeasurements = data.weight || data.height || data.bmi || data.ofc;
    if (hasMeasurements) {
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
    }

    // Additional parameters
    const hasAdditional = data.heightVelocity || data.bsa || data.mph || data.ghDose;
    if (hasAdditional) {
      lines.push('');
      lines.push('### Additional Parameters');
      lines.push('');

      if (data.heightVelocity) {
        lines.push(`- **Height Velocity:** ${data.heightVelocity.value} cm/year`);
      }

      if (data.bsa) {
        lines.push(`- **BSA (${data.bsa.method}):** ${data.bsa.value} m²`);
      }

      if (data.ghDose) {
        lines.push(`- **GH Dose:** ${data.ghDose.mgPerDay} mg/day (${data.ghDose.mgM2Week} mg/m²/week)`);
      }

      if (data.mph) {
        const range = (data.mph.rangeMin && data.mph.rangeMax) ?
          `, range: ${data.mph.rangeMin}-${data.mph.rangeMax} cm` : '';
        lines.push(`- **Mid-Parental Height:** ${data.mph.value} cm (${data.mph.centile}${range})`);
      }
    }

    // Warnings
    if (data.warnings && data.warnings.length > 0) {
      lines.push('');
      lines.push('### Warnings');
      lines.push('');
      data.warnings.forEach(warning => {
        lines.push(`- ${warning}`);
      });
    }

    return lines.join('\n');
  }

  /**
   * Format: JSON
   * For integration and automation
   */
  formatJSON(data) {
    return JSON.stringify(data, null, 2);
  }

  // Helper methods

  formatMeasurement(label, value, unit, centile, sds) {
    const paddedLabel = label.padEnd(12);
    const valueStr = `${value} ${unit}`.padEnd(15);
    const centileStr = centile && sds ? `(${centile}, SDS: ${sds})` : '';
    return `${paddedLabel}${valueStr}${centileStr}`;
  }

  formatMeasurementNew(label, value, unit, centile, sds) {
    // New format: "Weight      20 kg          (36.77%, SDS: -0.34)"
    const labelPadded = label.padEnd(12);
    const valueStr = `${value} ${unit}`.padEnd(15);
    const centilePercent = this.extractPercentage(centile);
    const centileStr = centile && sds ? `(${centilePercent}, SDS: ${sds})` : '';
    return `${labelPadded}${valueStr}${centileStr}`;
  }

  extractPercentage(centile) {
    // Extract percentage from centile strings like "36.77th centile" -> "36.77%"
    // or "50th" -> "50%"
    if (!centile) return '';
    const match = centile.match(/([\d.]+)/);
    return match ? `${match[1]}%` : centile;
  }

  formatDate(dateStr) {
    if (!dateStr) return '';
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
    if (!str) return '';
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
