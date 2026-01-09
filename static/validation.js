/**
 * Frontend validation and form utilities
 */

// Validation constants (match backend)
const VALIDATION = {
    WEIGHT: { min: 0.1, max: 300 },
    HEIGHT: { min: 10, max: 250 },
    OFC: { min: 10, max: 100 },
    GESTATION_WEEKS: { min: 22, max: 44 },
    GESTATION_DAYS: { min: 0, max: 6 }
};

/**
 * Validate form inputs before submission
 * @param {Object} formData - Form data to validate
 * @returns {Array} - Array of error messages (empty if valid)
 */
function validateFormInputs(formData) {
    const errors = [];

    // Weight validation
    if (formData.weight) {
        const weight = parseFloat(formData.weight);
        if (isNaN(weight)) {
            errors.push('Weight must be a valid number');
        } else if (weight < VALIDATION.WEIGHT.min || weight > VALIDATION.WEIGHT.max) {
            errors.push(`Weight must be between ${VALIDATION.WEIGHT.min} and ${VALIDATION.WEIGHT.max} kg`);
        }
    }

    // Height validation
    if (formData.height) {
        const height = parseFloat(formData.height);
        if (isNaN(height)) {
            errors.push('Height must be a valid number');
        } else if (height < VALIDATION.HEIGHT.min || height > VALIDATION.HEIGHT.max) {
            errors.push(`Height must be between ${VALIDATION.HEIGHT.min} and ${VALIDATION.HEIGHT.max} cm`);
        }
    }

    // OFC validation
    if (formData.ofc) {
        const ofc = parseFloat(formData.ofc);
        if (isNaN(ofc)) {
            errors.push('Head circumference must be a valid number');
        } else if (ofc < VALIDATION.OFC.min || ofc > VALIDATION.OFC.max) {
            errors.push(`Head circumference must be between ${VALIDATION.OFC.min} and ${VALIDATION.OFC.max} cm`);
        }
    }

    // Date validation
    if (formData.birth_date && formData.measurement_date) {
        const birthDate = new Date(formData.birth_date);
        const measurementDate = new Date(formData.measurement_date);
        const today = new Date();

        if (measurementDate > today) {
            errors.push('Measurement date cannot be in the future');
        }

        if (birthDate > today) {
            errors.push('Birth date cannot be in the future');
        }

        if (birthDate >= measurementDate) {
            errors.push('Birth date must be before measurement date');
        }
    }

    // Gestation validation
    if (formData.gestation_weeks) {
        const weeks = parseInt(formData.gestation_weeks);
        if (isNaN(weeks)) {
            errors.push('Gestation weeks must be a valid number');
        } else if (weeks < VALIDATION.GESTATION_WEEKS.min || weeks > VALIDATION.GESTATION_WEEKS.max) {
            errors.push(`Gestation weeks must be between ${VALIDATION.GESTATION_WEEKS.min} and ${VALIDATION.GESTATION_WEEKS.max}`);
        }
    }

    if (formData.gestation_days) {
        const days = parseInt(formData.gestation_days);
        if (isNaN(days)) {
            errors.push('Gestation days must be a valid number');
        } else if (days < VALIDATION.GESTATION_DAYS.min || days > VALIDATION.GESTATION_DAYS.max) {
            errors.push(`Gestation days must be between ${VALIDATION.GESTATION_DAYS.min} and ${VALIDATION.GESTATION_DAYS.max}`);
        }
    }

    return errors;
}

/**
 * Save form state to localStorage
 */
function saveFormState() {
    try {
        const formData = {
            sex: document.querySelector('input[name="sex"]:checked')?.value || '',
            birth_date: document.getElementById('birth_date').value || '',
            measurement_date: document.getElementById('measurement_date').value || '',
            weight: document.getElementById('weight').value || '',
            height: document.getElementById('height').value || '',
            ofc: document.getElementById('ofc').value || '',
            gestation_weeks: document.getElementById('gestation_weeks').value || '',
            gestation_days: document.getElementById('gestation_days').value || '',
            previous_date: document.getElementById('previous_date').value || '',
            previous_height: document.getElementById('previous_height').value || '',
            reference: document.getElementById('reference').value || 'uk-who',
            advanced_mode: isAdvancedMode
        };

        // Save parental height data
        formData.maternal_height = document.getElementById('maternal_height').value || '';
        formData.paternal_height = document.getElementById('paternal_height').value || '';
        formData.maternal_height_units = document.querySelector('input[name="maternal_height_units"]:checked')?.value || 'cm';
        formData.paternal_height_units = document.querySelector('input[name="paternal_height_units"]:checked')?.value || 'cm';

        if (formData.maternal_height_units === 'ft_in') {
            formData.maternal_height_ft = document.getElementById('maternal_height_ft').value || '';
            formData.maternal_height_in = document.getElementById('maternal_height_in').value || '';
        }

        if (formData.paternal_height_units === 'ft_in') {
            formData.paternal_height_ft = document.getElementById('paternal_height_ft').value || '';
            formData.paternal_height_in = document.getElementById('paternal_height_in').value || '';
        }

        localStorage.setItem('growthCalcForm', JSON.stringify(formData));
    } catch (error) {
        console.error('Error saving form state:', error);
    }
}

/**
 * Restore form state from localStorage
 */
function restoreFormState() {
    try {
        const saved = localStorage.getItem('growthCalcForm');
        if (!saved) return;

        const formData = JSON.parse(saved);

        // Restore basic fields
        if (formData.sex) {
            const sexInput = document.querySelector(`input[name="sex"][value="${formData.sex}"]`);
            if (sexInput) sexInput.checked = true;
        }

        if (formData.birth_date) document.getElementById('birth_date').value = formData.birth_date;
        if (formData.measurement_date) document.getElementById('measurement_date').value = formData.measurement_date;
        if (formData.weight) document.getElementById('weight').value = formData.weight;
        if (formData.height) document.getElementById('height').value = formData.height;
        if (formData.ofc) document.getElementById('ofc').value = formData.ofc;
        if (formData.gestation_weeks) document.getElementById('gestation_weeks').value = formData.gestation_weeks;
        if (formData.gestation_days) document.getElementById('gestation_days').value = formData.gestation_days;
        if (formData.previous_date) document.getElementById('previous_date').value = formData.previous_date;
        if (formData.previous_height) document.getElementById('previous_height').value = formData.previous_height;
        if (formData.reference) document.getElementById('reference').value = formData.reference;

        // Restore parental heights
        if (formData.maternal_height) document.getElementById('maternal_height').value = formData.maternal_height;
        if (formData.paternal_height) document.getElementById('paternal_height').value = formData.paternal_height;

        // Restore mode toggle
        if (formData.advanced_mode) {
            document.getElementById('modeToggle').checked = true;
            document.getElementById('modeToggle').dispatchEvent(new Event('change'));
        }

    } catch (error) {
        console.error('Error restoring form state:', error);
    }
}

/**
 * Clear saved form state from localStorage
 */
function clearSavedFormState() {
    try {
        localStorage.removeItem('growthCalcForm');
    } catch (error) {
        console.error('Error clearing form state:', error);
    }
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounced save function
const debouncedSave = debounce(saveFormState, 1000);
