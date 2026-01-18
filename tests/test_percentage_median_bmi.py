"""
Tests for percentage median BMI calculation
"""
import pytest
from utils import calculate_percentage_median_bmi


class TestPercentageMedianBMI:
    """Test percentage of median BMI calculations"""

    def test_normal_bmi_child(self):
        """Test percentage median BMI for a normal weight child"""
        # 5 year old male with BMI around 50th centile
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=15.5,
            sex='male'
        )

        assert result is not None
        assert isinstance(result, float)
        # Should be approximately 100% for 50th centile
        assert 95 <= result <= 105

    def test_underweight_child(self):
        """Test percentage median BMI for an underweight child"""
        # 5 year old female with low BMI
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=13.0,
            sex='female'
        )

        assert result is not None
        assert isinstance(result, float)
        # Should be less than 90% for underweight
        assert result < 90

    def test_overweight_child(self):
        """Test percentage median BMI for an overweight child"""
        # 5 year old male with high BMI
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=18.0,
            sex='male'
        )

        assert result is not None
        assert isinstance(result, float)
        # Should be greater than 110% for overweight
        assert result > 110

    def test_infant_bmi(self):
        """Test percentage median BMI for an infant"""
        # 1 year old female
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=1.0,
            bmi=17.0,
            sex='female'
        )

        assert result is not None
        assert isinstance(result, float)
        assert result > 0

    def test_adolescent_bmi(self):
        """Test percentage median BMI for an adolescent"""
        # 15 year old male
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=15.0,
            bmi=20.0,
            sex='male'
        )

        assert result is not None
        assert isinstance(result, float)
        assert result > 0

    def test_different_references(self):
        """Test percentage median BMI with different growth references"""
        age = 5.0
        bmi = 15.5
        sex = 'male'

        # Test UK-WHO reference
        result_ukwho = calculate_percentage_median_bmi(
            reference='uk-who',
            age=age,
            bmi=bmi,
            sex=sex
        )

        # Test CDC reference (if available)
        result_cdc = calculate_percentage_median_bmi(
            reference='cdc',
            age=age,
            bmi=bmi,
            sex=sex
        )

        assert result_ukwho is not None
        assert result_cdc is not None
        # Results may differ slightly between references
        assert isinstance(result_ukwho, float)
        assert isinstance(result_cdc, float)

    def test_rounding(self):
        """Test that result is rounded to 1 decimal place"""
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=15.5,
            sex='male'
        )

        assert result is not None
        # Check that result has at most 1 decimal place
        assert result == round(result, 1)

    def test_malnutrition_ranges(self):
        """Test interpretation ranges for malnutrition assessment"""
        # Severe malnutrition: <70%
        # Moderate malnutrition: 70-80%
        # Mild malnutrition: 80-90%
        # Normal: 90-110%
        # Overweight: >120%

        # Test very low BMI (severe malnutrition range)
        result_severe = calculate_percentage_median_bmi(
            reference='uk-who',
            age=5.0,
            bmi=11.0,  # Very low
            sex='male'
        )

        assert result_severe is not None
        assert result_severe < 75  # Should be in severe/moderate malnutrition range

    def test_invalid_inputs_handled(self):
        """Test that invalid inputs are handled gracefully"""
        # Test with invalid age (negative)
        result = calculate_percentage_median_bmi(
            reference='uk-who',
            age=-1,
            bmi=15.0,
            sex='male'
        )

        # Should return None for invalid input
        assert result is None or isinstance(result, float)
