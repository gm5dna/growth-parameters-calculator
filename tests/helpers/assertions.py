"""
Custom Assertion Helpers

Reusable assertion functions for common test patterns.
These make tests more readable and maintainable.
"""


def assert_valid_response(response, expected_status=200):
    """
    Assert that HTTP response is valid with expected status

    Args:
        response: Flask test client response
        expected_status: Expected HTTP status code

    Raises:
        AssertionError: If response is invalid
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.get_data(as_text=True)}"
    )

    if expected_status == 200:
        result = response.get_json()
        assert result is not None, "Response should contain JSON data"


def assert_error_response(response, expected_status=400, error_message_contains=None):
    """
    Assert that response is a properly formatted error

    Args:
        response: Flask test client response
        expected_status: Expected HTTP status code (default: 400)
        error_message_contains: Optional string that should appear in error message

    Raises:
        AssertionError: If response doesn't match error format
    """
    assert response.status_code == expected_status, (
        f"Expected error status {expected_status}, got {response.status_code}"
    )

    result = response.get_json()
    assert result is not None, "Error response should contain JSON"
    assert result.get('success') is False, "Error response should have success=False"
    assert 'error' in result, "Error response should contain 'error' field"

    if error_message_contains:
        error_msg = result['error'].lower()
        search_term = error_message_contains.lower()
        assert search_term in error_msg, (
            f"Expected error message to contain '{error_message_contains}', "
            f"but got: {result['error']}"
        )


def assert_measurement_result(measurement_data, measurement_type):
    """
    Assert that measurement result has correct structure

    Args:
        measurement_data: Measurement data from API response
        measurement_type: Type of measurement ('weight', 'height', 'bmi', 'ofc')

    Raises:
        AssertionError: If measurement structure is invalid
    """
    assert measurement_data is not None, f"{measurement_type} data should not be None"

    # Check required fields
    assert 'value' in measurement_data, f"{measurement_type} should have 'value'"
    assert 'centile' in measurement_data, f"{measurement_type} should have 'centile'"
    assert 'sds' in measurement_data, f"{measurement_type} should have 'sds'"

    # Validate data types and ranges
    value = measurement_data['value']
    assert isinstance(value, (int, float)), f"{measurement_type} value should be numeric"
    assert value > 0, f"{measurement_type} value should be positive"

    # Centile should be 0-100 (if not None)
    centile = measurement_data['centile']
    if centile is not None:
        assert 0 <= centile <= 100, (
            f"{measurement_type} centile should be 0-100, got {centile}"
        )

    # SDS should be reasonable (if not None)
    sds = measurement_data['sds']
    if sds is not None:
        assert -10 <= sds <= 10, (
            f"{measurement_type} SDS should be within reasonable range, got {sds}"
        )


def assert_age_result(age_data):
    """
    Assert that age result has correct structure

    Args:
        age_data: Age data from API response

    Raises:
        AssertionError: If age structure is invalid
    """
    assert age_data is not None, "Age data should not be None"
    assert 'decimal_age' in age_data, "Age should have 'decimal_age'"
    assert 'calendar_age' in age_data, "Age should have 'calendar_age'"

    decimal_age = age_data['decimal_age']
    assert isinstance(decimal_age, (int, float)), "Decimal age should be numeric"
    assert 0 <= decimal_age <= 25, f"Decimal age should be 0-25 years, got {decimal_age}"


def assert_chart_data(chart_data):
    """
    Assert that chart data has correct structure

    Args:
        chart_data: Chart data from API response

    Raises:
        AssertionError: If chart structure is invalid
    """
    assert isinstance(chart_data, list), "Chart data should be a list"
    assert len(chart_data) > 0, "Chart data should not be empty"

    # Check first centile structure
    first_centile = chart_data[0]
    assert 'centile' in first_centile, "Centile should have 'centile' field"
    assert 'data' in first_centile, "Centile should have 'data' field"
    assert isinstance(first_centile['data'], list), "Centile data should be a list"

    # Check data points
    if len(first_centile['data']) > 0:
        first_point = first_centile['data'][0]
        assert 'x' in first_point, "Data point should have 'x' (age)"
        assert 'y' in first_point, "Data point should have 'y' (value)"


def assert_mph_data(mph_data):
    """
    Assert that mid-parental height data has correct structure

    Args:
        mph_data: MPH data from API response

    Raises:
        AssertionError: If MPH structure is invalid
    """
    assert mph_data is not None, "MPH data should not be None"

    required_fields = [
        'mid_parental_height',
        'mid_parental_height_sds',
        'mid_parental_height_centile',
        'target_range_lower',
        'target_range_upper'
    ]

    for field in required_fields:
        assert field in mph_data, f"MPH data should have '{field}'"

    # Verify target range is logical
    mph_value = mph_data['mid_parental_height']
    lower = mph_data['target_range_lower']
    upper = mph_data['target_range_upper']

    assert lower < mph_value < upper, (
        f"MPH target range invalid: {lower} < {mph_value} < {upper}"
    )

    # Verify centile is valid
    centile = mph_data['mid_parental_height_centile']
    assert 0 <= centile <= 100, f"MPH centile should be 0-100, got {centile}"


def assert_pdf_response(response):
    """
    Assert that response is a valid PDF

    Args:
        response: Flask test client response

    Raises:
        AssertionError: If response is not a valid PDF
    """
    assert response.status_code == 200, f"PDF response should be 200, got {response.status_code}"
    assert response.content_type == 'application/pdf', (
        f"Content type should be application/pdf, got {response.content_type}"
    )

    pdf_data = response.data
    assert len(pdf_data) > 0, "PDF data should not be empty"
    assert pdf_data.startswith(b'%PDF'), "PDF should start with PDF magic number"


def assert_corrected_age_data(corrected_age_data):
    """
    Assert that corrected age data (for preterm) has correct structure

    Args:
        corrected_age_data: Corrected age data from API response

    Raises:
        AssertionError: If corrected age structure is invalid
    """
    assert corrected_age_data is not None, "Corrected age data should not be None"

    required_fields = ['decimal_age', 'calendar_age']
    for field in required_fields:
        assert field in corrected_age_data, (
            f"Corrected age data should have '{field}'"
        )

    decimal_age = corrected_age_data['decimal_age']
    assert isinstance(decimal_age, (int, float)), "Corrected decimal age should be numeric"
    assert decimal_age >= 0, "Corrected age should be non-negative"


def assert_bsa_data(bsa_data):
    """
    Assert that BSA (body surface area) data has correct structure

    Args:
        bsa_data: BSA data from API response

    Raises:
        AssertionError: If BSA structure is invalid
    """
    assert bsa_data is not None, "BSA data should not be None"
    assert 'value' in bsa_data, "BSA should have 'value'"
    assert 'method' in bsa_data, "BSA should have 'method'"

    bsa_value = bsa_data['value']
    assert isinstance(bsa_value, (int, float)), "BSA value should be numeric"
    assert 0.1 <= bsa_value <= 3.0, f"BSA should be 0.1-3.0 m², got {bsa_value}"


def assert_height_velocity_data(hv_data):
    """
    Assert that height velocity data has correct structure

    Args:
        hv_data: Height velocity data from API response

    Raises:
        AssertionError: If height velocity structure is invalid
    """
    assert hv_data is not None, "Height velocity data should not be None"
    assert 'value' in hv_data, "Height velocity should have 'value'"

    hv_value = hv_data['value']
    assert isinstance(hv_value, (int, float)), "Height velocity should be numeric"

    # Height velocity can be negative (measurement error) but typically 0-20 cm/year
    assert -10 <= hv_value <= 30, (
        f"Height velocity should be reasonable, got {hv_value} cm/year"
    )


def assert_success_with_measurements(response, *measurement_types):
    """
    Assert successful response with specified measurements

    Args:
        response: Flask test client response
        *measurement_types: Expected measurement types ('weight', 'height', etc.)

    Example:
        assert_success_with_measurements(response, 'weight', 'height', 'bmi')
    """
    assert_valid_response(response, 200)

    result = response.get_json()
    assert result['success'] is True, "Response should be successful"

    for measurement_type in measurement_types:
        field_name = f"{measurement_type}_data"
        assert field_name in result, f"Response should contain '{field_name}'"
        assert_measurement_result(result[field_name], measurement_type)


def assert_warning_present(response, warning_text):
    """
    Assert that response contains a warning message

    Args:
        response: Flask test client response
        warning_text: Text that should appear in warnings

    Raises:
        AssertionError: If warning not found
    """
    result = response.get_json()
    assert 'warnings' in result, "Response should have 'warnings' field"

    warnings = result['warnings']
    assert isinstance(warnings, list), "Warnings should be a list"
    assert len(warnings) > 0, "Should have at least one warning"

    warning_messages = ' '.join(warnings).lower()
    assert warning_text.lower() in warning_messages, (
        f"Expected warning containing '{warning_text}', got warnings: {warnings}"
    )
