/**
 * Tests for clipboard.js
 *
 * Tests ClipboardManager class for copying results in multiple formats
 */

const fs = require('fs');
const path = require('path');

// Read and execute the clipboard.js file
const clipboardCode = fs.readFileSync(
  path.join(__dirname, '../../static/clipboard.js'),
  'utf8'
);

eval(clipboardCode);

describe('ClipboardManager', () => {
  let manager;
  let testData;

  beforeEach(() => {
    manager = new ClipboardManager();

    // Standard test data
    testData = {
      sex: 'male',
      age: '1.00 years (1 year)',
      dateOfBirth: '2023-01-15',
      reference: 'uk-who',
      weight: {
        value: 12.5,
        centile: 50.2,
        sds: 0.05
      },
      height: {
        value: 85.0,
        centile: 48.5,
        sds: -0.04
      },
      bmi: {
        value: 17.3,
        centile: 55.0,
        sds: 0.13
      },
      ofc: {
        value: 48.2,
        centile: 52.0,
        sds: 0.05
      }
    };
  });

  describe('Constructor', () => {
    test('initializes with default format', () => {
      expect(manager.currentFormat).toBe('plain');
    });

    test('initializes formats object', () => {
      expect(manager.formats).toBeDefined();
      expect(typeof manager.formats.plain).toBe('function');
      expect(typeof manager.formats.compact).toBe('function');
      expect(typeof manager.formats.markdown).toBe('function');
      expect(typeof manager.formats.json).toBe('function');
    });

    test('reads format from localStorage if available', () => {
      localStorage.getItem.mockReturnValue('markdown');
      const newManager = new ClipboardManager();
      expect(newManager.currentFormat).toBe('markdown');
    });
  });

  describe('formatPlainText', () => {
    test('formats basic patient data', () => {
      const result = manager.formatPlainText(testData);

      expect(result).toContain('Growth Parameters');
      expect(result).toContain('Sex: Male');
      expect(result).toContain('Age: 1.00 years (1 year)');
      expect(result).toContain('DOB:');
      expect(result).toContain('Reference: UK-WHO');
    });

    test('formats weight measurement correctly', () => {
      const result = manager.formatPlainText(testData);

      expect(result).toContain('Weight');
      expect(result).toContain('12.5 kg');
      expect(result).toContain('50.2');
      expect(result).toContain('0.05 SDS');
    });

    test('formats height measurement correctly', () => {
      const result = manager.formatPlainText(testData);

      expect(result).toContain('Height');
      expect(result).toContain('85.0 cm');
      expect(result).toContain('48.5');
    });

    test('formats BMI measurement correctly', () => {
      const result = manager.formatPlainText(testData);

      expect(result).toContain('BMI');
      expect(result).toContain('17.3 kg/m²');
      expect(result).toContain('55.0');
    });

    test('formats OFC measurement correctly', () => {
      const result = manager.formatPlainText(testData);

      expect(result).toContain('OFC');
      expect(result).toContain('48.2 cm');
      expect(result).toContain('52.0');
    });

    test('handles missing optional fields', () => {
      const minimalData = {
        sex: 'female',
        weight: { value: 10.0, centile: 45, sds: -0.1 }
      };

      const result = manager.formatPlainText(minimalData);

      expect(result).toContain('Sex: Female');
      expect(result).toContain('Weight');
      expect(result).not.toContain('Height');
      expect(result).not.toContain('BMI');
    });

    test('includes height velocity if provided', () => {
      testData.heightVelocity = {
        value: 6.5,
        interval: '6 months'
      };

      const result = manager.formatPlainText(testData);

      expect(result).toContain('Height Velocity');
      expect(result).toContain('6.5 cm/year');
      expect(result).toContain('(6 months)');
    });

    test('includes BSA if provided', () => {
      testData.bsa = {
        value: 0.55,
        method: 'Mosteller'
      };

      const result = manager.formatPlainText(testData);

      expect(result).toContain('BSA');
      expect(result).toContain('0.55 m²');
      expect(result).toContain('Mosteller');
    });

    test('includes MPH if provided', () => {
      testData.mph = {
        value: 175.5,
        centile: 60.0,
        targetRange: '168.0 - 183.0'
      };

      const result = manager.formatPlainText(testData);

      expect(result).toContain('Mid-Parental Height');
      expect(result).toContain('175.5 cm');
      expect(result).toContain('60.0');
    });

    test('handles corrected age for preterm infants', () => {
      testData.correctedAge = '0.85 years (corrected)';

      const result = manager.formatPlainText(testData);

      // Should include corrected age in addition to chronological age
      expect(result).toBeTruthy();
    });
  });

  describe('formatCompact', () => {
    test('formats data in compact single-line format', () => {
      const result = manager.formatCompact(testData);

      expect(result).toContain('M 1.00y');
      expect(result).toContain('Wt:12.5kg');
      expect(result).toContain('Ht:85.0cm');
    });

    test('uses abbreviated labels', () => {
      const result = manager.formatCompact(testData);

      expect(result).toContain('Wt:'); // Weight
      expect(result).toContain('Ht:'); // Height
      expect(result).toContain('BMI:');
      expect(result).toContain('OFC:');
    });

    test('handles minimal data', () => {
      const minimalData = {
        sex: 'female',
        age: '2.00 years',
        weight: { value: 12.0, centile: 50 }
      };

      const result = manager.formatCompact(minimalData);

      expect(result).toContain('F 2.00y');
      expect(result).toContain('Wt:12.0kg');
    });
  });

  describe('formatMarkdown', () => {
    test('formats data as markdown table', () => {
      const result = manager.formatMarkdown(testData);

      expect(result).toContain('# Growth Parameters');
      expect(result).toContain('|');
      expect(result).toContain('Measurement');
      expect(result).toContain('Value');
      expect(result).toContain('Centile');
      expect(result).toContain('SDS');
    });

    test('includes patient info', () => {
      const result = manager.formatMarkdown(testData);

      expect(result).toContain('**Sex:**');
      expect(result).toContain('Male');
      expect(result).toContain('**Age:**');
      expect(result).toContain('1.00 years');
    });

    test('creates proper markdown table structure', () => {
      const result = manager.formatMarkdown(testData);

      // Check for table header separator
      expect(result).toContain('---');

      // Check for pipe separators
      const pipeCount = (result.match(/\|/g) || []).length;
      expect(pipeCount).toBeGreaterThan(10);
    });
  });

  describe('formatJSON', () => {
    test('formats data as valid JSON', () => {
      const result = manager.formatJSON(testData);
      const parsed = JSON.parse(result);

      expect(parsed.sex).toBe('male');
      expect(parsed.weight.value).toBe(12.5);
    });

    test('preserves all data fields', () => {
      const result = manager.formatJSON(testData);
      const parsed = JSON.parse(result);

      expect(parsed.weight).toBeDefined();
      expect(parsed.height).toBeDefined();
      expect(parsed.bmi).toBeDefined();
      expect(parsed.ofc).toBeDefined();
    });

    test('formats with readable indentation', () => {
      const result = manager.formatJSON(testData);

      // JSON.stringify with 2-space indent should have newlines
      expect(result).toContain('\n');
      expect(result).toContain('  '); // 2-space indent
    });
  });

  describe('copy', () => {
    test('uses Clipboard API when available', async () => {
      navigator.clipboard.writeText.mockResolvedValue(undefined);

      const result = await manager.copy(testData, 'plain');

      expect(result.success).toBe(true);
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    test('uses specified format', async () => {
      navigator.clipboard.writeText.mockResolvedValue(undefined);

      await manager.copy(testData, 'markdown');

      const copiedText = navigator.clipboard.writeText.mock.calls[0][0];
      expect(copiedText).toContain('# Growth Parameters');
    });

    test('uses default format if not specified', async () => {
      navigator.clipboard.writeText.mockResolvedValue(undefined);
      manager.currentFormat = 'compact';

      await manager.copy(testData);

      const copiedText = navigator.clipboard.writeText.mock.calls[0][0];
      expect(copiedText).toContain('Wt:');
    });

    test('falls back to execCommand if Clipboard API unavailable', async () => {
      // Make Clipboard API unavailable
      const originalClipboard = navigator.clipboard;
      delete navigator.clipboard;

      document.execCommand.mockReturnValue(true);

      const result = await manager.copy(testData, 'plain');

      expect(result.success).toBe(true);
      expect(document.execCommand).toHaveBeenCalledWith('copy');

      // Restore clipboard
      navigator.clipboard = originalClipboard;
    });

    test('handles copy errors gracefully', async () => {
      navigator.clipboard.writeText.mockRejectedValue(new Error('Copy failed'));

      const result = await manager.copy(testData, 'plain');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Copy failed');
    });
  });

  describe('fallbackCopy', () => {
    test('creates temporary textarea', () => {
      document.execCommand.mockReturnValue(true);

      manager.fallbackCopy('test text');

      expect(document.execCommand).toHaveBeenCalledWith('copy');
    });

    test('returns success when execCommand succeeds', () => {
      document.execCommand.mockReturnValue(true);

      const result = manager.fallbackCopy('test text');

      expect(result.success).toBe(true);
      expect(result.text).toBe('test text');
    });

    test('returns failure when execCommand fails', () => {
      document.execCommand.mockReturnValue(false);

      const result = manager.fallbackCopy('test text');

      expect(result.success).toBe(false);
    });

    test('cleans up textarea after copy', () => {
      const originalChildren = document.body.children.length;
      document.execCommand.mockReturnValue(true);

      manager.fallbackCopy('test text');

      expect(document.body.children.length).toBe(originalChildren);
    });
  });

  describe('Utility Methods', () => {
    test('capitalize() capitalizes first letter', () => {
      expect(manager.capitalize('male')).toBe('Male');
      expect(manager.capitalize('female')).toBe('Female');
    });

    test('formatDate() formats date string', () => {
      const result = manager.formatDate('2023-01-15');
      expect(result).toBeTruthy();
    });

    test('formatReference() formats reference names', () => {
      expect(manager.formatReference('uk-who')).toBe('UK-WHO');
      expect(manager.formatReference('turners-syndrome')).toContain('Turner');
    });
  });
});
