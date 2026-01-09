// Mode toggle functionality
let isAdvancedMode = false;

// Initialize basic mode on page load
document.addEventListener('DOMContentLoaded', function() {
    // Restore form state from localStorage
    restoreFormState();

    // Set measurement date to today in basic mode if not restored
    if (!isAdvancedMode) {
        const measurementDateInput = document.getElementById('measurement_date');
        if (!measurementDateInput.value) {
            measurementDateInput.value = new Date().toISOString().split('T')[0];
        }
    }

    // Add input event listeners for auto-save
    const formInputs = document.querySelectorAll('#growthForm input, #growthForm select');
    formInputs.forEach(input => {
        input.addEventListener('input', debouncedSave);
        input.addEventListener('change', debouncedSave);
    });
});

document.getElementById('modeToggle').addEventListener('change', function() {
    isAdvancedMode = this.checked;
    const modeText = document.getElementById('modeText');
    modeText.textContent = isAdvancedMode ? 'Advanced Mode' : 'Basic Mode';

    // Toggle advanced mode class on body
    if (isAdvancedMode) {
        document.body.classList.add('advanced-mode');
    } else {
        document.body.classList.remove('advanced-mode');

        // In basic mode, ensure reference is set to uk-who
        document.getElementById('reference').value = 'uk-who';

        // In basic mode, set measurement date to today if not set
        const measurementDateInput = document.getElementById('measurement_date');
        if (!measurementDateInput.value) {
            measurementDateInput.value = new Date().toISOString().split('T')[0];
        }
    }
});

// Convert feet and inches to cm
function feetInchesToCm(feet, inches) {
    const totalInches = (parseFloat(feet) || 0) * 12 + (parseFloat(inches) || 0);
    return totalInches * 2.54;
}

// Get parental height in cm based on selected units (independent for each parent)
function getParentalHeightInCm(parent) {
    const units = document.querySelector(`input[name="${parent}_height_units"]:checked`)?.value;

    if (units === 'ft_in') {
        const feet = document.getElementById(`${parent}_height_ft`).value;
        const inches = document.getElementById(`${parent}_height_in`).value;

        if (feet || inches) {
            return feetInchesToCm(feet, inches);
        }
        return null;
    } else {
        const cm = document.getElementById(`${parent}_height`).value;
        return cm ? parseFloat(cm) : null;
    }
}

document.getElementById('growthForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    const submitBtn = document.querySelector('.btn-submit');

    errorDiv.classList.remove('show');
    resultsDiv.classList.remove('show');

    const maternalHeightCm = getParentalHeightInCm('maternal');
    const paternalHeightCm = getParentalHeightInCm('paternal');

    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const ofc = document.getElementById('ofc').value;

    const gestationWeeks = document.getElementById('gestation_weeks').value;
    const gestationDays = document.getElementById('gestation_days').value;

    const formData = {
        sex: document.querySelector('input[name="sex"]:checked')?.value,
        birth_date: document.getElementById('birth_date').value,
        measurement_date: document.getElementById('measurement_date').value,
        weight: weight,
        height: height,
        ofc: ofc,
        previous_date: document.getElementById('previous_date').value,
        previous_height: document.getElementById('previous_height').value,
        maternal_height: maternalHeightCm,
        paternal_height: paternalHeightCm,
        gestation_weeks: gestationWeeks ? parseInt(gestationWeeks) : null,
        gestation_days: gestationDays ? parseInt(gestationDays) : null,
        reference: document.getElementById('reference').value
    };

    // Client-side validation
    const validationErrors = validateFormInputs(formData);
    if (validationErrors.length > 0) {
        showError(validationErrors.join('; '));
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';
    submitBtn.style.cursor = 'wait';

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.results);
            // Clear saved form state on successful calculation
            clearSavedFormState();
        } else {
            showError(data.error || 'An error occurred during calculation');
        }
    } catch (error) {
        showError('Failed to connect to server: ' + error.message);
    } finally {
        // Reset loading state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Calculate';
        submitBtn.style.cursor = 'pointer';
    }
});

function displayResults(results) {
    // Display reference note
    const referenceSelect = document.getElementById('reference');
    const selectedOption = referenceSelect.options[referenceSelect.selectedIndex].text;
    document.getElementById('reference-note').textContent = `Using ${selectedOption} growth reference`;

    // Display validation warnings if any
    const validationWarnings = document.getElementById('validation-warnings');
    if (results.validation_messages && results.validation_messages.length > 0) {
        let warningHTML = '<strong>⚠️ Advisory Warnings:</strong>';
        warningHTML += '<ul>';
        results.validation_messages.forEach(msg => {
            warningHTML += `<li>${msg}</li>`;
        });
        warningHTML += '</ul>';
        validationWarnings.innerHTML = warningHTML;
        validationWarnings.classList.add('show');
    } else {
        validationWarnings.classList.remove('show');
    }

    // Format calendar age display
    const calendarAge = results.age_calendar;
    const ageElement = document.getElementById('age');
    ageElement.innerHTML = `${calendarAge.years}y ${calendarAge.months}m ${calendarAge.days}d<br><span style="font-size: 0.8em; color: #666;">(${results.age_years} years)</span>`;

    // Display weight if provided
    const weightItem = document.getElementById('weight-item');
    if (results.weight !== null) {
        document.getElementById('weight-value').textContent = `${results.weight.value} kg`;
        document.getElementById('weight-centile').textContent = results.weight.centile !== null ? `${results.weight.centile}%` : 'N/A';
        document.getElementById('weight-sds').textContent = results.weight.sds !== null ? results.weight.sds : 'N/A';
        weightItem.style.display = 'block';
    } else {
        weightItem.style.display = 'none';
    }

    // Display height if provided
    const heightItem = document.getElementById('height-item');
    if (results.height !== null) {
        document.getElementById('height-value').textContent = `${results.height.value} cm`;
        document.getElementById('height-centile').textContent = results.height.centile !== null ? `${results.height.centile}%` : 'N/A';
        document.getElementById('height-sds').textContent = results.height.sds !== null ? results.height.sds : 'N/A';
        heightItem.style.display = 'block';
    } else {
        heightItem.style.display = 'none';
    }

    // Display BMI if calculated
    const bmiItem = document.getElementById('bmi-item');
    if (results.bmi !== null) {
        document.getElementById('bmi-value').textContent = `${results.bmi.value} kg/m²`;
        document.getElementById('bmi-centile').textContent = results.bmi.centile !== null ? `${results.bmi.centile}%` : 'N/A';
        document.getElementById('bmi-sds').textContent = results.bmi.sds !== null ? results.bmi.sds : 'N/A';
        bmiItem.style.display = 'block';
    } else {
        bmiItem.style.display = 'none';
    }

    // Display OFC if provided
    const ofcItem = document.getElementById('ofc-item');
    if (results.ofc !== null) {
        document.getElementById('ofc-value').textContent = `${results.ofc.value} cm`;
        document.getElementById('ofc-centile').textContent = results.ofc.centile !== null ? `${results.ofc.centile}%` : 'N/A';
        document.getElementById('ofc-sds').textContent = results.ofc.sds !== null ? results.ofc.sds : 'N/A';
        ofcItem.style.display = 'block';
    } else {
        ofcItem.style.display = 'none';
    }

    const heightVelocityItem = document.getElementById('height-velocity-item');
    const heightVelocityValue = document.getElementById('height-velocity');
    const heightVelocityMessage = document.getElementById('height-velocity-message');

    if (results.height_velocity !== null) {
        if (results.height_velocity.value !== null) {
            heightVelocityValue.textContent = `${results.height_velocity.value} cm/year`;
            heightVelocityMessage.textContent = '';
            heightVelocityMessage.style.display = 'none';
        } else if (results.height_velocity.message) {
            heightVelocityValue.textContent = 'Not calculated';
            heightVelocityMessage.textContent = results.height_velocity.message;
            heightVelocityMessage.style.display = 'block';
        }
        heightVelocityItem.style.display = 'block';
    } else {
        heightVelocityItem.style.display = 'none';
    }

    // Display BSA with method in label, not value
    if (results.bsa !== null) {
        document.getElementById('bsa').textContent = `${results.bsa} m²`;
        // Update label to show method used
        const bsaLabel = document.getElementById('bsa-label');
        if (results.bsa_method) {
            bsaLabel.textContent = `Body Surface Area (${results.bsa_method})`;
        } else {
            bsaLabel.textContent = 'Body Surface Area (Boyd)';
        }
    } else {
        document.getElementById('bsa').textContent = 'N/A';
        document.getElementById('bsa-label').textContent = 'Body Surface Area (Boyd)';
    }

    // Display GH dose with interactive adjuster
    const ghDoseItem = document.getElementById('gh-dose-item');
    if (results.gh_dose !== null && results.bsa !== null && results.weight !== null) {
        // Store BSA and weight for recalculation
        window.currentBSA = results.bsa;
        window.currentWeight = results.weight.value;

        // Set initial dose value with appropriate decimal places
        const ghDoseInput = document.getElementById('gh-dose-input');
        const initialDose = results.gh_dose.mg_per_day;

        // Determine decimal places based on dose level
        let decimalPlaces = 1;
        const precision = getIncrementForDose(initialDose);
        if (precision === 0.025) decimalPlaces = 3;
        else if (precision === 0.05) decimalPlaces = 2;

        ghDoseInput.value = initialDose.toFixed(decimalPlaces);

        // Update the mg/m²/week and mcg/kg/day displays
        updateGHDoseEquivalent(initialDose);

        ghDoseItem.style.display = 'block';
    } else {
        ghDoseItem.style.display = 'none';
    }

    // Display mid-parental height
    const mphItem = document.getElementById('mph-item');
    if (results.mid_parental_height !== null) {
        document.getElementById('mph-value').textContent = `${results.mid_parental_height.mid_parental_height} cm`;
        document.getElementById('mph-centile').textContent = `${results.mid_parental_height.mid_parental_height_centile}%`;
        document.getElementById('mph-range').textContent = `${results.mid_parental_height.target_range_lower} - ${results.mid_parental_height.target_range_upper} cm`;
        mphItem.style.display = 'block';
    } else {
        mphItem.style.display = 'none';
    }

    document.getElementById('results').classList.add('show');

    // Store results for growth charts
    calculationResults = results;

    // Store patient data from form inputs
    currentPatientData.sex = document.querySelector('input[name="sex"]:checked')?.value;
    currentPatientData.reference = document.getElementById('reference').value;
    currentPatientData.age = results.age_years;
    currentPatientData.birthDate = document.getElementById('birth_date').value;
    currentPatientData.measurementDate = document.getElementById('measurement_date').value;

    // Store current measurements
    currentPatientData.measurements = {
        height: results.height,
        weight: results.weight,
        bmi: results.bmi,
        ofc: results.ofc
    };

    // Store previous measurements (currently only height) with centile/SDS from backend
    const previousHeight = document.getElementById('previous_height').value;
    const previousDate = document.getElementById('previous_date').value;
    currentPatientData.previousMeasurements = {
        height: previousHeight ? parseFloat(previousHeight) : null,
        date: previousDate || null,
        centile: results.previous_height ? results.previous_height.centile : null,
        sds: results.previous_height ? results.previous_height.sds : null
    };

    // Store corrected age measurements if gestation correction was applied
    currentPatientData.weight_corrected = results.weight_corrected || null;
    currentPatientData.height_corrected = results.height_corrected || null;
    currentPatientData.bmi_corrected = results.bmi_corrected || null;
    currentPatientData.ofc_corrected = results.ofc_corrected || null;

    // Show "Show Charts" button
    const showChartsContainer = document.getElementById('show-charts-container');
    showChartsContainer.classList.add('show');
    showChartsContainer.style.display = '';  // Reset inline style

    // Hide charts section if it was previously open
    document.getElementById('charts-section').classList.remove('show');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
}

// Reset button functionality
document.getElementById('resetBtn').addEventListener('click', () => {
    // Reset the form
    document.getElementById('growthForm').reset();

    // Hide results and error
    document.getElementById('results').classList.remove('show');
    document.getElementById('error').classList.remove('show');

    // Reset measurement date to today
    document.getElementById('measurement_date').valueAsDate = new Date();

    // Reset parental height unit toggles to cm (default)
    document.getElementById('maternal-height-cm').style.display = 'block';
    document.getElementById('maternal-height-ft').style.display = 'none';
    document.getElementById('paternal-height-cm').style.display = 'block';
    document.getElementById('paternal-height-ft').style.display = 'none';

    // Hide and reset charts
    document.getElementById('charts-section').classList.remove('show');
    document.getElementById('show-charts-container').classList.remove('show');

    // Destroy chart instance to free memory
    if (currentChartInstance) {
        currentChartInstance.destroy();
        currentChartInstance = null;
    }

    // Clear stored data
    calculationResults = null;
    currentPatientData = {
        sex: null,
        reference: null,
        age: null,
        birthDate: null,
        measurementDate: null,
        measurements: {
            height: null,
            weight: null,
            bmi: null,
            ofc: null
        },
        previousMeasurements: {
            height: null,
            date: null
        }
    };
});

// Toggle between cm and ft/in inputs for parental heights (independent for each parent)
function toggleMaternalHeightUnits() {
    const units = document.querySelector('input[name="maternal_height_units"]:checked')?.value;
    const isCm = units === 'cm';

    document.getElementById('maternal-height-cm').style.display = isCm ? 'block' : 'none';
    document.getElementById('maternal-height-ft').style.display = isCm ? 'none' : 'block';

    // Clear the non-active input when switching units to avoid confusion
    if (isCm) {
        document.getElementById('maternal_height_ft').value = '';
        document.getElementById('maternal_height_in').value = '';
    } else {
        document.getElementById('maternal_height').value = '';
    }
}

function togglePaternalHeightUnits() {
    const units = document.querySelector('input[name="paternal_height_units"]:checked')?.value;
    const isCm = units === 'cm';

    document.getElementById('paternal-height-cm').style.display = isCm ? 'block' : 'none';
    document.getElementById('paternal-height-ft').style.display = isCm ? 'none' : 'block';

    // Clear the non-active input when switching units to avoid confusion
    if (isCm) {
        document.getElementById('paternal_height_ft').value = '';
        document.getElementById('paternal_height_in').value = '';
    } else {
        document.getElementById('paternal_height').value = '';
    }
}

// Add event listeners to height unit radio buttons for each parent
document.querySelectorAll('input[name="maternal_height_units"]').forEach(radio => {
    radio.addEventListener('change', toggleMaternalHeightUnits);
});

document.querySelectorAll('input[name="paternal_height_units"]').forEach(radio => {
    radio.addEventListener('change', togglePaternalHeightUnits);
});

// Set measurement date to today on page load
document.getElementById('measurement_date').valueAsDate = new Date();

// Sex selection - disable Turner syndrome for males
const sexInputs = document.querySelectorAll('input[name="sex"]');
const referenceSelect = document.getElementById('reference');
const turnerOption = referenceSelect.querySelector('option[value="turners-syndrome"]');

function updateReferenceOptions() {
    const selectedSex = document.querySelector('input[name="sex"]:checked');
    if (selectedSex && selectedSex.value === 'male') {
        turnerOption.disabled = true;
        // If Turner syndrome is currently selected, switch to UK-WHO
        if (referenceSelect.value === 'turners-syndrome') {
            referenceSelect.value = 'uk-who';
        }
    } else {
        turnerOption.disabled = false;
    }
}

sexInputs.forEach(input => {
    input.addEventListener('change', updateReferenceOptions);
});

// Run on page load in case a sex is pre-selected
updateReferenceOptions();

// Disclaimer dismiss functionality (non-persistent - reappears on page reload)
const disclaimerElement = document.getElementById('disclaimer');
const dismissButton = document.getElementById('dismiss-disclaimer');

// Handle dismiss button click
dismissButton.addEventListener('click', () => {
    disclaimerElement.style.display = 'none';
});

// GH Dose adjustment functions
function updateGHDoseEquivalent(mgPerDay) {
    if (!window.currentBSA || !window.currentWeight) return;

    // Calculate mg/m²/week
    const mgPerWeek = mgPerDay * 7;
    const mgM2Week = mgPerWeek / window.currentBSA;
    document.getElementById('gh-dose-mg-m2-week').textContent = mgM2Week.toFixed(1);

    // Calculate mcg/kg/day
    const mcgPerDay = mgPerDay * 1000;  // Convert mg to mcg
    const mcgKgDay = mcgPerDay / window.currentWeight;
    document.getElementById('gh-dose-mcg-kg-day').textContent = mcgKgDay.toFixed(1);
}

function getIncrementForDose(dose) {
    // Variable increments based on dose level
    if (dose < 0.5) {
        return 0.025;  // 0.025 mg increments for 0-0.5 mg
    } else if (dose < 1.5) {
        return 0.05;   // 0.05 mg increments for 0.5-1.5 mg
    } else {
        return 0.1;    // 0.1 mg increments above 1.5 mg
    }
}

function roundToPrecision(value, precision) {
    // Round to the specified precision (e.g., 0.025, 0.05, 0.1)
    return Math.round(value / precision) * precision;
}

function adjustGHDose(direction) {
    const input = document.getElementById('gh-dose-input');
    let currentValue = parseFloat(input.value) || 0;

    // Get appropriate increment for current dose level
    const increment = getIncrementForDose(currentValue);

    // Adjust by increment
    currentValue += direction * increment;

    // Ensure non-negative
    if (currentValue < 0) currentValue = 0;

    // Round to appropriate precision
    const precision = getIncrementForDose(currentValue);
    currentValue = roundToPrecision(currentValue, precision);

    // Determine decimal places needed
    let decimalPlaces = 1;
    if (precision === 0.025) decimalPlaces = 3;
    else if (precision === 0.05) decimalPlaces = 2;

    input.value = currentValue.toFixed(decimalPlaces);
    updateGHDoseEquivalent(currentValue);
}

// GH Dose button event listeners
document.getElementById('gh-dose-minus').addEventListener('click', () => {
    adjustGHDose(-1);
});

document.getElementById('gh-dose-plus').addEventListener('click', () => {
    adjustGHDose(1);
});

// =====================================
// GROWTH CHARTS FEATURE
// =====================================

// Store calculation results and chart instance
let calculationResults = null;
let currentChartInstance = null;
let isLoadingChart = false; // Flag to prevent overlapping chart loads

// Store patient data for chart requests
let currentPatientData = {
    sex: null,
    reference: null,
    age: null,
    birthDate: null,
    measurementDate: null,
    measurements: {
        height: null,
        weight: null,
        bmi: null,
        ofc: null
    },
    previousMeasurements: {
        height: null,
        date: null
    }
};

// Show Charts Button Click Handler
document.getElementById('showChartsBtn').addEventListener('click', () => {
    // Show charts section
    document.getElementById('charts-section').classList.add('show');

    // Hide the show charts button
    document.getElementById('show-charts-container').style.display = 'none';

    // Disable tabs for measurements that were not provided
    const heightTab = document.querySelector('.chart-tab[data-measurement="height"]');
    const weightTab = document.querySelector('.chart-tab[data-measurement="weight"]');
    const bmiTab = document.querySelector('.chart-tab[data-measurement="bmi"]');
    const ofcTab = document.querySelector('.chart-tab[data-measurement="ofc"]');

    // Height tab
    if (!currentPatientData.measurements.height || currentPatientData.measurements.height.value === null) {
        heightTab.disabled = true;
        heightTab.title = 'Height not provided in calculation';
    } else {
        heightTab.disabled = false;
        heightTab.title = '';
    }

    // Weight tab
    if (!currentPatientData.measurements.weight || currentPatientData.measurements.weight.value === null) {
        weightTab.disabled = true;
        weightTab.title = 'Weight not provided in calculation';
    } else {
        weightTab.disabled = false;
        weightTab.title = '';
    }

    // BMI tab (requires both height and weight)
    if (!currentPatientData.measurements.bmi || currentPatientData.measurements.bmi.value === null) {
        bmiTab.disabled = true;
        bmiTab.title = 'BMI requires both height and weight';
    } else {
        bmiTab.disabled = false;
        bmiTab.title = '';
    }

    // OFC tab
    if (!currentPatientData.measurements.ofc || currentPatientData.measurements.ofc.value === null) {
        ofcTab.disabled = true;
        ofcTab.title = 'OFC not provided in calculation';
    } else {
        ofcTab.disabled = false;
        ofcTab.title = '';
    }

    // Find first enabled tab and load it by default
    const firstEnabledTab = document.querySelector('.chart-tab:not([disabled])');
    if (firstEnabledTab) {
        document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
        firstEnabledTab.classList.add('active');

        // Show appropriate age range selector based on chart type
        showAgeRangeSelectorForMeasurement(firstEnabledTab.dataset.measurement);

        loadChart(firstEnabledTab.dataset.measurement);
    }

    // Scroll to charts section
    document.getElementById('charts-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Close Charts Button Click Handler
document.getElementById('closeChartsBtn').addEventListener('click', () => {
    // Hide charts section
    document.getElementById('charts-section').classList.remove('show');

    // Show the show charts button again
    document.getElementById('show-charts-container').style.display = 'block';

    // Destroy chart instance to free memory safely
    if (currentChartInstance) {
        try {
            currentChartInstance.destroy();
        } catch (e) {
            console.error('Error destroying chart on close:', e);
        }
        currentChartInstance = null;
    }

    // Scroll back to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Chart Tab Switching
document.querySelectorAll('.chart-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        // Don't do anything if tab is disabled
        if (e.target.disabled) {
            return;
        }

        const measurement = e.target.dataset.measurement;

        // Update active tab styling
        document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');

        // Show/hide age range selector based on measurement type
        showAgeRangeSelectorForMeasurement(measurement);

        // Load corresponding chart
        loadChart(measurement);
    });
});

// Helper function to show/hide appropriate age range selector
function showAgeRangeSelectorForMeasurement(measurement) {
    // Hide all age range selectors
    document.getElementById('heightAgeRangeSelector').style.display = 'none';
    document.getElementById('weightAgeRangeSelector').style.display = 'none';
    document.getElementById('bmiAgeRangeSelector').style.display = 'none';
    document.getElementById('ofcAgeRangeSelector').style.display = 'none';

    // Get patient age from current data
    const patientAge = calculationResults?.age_years || 0;

    // Set default age range based on patient age (for children 2 and under, default to 0-2 years)
    if (measurement === 'height') {
        document.getElementById('heightAgeRangeSelector').style.display = 'flex';

        // Set default based on age
        const heightRanges = document.querySelectorAll('input[name="height_age_range"]');
        heightRanges.forEach(radio => radio.checked = false);

        if (patientAge <= 2) {
            document.querySelector('input[name="height_age_range"][value="0-2"]').checked = true;
        } else {
            document.querySelector('input[name="height_age_range"][value="0-18"]').checked = true;
        }
    } else if (measurement === 'weight') {
        document.getElementById('weightAgeRangeSelector').style.display = 'flex';

        // Set default based on age
        const weightRanges = document.querySelectorAll('input[name="weight_age_range"]');
        weightRanges.forEach(radio => radio.checked = false);

        if (patientAge <= 2) {
            document.querySelector('input[name="weight_age_range"][value="0-2"]').checked = true;
        } else {
            document.querySelector('input[name="weight_age_range"][value="0-18"]').checked = true;
        }
    } else if (measurement === 'bmi') {
        document.getElementById('bmiAgeRangeSelector').style.display = 'flex';
    } else if (measurement === 'ofc') {
        document.getElementById('ofcAgeRangeSelector').style.display = 'flex';
    }
}

// Age Range Selection Handlers for all chart types
document.querySelectorAll('input[name="height_age_range"]').forEach(radio => {
    radio.addEventListener('change', () => loadChart('height'));
});

document.querySelectorAll('input[name="weight_age_range"]').forEach(radio => {
    radio.addEventListener('change', () => loadChart('weight'));
});

document.querySelectorAll('input[name="bmi_age_range"]').forEach(radio => {
    radio.addEventListener('change', () => loadChart('bmi'));
});

document.querySelectorAll('input[name="ofc_age_range"]').forEach(radio => {
    radio.addEventListener('change', () => loadChart('ofc'));
});

/**
 * Load and render a growth chart for the specified measurement type
 * @param {string} measurementMethod - 'height', 'weight', 'bmi', or 'ofc'
 */
async function loadChart(measurementMethod) {
    // Prevent overlapping chart loads
    if (isLoadingChart) {
        console.log('Chart already loading, skipping request');
        return;
    }

    isLoadingChart = true;
    const loadingEl = document.getElementById('chartLoading');
    const canvasEl = document.getElementById('growthChart');

    // Show loading indicator
    loadingEl.classList.add('show');

    try {
        // Destroy existing chart instance safely
        if (currentChartInstance) {
            try {
                currentChartInstance.destroy();
            } catch (e) {
                console.error('Error destroying chart:', e);
            }
            currentChartInstance = null;
        }

        // Clear the canvas
        const ctx = canvasEl.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
        }

        // Fetch chart data from backend
        const response = await fetch('/chart-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reference: currentPatientData.reference,
                measurement_method: measurementMethod,
                sex: currentPatientData.sex
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load chart data');
        }

        // Check if we have centile data
        if (!data.centiles || data.centiles.length === 0) {
            throw new Error('No chart data available for this combination');
        }

        // Prepare patient measurement points
        const patientData = preparePatientData(measurementMethod);

        // Render the growth chart
        currentChartInstance = renderGrowthChart(
            canvasEl,
            data.centiles,
            patientData,
            measurementMethod
        );

    } catch (error) {
        console.error('Chart loading error:', error);
        alert('Failed to load growth chart: ' + error.message);
    } finally {
        // Hide loading indicator
        loadingEl.classList.remove('show');
        // Reset loading flag
        isLoadingChart = false;
    }
}

/**
 * Prepare patient measurement data points for plotting
 * @param {string} measurementMethod - 'height', 'weight', 'bmi', or 'ofc'
 * @returns {Array} Array of patient data points with {x, y, label, isCurrent}
 */
function preparePatientData(measurementMethod) {
    const measurement = currentPatientData.measurements[measurementMethod];
    const patientPoints = [];

    // Check if measurement exists and has a value
    if (!measurement || measurement.value === null) {
        return patientPoints;
    }

    // Add current measurement point with centile and SDS
    patientPoints.push({
        x: currentPatientData.age,
        y: measurement.value,
        label: 'Current',
        isCurrent: true,
        centile: measurement.centile,
        sds: measurement.sds
    });

    // Add corrected age point if gestation correction was applied
    const correctedKey = `${measurementMethod}_corrected`;
    const correctedMeasurement = currentPatientData[correctedKey];
    if (correctedMeasurement && correctedMeasurement.age !== undefined) {
        patientPoints.push({
            x: correctedMeasurement.age,
            y: correctedMeasurement.value,
            label: 'Corrected Age',
            isCorrected: true,
            centile: correctedMeasurement.centile,
            sds: correctedMeasurement.sds
        });
    }

    // Add previous measurement (currently only available for height)
    if (measurementMethod === 'height' && currentPatientData.previousMeasurements.height && currentPatientData.previousMeasurements.date) {
        // Calculate previous age in decimal years
        const birthDate = new Date(currentPatientData.birthDate);
        const previousDate = new Date(currentPatientData.previousMeasurements.date);

        // Calculate age at previous measurement
        const diffTime = previousDate - birthDate;
        const diffYears = diffTime / (1000 * 60 * 60 * 24 * 365.25);

        // Only add if previous age is valid (positive and less than current)
        if (diffYears > 0 && diffYears < currentPatientData.age) {
            patientPoints.push({
                x: diffYears,
                y: currentPatientData.previousMeasurements.height,
                label: 'Previous',
                isCurrent: false,
                centile: currentPatientData.previousMeasurements.centile,
                sds: currentPatientData.previousMeasurements.sds
            });
        }
    }

    return patientPoints;
}

/**
 * Render a growth chart using Chart.js
 * @param {HTMLCanvasElement} canvas - Canvas element to render on
 * @param {Array} centiles - Array of centile curve data
 * @param {Array} patientData - Array of patient measurement points
 * @param {string} measurementMethod - Type of measurement being plotted
 * @returns {Chart} Chart.js instance
 */
function renderGrowthChart(canvas, centiles, patientData, measurementMethod) {
    const datasets = [];

    // Determine color based on sex (blue for boys, pink for girls)
    const sex = currentPatientData.sex;
    const centileColor = sex === 'male' ? '#3182ce' : '#ec4899'; // Blue for boys, pink for girls

    // Get age range settings based on measurement type
    let minAge = 0; // default
    let maxAge = 18; // default
    let mphAge = 18; // default (for height only)
    let showMph = true; // default (for height only)

    // Determine which age range selector to use
    const rangeInputName = `${measurementMethod}_age_range`;
    const selectedRange = document.querySelector(`input[name="${rangeInputName}"]:checked`);

    if (selectedRange) {
        minAge = parseInt(selectedRange.dataset.min);
        maxAge = parseInt(selectedRange.dataset.max);

        // MPH settings only apply to height charts
        if (measurementMethod === 'height') {
            const mphAgeValue = selectedRange.dataset.mphAge;
            showMph = mphAgeValue !== 'none';
            if (showMph) {
                mphAge = parseInt(mphAgeValue);
            }
        }
    }

    // Add centile curve datasets
    centiles.forEach(centile => {
        const isMedian = centile.centile === 50;
        const isDotted = [0.4, 9, 91, 99.6].includes(centile.centile);

        // Filter centile data based on age range for all chart types
        let centileData = centile.data.map(point => ({x: point.x, y: point.y}));
        centileData = centileData.filter(point => point.x >= minAge && point.x <= maxAge);

        datasets.push({
            label: `${centile.centile}th centile`,
            data: centileData,
            borderColor: centileColor,
            backgroundColor: 'transparent',
            borderWidth: isMedian ? 2 : 1.5,
            borderDash: isDotted ? [5, 5] : [],
            pointRadius: 0,
            pointHoverRadius: 0,
            tension: 0.4,
            fill: false
        });
    });

    // Add patient measurement points
    if (patientData.length > 0) {
        // Separate current, corrected, and previous measurements
        const currentPoints = patientData.filter(p => p.isCurrent);
        const correctedPoints = patientData.filter(p => p.isCorrected);
        const previousPoints = patientData.filter(p => !p.isCurrent && !p.isCorrected);

        // Add dotted line connecting corrected and chronological points (if both exist)
        if (correctedPoints.length > 0 && currentPoints.length > 0) {
            // Create a line dataset with both points
            const lineData = [
                {
                    x: correctedPoints[0].x,
                    y: correctedPoints[0].y
                },
                {
                    x: currentPoints[0].x,
                    y: currentPoints[0].y
                }
            ];

            datasets.push({
                label: 'Correction Line',
                data: lineData,
                borderColor: centileColor,
                borderWidth: 2,
                borderDash: [5, 5],  // Dotted line pattern
                pointRadius: 0,  // No points on the line itself
                showLine: true,
                fill: false,
                tension: 0  // Straight line
            });
        }

        // Add current measurement
        if (currentPoints.length > 0) {
            datasets.push({
                label: 'Current Measurement',
                data: currentPoints.map(p => ({
                    x: p.x,
                    y: p.y,
                    centile: p.centile,
                    sds: p.sds
                })),
                backgroundColor: centileColor,
                borderColor: '#ffffff',
                borderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                showLine: false
            });
        }

        // Add corrected age measurement (cross to distinguish from chronological)
        if (correctedPoints.length > 0) {
            datasets.push({
                label: 'Corrected Age',
                data: correctedPoints.map(p => ({
                    x: p.x,
                    y: p.y,
                    centile: p.centile,
                    sds: p.sds
                })),
                pointStyle: 'cross',
                backgroundColor: centileColor,
                borderColor: centileColor,
                borderWidth: 2,
                pointRadius: 8,
                pointHoverRadius: 10,
                rotation: 45,  // Rotate to make an X shape
                showLine: false
            });
        }

        // Add previous measurement
        if (previousPoints.length > 0) {
            datasets.push({
                label: 'Previous Measurement',
                data: previousPoints.map(p => ({
                    x: p.x,
                    y: p.y,
                    centile: p.centile,
                    sds: p.sds
                })),
                backgroundColor: '#f6ad55',
                borderColor: '#ffffff',
                borderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                showLine: false
            });
        }
    }

    // Add mid-parental height target range (only for height charts when enabled)
    if (measurementMethod === 'height' && showMph && calculationResults && calculationResults.mid_parental_height) {
        const mph = calculationResults.mid_parental_height;
        const targetAge = mphAge; // Use age from selected range
        // Use complementary colors that stand out clearly (dark teal for boys, dark magenta for girls)
        const mphColor = sex === 'male' ? '#059669' : '#a21caf';

        // Ensure all required values are present
        if (mph.target_range_lower && mph.target_range_upper && mph.mid_parental_height) {
            // Add vertical line showing target range
            datasets.push({
                label: 'Mid-Parental Height Target Range',
                data: [
                    { x: targetAge, y: parseFloat(mph.target_range_lower) },
                    { x: targetAge, y: parseFloat(mph.target_range_upper) }
                ],
                borderColor: mphColor,
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 0,
                showLine: true,
                tension: 0
            });

            // Add horizontal marker for mid-parental height
            // Only the center point (index 1) will have a tooltip
            datasets.push({
                label: 'Mid-Parental Height',
                data: [
                    { x: targetAge - 0.3, y: parseFloat(mph.mid_parental_height) },
                    { x: targetAge, y: parseFloat(mph.mid_parental_height) },
                    { x: targetAge + 0.3, y: parseFloat(mph.mid_parental_height) }
                ],
                borderColor: mphColor,
                backgroundColor: 'transparent',
                borderWidth: 2.5,
                pointRadius: [0, 3, 0], // Only center point visible
                pointHoverRadius: [0, 6, 0], // Only center point hoverable
                pointBackgroundColor: mphColor,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 1,
                showLine: true,
                tension: 0
            });
        }
    }

    // Define axis labels for each measurement type
    const axisLabels = {
        height: { x: 'Age (years)', y: 'Height (cm)' },
        weight: { x: 'Age (years)', y: 'Weight (kg)' },
        bmi: { x: 'Age (years)', y: 'BMI (kg/m²)' },
        ofc: { x: 'Age (years)', y: 'Head Circumference (cm)' }
    };

    const labels = axisLabels[measurementMethod] || { x: 'Age (years)', y: 'Value' };

    // Define chart title
    const titles = {
        height: 'Height',
        weight: 'Weight',
        bmi: 'BMI',
        ofc: 'Head Circumference (OFC)'
    };

    const measurementTitle = titles[measurementMethod] || measurementMethod.toUpperCase();

    // Format reference title with proper capitalization
    let referenceTitle;
    if (currentPatientData.reference === 'uk-who') {
        referenceTitle = 'UK-WHO';
    } else if (currentPatientData.reference === 'cdc') {
        referenceTitle = 'CDC';
    } else {
        referenceTitle = currentPatientData.reference.split('-').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    // Calculate x-axis min and max from centile data
    let minX = Infinity;
    let maxX = -Infinity;

    centiles.forEach(centile => {
        if (centile.data && centile.data.length > 0) {
            centile.data.forEach(point => {
                if (point.x < minX) minX = point.x;
                if (point.x > maxX) maxX = point.x;
            });
        }
    });

    // If no valid range found, use defaults
    if (minX === Infinity || maxX === -Infinity) {
        minX = 0;
        maxX = 20;
    }

    // Override min/max based on selected age range
    minX = minAge;
    if (measurementMethod === 'height' && showMph) {
        // Add 0.5 to accommodate mid-parental height marker if shown
        maxX = maxAge + 0.5;
    } else {
        maxX = maxAge;
    }

    // Generate explicit tick values - only integers from min to max
    const tickValues = [];
    for (let i = minAge; i <= maxAge; i++) {
        tickValues.push(i);
    }

    // Create Chart.js chart
    const chart = new Chart(canvas, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'point',
                intersect: true
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    displayColors: false,  // Remove colored box from tooltip
                    filter: function(tooltipItem) {
                        // Show tooltips for patient measurements, corrected age, and mid-parental height
                        if (!tooltipItem || !tooltipItem.dataset || !tooltipItem.dataset.label) {
                            return false;
                        }
                        return tooltipItem.dataset.label.includes('Measurement') ||
                               tooltipItem.dataset.label.includes('Corrected Age') ||
                               tooltipItem.dataset.label.includes('Mid-Parental');
                    },
                    callbacks: {
                        title: function(context) {
                            if (!context || context.length === 0 || !context[0].dataset) {
                                return '';
                            }
                            return context[0].dataset.label;
                        },
                        label: function(context) {
                            if (!context || !context.parsed) {
                                return '';
                            }

                            const datasetLabel = context.dataset.label;

                            // Special handling for mid-parental height markers
                            if (datasetLabel && datasetLabel.includes('Mid-Parental')) {
                                const lines = [];

                                if (datasetLabel === 'Mid-Parental Height') {
                                    if (calculationResults && calculationResults.mid_parental_height) {
                                        const mph = calculationResults.mid_parental_height;
                                        lines.push(`Mid-Parental Height: ${mph.mid_parental_height} cm`);
                                        lines.push(`Centile: ${mph.mid_parental_height_centile}%`);
                                        lines.push(`Target Range: ${mph.target_range_lower}-${mph.target_range_upper} cm`);
                                    }
                                } else if (datasetLabel === 'Mid-Parental Height Target Range') {
                                    if (calculationResults && calculationResults.mid_parental_height) {
                                        const mph = calculationResults.mid_parental_height;
                                        const value = context.parsed.y.toFixed(1);
                                        lines.push(`Range Limit: ${value} cm`);
                                        lines.push(`Full Range: ${mph.target_range_lower}-${mph.target_range_upper} cm`);
                                    }
                                }

                                return lines;
                            }

                            // Get data from the raw data point
                            const dataPoint = context.raw;
                            const age = context.parsed.x.toFixed(2);
                            const value = context.parsed.y.toFixed(1);

                            // Build tooltip lines for patient measurements
                            const lines = [];
                            lines.push(`Age: ${age} years`);
                            lines.push(`${labels.y}: ${value}`);

                            // Add centile if available
                            if (dataPoint.centile !== null && dataPoint.centile !== undefined) {
                                lines.push(`Centile: ${dataPoint.centile.toFixed(2)}%`);
                            }

                            // Add SDS if available
                            if (dataPoint.sds !== null && dataPoint.sds !== undefined) {
                                lines.push(`SDS: ${dataPoint.sds.toFixed(2)}`);
                            }

                            return lines;
                        }
                    }
                },
                title: {
                    display: true,
                    text: `${measurementTitle} (${referenceTitle})`,
                    font: { size: 16, weight: 'bold' },
                    color: '#333',
                    padding: { top: 10, bottom: 20 }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    min: minX,
                    max: maxX,
                    title: {
                        display: true,
                        text: labels.x,
                        font: { size: 14, weight: 'bold' },
                        color: '#555'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: true
                    },
                    afterBuildTicks: function(axis) {
                        // Replace auto-generated ticks with our custom integer ticks
                        axis.ticks = tickValues.map(value => ({ value }));
                    },
                    ticks: {
                        font: { size: 12 },
                        color: '#666',
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: labels.y,
                        font: { size: 14, weight: 'bold' },
                        color: '#555'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: true
                    },
                    ticks: {
                        font: { size: 12 },
                        color: '#666'
                    }
                }
            }
        }
    });

    return chart;
}
