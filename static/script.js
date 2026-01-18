// Dark Mode Functionality
function initDarkMode() {
    const htmlElement = document.documentElement;
    const themeToggleBtn = document.getElementById('themeToggle');
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');

    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Set initial theme
    let currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    setTheme(currentTheme);

    // Theme toggle click handler
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(currentTheme);
            localStorage.setItem('theme', currentTheme);

            // Reload chart if currently displayed to update colors
            reloadChartIfVisible();
        });
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('theme')) {
            currentTheme = e.matches ? 'dark' : 'light';
            setTheme(currentTheme);
        }
    });

    function setTheme(theme) {
        if (theme === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            htmlElement.setAttribute('data-theme', 'light');
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }
}

// Initialize dark mode as early as possible
initDarkMode();

/**
 * Reload chart if currently visible to update theme colors
 */
function reloadChartIfVisible() {
    // Check if charts section is visible
    const chartsSection = document.getElementById('chartsSection');
    if (chartsSection && chartsSection.classList.contains('show')) {
        // Find the active chart tab
        const activeTab = document.querySelector('.chart-tab.active');
        if (activeTab) {
            const measurementType = activeTab.getAttribute('data-chart');
            if (measurementType && currentPatientData) {
                // Reload the chart with new theme colors
                loadChart(measurementType);
            }
        }
    }
}

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
        previous_measurements: getPreviousMeasurements(),
        bone_age_assessments: getBoneAgeAssessments(),
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
            // Store results globally for PDF export
            window.calculationResults = data.results;

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

    let ageDisplay = `${calendarAge.years}y ${calendarAge.months}m ${calendarAge.days}d<br><span style="font-size: 0.8em; color: #666;">(${results.age_years} years)</span>`;

    // If gestation correction was applied, show corrected age as well
    if (results.gestation_correction_applied && results.corrected_age_calendar) {
        const correctedAge = results.corrected_age_calendar;
        ageDisplay += `<br><br><span style="font-size: 0.85em; color: #667eea; font-weight: 600;">Corrected Age:</span><br>`;
        ageDisplay += `${correctedAge.years}y ${correctedAge.months}m ${correctedAge.days}d`;
        ageDisplay += `<br><span style="font-size: 0.8em; color: #666;">(${results.corrected_age_years} years)</span>`;
    }

    ageElement.innerHTML = ageDisplay;

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

        // Display percentage of median BMI (advanced mode only)
        const percentageMedianElement = document.getElementById('bmi-percentage-median');
        if (results.bmi.percentage_median !== null && results.bmi.percentage_median !== undefined) {
            percentageMedianElement.textContent = `${results.bmi.percentage_median}%`;
        } else {
            percentageMedianElement.textContent = 'N/A';
        }

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

    // Only show height velocity box if there's an actual calculated value
    if (results.height_velocity !== null &&
        results.height_velocity !== undefined &&
        results.height_velocity.value !== null &&
        results.height_velocity.value !== undefined) {
        heightVelocityValue.textContent = `${results.height_velocity.value} cm/year`;
        heightVelocityMessage.textContent = '';
        heightVelocityMessage.style.display = 'none';
        heightVelocityItem.style.display = 'block';
    } else {
        // Hide if no value (whether there's a message or not)
        heightVelocityValue.textContent = '';
        heightVelocityMessage.textContent = '';
        heightVelocityMessage.style.display = 'none';
        heightVelocityItem.style.display = 'none';
    }

    // Display BSA with method in label, not value
    const bsaItem = document.getElementById('bsa-item');
    if (results.bsa !== null) {
        document.getElementById('bsa').textContent = `${results.bsa} m²`;
        // Update label to show method used
        const bsaLabel = document.getElementById('bsa-label');
        if (results.bsa_method) {
            bsaLabel.textContent = `Body Surface Area (${results.bsa_method})`;
        } else {
            bsaLabel.textContent = 'Body Surface Area (Boyd)';
        }
        bsaItem.style.display = 'block';
    } else {
        bsaItem.style.display = 'none';
    }

    // Display GH dose with interactive adjuster (only if child is on GH treatment)
    const ghDoseItem = document.getElementById('gh-dose-item');
    const onGhTreatment = document.getElementById('on_gh_treatment')?.checked || false;
    if (results.gh_dose !== null && results.bsa !== null && results.weight !== null && onGhTreatment) {
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

    // Store all previous measurements with their centile/SDS data from backend
    currentPatientData.previousMeasurements = results.previous_measurements || [];

    // Store corrected age measurements if gestation correction was applied
    currentPatientData.weight_corrected = results.weight_corrected || null;
    currentPatientData.height_corrected = results.height_corrected || null;
    currentPatientData.bmi_corrected = results.bmi_corrected || null;
    currentPatientData.ofc_corrected = results.ofc_corrected || null;

    // Store bone age height data
    currentPatientData.boneAgeHeight = results.bone_age_height || null;
    currentPatientData.boneAgeAssessments = results.bone_age_assessments || [];

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

// Previous Measurements Table Management
let previousMeasurementRowCounter = 0;
let previousMeasurementsExpanded = false;

function expandPreviousMeasurementsSection() {
    if (!previousMeasurementsExpanded) {
        document.getElementById('previous-measurements-collapsed').classList.add('hidden');
        document.getElementById('previous-measurements-expanded').classList.add('visible');
        previousMeasurementsExpanded = true;
    }
}

function addPreviousMeasurementRow() {
    expandPreviousMeasurementsSection();
    const tbody = document.getElementById('previousMeasurementsBody');
    const rowId = `prev-row-${previousMeasurementRowCounter++}`;

    const row = document.createElement('tr');
    row.id = rowId;
    row.innerHTML = `
        <td>
            <input type="date" class="prev-measurement-date" data-row-id="${rowId}" />
        </td>
        <td>
            <input type="number" class="prev-measurement-height" step="0.1" min="0" placeholder="e.g., 120.5" data-row-id="${rowId}" />
        </td>
        <td>
            <input type="number" class="prev-measurement-weight" step="0.1" min="0" placeholder="e.g., 25.0" data-row-id="${rowId}" />
        </td>
        <td>
            <input type="number" class="prev-measurement-ofc" step="0.1" min="0" placeholder="e.g., 50.0" data-row-id="${rowId}" />
        </td>
        <td>
            <button type="button" class="btn-remove-measurement" onclick="removePreviousMeasurementRow('${rowId}')">
                <span class="material-symbols-outlined">delete</span>
                Remove
            </button>
        </td>
    `;

    tbody.appendChild(row);
}

function removePreviousMeasurementRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
    }
}

function getPreviousMeasurements() {
    const rows = document.querySelectorAll('#previousMeasurementsBody tr');
    const measurements = [];

    rows.forEach(row => {
        const date = row.querySelector('.prev-measurement-date')?.value;
        const height = row.querySelector('.prev-measurement-height')?.value;
        const weight = row.querySelector('.prev-measurement-weight')?.value;
        const ofc = row.querySelector('.prev-measurement-ofc')?.value;

        // Only include row if at least date and one measurement is provided
        if (date && (height || weight || ofc)) {
            measurements.push({
                date: date,
                height: height ? parseFloat(height) : null,
                weight: weight ? parseFloat(weight) : null,
                ofc: ofc ? parseFloat(ofc) : null
            });
        }
    });

    return measurements;
}

function exportPreviousMeasurementsToCSV() {
    const measurements = getPreviousMeasurements();

    if (measurements.length === 0) {
        showToast('No previous measurements to export', 'error');
        return;
    }

    // Create CSV content
    const headers = ['Date', 'Height (cm)', 'Weight (kg)', 'OFC (cm)'];
    const csvRows = [headers.join(',')];

    measurements.forEach(m => {
        const row = [
            m.date,
            m.height !== null ? m.height : '',
            m.weight !== null ? m.weight : '',
            m.ofc !== null ? m.ofc : ''
        ];
        csvRows.push(row.join(','));
    });

    const csvContent = csvRows.join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `previous-measurements-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast('CSV exported successfully', 'success');
}

function importPreviousMeasurementsFromCSV(file) {
    const reader = new FileReader();

    reader.onload = function(e) {
        try {
            const csvContent = e.target.result;
            const rows = csvContent.split('\n').filter(row => row.trim());

            if (rows.length < 2) {
                showToast('CSV file is empty or invalid', 'error');
                return;
            }

            // Expand section before importing
            expandPreviousMeasurementsSection();

            // Clear existing table
            document.getElementById('previousMeasurementsBody').innerHTML = '';
            previousMeasurementRowCounter = 0;

            // Parse CSV (skip header row)
            let importedCount = 0;
            for (let i = 1; i < rows.length; i++) {
                const columns = rows[i].split(',').map(col => col.trim());

                if (columns.length < 4) continue;

                const date = columns[0];
                const height = columns[1];
                const weight = columns[2];
                const ofc = columns[3];

                // Validate date format (YYYY-MM-DD)
                if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                    continue;
                }

                // Add row to table
                addPreviousMeasurementRow();

                // Get the most recently added row
                const rows = document.querySelectorAll('#previousMeasurementsBody tr');
                const lastRow = rows[rows.length - 1];

                // Populate fields
                if (lastRow) {
                    const dateInput = lastRow.querySelector('.prev-measurement-date');
                    const heightInput = lastRow.querySelector('.prev-measurement-height');
                    const weightInput = lastRow.querySelector('.prev-measurement-weight');
                    const ofcInput = lastRow.querySelector('.prev-measurement-ofc');

                    if (dateInput) dateInput.value = date;
                    if (heightInput && height) heightInput.value = height;
                    if (weightInput && weight) weightInput.value = weight;
                    if (ofcInput && ofc) ofcInput.value = ofc;

                    importedCount++;
                }
            }

            if (importedCount > 0) {
                showToast(`Successfully imported ${importedCount} measurement(s)`, 'success');
            } else {
                showToast('No valid measurements found in CSV', 'error');
            }
        } catch (error) {
            console.error('Error importing CSV:', error);
            showToast('Failed to import CSV: ' + error.message, 'error');
        }
    };

    reader.onerror = function() {
        showToast('Failed to read CSV file', 'error');
    };

    reader.readAsText(file);
}

// Add event listener for Add Previous Measurement button
document.getElementById('addPreviousMeasurementBtn').addEventListener('click', addPreviousMeasurementRow);
document.getElementById('addPreviousMeasurementBtnExpanded').addEventListener('click', addPreviousMeasurementRow);

// Add event listeners for CSV import/export
document.getElementById('exportCsvBtn').addEventListener('click', exportPreviousMeasurementsToCSV);

document.getElementById('importCsvBtn').addEventListener('click', () => {
    document.getElementById('csvFileInput').click();
});

document.getElementById('csvFileInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        importPreviousMeasurementsFromCSV(file);
        // Reset file input so the same file can be imported again
        e.target.value = '';
    }
});

// Bone Age Assessment Management
let boneAgeRowCounter = 0;
let boneAgeExpanded = false;

function expandBoneAgeSection() {
    if (!boneAgeExpanded) {
        document.getElementById('bone-age-collapsed').classList.add('hidden');
        document.getElementById('bone-age-expanded').classList.add('visible');
        boneAgeExpanded = true;
    }
}

function addBoneAgeRow() {
    expandBoneAgeSection();
    const tbody = document.getElementById('boneAgeBody');
    const rowId = `bone-age-row-${boneAgeRowCounter++}`;

    const row = document.createElement('tr');
    row.id = rowId;
    row.innerHTML = `
        <td>
            <input type="date" class="bone-age-date" data-row-id="${rowId}" />
        </td>
        <td>
            <div class="bone-age-input-container">
                <div class="bone-age-format-toggle">
                    <button type="button" class="bone-age-format-btn active" data-format="decimal" data-row-id="${rowId}">Decimal</button>
                    <button type="button" class="bone-age-format-btn" data-format="ym" data-row-id="${rowId}">Years + Months</button>
                </div>
                <div class="bone-age-decimal-input active" data-row-id="${rowId}">
                    <input type="number" class="bone-age-decimal" step="0.1" min="0" max="18" placeholder="e.g., 8.5" data-row-id="${rowId}" />
                </div>
                <div class="bone-age-ym-input" data-row-id="${rowId}">
                    <input type="number" class="bone-age-years" min="0" max="18" placeholder="Y" data-row-id="${rowId}" />
                    <span>y</span>
                    <input type="number" class="bone-age-months" min="0" max="11" placeholder="M" data-row-id="${rowId}" />
                    <span>m</span>
                </div>
            </div>
        </td>
        <td>
            <select class="bone-age-standard" data-row-id="${rowId}">
                <option value="">Select...</option>
                <option value="greulich-pyle">Greulich & Pyle</option>
                <option value="tw3">TW3</option>
            </select>
        </td>
        <td>
            <button type="button" class="btn-remove-measurement" onclick="removeBoneAgeRow('${rowId}')">
                <span class="material-symbols-outlined">delete</span>
                Remove
            </button>
        </td>
    `;

    tbody.appendChild(row);

    // Add event listeners for format toggle buttons
    const formatBtns = row.querySelectorAll('.bone-age-format-btn');
    formatBtns.forEach(btn => {
        btn.addEventListener('click', toggleBoneAgeFormat);
    });
}

function toggleBoneAgeFormat(e) {
    const btn = e.target;
    const rowId = btn.getAttribute('data-row-id');
    const format = btn.getAttribute('data-format');
    const row = document.getElementById(rowId);

    // Update button active states
    row.querySelectorAll('.bone-age-format-btn').forEach(b => {
        b.classList.remove('active');
    });
    btn.classList.add('active');

    // Toggle input visibility
    const decimalInput = row.querySelector('.bone-age-decimal-input');
    const ymInput = row.querySelector('.bone-age-ym-input');

    if (format === 'decimal') {
        decimalInput.classList.add('active');
        ymInput.classList.remove('active');
    } else {
        decimalInput.classList.remove('active');
        ymInput.classList.add('active');
    }
}

function removeBoneAgeRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
    }
}

function getBoneAgeAssessments() {
    const rows = document.querySelectorAll('#boneAgeBody tr');
    const assessments = [];

    rows.forEach(row => {
        const rowId = row.id;
        const date = row.querySelector('.bone-age-date')?.value;
        const standard = row.querySelector('.bone-age-standard')?.value;

        // Determine which format is active
        const decimalInput = row.querySelector('.bone-age-decimal-input');
        const isDecimalActive = decimalInput?.classList.contains('active');

        let boneAge = null;

        if (isDecimalActive) {
            const decimalValue = row.querySelector('.bone-age-decimal')?.value;
            if (decimalValue) {
                boneAge = parseFloat(decimalValue);
            }
        } else {
            const years = row.querySelector('.bone-age-years')?.value;
            const months = row.querySelector('.bone-age-months')?.value;
            if (years) {
                boneAge = parseInt(years) + (months ? parseInt(months) / 12 : 0);
            }
        }

        // Only include if date, bone age, and standard are provided
        if (date && boneAge !== null && standard) {
            assessments.push({
                date: date,
                bone_age: boneAge,
                standard: standard
            });
        }
    });

    return assessments;
}

// Add event listener for Add Bone Age button
document.getElementById('addBoneAgeBtn').addEventListener('click', addBoneAgeRow);
document.getElementById('addBoneAgeBtnExpanded').addEventListener('click', addBoneAgeRow);

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

    // Clear previous measurements table
    document.getElementById('previousMeasurementsBody').innerHTML = '';
    previousMeasurementRowCounter = 0;

    // Clear bone age table
    document.getElementById('boneAgeBody').innerHTML = '';
    boneAgeRowCounter = 0;

    // Collapse previous measurements section
    document.getElementById('previous-measurements-collapsed').classList.remove('hidden');
    document.getElementById('previous-measurements-expanded').classList.remove('visible');
    previousMeasurementsExpanded = false;

    // Collapse bone age section
    document.getElementById('bone-age-collapsed').classList.remove('hidden');
    document.getElementById('bone-age-expanded').classList.remove('visible');
    boneAgeExpanded = false;

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

// Download Chart Button Click Handler
document.getElementById('downloadChartBtn').addEventListener('click', () => {
    downloadCurrentChart();
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

/**
 * Intelligently select the optimal age range for a measurement chart
 * based on the child's age and available measurements
 *
 * @param {string} measurement - 'height', 'weight', 'bmi', or 'ofc'
 * @returns {string} - The optimal age range value (e.g., '0-2', '2-18')
 */
function selectOptimalAgeRange(measurement) {
    const age = calculationResults?.age_years || 0;
    const hasMph = calculationResults?.mid_parental_height !== null && calculationResults?.mid_parental_height !== undefined;

    let optimalRange = null;

    switch(measurement) {
        case 'height':
            if (age < 2) {
                optimalRange = '0-2'; // Detailed infant view, most clinically relevant
            } else if (age < 4) {
                optimalRange = '0-4'; // Shows growth trajectory from birth
            } else {
                // For older children, show 2-18 with MPH if available
                // Otherwise show full range 0-18
                optimalRange = hasMph ? '2-18' : '0-18';
            }
            break;

        case 'weight':
            if (age < 2) {
                optimalRange = '0-2'; // Detailed infant view
            } else if (age < 4) {
                optimalRange = '0-4'; // Shows transition from infant to child
            } else {
                optimalRange = '0-18'; // Full range for context
            }
            break;

        case 'bmi':
            // BMI is most meaningful from age 2+ years
            if (age < 4) {
                optimalRange = '0-4'; // Shows early BMI pattern if needed
            } else if (age < 10) {
                optimalRange = '2-18'; // Most clinically relevant range (default)
            } else {
                optimalRange = '0-18'; // Full pattern for adolescents
            }
            break;

        case 'ofc':
            // OFC is primarily measured in young children
            if (age < 2) {
                optimalRange = '0-2'; // Most detailed and clinically relevant
            } else {
                // If still measuring OFC in older child, show full range for context
                optimalRange = '0-18';
            }
            break;
    }

    return optimalRange;
}

// Helper function to show/hide appropriate age range selector
function showAgeRangeSelectorForMeasurement(measurement) {
    // Hide all age range selectors
    document.getElementById('heightAgeRangeSelector').style.display = 'none';
    document.getElementById('weightAgeRangeSelector').style.display = 'none';
    document.getElementById('bmiAgeRangeSelector').style.display = 'none';
    document.getElementById('ofcAgeRangeSelector').style.display = 'none';

    // Show the appropriate selector for this measurement
    const selectorId = `${measurement}AgeRangeSelector`;
    const selector = document.getElementById(selectorId);

    if (selector) {
        selector.style.display = 'flex';

        // Get optimal age range for this measurement
        const optimalRange = selectOptimalAgeRange(measurement);

        // Clear all selections for this measurement first
        const rangeInputs = document.querySelectorAll(`input[name="${measurement}_age_range"]`);
        rangeInputs.forEach(radio => radio.checked = false);

        // Select the optimal range
        if (optimalRange) {
            const optimalInput = document.querySelector(`input[name="${measurement}_age_range"][value="${optimalRange}"]`);
            if (optimalInput) {
                optimalInput.checked = true;
            } else {
                // Fallback: select first available option if optimal not found
                if (rangeInputs.length > 0) {
                    rangeInputs[0].checked = true;
                }
            }
        }
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

    // Add all previous measurements for the current measurement type
    if (currentPatientData.previousMeasurements && currentPatientData.previousMeasurements.length > 0) {
        currentPatientData.previousMeasurements.forEach(prevMeasurement => {
            // Check if this previous measurement has data for the current measurement type
            const prevData = prevMeasurement[measurementMethod];
            if (prevData && prevData.value !== null && prevMeasurement.age) {
                // Only add if previous age is valid (positive and less than current)
                if (prevMeasurement.age > 0 && prevMeasurement.age < currentPatientData.age) {
                    patientPoints.push({
                        x: prevMeasurement.age,
                        y: prevData.value,
                        label: 'Previous',
                        isPrevious: true,
                        centile: prevData.centile,
                        sds: prevData.sds
                    });
                }
            }
        });
    }

    // Add bone age height point (only for height measurements)
    if (measurementMethod === 'height' && currentPatientData.boneAgeHeight) {
        patientPoints.push({
            x: currentPatientData.boneAgeHeight.bone_age,
            y: currentPatientData.boneAgeHeight.height,
            label: 'Bone Age',
            isBoneAge: true,
            centile: currentPatientData.boneAgeHeight.centile,
            sds: currentPatientData.boneAgeHeight.sds
        });
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
/**
 * Get theme-aware colors for charts
 * @returns {Object} Object with color values for current theme
 */
function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    return {
        title: isDark ? '#e0e0e0' : '#333',
        axisTitle: isDark ? '#b0b0b0' : '#555',
        axisTicks: isDark ? '#808080' : '#666',
        gridLines: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
        tooltip: isDark ? 'rgba(30, 30, 46, 0.95)' : 'rgba(0, 0, 0, 0.8)',
        pointBorder: isDark ? '#1e1e2e' : '#ffffff'
    };
}

function renderGrowthChart(canvas, centiles, patientData, measurementMethod) {
    const datasets = [];
    const colors = getChartColors();

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
        // Separate current, corrected, previous, and bone age measurements
        const currentPoints = patientData.filter(p => p.isCurrent);
        const correctedPoints = patientData.filter(p => p.isCorrected);
        const boneAgePoints = patientData.filter(p => p.isBoneAge);
        const previousPoints = patientData.filter(p => p.isPrevious);

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
                borderColor: colors.pointBorder,
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
                borderColor: colors.pointBorder,
                borderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                showLine: false
            });
        }

        // Add dotted line connecting chronological and bone age points (if both exist)
        if (boneAgePoints.length > 0 && currentPoints.length > 0) {
            const lineData = [
                {
                    x: currentPoints[0].x,
                    y: currentPoints[0].y
                },
                {
                    x: boneAgePoints[0].x,
                    y: boneAgePoints[0].y
                }
            ];

            datasets.push({
                label: 'Bone Age Connection',
                data: lineData,
                borderColor: '#10b981', // Green
                borderWidth: 2,
                borderDash: [5, 5],  // Dotted line pattern
                pointRadius: 0,  // No points on the line itself
                showLine: true,
                fill: false,
                tension: 0  // Straight line
            });
        }

        // Add bone age measurement (green marker)
        if (boneAgePoints.length > 0) {
            datasets.push({
                label: 'Height for Bone Age',
                data: boneAgePoints.map(p => ({
                    x: p.x,
                    y: p.y,
                    centile: p.centile,
                    sds: p.sds
                })),
                backgroundColor: '#10b981', // Green
                borderColor: colors.pointBorder,
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointStyle: 'circle',
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
                pointBorderColor: colors.pointBorder,
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
    // Use step size based on screen width for better mobile display
    const screenWidth = window.innerWidth;
    const ageRange = maxAge - minAge;
    let stepSize;

    if (screenWidth < 400) {
        // Very small screens: show fewer ticks (every 2-4 years depending on range)
        stepSize = ageRange > 10 ? 4 : 2;
    } else if (screenWidth < 600) {
        // Small screens: show moderate ticks (every 2-3 years)
        stepSize = ageRange > 10 ? 3 : 2;
    } else {
        // Larger screens: show all years
        stepSize = 1;
    }

    const tickValues = [];
    for (let i = minAge; i <= maxAge; i += stepSize) {
        tickValues.push(i);
    }
    // Always include the max age
    if (tickValues[tickValues.length - 1] !== maxAge) {
        tickValues.push(maxAge);
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
                    backgroundColor: colors.tooltip,
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    displayColors: false,  // Remove colored box from tooltip
                    filter: function(tooltipItem) {
                        // Show tooltips for patient measurements, corrected age, bone age, and mid-parental height
                        if (!tooltipItem || !tooltipItem.dataset || !tooltipItem.dataset.label) {
                            return false;
                        }
                        return tooltipItem.dataset.label.includes('Measurement') ||
                               tooltipItem.dataset.label.includes('Corrected Age') ||
                               tooltipItem.dataset.label.includes('Bone Age') ||
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

                            // Special handling for bone age measurements
                            if (datasetLabel && datasetLabel.includes('Bone Age')) {
                                const lines = [];
                                lines.push(`Age: ${age} years`);
                                lines.push(`Height: ${value} cm`);

                                // Show all bone age assessments
                                if (currentPatientData.boneAgeAssessments && currentPatientData.boneAgeAssessments.length > 0) {
                                    lines.push(''); // Empty line for separation
                                    currentPatientData.boneAgeAssessments.forEach((assessment, index) => {
                                        const standardLabel = assessment.standard === 'tw3' ? 'TW3' :
                                                            assessment.standard === 'greulich-pyle' ? 'Greulich & Pyle' :
                                                            assessment.standard;
                                        lines.push(`${standardLabel}:`);
                                        lines.push(`  Bone Age: ${assessment.bone_age} years`);
                                        lines.push(`  Centile: ${assessment.centile}%`);
                                        lines.push(`  SDS: ${assessment.sds}`);
                                        if (index < currentPatientData.boneAgeAssessments.length - 1) {
                                            lines.push(''); // Separator between assessments
                                        }
                                    });
                                }

                                return lines;
                            }

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
                    color: colors.title,
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
                        color: colors.axisTitle
                    },
                    grid: {
                        color: colors.gridLines,
                        drawBorder: true
                    },
                    afterBuildTicks: function(axis) {
                        // Replace auto-generated ticks with our custom integer ticks
                        axis.ticks = tickValues.map(value => ({ value }));
                    },
                    ticks: {
                        font: { size: 12 },
                        color: colors.axisTicks,
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
                        color: colors.axisTitle
                    },
                    grid: {
                        color: colors.gridLines,
                        drawBorder: true
                    },
                    ticks: {
                        font: { size: 12 },
                        color: colors.axisTicks
                    }
                }
            }
        }
    });

    return chart;
}

// ============================================================
// COPY RESULTS TO CLIPBOARD
// ============================================================

/**
 * Copy results button event listener
 */
document.getElementById('copyResultsBtn')?.addEventListener('click', async () => {
    const data = extractResultsData();
    const result = await clipboardManager.copy(data, 'plain');

    if (result.success) {
        showToast('Results copied to clipboard', 'success');
    } else {
        showToast('Failed to copy results. Please try again.', 'error');
        console.error('Copy failed:', result.error);
    }
});

/**
 * Keyboard shortcut: Ctrl/Cmd + C to copy results
 */
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
 * Extract all results data from DOM for copying
 * @returns {Object} Structured results data
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

/**
 * Extract measurement data (weight, height, BMI, OFC)
 */
function extractMeasurement(type) {
    const valueEl = document.getElementById(`${type}-value`);
    if (!valueEl || !valueEl.textContent) return null;

    return {
        value: parseFloat(valueEl.textContent),
        centile: document.getElementById(`${type}-centile`)?.textContent || '',
        sds: document.getElementById(`${type}-sds`)?.textContent || ''
    };
}

/**
 * Extract height velocity data
 */
function extractHeightVelocity() {
    const el = document.getElementById('height-velocity');
    if (!el || !el.textContent || el.textContent === 'N/A') return null;

    const messageEl = document.getElementById('height-velocity-message');
    let interval = null;

    if (messageEl && messageEl.textContent) {
        // Extract interval from message like "interval of 6.0 months"
        const match = messageEl.textContent.match(/interval of ([\d.]+) months?/);
        if (match) {
            interval = `${match[1]} months`;
        }
    }

    return {
        value: parseFloat(el.textContent),
        interval: interval
    };
}

/**
 * Extract BSA data
 */
function extractBSA() {
    const el = document.getElementById('bsa');
    if (!el || !el.textContent) return null;

    const labelEl = document.getElementById('bsa-label');
    let method = 'Boyd';

    if (labelEl && labelEl.textContent) {
        if (labelEl.textContent.includes('cBNF')) {
            method = 'cBNF';
        }
    }

    return {
        value: parseFloat(el.textContent),
        method: method
    };
}

/**
 * Extract GH Dose data
 */
function extractGHDose() {
    const el = document.getElementById('gh-dose-input');
    if (!el || !el.value || parseFloat(el.value) === 0) return null;

    return {
        mgPerDay: parseFloat(el.value).toFixed(3),
        mgM2Week: document.getElementById('gh-dose-mg-m2-week')?.textContent || '',
        mcgKgDay: document.getElementById('gh-dose-mcg-kg-day')?.textContent || ''
    };
}

/**
 * Extract Mid-Parental Height data
 */
function extractMPH() {
    const el = document.getElementById('mph-value');
    if (!el || !el.textContent) return null;

    const rangeText = document.getElementById('mph-range')?.textContent || '';
    let rangeMin = null;
    let rangeMax = null;

    if (rangeText) {
        const match = rangeText.match(/([\d.]+)\s*-\s*([\d.]+)/);
        if (match) {
            rangeMin = parseFloat(match[1]);
            rangeMax = parseFloat(match[2]);
        }
    }

    return {
        value: parseFloat(el.textContent),
        centile: document.getElementById('mph-centile')?.textContent || '',
        rangeMin: rangeMin,
        rangeMax: rangeMax
    };
}

/**
 * Extract warnings from validation warnings section
 */
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
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('copyToast');
    const messageEl = toast.querySelector('.toast-message');
    const iconEl = toast.querySelector('.toast-icon');

    messageEl.textContent = message;
    toast.classList.remove('success', 'error');
    toast.classList.add(type);

    // Update icon based on type
    iconEl.textContent = type === 'success' ? '✓' : '✗';

    toast.classList.add('show');

    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Export chart as base64 image
 * @returns {string|null} Base64 encoded PNG image or null if no chart
 */
function exportChartAsImage() {
    if (!currentChartInstance) {
        return null;
    }

    try {
        // Use Chart.js built-in toBase64Image() method for high quality
        return currentChartInstance.toBase64Image('image/png', 1.0);
    } catch (error) {
        console.error('Error exporting chart:', error);
        return null;
    }
}

/**
 * Download current chart as PNG file
 */
function downloadCurrentChart() {
    if (!currentChartInstance) {
        showToast('No chart available to download', 'error');
        return;
    }

    try {
        // Get the base64 image
        const base64Image = exportChartAsImage();
        if (!base64Image) {
            showToast('Failed to export chart', 'error');
            return;
        }

        // Determine the chart type from active tab
        const activeTab = document.querySelector('.chart-tab.active');
        const chartType = activeTab ? activeTab.getAttribute('data-measurement') : 'chart';

        // Get the current date for filename
        const date = new Date().toISOString().split('T')[0];

        // Convert base64 to blob
        const base64Data = base64Image.replace(/^data:image\/png;base64,/, '');
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'image/png' });

        // Create download link and trigger download
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `growth-chart-${chartType}-${date}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        showToast('Chart downloaded successfully', 'success');
    } catch (error) {
        console.error('Error downloading chart:', error);
        showToast('Failed to download chart', 'error');
    }
}

/**
 * Export all currently visible charts
 * @returns {Object} Object with chart type as key and base64 image as value
 */
async function exportAllChartImages() {
    const images = {};

    // Get all chart tabs
    const chartTabs = document.querySelectorAll('.chart-tab');

    for (const tab of chartTabs) {
        if (tab.classList.contains('active')) {
            // Get chart type from data attribute
            const chartType = tab.getAttribute('data-chart');

            // Export the current chart
            const imageData = exportChartAsImage();
            if (imageData) {
                images[chartType] = imageData;
            }
        }
    }

    return images;
}

/**
 * Handle PDF export
 */
async function handlePdfExport() {
    const exportBtn = document.getElementById('exportPdfBtn');

    // Disable button during export
    if (exportBtn) {
        exportBtn.disabled = true;
    }

    showToast('Generating PDF...', 'info');

    try {
        // Check if we have calculation results
        if (!window.calculationResults) {
            showToast('No calculation results available', 'error');
            return;
        }

        // 1. Prepare patient info
        const patientInfo = {
            sex: document.querySelector('input[name="sex"]:checked')?.value || 'unknown',
            birth_date: document.getElementById('birth_date')?.value || '',
            measurement_date: document.getElementById('measurement_date')?.value || '',
            reference: document.getElementById('reference')?.value || 'uk-who'
        };

        // 2. Prepare payload (without chart images)
        const pdfData = {
            results: window.calculationResults,
            patient_info: patientInfo,
            chart_images: {}  // Empty - don't include charts in PDF
        };

        // 4. Request PDF from server
        const response = await fetch('/export-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pdfData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate PDF');
        }

        // 5. Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `growth-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showToast('PDF downloaded successfully', 'success');
    } catch (error) {
        console.error('PDF export error:', error);
        showToast(`Failed to generate PDF: ${error.message}`, 'error');
    } finally {
        // Re-enable button
        if (exportBtn) {
            exportBtn.disabled = false;
        }
    }
}

// Add event listener for PDF export button when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', handlePdfExport);
    }
});
