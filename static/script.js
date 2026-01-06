// Convert feet and inches to cm
function feetInchesToCm(feet, inches) {
    const totalInches = (parseFloat(feet) || 0) * 12 + (parseFloat(inches) || 0);
    return totalInches * 2.54;
}

// Get parental height in cm based on selected units
function getParentalHeightInCm(parent) {
    const units = document.querySelector('input[name="height_units"]:checked')?.value;

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

    errorDiv.classList.remove('show');
    resultsDiv.classList.remove('show');

    const maternalHeightCm = getParentalHeightInCm('maternal');
    const paternalHeightCm = getParentalHeightInCm('paternal');

    const formData = {
        sex: document.querySelector('input[name="sex"]:checked')?.value,
        birth_date: document.getElementById('birth_date').value,
        measurement_date: document.getElementById('measurement_date').value,
        weight: document.getElementById('weight').value,
        height: document.getElementById('height').value,
        ofc: document.getElementById('ofc').value,
        previous_date: document.getElementById('previous_date').value,
        previous_height: document.getElementById('previous_height').value,
        maternal_height: maternalHeightCm,
        paternal_height: paternalHeightCm,
        reference: document.getElementById('reference').value
    };

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
        } else {
            showError(data.error || 'An error occurred during calculation');
        }
    } catch (error) {
        showError('Failed to connect to server: ' + error.message);
    }
});

function displayResults(results) {
    // Display reference note
    const referenceSelect = document.getElementById('reference');
    const selectedOption = referenceSelect.options[referenceSelect.selectedIndex].text;
    document.getElementById('reference-note').textContent = `Using ${selectedOption} growth reference`;

    document.getElementById('age').textContent = `${results.age_years} years`;

    document.getElementById('weight-value').textContent = `${results.weight.value} kg`;
    document.getElementById('weight-centile').textContent = results.weight.centile !== null ? `${results.weight.centile}%` : 'N/A';
    document.getElementById('weight-sds').textContent = results.weight.sds !== null ? results.weight.sds : 'N/A';

    document.getElementById('height-value').textContent = `${results.height.value} cm`;
    document.getElementById('height-centile').textContent = results.height.centile !== null ? `${results.height.centile}%` : 'N/A';
    document.getElementById('height-sds').textContent = results.height.sds !== null ? results.height.sds : 'N/A';

    document.getElementById('bmi-value').textContent = results.bmi.value;
    document.getElementById('bmi-centile').textContent = results.bmi.centile !== null ? `${results.bmi.centile}%` : 'N/A';
    document.getElementById('bmi-sds').textContent = results.bmi.sds !== null ? results.bmi.sds : 'N/A';

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
        } else if (results.height_velocity.message) {
            heightVelocityValue.textContent = 'Not calculated';
            heightVelocityMessage.textContent = results.height_velocity.message;
        }
        heightVelocityItem.style.display = 'block';
    } else {
        heightVelocityItem.style.display = 'none';
    }

    document.getElementById('bsa').textContent = results.bsa !== null ? `${results.bsa} m²` : 'N/A';

    // Display GH dose with interactive adjuster
    const ghDoseItem = document.getElementById('gh-dose-item');
    if (results.gh_dose !== null && results.bsa !== null) {
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
});

// Toggle between cm and ft/in inputs for parental heights
function toggleHeightUnits() {
    const units = document.querySelector('input[name="height_units"]:checked')?.value;
    const isCm = units === 'cm';

    // Toggle maternal height inputs
    document.getElementById('maternal-height-cm').style.display = isCm ? 'block' : 'none';
    document.getElementById('maternal-height-ft').style.display = isCm ? 'none' : 'block';

    // Toggle paternal height inputs
    document.getElementById('paternal-height-cm').style.display = isCm ? 'block' : 'none';
    document.getElementById('paternal-height-ft').style.display = isCm ? 'none' : 'block';
}

// Add event listeners to height unit radio buttons
document.querySelectorAll('input[name="height_units"]').forEach(radio => {
    radio.addEventListener('change', toggleHeightUnits);
});

// Set measurement date to today on page load
document.getElementById('measurement_date').valueAsDate = new Date();

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
    if (dose < 0.25) {
        return 0.025;  // 0.025 mg increments for 0-0.25 mg
    } else if (dose < 1.5) {
        return 0.05;   // 0.05 mg increments for 0.25-1.5 mg
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
