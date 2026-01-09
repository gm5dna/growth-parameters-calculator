"""
Utility functions for mid-parental height and chart data
"""
from rcpchgrowth import mid_parental_height, mid_parental_height_z
from rcpchgrowth import lower_and_upper_limits_of_expected_height_z, measurement_from_sds
from rcpchgrowth.chart_functions import create_chart
from scipy import stats
from constants import MPH_ADULT_AGE


def calculate_mid_parental_height(maternal_height, paternal_height, sex):
    """
    Calculate mid-parental height with target range

    Args:
        maternal_height: Mother's height in cm
        paternal_height: Father's height in cm
        sex: Child's sex ('male' or 'female')

    Returns:
        dict: Mid-parental height data with centile and target range, or None
    """
    if not maternal_height or not paternal_height:
        return None

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

    # Convert z-scores to heights at adult age
    lower_height = measurement_from_sds(
        reference='uk-who',
        requested_sds=lower_z,
        measurement_method='height',
        sex=sex,
        age=MPH_ADULT_AGE
    )

    upper_height = measurement_from_sds(
        reference='uk-who',
        requested_sds=upper_z,
        measurement_method='height',
        sex=sex,
        age=MPH_ADULT_AGE
    )

    # Calculate centile from z-score (using standard normal distribution)
    mph_centile = stats.norm.cdf(mph_z) * 100

    return {
        'mid_parental_height': round(mph_cm, 1),
        'mid_parental_height_sds': round(mph_z, 2),
        'mid_parental_height_centile': round(mph_centile, 1),
        'target_range_lower': round(lower_height, 1),
        'target_range_upper': round(upper_height, 1)
    }


def get_chart_data(reference, measurement_method, sex, min_age=0, max_age=20):
    """
    Fetch centile chart data from rcpchgrowth library

    Args:
        reference: Growth reference ('uk-who', 'turners-syndrome', etc.)
        measurement_method: 'weight', 'height', 'bmi', or 'ofc'
        sex: 'male' or 'female'
        min_age: Minimum age for chart (years)
        max_age: Maximum age for chart (years)

    Returns:
        list: Centile curve data for chart rendering
    """
    try:
        chart_data = create_chart(
            reference=reference,
            centile_selection=[0.4, 2, 9, 25, 50, 75, 91, 98, 99.6],
            measurement_method=measurement_method,
            sex=sex
        )

        # Extract centile lines
        centiles = []
        for centile in chart_data['centile_data']:
            centile_data = {
                'centile': centile['centile'],
                'data': centile['data']
            }
            centiles.append(centile_data)

        return centiles
    except Exception as e:
        # Return empty list if chart generation fails
        print(f"Chart generation error: {str(e)}")
        return []


def format_error_response(error_code, error_message):
    """
    Format standardized error response

    Args:
        error_code: Error code from ErrorCodes
        error_message: Human-readable error message

    Returns:
        dict: Formatted error response
    """
    return {
        'success': False,
        'error': error_message,
        'error_code': error_code
    }


def format_success_response(results):
    """
    Format standardized success response

    Args:
        results: Calculation results dictionary

    Returns:
        dict: Formatted success response
    """
    return {
        'success': True,
        'results': results
    }
