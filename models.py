"""
Models and measurement creation functions
"""
from rcpchgrowth import Measurement
from constants import SDS_HARD_LIMIT, SDS_WARNING_LIMIT, ErrorCodes
from validation import ValidationError


def create_measurement(sex, birth_date, observation_date, measurement_method,
                      observation_value, reference, gestation_weeks=None, gestation_days=None):
    """
    Create a measurement object using rcpchgrowth library

    Args:
        sex: 'male' or 'female'
        birth_date: Date of birth
        observation_date: Date of measurement
        measurement_method: 'weight', 'height', 'bmi', or 'ofc'
        observation_value: Measurement value
        reference: Growth reference ('uk-who', 'turners-syndrome', etc.)
        gestation_weeks: Optional gestation weeks
        gestation_days: Optional gestation days

    Returns:
        Measurement: rcpchgrowth Measurement object
    """
    if gestation_weeks is not None:
        return Measurement(
            sex=sex,
            birth_date=birth_date,
            observation_date=observation_date,
            measurement_method=measurement_method,
            observation_value=observation_value,
            reference=reference,
            gestation_weeks=gestation_weeks,
            gestation_days=gestation_days or 0
        )
    else:
        return Measurement(
            sex=sex,
            birth_date=birth_date,
            observation_date=observation_date,
            measurement_method=measurement_method,
            observation_value=observation_value,
            reference=reference
        )


def validate_measurement_sds(measurement_data, measurement_type):
    """
    Validate SDS values from measurements

    Args:
        measurement_data: Measurement calculation results
        measurement_type: Type of measurement (for error messages)

    Returns:
        list: Warning messages (empty if no warnings)

    Raises:
        ValidationError: If SDS exceeds hard limits
    """
    warnings = []

    if not measurement_data:
        return warnings

    sds = float(measurement_data.get('corrected_sds', 0))

    # Hard limit check - reject measurements
    if abs(sds) > SDS_HARD_LIMIT:
        raise ValidationError(
            f'{measurement_type} SDS ({sds:.2f}) exceeds acceptable range (±{SDS_HARD_LIMIT} SDS). Please check measurement accuracy.',
            ErrorCodes.SDS_OUT_OF_RANGE
        )

    # Warning check
    if abs(sds) > SDS_WARNING_LIMIT:
        warnings.append(
            f'{measurement_type} SDS ({sds:.2f}) is beyond ±{SDS_WARNING_LIMIT} SDS. Please verify measurement accuracy.'
        )

    return warnings


def extract_measurement_result(measurement_obj, measurement_type):
    """
    Extract standardized result from measurement object

    Args:
        measurement_obj: rcpchgrowth Measurement object
        measurement_type: 'weight', 'height', 'bmi', or 'ofc'

    Returns:
        dict: Formatted measurement result with value, centile, and SDS
    """
    if not measurement_obj:
        return None

    calc = measurement_obj.measurement['measurement_calculated_values']

    result = {
        'value': measurement_obj.measurement['child_observation_value']['observation_value'],
        'centile': round(float(calc['corrected_centile']), 2) if calc['corrected_centile'] else None,
        'sds': round(float(calc['corrected_sds']), 2) if calc['corrected_sds'] is not None else None
    }

    # For BMI, extract the calculated BMI value
    if measurement_type == 'bmi':
        result['value'] = round(result['value'], 1)

    return result


def create_corrected_measurement_result(measurement_obj, corrected_age_decimal, measurement_value):
    """
    Create result for corrected age measurement

    Args:
        measurement_obj: rcpchgrowth Measurement object (with gestation)
        corrected_age_decimal: Corrected age in decimal years
        measurement_value: The measurement value

    Returns:
        dict: Formatted corrected measurement result
    """
    if not measurement_obj:
        return None

    calc = measurement_obj.measurement['measurement_calculated_values']

    return {
        'age': round(corrected_age_decimal, 2),
        'value': measurement_value,
        'centile': round(float(calc['corrected_centile']), 2) if calc['corrected_centile'] else None,
        'sds': round(float(calc['corrected_sds']), 2) if calc['corrected_sds'] is not None else None
    }
