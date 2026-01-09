"""
Unit tests for validation functions
"""
import pytest
from datetime import date, timedelta
from validation import (
    ValidationError,
    validate_date,
    validate_date_range,
    validate_weight,
    validate_height,
    validate_ofc,
    validate_gestation,
    validate_at_least_one_measurement
)
from constants import ErrorCodes


class TestDateValidation:
    """Tests for date validation"""

    def test_valid_date(self):
        """Test validation of valid date"""
        result = validate_date('2025-01-01', 'Test Date')
        assert result == date(2025, 1, 1)

    def test_invalid_date_format(self):
        """Test validation of invalid date format"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date('01/01/2025', 'Test Date')
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_FORMAT

    def test_future_date(self):
        """Test validation of future date"""
        future = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        with pytest.raises(ValidationError) as exc_info:
            validate_date(future, 'Test Date')
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_RANGE
        assert 'future' in exc_info.value.message.lower()

    def test_too_old_date(self):
        """Test validation of date too far in past"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date('1800-01-01', 'Test Date')
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_RANGE

    def test_missing_date(self):
        """Test validation of missing date"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date('', 'Test Date')
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_FORMAT


class TestDateRangeValidation:
    """Tests for date range validation"""

    def test_valid_date_range(self):
        """Test validation of valid date range"""
        birth = date(2020, 1, 1)
        measurement = date(2025, 1, 1)
        validate_date_range(birth, measurement)  # Should not raise

    def test_invalid_date_range(self):
        """Test validation when measurement before birth"""
        birth = date(2025, 1, 1)
        measurement = date(2020, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(birth, measurement)
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_RANGE

    def test_same_date(self):
        """Test validation when dates are same"""
        same_date = date(2025, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(same_date, same_date)
        assert exc_info.value.code == ErrorCodes.INVALID_DATE_RANGE


class TestWeightValidation:
    """Tests for weight validation"""

    def test_valid_weight(self):
        """Test validation of valid weight"""
        assert validate_weight(7.5) == 7.5
        assert validate_weight(0.5) == 0.5
        assert validate_weight(100) == 100.0

    def test_none_weight(self):
        """Test validation of None weight"""
        assert validate_weight(None) is None

    def test_weight_too_low(self):
        """Test validation of weight below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_weight(0.05)
        assert exc_info.value.code == ErrorCodes.INVALID_WEIGHT

    def test_weight_too_high(self):
        """Test validation of weight above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_weight(350)
        assert exc_info.value.code == ErrorCodes.INVALID_WEIGHT

    def test_weight_invalid_type(self):
        """Test validation of invalid weight type"""
        with pytest.raises(ValidationError) as exc_info:
            validate_weight('invalid')
        assert exc_info.value.code == ErrorCodes.INVALID_WEIGHT


class TestHeightValidation:
    """Tests for height validation"""

    def test_valid_height(self):
        """Test validation of valid height"""
        assert validate_height(50) == 50.0
        assert validate_height(180.5) == 180.5

    def test_none_height(self):
        """Test validation of None height"""
        assert validate_height(None) is None

    def test_height_too_low(self):
        """Test validation of height below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_height(5)
        assert exc_info.value.code == ErrorCodes.INVALID_HEIGHT

    def test_height_too_high(self):
        """Test validation of height above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_height(300)
        assert exc_info.value.code == ErrorCodes.INVALID_HEIGHT


class TestOFCValidation:
    """Tests for OFC validation"""

    def test_valid_ofc(self):
        """Test validation of valid OFC"""
        assert validate_ofc(35) == 35.0
        assert validate_ofc(50.5) == 50.5

    def test_none_ofc(self):
        """Test validation of None OFC"""
        assert validate_ofc(None) is None

    def test_ofc_too_low(self):
        """Test validation of OFC below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_ofc(5)
        assert exc_info.value.code == ErrorCodes.INVALID_OFC

    def test_ofc_too_high(self):
        """Test validation of OFC above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_ofc(150)
        assert exc_info.value.code == ErrorCodes.INVALID_OFC


class TestGestationValidation:
    """Tests for gestation validation"""

    def test_valid_gestation(self):
        """Test validation of valid gestation"""
        weeks, days = validate_gestation(34, 3)
        assert weeks == 34
        assert days == 3

    def test_none_gestation(self):
        """Test validation of None gestation"""
        weeks, days = validate_gestation(None, None)
        assert weeks is None
        assert days is None

    def test_gestation_weeks_too_low(self):
        """Test validation of gestation weeks below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_gestation(20, 0)
        assert exc_info.value.code == ErrorCodes.INVALID_GESTATION

    def test_gestation_weeks_too_high(self):
        """Test validation of gestation weeks above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_gestation(45, 0)
        assert exc_info.value.code == ErrorCodes.INVALID_GESTATION

    def test_gestation_days_too_high(self):
        """Test validation of gestation days above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            validate_gestation(34, 7)
        assert exc_info.value.code == ErrorCodes.INVALID_GESTATION

    def test_gestation_days_negative(self):
        """Test validation of negative gestation days"""
        with pytest.raises(ValidationError) as exc_info:
            validate_gestation(34, -1)
        assert exc_info.value.code == ErrorCodes.INVALID_GESTATION


class TestAtLeastOneMeasurement:
    """Tests for at least one measurement validation"""

    def test_has_weight(self):
        """Test with weight provided"""
        validate_at_least_one_measurement(7.5, None, None)  # Should not raise

    def test_has_height(self):
        """Test with height provided"""
        validate_at_least_one_measurement(None, 110, None)  # Should not raise

    def test_has_ofc(self):
        """Test with OFC provided"""
        validate_at_least_one_measurement(None, None, 45)  # Should not raise

    def test_no_measurements(self):
        """Test with no measurements"""
        with pytest.raises(ValidationError) as exc_info:
            validate_at_least_one_measurement(None, None, None)
        assert exc_info.value.code == ErrorCodes.MISSING_MEASUREMENT
