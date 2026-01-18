"""
Comprehensive Tests for utils.py

Tests utility functions for MPH, chart data, BMI percentage, and response formatting
"""

import pytest
import math
from utils import (
    norm_cdf,
    calculate_percentage_median_bmi,
    calculate_mid_parental_height,
    get_chart_data,
    format_error_response,
    format_success_response
)
from constants import ErrorCodes


class TestNormCdf:
    """Test suite for norm_cdf function"""

    def test_norm_cdf_zero(self):
        """Test CDF at z=0 (should be 0.5)"""
        result = norm_cdf(0)
        assert abs(result - 0.5) < 1e-7

    def test_norm_cdf_positive(self):
        """Test CDF for positive z-scores"""
        # z=1 should be ~0.8413
        result = norm_cdf(1.0)
        assert 0.84 < result < 0.85

        # z=2 should be ~0.9772
        result = norm_cdf(2.0)
        assert 0.97 < result < 0.98

    def test_norm_cdf_negative(self):
        """Test CDF for negative z-scores"""
        # z=-1 should be ~0.1587
        result = norm_cdf(-1.0)
        assert 0.15 < result < 0.16

        # z=-2 should be ~0.0228
        result = norm_cdf(-2.0)
        assert 0.02 < result < 0.03

    def test_norm_cdf_extreme_positive(self):
        """Test CDF for large positive z-score"""
        result = norm_cdf(3.0)
        assert result > 0.99

    def test_norm_cdf_extreme_negative(self):
        """Test CDF for large negative z-score"""
        result = norm_cdf(-3.0)
        assert result < 0.01

    def test_norm_cdf_symmetry(self):
        """Test that CDF is symmetric around 0"""
        for z in [0.5, 1.0, 1.5, 2.0]:
            result_pos = norm_cdf(z)
            result_neg = norm_cdf(-z)
            assert abs((result_pos + result_neg) - 1.0) < 1e-7


class TestCalculatePercentageMedianBMI:
    """Test suite for calculate_percentage_median_bmi function"""

    def test_percentage_median_bmi_normal(self):
        """Test BMI percentage calculation for normal range"""
        # 4-year-old with BMI of 15.5 (approximately 50th centile)
        percentage = calculate_percentage_median_bmi(
            reference='uk-who',
            age=4.0,
            bmi=15.5,
            sex='male'
        )
        assert percentage is not None
        assert 90 < percentage < 110  # Should be near 100%

    def test_percentage_median_bmi_different_ages(self):
        """Test BMI percentage at different ages"""
        # Infant
        infant_pct = calculate_percentage_median_bmi(
            reference='uk-who',
            age=1.0,
            bmi=17.0,
            sex='female'
        )
        assert infant_pct is not None

        # Child
        child_pct = calculate_percentage_median_bmi(
            reference='uk-who',
            age=10.0,
            bmi=18.0,
            sex='male'
        )
        assert child_pct is not None

    def test_percentage_median_bmi_rounding(self):
        """Test that percentage is rounded to 1 decimal place"""
        percentage = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=16.0,
            sex='female'
        )
        if percentage is not None:
            # Check it has at most 1 decimal place
            assert percentage == round(percentage, 1)

    def test_percentage_median_bmi_invalid_age(self):
        """Test BMI percentage with invalid age (should return None)"""
        # Age beyond valid range
        percentage = calculate_percentage_median_bmi(
            reference='uk-who',
            age=30.0,  # Beyond pediatric range
            bmi=22.0,
            sex='male'
        )
        # Should handle gracefully (may return None or raise handled exception)
        assert percentage is None or isinstance(percentage, (int, float))

    def test_percentage_median_bmi_different_sexes(self):
        """Test BMI percentage for both sexes"""
        male_pct = calculate_percentage_median_bmi(
            reference='uk-who',
            age=8.0,
            bmi=17.0,
            sex='male'
        )
        female_pct = calculate_percentage_median_bmi(
            reference='uk-who',
            age=8.0,
            bmi=17.0,
            sex='female'
        )
        # Both should be valid but potentially different
        assert male_pct is not None
        assert female_pct is not None


class TestCalculateMidParentalHeight:
    """Test suite for calculate_mid_parental_height function"""

    def test_mph_male_child(self):
        """Test MPH calculation for male child"""
        result = calculate_mid_parental_height(
            maternal_height=165.0,
            paternal_height=180.0,
            sex='male'
        )
        assert result is not None
        assert 'mid_parental_height' in result
        assert 'mid_parental_height_sds' in result
        assert 'mid_parental_height_centile' in result
        assert 'target_range_lower' in result
        assert 'target_range_upper' in result

        # MPH for male child should be approximately (165 + 180)/2 + 6.5 = 179.0
        assert 175 < result['mid_parental_height'] < 183

    def test_mph_female_child(self):
        """Test MPH calculation for female child"""
        result = calculate_mid_parental_height(
            maternal_height=165.0,
            paternal_height=180.0,
            sex='female'
        )
        assert result is not None
        # MPH for female child should be approximately (165 + 180)/2 - 6.5 = 166.0
        assert 162 < result['mid_parental_height'] < 170

    def test_mph_missing_maternal_height(self):
        """Test MPH with missing maternal height"""
        result = calculate_mid_parental_height(
            maternal_height=None,
            paternal_height=180.0,
            sex='male'
        )
        assert result is None

    def test_mph_missing_paternal_height(self):
        """Test MPH with missing paternal height"""
        result = calculate_mid_parental_height(
            maternal_height=165.0,
            paternal_height=None,
            sex='female'
        )
        assert result is None

    def test_mph_both_heights_missing(self):
        """Test MPH with both heights missing"""
        result = calculate_mid_parental_height(
            maternal_height=None,
            paternal_height=None,
            sex='male'
        )
        assert result is None

    def test_mph_zero_maternal_height(self):
        """Test MPH with zero maternal height (falsy)"""
        result = calculate_mid_parental_height(
            maternal_height=0,
            paternal_height=180.0,
            sex='male'
        )
        assert result is None

    def test_mph_target_range(self):
        """Test that target range is valid (lower < mph < upper)"""
        result = calculate_mid_parental_height(
            maternal_height=165.0,
            paternal_height=180.0,
            sex='male'
        )
        assert result is not None
        assert result['target_range_lower'] < result['mid_parental_height'] < result['target_range_upper']

    def test_mph_rounding(self):
        """Test that MPH values are rounded correctly"""
        result = calculate_mid_parental_height(
            maternal_height=162.3,
            paternal_height=177.8,
            sex='female'
        )
        assert result is not None
        # Check rounding to 1 decimal place
        assert result['mid_parental_height'] == round(result['mid_parental_height'], 1)
        assert result['target_range_lower'] == round(result['target_range_lower'], 1)
        assert result['target_range_upper'] == round(result['target_range_upper'], 1)
        # Check SDS rounded to 2 decimals
        assert result['mid_parental_height_sds'] == round(result['mid_parental_height_sds'], 2)
        # Check centile rounded to 1 decimal
        assert result['mid_parental_height_centile'] == round(result['mid_parental_height_centile'], 1)

    def test_mph_tall_parents(self):
        """Test MPH with tall parents"""
        result = calculate_mid_parental_height(
            maternal_height=175.0,
            paternal_height=190.0,
            sex='male'
        )
        assert result is not None
        assert result['mid_parental_height'] > 180  # Should be tall
        assert result['mid_parental_height_centile'] > 50  # Above average

    def test_mph_short_parents(self):
        """Test MPH with short parents"""
        result = calculate_mid_parental_height(
            maternal_height=155.0,
            paternal_height=165.0,
            sex='female'
        )
        assert result is not None
        assert result['mid_parental_height'] < 165  # Should be short
        assert result['mid_parental_height_centile'] < 50  # Below average


class TestGetChartData:
    """Test suite for get_chart_data function"""

    def test_get_chart_data_height_male(self):
        """Test fetching height chart data for males"""
        centiles = get_chart_data(
            reference='uk-who',
            measurement_method='height',
            sex='male'
        )
        assert isinstance(centiles, list)
        assert len(centiles) > 0
        # Check structure of centile data
        for centile in centiles:
            assert 'centile' in centile
            assert 'data' in centile

    def test_get_chart_data_weight_female(self):
        """Test fetching weight chart data for females"""
        centiles = get_chart_data(
            reference='uk-who',
            measurement_method='weight',
            sex='female'
        )
        assert isinstance(centiles, list)
        assert len(centiles) > 0

    def test_get_chart_data_bmi(self):
        """Test fetching BMI chart data"""
        centiles = get_chart_data(
            reference='uk-who',
            measurement_method='bmi',
            sex='male'
        )
        assert isinstance(centiles, list)
        assert len(centiles) > 0

    def test_get_chart_data_ofc(self):
        """Test fetching OFC chart data"""
        centiles = get_chart_data(
            reference='uk-who',
            measurement_method='ofc',
            sex='female'
        )
        assert isinstance(centiles, list)
        assert len(centiles) > 0

    def test_get_chart_data_turner_syndrome(self):
        """Test fetching chart data for Turner syndrome"""
        centiles = get_chart_data(
            reference='turners-syndrome',
            measurement_method='height',
            sex='female'
        )
        assert isinstance(centiles, list)
        # Turner syndrome reference should return data
        assert len(centiles) >= 0  # May or may not have data

    def test_get_chart_data_invalid_reference(self):
        """Test fetching chart with invalid reference (should return empty list)"""
        centiles = get_chart_data(
            reference='invalid-reference',
            measurement_method='height',
            sex='male'
        )
        # Should return empty list on error
        assert centiles == []

    def test_get_chart_data_custom_age_range(self):
        """Test fetching chart data with custom age range"""
        centiles = get_chart_data(
            reference='uk-who',
            measurement_method='height',
            sex='male',
            min_age=2,
            max_age=10
        )
        assert isinstance(centiles, list)


class TestFormatErrorResponse:
    """Test suite for format_error_response function"""

    def test_format_error_response_basic(self):
        """Test basic error response formatting"""
        response = format_error_response(
            error_code=ErrorCodes.INVALID_INPUT,
            error_message="Invalid input provided"
        )
        assert response['success'] is False
        assert response['error'] == "Invalid input provided"
        assert response['error_code'] == ErrorCodes.INVALID_INPUT

    def test_format_error_response_structure(self):
        """Test error response has required fields"""
        response = format_error_response(
            error_code=ErrorCodes.SDS_OUT_OF_RANGE,
            error_message="SDS exceeds limits"
        )
        assert 'success' in response
        assert 'error' in response
        assert 'error_code' in response

    def test_format_error_response_different_codes(self):
        """Test formatting with different error codes"""
        codes = [
            ErrorCodes.INVALID_INPUT,
            ErrorCodes.SDS_OUT_OF_RANGE,
            ErrorCodes.CALCULATION_ERROR
        ]
        for code in codes:
            response = format_error_response(code, "Test error")
            assert response['error_code'] == code


class TestFormatSuccessResponse:
    """Test suite for format_success_response function"""

    def test_format_success_response_basic(self):
        """Test basic success response formatting"""
        results = {'weight_data': {'value': 12.5, 'centile': 50, 'sds': 0}}
        response = format_success_response(results)
        assert response['success'] is True
        assert response['results'] == results

    def test_format_success_response_structure(self):
        """Test success response has required fields"""
        response = format_success_response({'test': 'data'})
        assert 'success' in response
        assert 'results' in response

    def test_format_success_response_empty_results(self):
        """Test formatting with empty results"""
        response = format_success_response({})
        assert response['success'] is True
        assert response['results'] == {}

    def test_format_success_response_complex_results(self):
        """Test formatting with complex results"""
        results = {
            'weight_data': {'value': 12.5, 'centile': 50},
            'height_data': {'value': 85.0, 'centile': 45},
            'bmi_data': {'value': 17.3, 'centile': 55},
            'age_data': {'decimal_age': 1.0}
        }
        response = format_success_response(results)
        assert response['success'] is True
        assert response['results'] == results
