"""
Unit tests for calculation functions
"""
import pytest
from datetime import date, timedelta
from calculations import (
    calculate_age_in_years,
    should_apply_gestation_correction,
    calculate_corrected_age,
    calculate_boyd_bsa,
    calculate_cbnf_bsa,
    calculate_height_velocity,
    calculate_gh_dose
)


class TestAgeCalculation:
    """Tests for age calculation functions"""

    def test_calculate_age_exact_years(self):
        """Test age calculation with exact years"""
        birth = date(2020, 1, 1)
        measurement = date(2025, 1, 1)
        decimal_years, calendar = calculate_age_in_years(birth, measurement)

        assert decimal_years == pytest.approx(5.0, rel=0.01)
        assert calendar['years'] == 5
        assert calendar['months'] == 0
        assert calendar['days'] == 0

    def test_calculate_age_with_months(self):
        """Test age calculation with months"""
        birth = date(2024, 1, 1)
        measurement = date(2024, 7, 1)
        decimal_years, calendar = calculate_age_in_years(birth, measurement)

        assert decimal_years == pytest.approx(0.5, rel=0.01)
        assert calendar['years'] == 0
        assert calendar['months'] == 6

    def test_calculate_age_leap_year(self):
        """Test age calculation over leap year"""
        birth = date(2020, 2, 29)  # Leap year
        measurement = date(2021, 2, 28)
        decimal_years, calendar = calculate_age_in_years(birth, measurement)

        # Feb 29, 2020 to Feb 28, 2021 is exactly 1 year (365 days)
        assert decimal_years == pytest.approx(1.0, rel=0.02)
        assert calendar['years'] == 1
        assert calendar['months'] == 0
        assert calendar['days'] == 0


class TestGestationCorrection:
    """Tests for gestation correction logic"""

    def test_no_correction_full_term(self):
        """No correction for full-term babies (37+ weeks)"""
        assert should_apply_gestation_correction(39, 0, 0.5) == False
        assert should_apply_gestation_correction(40, 0, 0.5) == False

    def test_correction_moderate_preterm_under_1_year(self):
        """Correction for 32-36 weeks under 1 year"""
        assert should_apply_gestation_correction(34, 0, 0.5) == True
        assert should_apply_gestation_correction(36, 5, 1.0) == True

    def test_no_correction_moderate_preterm_over_1_year(self):
        """No correction for 32-36 weeks over 1 year"""
        assert should_apply_gestation_correction(34, 0, 1.1) == False
        assert should_apply_gestation_correction(36, 0, 2.0) == False

    def test_correction_extreme_preterm_under_2_years(self):
        """Correction for <32 weeks under 2 years"""
        assert should_apply_gestation_correction(28, 0, 0.5) == True
        assert should_apply_gestation_correction(30, 0, 1.5) == True
        assert should_apply_gestation_correction(28, 0, 2.0) == True

    def test_no_correction_extreme_preterm_over_2_years(self):
        """No correction for <32 weeks over 2 years"""
        assert should_apply_gestation_correction(28, 0, 2.1) == False
        assert should_apply_gestation_correction(30, 0, 3.0) == False

    def test_no_correction_no_gestation(self):
        """No correction when gestation not provided"""
        assert should_apply_gestation_correction(None, None, 0.5) == False


class TestCorrectedAge:
    """Tests for corrected age calculation"""

    def test_corrected_age_34_weeks(self):
        """Test corrected age for 34 week baby"""
        birth = date(2025, 1, 1)
        measurement = date(2025, 7, 1)
        corrected_decimal, corrected_calendar = calculate_corrected_age(
            birth, measurement, 34, 0
        )

        # Should be about 6 weeks less than chronological age
        chronological, _ = calculate_age_in_years(birth, measurement)
        assert corrected_decimal < chronological
        assert abs(corrected_decimal - (chronological - 6/52)) < 0.05

    def test_corrected_age_28_weeks(self):
        """Test corrected age for 28 week baby"""
        birth = date(2025, 1, 1)
        measurement = date(2025, 7, 1)
        corrected_decimal, _ = calculate_corrected_age(
            birth, measurement, 28, 0
        )

        # Should be about 12 weeks less than chronological age
        chronological, _ = calculate_age_in_years(birth, measurement)
        assert corrected_decimal < chronological
        assert abs(corrected_decimal - (chronological - 12/52)) < 0.05


class TestBSACalculation:
    """Tests for Body Surface Area calculations"""

    def test_boyd_bsa_typical_infant(self):
        """Test Boyd BSA for typical infant"""
        bsa = calculate_boyd_bsa(weight_kg=7.5, height_cm=67)
        assert bsa is not None
        assert 0.3 < bsa < 0.5  # Reasonable range for infant

    def test_boyd_bsa_typical_child(self):
        """Test Boyd BSA for typical child"""
        bsa = calculate_boyd_bsa(weight_kg=20, height_cm=110)
        assert bsa is not None
        assert 0.7 < bsa < 1.0  # Reasonable range for child

    def test_boyd_bsa_invalid_inputs(self):
        """Test Boyd BSA with invalid inputs"""
        assert calculate_boyd_bsa(0, 100) is None
        assert calculate_boyd_bsa(50, 0) is None
        assert calculate_boyd_bsa(-10, 100) is None

    def test_cbnf_bsa_exact_weight(self):
        """Test cBNF BSA with exact table weight"""
        bsa = calculate_cbnf_bsa(10)
        assert bsa == 0.49

    def test_cbnf_bsa_interpolation(self):
        """Test cBNF BSA with interpolated weight"""
        bsa = calculate_cbnf_bsa(10.5)
        assert bsa is not None
        assert 0.49 < bsa < 0.53  # Between 10kg and 11kg

    def test_cbnf_bsa_invalid_weight(self):
        """Test cBNF BSA with invalid weight"""
        assert calculate_cbnf_bsa(0) is None
        assert calculate_cbnf_bsa(-5) is None


class TestHeightVelocity:
    """Tests for height velocity calculation"""

    def test_height_velocity_normal(self):
        """Test height velocity calculation with valid data"""
        current_date = date(2025, 1, 1)
        previous_date = date(2024, 1, 1)  # 1 year ago
        result = calculate_height_velocity(110, 105, current_date, previous_date)

        assert result is not None
        assert result['value'] == pytest.approx(5.0, rel=0.1)  # 5 cm/year
        assert result['message'] is None

    def test_height_velocity_short_interval(self):
        """Test height velocity with interval < 4 months"""
        current_date = date(2025, 1, 1)
        previous_date = date(2024, 11, 1)  # 2 months ago
        result = calculate_height_velocity(110, 109, current_date, previous_date)

        assert result is not None
        assert result['value'] is None
        assert 'at least 4 months' in result['message']

    def test_height_velocity_invalid_dates(self):
        """Test height velocity with invalid date order"""
        current_date = date(2024, 1, 1)
        previous_date = date(2025, 1, 1)  # After current
        result = calculate_height_velocity(110, 105, current_date, previous_date)

        assert result is not None
        assert result['value'] is None
        assert 'before current' in result['message']

    def test_height_velocity_missing_data(self):
        """Test height velocity with missing data"""
        assert calculate_height_velocity(None, 105, date.today(), date.today()) is None


class TestGHDose:
    """Tests for GH dose calculation"""

    def test_gh_dose_calculation(self):
        """Test GH dose calculation with typical values"""
        bsa = 0.5  # m²
        weight = 10  # kg
        result = calculate_gh_dose(bsa, weight)

        assert result is not None
        assert 'mg_per_day' in result
        assert 'mg_m2_week' in result
        assert 'mcg_kg_day' in result
        assert result['mg_m2_week'] == pytest.approx(7.0, rel=0.1)

    def test_gh_dose_missing_data(self):
        """Test GH dose with missing data"""
        assert calculate_gh_dose(None, 10) is None
        assert calculate_gh_dose(0.5, None) is None
        assert calculate_gh_dose(0, 10) is None
