from flask import Flask, render_template, request, jsonify, send_file
from rcpchgrowth import Measurement, mid_parental_height, mid_parental_height_z, lower_and_upper_limits_of_expected_height_z, measurement_from_sds
from rcpchgrowth.chart_functions import create_chart
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import random

# Import from our modules
from constants import ErrorCodes
from validation import ValidationError, validate_date, validate_date_range, validate_weight, validate_height, validate_ofc, validate_gestation
from calculations import calculate_age_in_years, should_apply_gestation_correction, calculate_corrected_age, calculate_boyd_bsa, calculate_cbnf_bsa, calculate_height_velocity, calculate_gh_dose
from models import create_measurement, validate_measurement_sds
from utils import calculate_mid_parental_height, get_chart_data, calculate_percentage_median_bmi

app = Flask(__name__)

# Initialize rate limiter (optional - only if Flask-Limiter is installed)
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    RATE_LIMITING_ENABLED = True
    print("✓ Rate limiting enabled")
except ImportError:
    print("⚠ Flask-Limiter not installed - rate limiting disabled")
    RATE_LIMITING_ENABLED = False
    limiter = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json

        # Parse required input data
        birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        measurement_date = datetime.strptime(data['measurement_date'], '%Y-%m-%d').date()
        sex = data['sex']
        reference = data.get('reference', 'uk-who')

        # Optional measurements - height, weight, OFC
        weight = float(data['weight']) if data.get('weight') else None
        height = float(data['height']) if data.get('height') else None
        ofc = float(data.get('ofc', 0)) if data.get('ofc') else None

        # Validate that at least one measurement is provided
        if not any([weight, height, ofc]):
            return jsonify({
                'success': False,
                'error': 'At least one measurement (weight, height, or OFC) is required.'
            }), 400

        # Optional previous measurements data
        previous_measurements = data.get('previous_measurements', [])

        # Optional parental heights
        maternal_height = float(data.get('maternal_height', 0)) if data.get('maternal_height') else None
        paternal_height = float(data.get('paternal_height', 0)) if data.get('paternal_height') else None

        # Optional bone age assessments
        bone_age_assessments = data.get('bone_age_assessments', [])

        # Optional gestation data
        gestation_weeks = data.get('gestation_weeks')
        gestation_days = data.get('gestation_days')

        # Calculate chronological age
        age_decimal, calendar_age = calculate_age_in_years(birth_date, measurement_date)

        # Determine if gestational age correction should be applied
        apply_correction = should_apply_gestation_correction(gestation_weeks, gestation_days, age_decimal)

        # Calculate corrected age if applicable
        corrected_age_decimal = None
        corrected_calendar_age = None
        if apply_correction:
            corrected_age_decimal, corrected_calendar_age = calculate_corrected_age(
                birth_date, measurement_date, gestation_weeks, gestation_days
            )

        # Create measurement objects only for provided values
        weight_measurement = None
        height_measurement = None
        bmi_measurement = None
        ofc_measurement = None

        if weight:
            weight_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=measurement_date,
                measurement_method='weight',
                observation_value=weight,
                reference=reference
            )

        if height:
            height_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=measurement_date,
                measurement_method='height',
                observation_value=height,
                reference=reference
            )

        # BMI requires both weight and height
        if weight and height:
            bmi_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=measurement_date,
                measurement_method='bmi',
                observation_value=weight / ((height / 100) ** 2),
                reference=reference
            )

        # Calculate OFC if provided
        if ofc:
            ofc_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=measurement_date,
                measurement_method='ofc',
                observation_value=ofc,
                reference=reference
            )

        # Create corrected age measurements if gestation correction applies
        weight_corrected = None
        height_corrected = None
        bmi_corrected = None
        ofc_corrected = None

        if apply_correction and gestation_weeks:
            if weight:
                weight_corrected = Measurement(
                    sex=sex,
                    birth_date=birth_date,
                    observation_date=measurement_date,
                    measurement_method='weight',
                    observation_value=weight,
                    reference=reference,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days or 0
                )

            if height:
                height_corrected = Measurement(
                    sex=sex,
                    birth_date=birth_date,
                    observation_date=measurement_date,
                    measurement_method='height',
                    observation_value=height,
                    reference=reference,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days or 0
                )

            if weight and height:
                bmi_corrected = Measurement(
                    sex=sex,
                    birth_date=birth_date,
                    observation_date=measurement_date,
                    measurement_method='bmi',
                    observation_value=weight / ((height / 100) ** 2),
                    reference=reference,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days or 0
                )

            if ofc:
                ofc_corrected = Measurement(
                    sex=sex,
                    birth_date=birth_date,
                    observation_date=measurement_date,
                    measurement_method='ofc',
                    observation_value=ofc,
                    reference=reference,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days or 0
                )

        # Process previous measurements and calculate height velocity
        height_velocity = None
        previous_height_data = None
        processed_previous_measurements = []

        if previous_measurements:
            # Process each previous measurement
            for prev_measurement in previous_measurements:
                try:
                    prev_date = datetime.strptime(prev_measurement['date'], '%Y-%m-%d').date()
                    prev_height = prev_measurement.get('height')
                    prev_weight = prev_measurement.get('weight')
                    prev_ofc = prev_measurement.get('ofc')

                    processed_measurement = {
                        'date': prev_date.isoformat(),
                        'age': None,
                        'height': None,
                        'weight': None,
                        'ofc': None
                    }

                    # Calculate age at previous measurement
                    prev_age_decimal, _ = calculate_age_in_years(birth_date, prev_date)
                    processed_measurement['age'] = round(prev_age_decimal, 2)

                    # Process height
                    if prev_height:
                        prev_height_measurement = Measurement(
                            sex=sex,
                            birth_date=birth_date,
                            observation_date=prev_date,
                            measurement_method='height',
                            observation_value=float(prev_height),
                            reference=reference
                        )
                        prev_height_calc = prev_height_measurement.measurement['measurement_calculated_values']
                        prev_height_sds = float(prev_height_calc['corrected_sds']) if prev_height_calc['corrected_sds'] else None

                        processed_measurement['height'] = {
                            'value': float(prev_height),
                            'centile': round(float(prev_height_calc['corrected_centile']), 2) if prev_height_calc['corrected_centile'] else None,
                            'sds': round(prev_height_sds, 2) if prev_height_sds is not None else None
                        }

                    # Process weight
                    if prev_weight:
                        prev_weight_measurement = Measurement(
                            sex=sex,
                            birth_date=birth_date,
                            observation_date=prev_date,
                            measurement_method='weight',
                            observation_value=float(prev_weight),
                            reference=reference
                        )
                        prev_weight_calc = prev_weight_measurement.measurement['measurement_calculated_values']
                        prev_weight_sds = float(prev_weight_calc['corrected_sds']) if prev_weight_calc['corrected_sds'] else None

                        processed_measurement['weight'] = {
                            'value': float(prev_weight),
                            'centile': round(float(prev_weight_calc['corrected_centile']), 2) if prev_weight_calc['corrected_centile'] else None,
                            'sds': round(prev_weight_sds, 2) if prev_weight_sds is not None else None
                        }

                    # Process OFC
                    if prev_ofc:
                        prev_ofc_measurement = Measurement(
                            sex=sex,
                            birth_date=birth_date,
                            observation_date=prev_date,
                            measurement_method='ofc',
                            observation_value=float(prev_ofc),
                            reference=reference
                        )
                        prev_ofc_calc = prev_ofc_measurement.measurement['measurement_calculated_values']
                        prev_ofc_sds = float(prev_ofc_calc['corrected_sds']) if prev_ofc_calc['corrected_sds'] else None

                        processed_measurement['ofc'] = {
                            'value': float(prev_ofc),
                            'centile': round(float(prev_ofc_calc['corrected_centile']), 2) if prev_ofc_calc['corrected_centile'] else None,
                            'sds': round(prev_ofc_sds, 2) if prev_ofc_sds is not None else None
                        }

                    processed_previous_measurements.append(processed_measurement)

                except (ValueError, KeyError) as e:
                    # Skip invalid previous measurements
                    continue

            # Calculate height velocity using most recent previous height measurement > 4 months prior
            if height:
                # Get all height measurements from previous measurements
                all_height_measurements = [
                    pm for pm in processed_previous_measurements
                    if pm['height'] is not None
                ]

                if all_height_measurements:
                    # Check for error conditions
                    error_message = None

                    # Check if any measurements are in the future
                    for pm in all_height_measurements:
                        pm_date = datetime.strptime(pm['date'], '%Y-%m-%d').date()
                        if pm_date >= measurement_date:
                            error_message = f"Previous measurement date must be before current measurement date"
                            break

                    if not error_message:
                        # Filter height measurements that are >4 months (122 days) prior to current measurement
                        valid_height_measurements = [
                            pm for pm in all_height_measurements
                            if (measurement_date - datetime.strptime(pm['date'], '%Y-%m-%d').date()).days > 122
                        ]

                        if valid_height_measurements:
                            # Sort by date (most recent first)
                            valid_height_measurements.sort(
                                key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date(),
                                reverse=True
                            )

                            # Use most recent valid measurement
                            most_recent = valid_height_measurements[0]
                            most_recent_date = datetime.strptime(most_recent['date'], '%Y-%m-%d').date()
                            most_recent_height = most_recent['height']['value']

                            # Calculate height velocity
                            height_velocity = calculate_height_velocity(
                                height,
                                most_recent_height,
                                measurement_date,
                                most_recent_date
                            )

                            # Store the previous height data used for velocity calculation
                            previous_height_data = most_recent['height']
                        else:
                            # All previous measurements are < 4 months
                            error_message = "Height velocity requires at least 4 months between measurements"

                    # If we have an error message, return it as height_velocity
                    if error_message:
                        height_velocity = {
                            'value': None,
                            'message': error_message
                        }

        # Process bone age assessments - calculate height for bone age if within +/- 1 month
        bone_age_height_data = []
        bone_age_for_plotting = None  # The one to plot (prefer TW3)

        if height and bone_age_assessments:
            for assessment in bone_age_assessments:
                try:
                    assessment_date = datetime.strptime(assessment['date'], '%Y-%m-%d').date()
                    bone_age_value = float(assessment['bone_age'])
                    standard = assessment.get('standard', '')

                    # Check if assessment is within +/- 1 month of measurement date
                    days_difference = abs((measurement_date - assessment_date).days)

                    # Approximately 30.44 days per month
                    if days_difference <= 30.44:
                        # Calculate height centile/SDS using bone age instead of chronological age
                        # Create synthetic birth date such that the "age" at measurement equals bone age
                        bone_age_birth_date = measurement_date - relativedelta(
                            years=int(bone_age_value),
                            days=int((bone_age_value % 1) * 365.25)
                        )

                        bone_age_height_measurement = Measurement(
                            sex=sex,
                            birth_date=bone_age_birth_date,
                            observation_date=measurement_date,
                            measurement_method='height',
                            observation_value=height,
                            reference=reference
                        )

                        bone_age_height_calc = bone_age_height_measurement.measurement['measurement_calculated_values']
                        bone_age_height_sds = float(bone_age_height_calc['corrected_sds']) if bone_age_height_calc['corrected_sds'] else None

                        assessment_data = {
                            'bone_age': bone_age_value,
                            'assessment_date': assessment_date.isoformat(),
                            'standard': standard,
                            'height': height,
                            'centile': round(float(bone_age_height_calc['corrected_centile']), 2) if bone_age_height_calc['corrected_centile'] else None,
                            'sds': round(bone_age_height_sds, 2) if bone_age_height_sds is not None else None,
                            'within_window': True
                        }

                        bone_age_height_data.append(assessment_data)

                        # Determine which to plot - prefer TW3, otherwise use first
                        if bone_age_for_plotting is None or standard == 'tw3':
                            bone_age_for_plotting = assessment_data

                except (ValueError, KeyError) as e:
                    # Skip invalid bone age assessments
                    continue

        # Calculate BSA
        # Use Boyd formula if both weight and height available
        # Use cBNF lookup table if only weight available
        bsa = None
        bsa_method = None
        if weight and height:
            bsa = calculate_boyd_bsa(weight, height)
            bsa_method = 'Boyd'
        elif weight:
            bsa = calculate_cbnf_bsa(weight)
            bsa_method = 'cBNF'

        # Calculate GH dose for 7 mg/m2/week (requires BSA and weight)
        gh_dose = None
        if bsa and weight:
            gh_dose = calculate_gh_dose(bsa, weight)

        # Calculate mid-parental height if parental heights provided
        mph_data = None
        if maternal_height and paternal_height:
            # Calculate mid-parental height
            mph_cm = mid_parental_height(
                maternal_height=maternal_height,
                paternal_height=paternal_height,
                sex=sex
            )

            # Calculate mid-parental height z-score
            mph_z = mid_parental_height_z(
                maternal_height=maternal_height,
                paternal_height=paternal_height
            )

            # Calculate target range (z-score limits)
            lower_z, upper_z = lower_and_upper_limits_of_expected_height_z(
                mid_parental_height_z=mph_z
            )

            # Convert z-scores to heights
            lower_height = measurement_from_sds(
                reference='uk-who',
                requested_sds=lower_z,
                measurement_method='height',
                sex=sex,
                age=18.0  # Adult height at 18 years
            )

            upper_height = measurement_from_sds(
                reference='uk-who',
                requested_sds=upper_z,
                measurement_method='height',
                sex=sex,
                age=18.0  # Adult height at 18 years
            )

            # Calculate centile from z-score (using standard normal distribution)
            from utils import norm_cdf
            mph_centile = norm_cdf(mph_z) * 100

            mph_data = {
                'mid_parental_height': round(mph_cm, 1),
                'mid_parental_height_sds': round(mph_z, 2),
                'mid_parental_height_centile': round(mph_centile, 1),
                'target_range_lower': round(lower_height, 1),
                'target_range_upper': round(upper_height, 1)
            }

        # Extract calculated values only for measurements that were performed
        weight_calc = None
        height_calc = None
        bmi_calc = None
        bmi_value = None
        bmi_percentage_median = None

        if weight_measurement:
            weight_calc = weight_measurement.measurement['measurement_calculated_values']
        if height_measurement:
            height_calc = height_measurement.measurement['measurement_calculated_values']
        if bmi_measurement:
            bmi_calc = bmi_measurement.measurement['measurement_calculated_values']
            bmi_value = bmi_measurement.measurement['child_observation_value']['observation_value']

            # Calculate percentage of median BMI (for malnutrition assessment)
            bmi_percentage_median = calculate_percentage_median_bmi(
                reference=reference,
                age=age_decimal,
                bmi=float(bmi_value),
                sex=sex
            )

        # Get SDS values for validation
        weight_sds = float(weight_calc['corrected_sds']) if weight_calc and weight_calc['corrected_sds'] else None
        height_sds = float(height_calc['corrected_sds']) if height_calc and height_calc['corrected_sds'] else None
        bmi_sds = float(bmi_calc['corrected_sds']) if bmi_calc and bmi_calc['corrected_sds'] else None

        # Validate SDS values - Height, Weight, OFC
        # Hard cut-off at +/-8 SDS (reject)
        # Advisory warning at +/-4 SDS
        validation_messages = []

        if weight_sds is not None:
            if abs(weight_sds) > 8:
                return jsonify({
                    'success': False,
                    'error': f'Weight SDS ({weight_sds:.2f}) exceeds acceptable range (±8 SDS). Please check measurement accuracy.'
                }), 400
            elif abs(weight_sds) > 4:
                validation_messages.append(f'Weight SDS ({weight_sds:.2f}) is very extreme (>±4 SDS). Please verify measurement accuracy and consider remeasuring.')

        if height_sds is not None:
            if abs(height_sds) > 8:
                return jsonify({
                    'success': False,
                    'error': f'Height SDS ({height_sds:.2f}) exceeds acceptable range (±8 SDS). Please check measurement accuracy.'
                }), 400
            elif abs(height_sds) > 4:
                validation_messages.append(f'Height SDS ({height_sds:.2f}) is very extreme (>±4 SDS). Please verify measurement accuracy and consider remeasuring.')

        # BMI validation - advisory at +/-4, hard cut-off at +/-15
        if bmi_sds is not None:
            if abs(bmi_sds) > 15:
                return jsonify({
                    'success': False,
                    'error': f'BMI SDS ({bmi_sds:.2f}) exceeds acceptable range (±15 SDS). Please check measurement accuracy.'
                }), 400
            elif abs(bmi_sds) > 4:
                validation_messages.append(f'BMI SDS ({bmi_sds:.2f}) is very extreme (>±4 SDS). Please verify measurement accuracy and consider remeasuring.')

        # Extract OFC values if calculated and validate
        ofc_data = None
        if ofc_measurement:
            ofc_calc = ofc_measurement.measurement['measurement_calculated_values']
            ofc_sds = float(ofc_calc['corrected_sds']) if ofc_calc['corrected_sds'] else None

            if ofc_sds is not None:
                if abs(ofc_sds) > 8:
                    return jsonify({
                        'success': False,
                        'error': f'OFC SDS ({ofc_sds:.2f}) exceeds acceptable range (±8 SDS). Please check measurement accuracy.'
                    }), 400
                elif abs(ofc_sds) > 4:
                    validation_messages.append(f'OFC SDS ({ofc_sds:.2f}) is very extreme (>±4 SDS). Please verify measurement accuracy and consider remeasuring.')

            ofc_data = {
                'value': ofc,
                'centile': round(float(ofc_calc['corrected_centile']), 2) if ofc_calc['corrected_centile'] else None,
                'sds': round(ofc_sds, 2) if ofc_sds else None
            }

        # Extract corrected measurement data if gestation correction was applied
        weight_corrected_data = None
        height_corrected_data = None
        bmi_corrected_data = None
        ofc_corrected_data = None

        if apply_correction:
            if weight_corrected:
                weight_corr_calc = weight_corrected.measurement['measurement_calculated_values']
                weight_corrected_data = {
                    'age': round(corrected_age_decimal, 2),
                    'value': weight,
                    'centile': round(float(weight_corr_calc['corrected_centile']), 2) if weight_corr_calc['corrected_centile'] else None,
                    'sds': round(float(weight_corr_calc['corrected_sds']), 2) if weight_corr_calc['corrected_sds'] else None
                }

            if height_corrected:
                height_corr_calc = height_corrected.measurement['measurement_calculated_values']
                height_corrected_data = {
                    'age': round(corrected_age_decimal, 2),
                    'value': height,
                    'centile': round(float(height_corr_calc['corrected_centile']), 2) if height_corr_calc['corrected_centile'] else None,
                    'sds': round(float(height_corr_calc['corrected_sds']), 2) if height_corr_calc['corrected_sds'] else None
                }

            if bmi_corrected:
                bmi_corr_calc = bmi_corrected.measurement['measurement_calculated_values']
                bmi_corrected_data = {
                    'age': round(corrected_age_decimal, 2),
                    'value': round(float(bmi_value), 1) if bmi_value else None,
                    'centile': round(float(bmi_corr_calc['corrected_centile']), 2) if bmi_corr_calc['corrected_centile'] else None,
                    'sds': round(float(bmi_corr_calc['corrected_sds']), 2) if bmi_corr_calc['corrected_sds'] else None
                }

            if ofc_corrected:
                ofc_corr_calc = ofc_corrected.measurement['measurement_calculated_values']
                ofc_corrected_data = {
                    'age': round(corrected_age_decimal, 2),
                    'value': ofc,
                    'centile': round(float(ofc_corr_calc['corrected_centile']), 2) if ofc_corr_calc['corrected_centile'] else None,
                    'sds': round(float(ofc_corr_calc['corrected_sds']), 2) if ofc_corr_calc['corrected_sds'] else None
                }

        # Prepare results - only include data for measurements that were provided
        results = {
            'age_years': round(age_decimal, 2),
            'age_calendar': calendar_age,
            'gestation_correction_applied': apply_correction,
            'corrected_age_years': round(corrected_age_decimal, 2) if corrected_age_decimal else None,
            'corrected_age_calendar': corrected_calendar_age,
            'weight': {
                'value': weight,
                'centile': round(float(weight_calc['corrected_centile']), 2) if weight_calc and weight_calc['corrected_centile'] else None,
                'sds': round(weight_sds, 2) if weight_sds is not None else None
            } if weight else None,
            'height': {
                'value': height,
                'centile': round(float(height_calc['corrected_centile']), 2) if height_calc and height_calc['corrected_centile'] else None,
                'sds': round(height_sds, 2) if height_sds is not None else None
            } if height else None,
            'bmi': {
                'value': round(float(bmi_value), 1) if bmi_value else None,
                'centile': round(float(bmi_calc['corrected_centile']), 2) if bmi_calc and bmi_calc['corrected_centile'] else None,
                'sds': round(bmi_sds, 2) if bmi_sds is not None else None,
                'percentage_median': bmi_percentage_median
            } if bmi_measurement else None,
            'ofc': ofc_data,
            'weight_corrected': weight_corrected_data,
            'height_corrected': height_corrected_data,
            'bmi_corrected': bmi_corrected_data,
            'ofc_corrected': ofc_corrected_data,
            'height_velocity': height_velocity,
            'previous_height': previous_height_data,
            'previous_measurements': processed_previous_measurements,
            'bone_age_height': bone_age_for_plotting,  # Single bone age for plotting (TW3 preferred)
            'bone_age_assessments': bone_age_height_data,  # All bone age assessments with calculations
            'bsa': bsa,
            'bsa_method': bsa_method,
            'gh_dose': gh_dose,
            'mid_parental_height': mph_data,
            'validation_messages': validation_messages
        }

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/chart-data', methods=['POST'])
def get_chart_data():
    """
    Return centile curve data for plotting growth charts

    Expected POST data:
    {
        'reference': 'uk-who' | 'turners-syndrome' | 'trisomy-21',
        'measurement_method': 'height' | 'weight' | 'bmi' | 'ofc',
        'sex': 'male' | 'female'
    }

    Returns:
    {
        'success': True,
        'centiles': [
            {
                'centile': 0.4,
                'sds': -2.67,
                'data': [{'x': age, 'y': value}, ...]
            },
            ... (9 centile bands total)
        ]
    }
    """
    try:
        data = request.json
        reference = data.get('reference', 'uk-who')
        measurement_method = data.get('measurement_method')
        sex = data.get('sex')

        # Validate required parameters
        if not measurement_method or not sex:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: measurement_method or sex'
            }), 400

        # Validate measurement_method
        valid_methods = ['height', 'weight', 'bmi', 'ofc']
        if measurement_method not in valid_methods:
            return jsonify({
                'success': False,
                'error': f'Invalid measurement_method. Must be one of: {", ".join(valid_methods)}'
            }), 400

        # Get chart data using utils function
        from utils import get_chart_data as fetch_chart_data
        centile_curves = fetch_chart_data(
            reference=reference,
            measurement_method=measurement_method,
            sex=sex
        )

        return jsonify({
            'success': True,
            'centiles': centile_curves
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Chart data error: {str(e)}'
        }), 400

@app.route('/generate-demo-data', methods=['GET'])
def generate_demo_data():
    """
    Generate realistic demo data using rcpchgrowth library
    Returns populated form data that can be used to demonstrate the app
    """
    try:
        # Random sex
        sex = random.choice(['male', 'female'])

        # Random age between 2 and 15 years
        age_years = random.uniform(2, 15)

        # Calculate birth date from age
        measurement_date = datetime.now().date()
        birth_date = measurement_date - relativedelta(years=int(age_years), days=int((age_years % 1) * 365.25))

        # Random reference (mostly uk-who, occasionally others)
        reference = random.choices(
            ['uk-who', 'turner', 'trisomy-21'],
            weights=[0.85, 0.1, 0.05]
        )[0]

        # Generate measurements from realistic centiles
        # Pick centiles that are slightly varied to make it interesting
        height_centile_sds = random.uniform(-2, 2)  # -2 to +2 SDS range
        weight_centile_sds = height_centile_sds + random.uniform(-0.5, 0.5)  # Correlated but slightly different
        ofc_centile_sds = random.uniform(-1.5, 1.5)

        # Use measurement_from_sds to generate realistic measurements
        height_measurement = measurement_from_sds(
            measurement_method='height',
            requested_sds=height_centile_sds,
            sex=sex,
            decimal_age=age_years,
            reference=reference
        )
        height = round(height_measurement, 1)

        weight_measurement = measurement_from_sds(
            measurement_method='weight',
            requested_sds=weight_centile_sds,
            sex=sex,
            decimal_age=age_years,
            reference=reference
        )
        weight = round(weight_measurement, 1)

        # OFC for younger children
        ofc = None
        if age_years < 5:
            ofc_measurement = measurement_from_sds(
                measurement_method='ofc',
                requested_sds=ofc_centile_sds,
                sex=sex,
                decimal_age=age_years,
                reference=reference
            )
            ofc = round(ofc_measurement, 1)

        # Generate 2-4 previous measurements
        num_previous = random.randint(2, 4)
        previous_measurements = []

        for i in range(num_previous):
            # Go back 6-18 months for each measurement
            months_ago = (i + 1) * random.randint(6, 18)
            prev_age = age_years - (months_ago / 12)

            if prev_age > 0:  # Only if positive age
                prev_date = measurement_date - relativedelta(months=months_ago)

                # Generate measurements with slight growth trajectory
                prev_height_sds = height_centile_sds + random.uniform(-0.2, 0.2)
                prev_weight_sds = weight_centile_sds + random.uniform(-0.3, 0.3)

                prev_height = round(measurement_from_sds(
                    measurement_method='height',
                    requested_sds=prev_height_sds,
                    sex=sex,
                    decimal_age=prev_age,
                    reference=reference
                ), 1)

                prev_weight = round(measurement_from_sds(
                    measurement_method='weight',
                    requested_sds=prev_weight_sds,
                    sex=sex,
                    decimal_age=prev_age,
                    reference=reference
                ), 1)

                prev_ofc = None
                if age_years < 5 and ofc:
                    prev_ofc_sds = ofc_centile_sds + random.uniform(-0.2, 0.2)
                    prev_ofc = round(measurement_from_sds(
                        measurement_method='ofc',
                        requested_sds=prev_ofc_sds,
                        sex=sex,
                        decimal_age=prev_age,
                        reference=reference
                    ), 1)

                previous_measurements.append({
                    'date': prev_date.isoformat(),
                    'height': prev_height,
                    'weight': prev_weight,
                    'ofc': prev_ofc
                })

        # Sort previous measurements by date (oldest first)
        previous_measurements.sort(key=lambda x: x['date'])

        # Generate parental heights
        # Use population averages with some variation
        maternal_height = round(random.gauss(163, 6), 1)  # Female average ~163cm
        paternal_height = round(random.gauss(176, 7), 1)  # Male average ~176cm

        # Bone age assessment (30% chance)
        bone_age_assessments = []
        if random.random() < 0.3 and age_years >= 3:
            # Bone age can be delayed or advanced
            bone_age_offset = random.uniform(-2, 2)
            bone_age = max(0, age_years + bone_age_offset)

            # Assessment date within ±2 weeks of measurement
            assessment_date = measurement_date + relativedelta(days=random.randint(-14, 14))

            # Randomly choose standard(s)
            standards = ['greulich-pyle', 'tw3']
            num_standards = random.choice([1, 2])  # Sometimes both

            for standard in random.sample(standards, num_standards):
                # TW3 might be slightly different from GP
                ba_variation = random.uniform(-0.3, 0.3) if len(bone_age_assessments) > 0 else 0
                assessment_bone_age = round(bone_age + ba_variation, 1)

                bone_age_assessments.append({
                    'date': assessment_date.isoformat(),
                    'bone_age': assessment_bone_age,
                    'standard': standard
                })

        # Gestation data for younger children (20% chance of being preterm)
        gestation_weeks = None
        gestation_days = None
        if age_years < 3 and random.random() < 0.2:
            gestation_weeks = random.randint(28, 36)
            gestation_days = random.randint(0, 6)

        # Build response
        demo_data = {
            'sex': sex,
            'birth_date': birth_date.isoformat(),
            'measurement_date': measurement_date.isoformat(),
            'height': height,
            'weight': weight,
            'ofc': ofc,
            'previous_measurements': previous_measurements,
            'bone_age_assessments': bone_age_assessments,
            'maternal_height': maternal_height,
            'paternal_height': paternal_height,
            'gestation_weeks': gestation_weeks,
            'gestation_days': gestation_days,
            'reference': reference
        }

        return jsonify({
            'success': True,
            'data': demo_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Demo data generation error: {str(e)}'
        }), 400

@app.route('/export-pdf', methods=['POST'])
@limiter.limit("10 per minute")
def export_pdf():
    """
    Generate PDF report from calculation results

    Expected JSON payload:
    {
        "results": {...},  # Complete calculation results
        "patient_info": {
            "sex": "male" | "female",
            "birth_date": "YYYY-MM-DD",
            "measurement_date": "YYYY-MM-DD",
            "reference": "uk-who" | "uk90" | "who"
        },
        "chart_images": {
            "height": "base64_image_data",
            "weight": "base64_image_data",
            ...
        }
    }

    Returns:
        PDF file download
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        results = data.get('results')
        patient_info = data.get('patient_info')
        chart_images = data.get('chart_images', {})

        if not results or not patient_info:
            return jsonify({
                'success': False,
                'error': 'Missing required data (results or patient_info)'
            }), 400

        # Generate PDF using pdf_utils
        from pdf_utils import GrowthReportPDF
        pdf_generator = GrowthReportPDF(results, patient_info, chart_images)
        pdf_buffer = pdf_generator.generate()

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"growth-report-{timestamp}.pdf"

        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'PDF generation error: {str(e)}'
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
