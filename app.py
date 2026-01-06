from flask import Flask, render_template, request, jsonify
from rcpchgrowth import Measurement, mid_parental_height, mid_parental_height_z, lower_and_upper_limits_of_expected_height_z, measurement_from_sds
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

app = Flask(__name__)

def calculate_age_in_years(birth_date, measurement_date):
    """Calculate age in decimal years"""
    delta = relativedelta(measurement_date, birth_date)
    years = delta.years
    months = delta.months
    days = delta.days

    # Convert to decimal years
    decimal_years = years + (months / 12.0) + (days / 365.25)
    return decimal_years

def calculate_boyd_bsa(weight_kg, height_cm):
    """Calculate Body Surface Area using Boyd formula"""
    # Boyd formula: BSA = 0.0003207 * (height_cm^0.3) * (weight_g^(0.7285 - (0.0188 * log10(weight_g))))
    if weight_kg <= 0 or height_cm <= 0:
        return None

    weight_g = weight_kg * 1000
    log_weight = math.log10(weight_g)
    bsa = 0.0003207 * (height_cm ** 0.3) * (weight_g ** (0.7285 - (0.0188 * log_weight)))
    return round(bsa, 3)

def calculate_height_velocity(current_height, previous_height, current_date, previous_date):
    """Calculate yearly derived height velocity"""
    if not all([current_height, previous_height, current_date, previous_date]):
        return None

    height_diff = current_height - previous_height
    time_diff_days = (current_date - previous_date).days

    if time_diff_days <= 0:
        return None

    # Convert to cm per year
    velocity = (height_diff / time_diff_days) * 365.25
    return round(velocity, 2)

def calculate_gh_dose(bsa):
    """Calculate GH dose in mg/day for 7 mg/m2/week"""
    if not bsa:
        return None

    # Calculate for 7 mg/m2/week
    mg_per_week = 7 * bsa
    mg_per_day = mg_per_week / 7

    # Round to nearest 0.1 mg
    mg_per_day_rounded = round(mg_per_day, 1)

    # Calculate precise mg/m2/week from the rounded daily dose
    mg_per_week_actual = mg_per_day_rounded * 7
    mg_m2_week_actual = mg_per_week_actual / bsa

    return {
        'mg_per_day': mg_per_day_rounded,
        'mg_m2_week': round(mg_m2_week_actual, 1)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json

        # Parse input data
        weight = float(data['weight'])
        height = float(data['height'])
        birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        measurement_date = datetime.strptime(data['measurement_date'], '%Y-%m-%d').date()
        sex = data['sex']
        reference = data.get('reference', 'uk-who')

        # Optional previous height data
        previous_height = float(data.get('previous_height', 0)) if data.get('previous_height') else None
        previous_date = datetime.strptime(data['previous_date'], '%Y-%m-%d').date() if data.get('previous_date') else None

        # Optional parental heights
        maternal_height = float(data.get('maternal_height', 0)) if data.get('maternal_height') else None
        paternal_height = float(data.get('paternal_height', 0)) if data.get('paternal_height') else None

        # Optional OFC (head circumference)
        ofc = float(data.get('ofc', 0)) if data.get('ofc') else None

        # Calculate age
        age_decimal = calculate_age_in_years(birth_date, measurement_date)

        # Create measurement objects using selected reference
        weight_measurement = Measurement(
            sex=sex,
            birth_date=birth_date,
            observation_date=measurement_date,
            measurement_method='weight',
            observation_value=weight,
            reference=reference
        )

        height_measurement = Measurement(
            sex=sex,
            birth_date=birth_date,
            observation_date=measurement_date,
            measurement_method='height',
            observation_value=height,
            reference=reference
        )

        bmi_measurement = Measurement(
            sex=sex,
            birth_date=birth_date,
            observation_date=measurement_date,
            measurement_method='bmi',
            observation_value=weight / ((height / 100) ** 2),
            reference=reference
        )

        # Calculate OFC if provided
        ofc_measurement = None
        if ofc:
            ofc_measurement = Measurement(
                sex=sex,
                birth_date=birth_date,
                observation_date=measurement_date,
                measurement_method='ofc',
                observation_value=ofc,
                reference=reference
            )

        # Calculate height velocity if previous data available
        height_velocity = None
        if previous_height and previous_date:
            height_velocity = calculate_height_velocity(height, previous_height, measurement_date, previous_date)

        # Calculate BSA
        bsa = calculate_boyd_bsa(weight, height)

        # Calculate GH dose for 7 mg/m2/week
        gh_dose = calculate_gh_dose(bsa)

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

        # Extract calculated values
        weight_calc = weight_measurement.measurement['measurement_calculated_values']
        height_calc = height_measurement.measurement['measurement_calculated_values']
        bmi_calc = bmi_measurement.measurement['measurement_calculated_values']
        bmi_value = bmi_measurement.measurement['child_observation_value']['observation_value']

        # Extract OFC values if calculated
        ofc_data = None
        if ofc_measurement:
            ofc_calc = ofc_measurement.measurement['measurement_calculated_values']
            ofc_data = {
                'value': ofc,
                'centile': round(float(ofc_calc['corrected_centile']), 2) if ofc_calc['corrected_centile'] else None,
                'sds': round(float(ofc_calc['corrected_sds']), 2) if ofc_calc['corrected_sds'] else None
            }

        # Prepare results
        results = {
            'age_years': round(age_decimal, 2),
            'weight': {
                'value': weight,
                'centile': round(float(weight_calc['corrected_centile']), 2) if weight_calc['corrected_centile'] else None,
                'sds': round(float(weight_calc['corrected_sds']), 2) if weight_calc['corrected_sds'] else None
            },
            'height': {
                'value': height,
                'centile': round(float(height_calc['corrected_centile']), 2) if height_calc['corrected_centile'] else None,
                'sds': round(float(height_calc['corrected_sds']), 2) if height_calc['corrected_sds'] else None
            },
            'bmi': {
                'value': round(float(bmi_value), 2),
                'centile': round(float(bmi_calc['corrected_centile']), 2) if bmi_calc['corrected_centile'] else None,
                'sds': round(float(bmi_calc['corrected_sds']), 2) if bmi_calc['corrected_sds'] else None
            },
            'ofc': ofc_data,
            'height_velocity': height_velocity,
            'bsa': bsa,
            'gh_dose': gh_dose,
            'mid_parental_height': mph_data
        }

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
