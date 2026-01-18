"""
Utility functions for mid-parental height and chart data
"""
import math
from rcpchgrowth import mid_parental_height, mid_parental_height_z
from rcpchgrowth import lower_and_upper_limits_of_expected_height_z, measurement_from_sds
from rcpchgrowth import percentage_median_bmi
from rcpchgrowth.chart_functions import create_chart
from constants import MPH_ADULT_AGE


def norm_cdf(z):
    """
    Calculate cumulative distribution function for standard normal distribution
    Uses the error function approximation (accurate to ~1e-7)

    Args:
        z: z-score (standard deviations from mean)

    Returns:
        Probability (0 to 1) that a value is less than z
    """
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def calculate_percentage_median_bmi(reference, age, bmi, sex):
    """
    Calculate BMI as percentage of median for age and sex

    This is particularly useful for malnutrition assessment:
    - <70% indicates severe malnutrition
    - 70-80% indicates moderate malnutrition
    - 80-90% indicates mild malnutrition
    - 90-110% indicates normal nutritional status
    - >120% may indicate overweight/obesity

    Args:
        reference: Growth reference ('uk-who', 'turners-syndrome', etc.)
        age: Age in years (decimal)
        bmi: Actual BMI value
        sex: Child's sex ('male' or 'female')

    Returns:
        float: BMI as percentage of median, rounded to 1 decimal place, or None if calculation fails
    """
    try:
        percentage = percentage_median_bmi(
            reference=reference,
            age=age,
            actual_bmi=bmi,
            sex=sex
        )
        return round(percentage, 1) if percentage is not None else None
    except Exception as e:
        print(f"Error calculating percentage median BMI: {str(e)}")
        return None


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
    mph_centile = norm_cdf(mph_z) * 100

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
            centile_format=[0.4, 2, 9, 25, 50, 75, 91, 98, 99.6],
            measurement_method=measurement_method,
            sex=sex
        )

        # chart_data is a list of dicts with reference names as keys
        # Extract centile curves from the structure
        centiles = []
        if isinstance(chart_data, list) and len(chart_data) > 0:
            for dataset in chart_data:
                for ref_name, ref_data in dataset.items():
                    if sex in ref_data and measurement_method in ref_data[sex]:
                        for centile_obj in ref_data[sex][measurement_method]:
                            centiles.append({
                                'centile': centile_obj.get('centile'),
                                'data': centile_obj.get('data', [])
                            })

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
