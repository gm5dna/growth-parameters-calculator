"""
Test Data Generators

Reusable functions for generating test data across test modules.
This ensures consistency and reduces duplication in tests.
"""

from datetime import date, timedelta


def valid_calculation_data(**overrides):
    """
    Generate valid calculation data with sensible defaults

    Args:
        **overrides: Any fields to override in the default data

    Returns:
        dict: Valid calculation request data

    Example:
        data = valid_calculation_data(sex='female', weight='15.0')
    """
    base_data = {
        'birth_date': '2020-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '18.5',
        'height': '105.0',
        'reference': 'uk-who'
    }
    base_data.update(overrides)
    return base_data


def infant_data(**overrides):
    """
    Generate data for typical infant (0-2 years)

    Example:
        data = infant_data(age_months=6)
    """
    # If age_months provided, calculate dates
    if 'age_months' in overrides:
        age_months = overrides.pop('age_months')
        measurement_date = date.today()
        birth_date = measurement_date - timedelta(days=age_months * 30)
        overrides['birth_date'] = birth_date.isoformat()
        overrides['measurement_date'] = measurement_date.isoformat()

    base_data = {
        'birth_date': '2023-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '10.5',
        'height': '76.0',
        'ofc': '47.0'
    }
    base_data.update(overrides)
    return base_data


def child_data(age_years=5, **overrides):
    """
    Generate data for typical child (2-12 years)

    Args:
        age_years: Age in years (default: 5)
        **overrides: Additional fields to override
    """
    measurement_date = date.today()
    birth_date = measurement_date - timedelta(days=age_years * 365)

    base_data = {
        'birth_date': birth_date.isoformat(),
        'measurement_date': measurement_date.isoformat(),
        'sex': 'female',
        'weight': str(15.0 + age_years * 2),  # Rough estimate
        'height': str(85.0 + age_years * 6)   # Rough estimate
    }
    base_data.update(overrides)
    return base_data


def preterm_data(gestation_weeks=32, gestation_days=4, **overrides):
    """
    Generate data for preterm infant

    Args:
        gestation_weeks: Gestational age in weeks (default: 32)
        gestation_days: Additional days (default: 4)
        **overrides: Additional fields
    """
    base_data = {
        'birth_date': '2023-10-01',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '5.8',
        'height': '65.0',
        'gestation_weeks': gestation_weeks,
        'gestation_days': gestation_days
    }
    base_data.update(overrides)
    return base_data


def turner_syndrome_data(**overrides):
    """
    Generate data for Turner syndrome patient

    Example:
        data = turner_syndrome_data(height='95.0')
    """
    base_data = {
        'birth_date': '2018-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'female',
        'height': '110.0',
        'weight': '20.0',
        'reference': 'turners-syndrome'
    }
    base_data.update(overrides)
    return base_data


def with_parental_heights(data, maternal_height='165', paternal_height='180'):
    """
    Add parental height data to existing calculation data

    Args:
        data: Base calculation data dictionary
        maternal_height: Mother's height in cm
        paternal_height: Father's height in cm

    Returns:
        dict: Data with parental heights added
    """
    data['maternal_height'] = maternal_height
    data['paternal_height'] = paternal_height
    return data


def with_previous_measurement(data, months_ago=6, height_change=-5.0, weight_change=-2.0):
    """
    Add previous measurement data for height velocity calculation

    Args:
        data: Base calculation data
        months_ago: How many months ago was the previous measurement
        height_change: Height difference (negative = shorter before)
        weight_change: Weight difference (negative = lighter before)

    Returns:
        dict: Data with previous measurements added
    """
    from datetime import datetime

    current_date = datetime.fromisoformat(data['measurement_date'])
    previous_date = current_date - timedelta(days=months_ago * 30)

    current_height = float(data.get('height', 100))
    current_weight = float(data.get('weight', 15))

    data['previous_measurements'] = [
        {
            'date': previous_date.isoformat()[:10],
            'height': current_height + height_change,
            'weight': current_weight + weight_change
        }
    ]
    return data


def with_bone_age(data, bone_age_years, bone_age_months=0):
    """
    Add bone age assessment to calculation data

    Args:
        data: Base calculation data
        bone_age_years: Bone age in years
        bone_age_months: Additional months

    Returns:
        dict: Data with bone age assessment
    """
    data['bone_age_assessments'] = [
        {
            'assessment_date': data['measurement_date'],
            'bone_age_years': bone_age_years,
            'bone_age_months': bone_age_months
        }
    ]
    return data


def extreme_sds_data(sds_target=-5.0, **overrides):
    """
    Generate data likely to produce extreme SDS values

    Args:
        sds_target: Target SDS (approximate)
        **overrides: Additional fields

    Note:
        This generates data that should trigger SDS warnings or errors
    """
    # For very low SDS, use very low weight
    if sds_target < 0:
        base_weight = '0.5'  # Extremely low
    else:
        base_weight = '50.0'  # Extremely high for age

    base_data = {
        'birth_date': '2023-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': base_weight
    }
    base_data.update(overrides)
    return base_data


def chart_data_request(measurement_method='height', sex='male', reference='uk-who'):
    """
    Generate valid chart data request

    Args:
        measurement_method: 'height', 'weight', 'bmi', or 'ofc'
        sex: 'male' or 'female'
        reference: Growth reference

    Returns:
        dict: Valid chart data request
    """
    return {
        'reference': reference,
        'measurement_method': measurement_method,
        'sex': sex
    }


def malformed_data_examples():
    """
    Generate collection of malformed data examples for error testing

    Returns:
        list: List of (description, data) tuples
    """
    return [
        ('Empty object', {}),
        ('Null values', {'birth_date': None, 'sex': None, 'weight': None}),
        ('Wrong types', {'birth_date': 123, 'sex': True, 'weight': [10.5]}),
        ('Invalid sex', {'birth_date': '2023-01-15', 'measurement_date': '2024-01-15', 'sex': 'invalid', 'weight': '10'}),
        ('Future dates', {
            'birth_date': (date.today() + timedelta(days=30)).isoformat(),
            'measurement_date': date.today().isoformat(),
            'sex': 'male',
            'weight': '10'
        }),
        ('Missing required fields', {'sex': 'male', 'weight': '10'}),
    ]


def boundary_values():
    """
    Generate boundary value test cases

    Returns:
        dict: Dictionary of measurement types to (min, max, just_below_min, just_above_max) tuples
    """
    return {
        'weight': (0.1, 300, 0.09, 300.1),
        'height': (10, 250, 9.9, 250.1),
        'ofc': (10, 100, 9.9, 100.1),
        'gestation_weeks': (22, 44, 21, 45),
        'gestation_days': (0, 6, -1, 7)
    }


# Convenience functions for quick test data access
def quick_infant():
    """Quick infant data (1 year old)"""
    return infant_data()


def quick_child():
    """Quick child data (5 years old)"""
    return child_data(age_years=5)


def quick_preterm():
    """Quick preterm data (32 weeks)"""
    return preterm_data()
