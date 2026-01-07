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

    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const ofc = document.getElementById('ofc').value;

    // Validate that at least one measurement is provided
    if (!weight && !height && !ofc) {
        showError('At least one measurement (weight, height, or OFC) is required.');
        return;
    }

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

    document.getElementById('bsa').textContent = results.bsa !== null ? `${results.bsa} m²` : 'N/A';

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

    // Store previous measurements (currently only height)
    const previousHeight = document.getElementById('previous_height').value;
    const previousDate = document.getElementById('previous_date').value;
    currentPatientData.previousMeasurements = {
        height: previousHeight ? parseFloat(previousHeight) : null,
        date: previousDate || null
    };

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

        // Load corresponding chart
        loadChart(measurement);
    });
});

/**
 * Load and render a growth chart for the specified measurement type
 * @param {string} measurementMethod - 'height', 'weight', 'bmi', or 'ofc'
 */
async function loadChart(measurementMethod) {
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
                centile: null,  // Previous measurements don't have centile data
                sds: null
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

    // Add centile curve datasets
    centiles.forEach(centile => {
        const isMedian = centile.centile === 50;
        const isDotted = [0.4, 9, 91, 99.6].includes(centile.centile);

        datasets.push({
            label: `${centile.centile}th centile`,
            data: centile.data.map(point => ({x: point.x, y: point.y})),
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
        // Separate current and previous measurements
        const currentPoints = patientData.filter(p => p.isCurrent);
        const previousPoints = patientData.filter(p => !p.isCurrent);

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
    const referenceTitle = currentPatientData.reference.split('-').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');


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
                    filter: function(tooltipItem) {
                        // Only show tooltips for patient measurements
                        if (!tooltipItem || !tooltipItem.dataset || !tooltipItem.dataset.label) {
                            return false;
                        }
                        return tooltipItem.dataset.label.includes('Measurement');
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

                            // Get data from the raw data point
                            const dataPoint = context.raw;
                            const age = context.parsed.x.toFixed(2);
                            const value = context.parsed.y.toFixed(1);

                            // Build tooltip lines
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
                    text: `${measurementTitle} Growth Chart (${referenceTitle})`,
                    font: { size: 16, weight: 'bold' },
                    color: '#333',
                    padding: { top: 10, bottom: 20 }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    min: -0.0385,  // -2 weeks
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
                    ticks: {
                        font: { size: 12 },
                        color: '#666'
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
