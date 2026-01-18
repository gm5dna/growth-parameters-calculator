/**
 * Tests for validation.js
 *
 * Tests frontend validation, form state management, and utility functions
 */

// Mock the validation module by reading and executing the file
const fs = require('fs');
const path = require('path');

// Read and execute the validation.js file in the global scope
const validationCode = fs.readFileSync(
  path.join(__dirname, '../../static/validation.js'),
  'utf8'
);

// Execute the code to make functions available globally
eval(validationCode);

describe('validateFormInputs', () => {
  describe('Weight Validation', () => {
    test('accepts valid weight', () => {
      const formData = { weight: '12.5' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects weight below minimum', () => {
      const formData = { weight: '0.05' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Weight must be between');
    });

    test('rejects weight above maximum', () => {
      const formData = { weight: '350' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Weight must be between');
    });

    test('rejects non-numeric weight', () => {
      const formData = { weight: 'not a number' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('must be a valid number');
    });

    test('accepts weight at minimum boundary', () => {
      const formData = { weight: '0.1' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('accepts weight at maximum boundary', () => {
      const formData = { weight: '300' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });
  });

  describe('Height Validation', () => {
    test('accepts valid height', () => {
      const formData = { height: '85.5' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects height below minimum', () => {
      const formData = { height: '5' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Height must be between');
    });

    test('rejects height above maximum', () => {
      const formData = { height: '300' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });

    test('rejects non-numeric height', () => {
      const formData = { height: 'tall' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('OFC Validation', () => {
    test('accepts valid OFC', () => {
      const formData = { ofc: '48.2' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects OFC below minimum', () => {
      const formData = { ofc: '5' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Head circumference');
    });

    test('rejects OFC above maximum', () => {
      const formData = { ofc: '150' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Date Validation', () => {
    test('accepts valid dates', () => {
      const formData = {
        birth_date: '2023-01-15',
        measurement_date: '2024-01-15'
      };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects future measurement date', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 10);
      const formData = {
        birth_date: '2023-01-15',
        measurement_date: futureDate.toISOString().split('T')[0]
      };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('future'))).toBe(true);
    });

    test('rejects future birth date', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 10);
      const formData = {
        birth_date: futureDate.toISOString().split('T')[0],
        measurement_date: '2024-01-15'
      };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });

    test('rejects measurement date before birth date', () => {
      const formData = {
        birth_date: '2024-01-15',
        measurement_date: '2023-01-15'
      };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('before measurement'))).toBe(true);
    });

    test('rejects measurement date equal to birth date', () => {
      const formData = {
        birth_date: '2024-01-15',
        measurement_date: '2024-01-15'
      };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Gestation Validation', () => {
    test('accepts valid gestation weeks', () => {
      const formData = { gestation_weeks: '32' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects gestation weeks below minimum', () => {
      const formData = { gestation_weeks: '20' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Gestation weeks');
    });

    test('rejects gestation weeks above maximum', () => {
      const formData = { gestation_weeks: '50' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });

    test('accepts valid gestation days', () => {
      const formData = { gestation_days: '4' };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });

    test('rejects gestation days above maximum', () => {
      const formData = { gestation_days: '8' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });

    test('rejects non-numeric gestation values', () => {
      const formData = { gestation_weeks: 'abc' };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Multiple Errors', () => {
    test('returns multiple errors for multiple invalid fields', () => {
      const formData = {
        weight: '500',
        height: '5',
        ofc: 'abc'
      };
      const errors = validateFormInputs(formData);
      expect(errors.length).toBeGreaterThanOrEqual(3);
    });

    test('returns empty array for valid complete form', () => {
      const formData = {
        birth_date: '2023-01-15',
        measurement_date: '2024-01-15',
        weight: '12.5',
        height: '85.0',
        ofc: '48.2',
        gestation_weeks: '32',
        gestation_days: '4'
      };
      const errors = validateFormInputs(formData);
      expect(errors).toHaveLength(0);
    });
  });
});

describe('saveFormState', () => {
  beforeEach(() => {
    // Set up minimal DOM for saveFormState
    document.body.innerHTML = `
      <input type="radio" name="sex" value="male" checked>
      <input type="radio" name="sex" value="female">
      <input type="text" id="birth_date" value="2023-01-15">
      <input type="text" id="measurement_date" value="2024-01-15">
      <input type="text" id="weight" value="12.5">
      <input type="text" id="height" value="85.0">
      <input type="text" id="ofc" value="48.0">
      <input type="text" id="gestation_weeks" value="">
      <input type="text" id="gestation_days" value="">
      <input type="text" id="previous_date" value="">
      <input type="text" id="previous_height" value="">
      <select id="reference"><option value="uk-who" selected>UK-WHO</option></select>
      <input type="text" id="maternal_height" value="">
      <input type="text" id="paternal_height" value="">
      <input type="radio" name="maternal_height_units" value="cm" checked>
      <input type="radio" name="paternal_height_units" value="cm" checked>
      <input type="text" id="maternal_height_ft" value="">
      <input type="text" id="maternal_height_in" value="">
      <input type="text" id="paternal_height_ft" value="">
      <input type="text" id="paternal_height_in" value="">
    `;

    global.isAdvancedMode = false;
  });

  test('saves form data to localStorage', () => {
    saveFormState();

    expect(localStorage.setItem).toHaveBeenCalled();
    const savedData = JSON.parse(localStorage.setItem.mock.calls[0][1]);
    expect(savedData.sex).toBe('male');
    expect(savedData.birth_date).toBe('2023-01-15');
    expect(savedData.weight).toBe('12.5');
  });

  test('saves with growthCalcForm key', () => {
    localStorage.setItem.mockClear();
    saveFormState();

    expect(localStorage.setItem).toHaveBeenCalled();
    if (localStorage.setItem.mock.calls.length > 0) {
      expect(localStorage.setItem.mock.calls[0][0]).toBe('growthCalcForm');
    }
  });

  test('handles missing elements gracefully', () => {
    document.body.innerHTML = ''; // Empty DOM

    expect(() => saveFormState()).not.toThrow();
  });
});

describe('restoreFormState', () => {
  beforeEach(() => {

    document.body.innerHTML = `
      <input type="radio" name="sex" value="male">
      <input type="radio" name="sex" value="female">
      <input type="text" id="birth_date" value="">
      <input type="text" id="measurement_date" value="">
      <input type="text" id="weight" value="">
      <input type="text" id="height" value="">
      <input type="text" id="ofc" value="">
      <input type="text" id="gestation_weeks" value="">
      <input type="text" id="gestation_days" value="">
      <input type="text" id="previous_date" value="">
      <input type="text" id="previous_height" value="">
      <select id="reference"><option value="uk-who">UK-WHO</option></select>
      <input type="text" id="maternal_height" value="">
      <input type="text" id="paternal_height" value="">
      <input type="checkbox" id="modeToggle">
    `;
  });

  test('restores form data from localStorage', () => {
    const savedData = {
      sex: 'female',
      birth_date: '2023-01-15',
      measurement_date: '2024-01-15',
      weight: '12.5',
      height: '85.0',
      reference: 'uk-who'
    };

    localStorage.getItem = jest.fn(() => JSON.stringify(savedData));

    restoreFormState();

    expect(document.getElementById('birth_date').value).toBe('2023-01-15');
    expect(document.getElementById('weight').value).toBe('12.5');
    expect(document.querySelector('input[name="sex"][value="female"]').checked).toBe(true);
  });

  test('handles no saved data gracefully', () => {
    localStorage.getItem = jest.fn(() => null);

    expect(() => restoreFormState()).not.toThrow();
  });

  test('handles corrupted localStorage data', () => {
    localStorage.getItem = jest.fn(() => 'not valid json{');

    expect(() => restoreFormState()).not.toThrow();
  });
});

describe('debounce', () => {
  jest.useFakeTimers();

  test('delays function execution', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 500);

    debouncedFn();
    expect(mockFn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(500);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  test('cancels previous calls', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 500);

    debouncedFn();
    debouncedFn();
    debouncedFn();

    jest.advanceTimersByTime(500);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  test('passes arguments to debounced function', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 500);

    debouncedFn('arg1', 'arg2');
    jest.advanceTimersByTime(500);

    expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
  });

  afterEach(() => {
    jest.clearAllTimers();
  });
});
