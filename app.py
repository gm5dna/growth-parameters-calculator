from flask import Flask, render_template, request, jsonify
from rcpchgrowth import Measurement, mid_parental_height, mid_parental_height_z, lower_and_upper_limits_of_expected_height_z, measurement_from_sds
from rcpchgrowth.chart_functions import create_chart
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

app = Flask(__name__)

def calculate_age_in_years(birth_date, measurement_date):
    """Calculate age in decimal years and calendar age

    Returns:
        tuple: (decimal_years, calendar_age_dict)
    """
    delta = relativedelta(measurement_date, birth_date)
    years = delta.years
    months = delta.months
    days = delta.days

    # Convert to decimal years
    decimal_years = years + (months / 12.0) + (days / 365.25)

    # Calendar age
    calendar_age = {
        'years': years,
        'months': months,
        'days': days
    }

    return decimal_years, calendar_age

def calculate_boyd_bsa(weight_kg, height_cm):
    """Calculate Body Surface Area using Boyd formula"""
    # Boyd formula: BSA = 0.0003207 * (height_cm^0.3) * (weight_g^(0.7285 - (0.0188 * log10(weight_g))))
    if weight_kg <= 0 or height_cm <= 0:
        return None

    weight_g = weight_kg * 1000
    log_weight = math.log10(weight_g)
    bsa = 0.0003207 * (height_cm ** 0.3) * (weight_g ** (0.7285 - (0.0188 * log_weight)))
    return round(bsa, 2)

def calculate_cbnf_bsa(weight_kg):
    """Calculate Body Surface Area from weight alone using cBNF lookup tables

    Based on tables from British National Formulary for Children (BNFc)
    Adapted from Sharkey I et al., British Journal of Cancer 2001; 85 (1): 23–28
    Values are calculated using the Boyd equation

    Args:
        weight_kg: Body weight in kilograms

    Returns:
        BSA in m² (rounded to 2 decimal places), or None if weight is invalid
    """
    if weight_kg <= 0:
        return None

    # cBNF lookup table: weight (kg) -> BSA (m²)
    # Combined data from both under 40kg and over 40kg tables
    lookup_table = {
        1: 0.10, 1.5: 0.13, 2: 0.16, 2.5: 0.19, 3: 0.21, 3.5: 0.24,
        4: 0.26, 4.5: 0.28, 5: 0.30, 5.5: 0.32, 6: 0.34, 6.5: 0.36,
        7: 0.38, 7.5: 0.40, 8: 0.42, 8.5: 0.44, 9: 0.46, 9.5: 0.47,
        10: 0.49, 11: 0.53, 12: 0.56, 13: 0.59, 14: 0.62, 15: 0.65,
        16: 0.68, 17: 0.71, 18: 0.74, 19: 0.77, 20: 0.79, 21: 0.82,
        22: 0.85, 23: 0.87, 24: 0.90, 25: 0.92, 26: 0.95, 27: 0.97,
        28: 1.0, 29: 1.0, 30: 1.1, 31: 1.1, 32: 1.1, 33: 1.1,
        34: 1.1, 35: 1.2, 36: 1.2, 37: 1.2, 38: 1.2, 39: 1.3, 40: 1.3,
        41: 1.3, 42: 1.3, 43: 1.3, 44: 1.4, 45: 1.4, 46: 1.4,
        47: 1.4, 48: 1.4, 49: 1.5, 50: 1.5, 51: 1.5, 52: 1.5,
        53: 1.5, 54: 1.6, 55: 1.6, 56: 1.6, 57: 1.6, 58: 1.6,
        59: 1.7, 60: 1.7, 61: 1.7, 62: 1.7, 63: 1.7, 64: 1.7,
        65: 1.8, 66: 1.8, 67: 1.8, 68: 1.8, 69: 1.8, 70: 1.9,
        71: 1.9, 72: 1.9, 73: 1.9, 74: 1.9, 75: 1.9, 76: 2.0,
        77: 2.0, 78: 2.0, 79: 2.0, 80: 2.0, 81: 2.0, 82: 2.1,
        83: 2.1, 84: 2.1, 85: 2.1, 86: 2.1, 87: 2.1, 88: 2.2,
        89: 2.2, 90: 2.2
    }

    # If exact weight is in the table, return it
    if weight_kg in lookup_table:
        return lookup_table[weight_kg]

    # For weights below 1 kg or above 90 kg, or between table values,
    # use linear interpolation between nearest values
    weights = sorted(lookup_table.keys())

    if weight_kg < weights[0]:
        # Extrapolate below minimum (use first two points)
        w1, w2 = weights[0], weights[1]
        bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
        slope = (bsa2 - bsa1) / (w2 - w1)
        bsa = bsa1 + slope * (weight_kg - w1)
    elif weight_kg > weights[-1]:
        # Extrapolate above maximum (use last two points)
        w1, w2 = weights[-2], weights[-1]
        bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
        slope = (bsa2 - bsa1) / (w2 - w1)
        bsa = bsa2 + slope * (weight_kg - w2)
    else:
        # Interpolate between two nearest values
        for i in range(len(weights) - 1):
            if weights[i] < weight_kg < weights[i + 1]:
                w1, w2 = weights[i], weights[i + 1]
                bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
                # Linear interpolation
                slope = (bsa2 - bsa1) / (w2 - w1)
                bsa = bsa1 + slope * (weight_kg - w1)
                break

    return round(bsa, 2)

def calculate_height_velocity(current_height, previous_height, current_date, previous_date):
    """Calculate yearly derived height velocity

    Returns:
        dict with 'value' and optional 'message', or None
    """
    if not all([current_height, previous_height, current_date, previous_date]):
        return None

    height_diff = current_height - previous_height
    time_diff_days = (current_date - previous_date).days

    if time_diff_days <= 0:
        return {'value': None, 'message': 'Previous measurement date must be before current measurement date'}

    # Check if interval is at least 4 months (approximately 122 days)
    min_days = 122  # ~4 months
    if time_diff_days < min_days:
        months = round(time_diff_days / 30.44, 1)  # Convert to months for display
        return {
            'value': None,
            'message': f'Height velocity requires at least 4 months between measurements (current interval: {months} months)'
        }

    # Convert to cm per year
    velocity = (height_diff / time_diff_days) * 365.25
    return {'value': round(velocity, 1), 'message': None}

def calculate_gh_dose(bsa, weight_kg):
    """Calculate GH dose in mg/day for 7 mg/m2/week"""
    if not bsa or not weight_kg:
        return None

    # Calculate for 7 mg/m2/week
    mg_per_week = 7 * bsa
    mg_per_day = mg_per_week / 7

    # Round to nearest 0.1 mg
    mg_per_day_rounded = round(mg_per_day, 1)

    # Calculate precise mg/m2/week from the rounded daily dose
    mg_per_week_actual = mg_per_day_rounded * 7
    mg_m2_week_actual = mg_per_week_actual / bsa

    # Calculate mcg/kg/day
    mcg_per_day = mg_per_day_rounded * 1000  # Convert mg to mcg
    mcg_kg_day = mcg_per_day / weight_kg

    return {
        'mg_per_day': mg_per_day_rounded,
        'mg_m2_week': round(mg_m2_week_actual, 1),
        'mcg_kg_day': round(mcg_kg_day, 1)
    }

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

        # Optional previous height data
        previous_height = float(data.get('previous_height', 0)) if data.get('previous_height') else None
        previous_date = datetime.strptime(data['previous_date'], '%Y-%m-%d').date() if data.get('previous_date') else None

        # Optional parental heights
        maternal_height = float(data.get('maternal_height', 0)) if data.get('maternal_height') else None
        paternal_height = float(data.get('paternal_height', 0)) if data.get('paternal_height') else None

        # Calculate age
        age_decimal, calendar_age = calculate_age_in_years(birth_date, measurement_date)

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

        # Calculate height velocity and previous height centile/SDS if previous data available
        height_velocity = None
        previous_height_data = None
        if height and previous_height and previous_date:
            height_velocity = calculate_height_velocity(height, previous_height, measurement_date, previous_date)

            # Calculate centile and SDS for previous height measurement
            previous_height_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=previous_date,
                measurement_method='height',
                observation_value=previous_height,
                reference=reference
            )

            previous_height_calc = previous_height_measurement.measurement['measurement_calculated_values']
            previous_height_sds = float(previous_height_calc['corrected_sds']) if previous_height_calc['corrected_sds'] else None

            previous_height_data = {
                'value': previous_height,
                'centile': round(float(previous_height_calc['corrected_centile']), 2) if previous_height_calc['corrected_centile'] else None,
                'sds': round(previous_height_sds, 2) if previous_height_sds is not None else None
            }

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

            # Calculate centile from z-score (approximate using standard normal distribution)
            from scipy import stats
            mph_centile = stats.norm.cdf(mph_z) * 100

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

        if weight_measurement:
            weight_calc = weight_measurement.measurement['measurement_calculated_values']
        if height_measurement:
            height_calc = height_measurement.measurement['measurement_calculated_values']
        if bmi_measurement:
            bmi_calc = bmi_measurement.measurement['measurement_calculated_values']
            bmi_value = bmi_measurement.measurement['child_observation_value']['observation_value']

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

        # Prepare results - only include data for measurements that were provided
        results = {
            'age_years': round(age_decimal, 2),
            'age_calendar': calendar_age,
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
                'sds': round(bmi_sds, 2) if bmi_sds is not None else None
            } if bmi_measurement else None,
            'ofc': ofc_data,
            'height_velocity': height_velocity,
            'previous_height': previous_height_data,
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

        # Get chart data from rcpchgrowth library
        chart_data = create_chart(
            reference=reference,
            measurement_method=measurement_method,
            sex=sex
        )

        # Extract and flatten centile data from nested structure
        # chart_data is a list of dicts, each with a reference dataset name as key
        centile_curves = []

        for dataset in chart_data:
            for ref_key, ref_data in dataset.items():
                # Navigate: ref_data[sex][measurement_method] = list of centile objects
                if sex in ref_data and measurement_method in ref_data[sex]:
                    for centile_obj in ref_data[sex][measurement_method]:
                        centile_curves.append({
                            'centile': centile_obj.get('centile'),
                            'sds': centile_obj.get('sds'),
                            'data': centile_obj.get('data', [])
                        })

        return jsonify({
            'success': True,
            'centiles': centile_curves
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Chart data error: {str(e)}'
        }), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
