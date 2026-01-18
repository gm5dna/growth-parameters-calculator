"""
Comprehensive Tests for models.py

Tests measurement creation, SDS validation, and result extraction functions
"""

import pytest
from datetime import date
from models import (
    create_measurement,
    validate_measurement_sds,
    extract_measurement_result,
    create_corrected_measurement_result
)
from validation import ValidationError
from constants import SDS_HARD_LIMIT, SDS_WARNING_LIMIT


class TestCreateMeasurement:
    """Test suite for create_measurement function"""

    def test_create_measurement_without_gestation(self):
        """Test creating measurement for term baby (no gestation data)"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=12.5,
            reference='uk-who'
        )
        assert measurement is not None
        assert measurement.measurement is not None

    def test_create_measurement_with_gestation(self):
        """Test creating measurement for preterm baby with gestation"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2023, 10, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=5.8,
            reference='uk-who',
            gestation_weeks=32,
            gestation_days=4
        )
        assert measurement is not None
        assert measurement.measurement is not None

    def test_create_measurement_with_gestation_weeks_only(self):
        """Test creating measurement with gestation weeks but no days"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 10, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=65.0,
            reference='uk-who',
            gestation_weeks=34,
            gestation_days=None  # Should default to 0
        )
        assert measurement is not None

    def test_create_height_measurement(self):
        """Test creating height measurement"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=105.2,
            reference='uk-who'
        )
        assert measurement is not None
        assert measurement.measurement['child_observation_value']['observation_value'] == 105.2

    def test_create_bmi_measurement(self):
        """Test creating BMI measurement"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='bmi',
            observation_value=16.8,
            reference='uk-who'
        )
        assert measurement is not None

    def test_create_ofc_measurement(self):
        """Test creating OFC measurement"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2023, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='ofc',
            observation_value=48.2,
            reference='uk-who'
        )
        assert measurement is not None

    def test_create_measurement_turner_syndrome(self):
        """Test creating measurement with Turner syndrome reference"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=95.0,
            reference='turners-syndrome'
        )
        assert measurement is not None

    def test_create_measurement_trisomy_21(self):
        """Test creating measurement with Trisomy 21 reference"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=16.0,
            reference='trisomy-21'
        )
        assert measurement is not None

    def test_create_measurement_different_ages(self):
        """Test creating measurements at different ages"""
        # Infant
        infant = create_measurement(
            sex='male',
            birth_date=date(2023, 6, 1),
            observation_date=date(2023, 12, 1),
            measurement_method='weight',
            observation_value=8.5,
            reference='uk-who'
        )
        assert infant is not None

        # Child
        child = create_measurement(
            sex='female',
            birth_date=date(2015, 1, 1),
            observation_date=date(2024, 1, 1),
            measurement_method='height',
            observation_value=130.0,
            reference='uk-who'
        )
        assert child is not None

    def test_create_measurement_extreme_preterm(self):
        """Test creating measurement for extreme preterm infant"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2023, 10, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=4.5,
            reference='uk-who',
            gestation_weeks=24,
            gestation_days=3
        )
        assert measurement is not None


class TestValidateMeasurementSDS:
    """Test suite for validate_measurement_sds function"""

    def test_validate_normal_sds(self):
        """Test validation with normal SDS values"""
        measurement_data = {'corrected_sds': 1.5}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 0

    def test_validate_zero_sds(self):
        """Test validation with zero SDS (50th centile)"""
        measurement_data = {'corrected_sds': 0.0}
        warnings = validate_measurement_sds(measurement_data, 'height')
        assert len(warnings) == 0

    def test_validate_negative_sds(self):
        """Test validation with negative SDS"""
        measurement_data = {'corrected_sds': -2.0}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 0

    def test_validate_sds_at_warning_threshold(self):
        """Test validation at warning threshold (±4 SDS)"""
        # Exactly at warning threshold
        measurement_data = {'corrected_sds': SDS_WARNING_LIMIT}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 0

        # Just above warning threshold
        measurement_data = {'corrected_sds': SDS_WARNING_LIMIT + 0.1}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 1
        assert 'verify measurement' in warnings[0].lower()

    def test_validate_sds_warning_positive(self):
        """Test validation with SDS above warning threshold"""
        measurement_data = {'corrected_sds': 5.0}
        warnings = validate_measurement_sds(measurement_data, 'height')
        assert len(warnings) == 1
        assert '5.00' in warnings[0]

    def test_validate_sds_warning_negative(self):
        """Test validation with negative SDS below warning threshold"""
        measurement_data = {'corrected_sds': -5.5}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 1

    def test_validate_sds_at_hard_limit(self):
        """Test validation at hard limit (±8 SDS)"""
        # Just below hard limit - should warn but not error
        measurement_data = {'corrected_sds': SDS_HARD_LIMIT - 0.1}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 1

    def test_validate_sds_exceeds_hard_limit_positive(self):
        """Test validation with SDS exceeding hard limit (positive)"""
        measurement_data = {'corrected_sds': SDS_HARD_LIMIT + 0.1}
        with pytest.raises(ValidationError) as exc_info:
            validate_measurement_sds(measurement_data, 'weight')
        assert 'exceeds acceptable range' in str(exc_info.value)

    def test_validate_sds_exceeds_hard_limit_negative(self):
        """Test validation with SDS exceeding hard limit (negative)"""
        measurement_data = {'corrected_sds': -(SDS_HARD_LIMIT + 0.1)}
        with pytest.raises(ValidationError) as exc_info:
            validate_measurement_sds(measurement_data, 'height')
        assert 'exceeds acceptable range' in str(exc_info.value)

    def test_validate_extreme_sds(self):
        """Test validation with extreme SDS values"""
        measurement_data = {'corrected_sds': 12.0}
        with pytest.raises(ValidationError):
            validate_measurement_sds(measurement_data, 'weight')

    def test_validate_empty_measurement_data(self):
        """Test validation with empty measurement data"""
        warnings = validate_measurement_sds(None, 'weight')
        assert len(warnings) == 0

    def test_validate_missing_sds_field(self):
        """Test validation when SDS field is missing (defaults to 0)"""
        measurement_data = {}
        warnings = validate_measurement_sds(measurement_data, 'weight')
        assert len(warnings) == 0


class TestExtractMeasurementResult:
    """Test suite for extract_measurement_result function"""

    def test_extract_weight_result(self):
        """Test extracting weight measurement result"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=12.5,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'weight')

        assert result is not None
        assert 'value' in result
        assert 'centile' in result
        assert 'sds' in result
        assert result['value'] == 12.5

    def test_extract_height_result(self):
        """Test extracting height measurement result"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=105.2,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'height')

        assert result is not None
        assert result['value'] == 105.2
        assert isinstance(result['centile'], (int, float)) or result['centile'] is None
        assert isinstance(result['sds'], (int, float)) or result['sds'] is None

    def test_extract_bmi_result_rounding(self):
        """Test BMI result is rounded to 1 decimal place"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='bmi',
            observation_value=16.789,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'bmi')

        assert result is not None
        assert result['value'] == 16.8  # Rounded to 1 decimal

    def test_extract_ofc_result(self):
        """Test extracting OFC measurement result"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2023, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='ofc',
            observation_value=48.2,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'ofc')

        assert result is not None
        assert result['value'] == 48.2

    def test_extract_none_measurement(self):
        """Test extracting result from None measurement"""
        result = extract_measurement_result(None, 'weight')
        assert result is None

    def test_extract_result_centile_rounding(self):
        """Test that centile is rounded to 2 decimal places"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=10.0,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'weight')

        assert result is not None
        if result['centile'] is not None:
            # Check it's rounded to 2 decimals
            assert result['centile'] == round(result['centile'], 2)

    def test_extract_result_sds_rounding(self):
        """Test that SDS is rounded to 2 decimal places"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2020, 1, 15),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=105.0,
            reference='uk-who'
        )
        result = extract_measurement_result(measurement, 'height')

        assert result is not None
        if result['sds'] is not None:
            # Check it's rounded to 2 decimals
            assert result['sds'] == round(result['sds'], 2)


class TestCreateCorrectedMeasurementResult:
    """Test suite for create_corrected_measurement_result function"""

    def test_create_corrected_result(self):
        """Test creating corrected age measurement result"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 10, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=5.8,
            reference='uk-who',
            gestation_weeks=32,
            gestation_days=4
        )

        corrected_age = 0.15  # Approximately
        result = create_corrected_measurement_result(measurement, corrected_age, 5.8)

        assert result is not None
        assert 'age' in result
        assert 'value' in result
        assert 'centile' in result
        assert 'sds' in result
        assert result['age'] == round(corrected_age, 2)
        assert result['value'] == 5.8

    def test_create_corrected_result_age_rounding(self):
        """Test corrected age is rounded to 2 decimal places"""
        measurement = create_measurement(
            sex='female',
            birth_date=date(2023, 10, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='height',
            observation_value=65.0,
            reference='uk-who',
            gestation_weeks=34,
            gestation_days=2
        )

        corrected_age = 0.123456
        result = create_corrected_measurement_result(measurement, corrected_age, 65.0)

        assert result['age'] == 0.12  # Rounded to 2 decimals

    def test_create_corrected_result_none_measurement(self):
        """Test creating result with None measurement"""
        result = create_corrected_measurement_result(None, 0.5, 10.0)
        assert result is None

    def test_create_corrected_result_different_values(self):
        """Test creating corrected results with various measurement values"""
        measurement = create_measurement(
            sex='male',
            birth_date=date(2023, 9, 1),
            observation_date=date(2024, 1, 15),
            measurement_method='weight',
            observation_value=6.5,
            reference='uk-who',
            gestation_weeks=30,
            gestation_days=0
        )

        result = create_corrected_measurement_result(measurement, 0.2, 6.5)

        assert result['value'] == 6.5
        assert result['age'] == 0.2
