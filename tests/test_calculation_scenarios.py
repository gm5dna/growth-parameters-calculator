"""
Comprehensive tests for calculation scenarios

Tests all calculation logic with various edge cases, particularly:
- Preterm infants with and without correction
- Height velocity calculations (valid and invalid scenarios)
- BSA calculations
- GH dose calculations
- Mid-parental height calculations
"""

import pytest
import json
from datetime import datetime, timedelta


class TestPretermCalculations:
    """Test calculations for preterm infants"""

    def test_preterm_no_previous_height_no_velocity(self, client):
        """Preterm infant without previous height should not show height velocity"""
        payload = {
            'sex': 'male',
            'birth_date': '2025-06-01',
            'measurement_date': '2026-01-18',  # ~7.5 months old
            'gestation_weeks': 32,
            'gestation_days': 3,
            'weight': 8.5,
            'height': 72.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Should apply gestation correction for 32 week infant < 1 year old
        assert results['gestation_correction_applied'] is True

        # Height velocity should be None (not a dict with value: None)
        assert results['height_velocity'] is None

        # Previous height should be None
        assert results['previous_height'] is None

    def test_preterm_with_previous_height_insufficient_interval(self, client):
        """Preterm infant with previous height but < 4 months interval"""
        payload = {
            'sex': 'female',
            'birth_date': '2025-06-01',
            'measurement_date': '2026-01-18',
            'gestation_weeks': 28,
            'gestation_days': 0,
            'weight': 8.0,
            'height': 70.0,
            'previous_measurements': [
                {
                    'date': '2025-11-01',  # ~2.5 months ago
                    'height': 65.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Should apply correction for 28 week infant < 2 years old
        assert results['gestation_correction_applied'] is True

        # Height velocity should have error message about insufficient interval
        assert results['height_velocity'] is not None
        assert isinstance(results['height_velocity'], dict)
        assert results['height_velocity']['value'] is None
        assert 'at least 4 months' in results['height_velocity']['message']

    def test_preterm_with_valid_height_velocity(self, client):
        """Preterm infant with valid height velocity measurement"""
        payload = {
            'sex': 'male',
            'birth_date': '2025-04-01',
            'measurement_date': '2026-01-18',  # ~9.5 months old
            'gestation_weeks': 34,
            'gestation_days': 0,
            'weight': 10.0,
            'height': 77.0,
            'previous_measurements': [
                {
                    'date': '2025-09-01',  # ~4.5 months ago
                    'height': 72.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Should apply correction for 34 week infant < 1 year old
        assert results['gestation_correction_applied'] is True

        # Height velocity should have a valid value
        assert results['height_velocity'] is not None
        assert isinstance(results['height_velocity'], dict)
        assert results['height_velocity']['value'] is not None
        assert isinstance(results['height_velocity']['value'], (int, float))
        assert results['height_velocity']['value'] > 0
        assert results['height_velocity']['message'] is None

    def test_extreme_preterm_no_correction_after_2_years(self, client):
        """Extreme preterm (< 32 weeks) should not have correction after 2 years"""
        payload = {
            'sex': 'female',
            'birth_date': '2023-06-01',
            'measurement_date': '2026-01-18',  # ~2.6 years old
            'gestation_weeks': 28,
            'gestation_days': 0,
            'weight': 13.0,
            'height': 92.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Should NOT apply correction (child > 2 years old)
        assert results['gestation_correction_applied'] is False
        assert results['corrected_age_years'] is None


class TestHeightVelocityScenarios:
    """Test height velocity calculation edge cases"""

    def test_no_previous_height_returns_none(self, client):
        """No previous height should return None for height_velocity"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            'height': 115.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Height velocity should be None (not a dict)
        assert data['results']['height_velocity'] is None

    def test_previous_height_without_date_returns_none(self, client):
        """Previous height without date should return None"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            'height': 115.0,
            # No previous_measurements provided
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Height velocity should be None
        assert data['results']['height_velocity'] is None

    def test_interval_less_than_4_months(self, client):
        """Interval < 4 months should return error message"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'previous_measurements': [
                {
                    'date': '2025-12-01',  # ~1.5 months ago
                    'height': 113.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        hv = data['results']['height_velocity']
        assert hv is not None
        assert hv['value'] is None
        assert 'at least 4 months' in hv['message']

    def test_previous_date_after_current_date(self, client):
        """Previous date after current should return error"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'previous_measurements': [
                {
                    'date': '2026-02-01',  # Future date
                    'height': 110.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        hv = data['results']['height_velocity']
        assert hv is not None
        assert hv['value'] is None
        assert 'must be before' in hv['message']

    def test_valid_height_velocity_6_months(self, client):
        """Valid height velocity over 6 months"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 120.0,
            'previous_measurements': [
                {
                    'date': '2025-07-18',  # 6 months ago
                    'height': 117.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        hv = data['results']['height_velocity']
        assert hv is not None
        assert hv['value'] is not None
        # 3 cm over 6 months = 6 cm/year
        assert abs(hv['value'] - 6.0) < 0.2
        assert hv['message'] is None

    def test_valid_height_velocity_1_year(self, client):
        """Valid height velocity over 1 year"""
        payload = {
            'sex': 'female',
            'birth_date': '2018-01-01',
            'measurement_date': '2026-01-18',
            'height': 130.0,
            'previous_measurements': [
                {
                    'date': '2025-01-18',  # 1 year ago
                    'height': 125.0
                }
            ],
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        hv = data['results']['height_velocity']
        assert hv is not None
        assert hv['value'] is not None
        # 5 cm over 1 year = 5 cm/year
        assert abs(hv['value'] - 5.0) < 0.2
        assert hv['message'] is None


class TestBSACalculations:
    """Test Body Surface Area calculations"""

    def test_bsa_with_both_weight_and_height_uses_boyd(self, client):
        """With both weight and height, should use Boyd formula"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            'height': 115.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['bsa'] is not None
        assert data['results']['bsa_method'] == 'Boyd'
        assert isinstance(data['results']['bsa'], (int, float))
        assert data['results']['bsa'] > 0

    def test_bsa_with_only_weight_uses_cbnf(self, client):
        """With only weight, should use cBNF lookup"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            # No height
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['bsa'] is not None
        assert data['results']['bsa_method'] == 'cBNF'
        assert isinstance(data['results']['bsa'], (int, float))
        assert data['results']['bsa'] > 0

    def test_no_bsa_without_weight(self, client):
        """Without weight, BSA should be None"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            # No weight
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['bsa'] is None
        assert data['results']['bsa_method'] is None


class TestGHDoseCalculations:
    """Test Growth Hormone dose calculations"""

    def test_gh_dose_with_weight_and_bsa(self, client):
        """GH dose should be calculated with weight and BSA"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            'height': 115.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['gh_dose'] is not None
        assert isinstance(data['results']['gh_dose'], dict)
        assert 'mg_per_day' in data['results']['gh_dose']
        assert data['results']['gh_dose']['mg_per_day'] > 0
        assert 'mg_m2_week' in data['results']['gh_dose']
        assert 'mcg_kg_day' in data['results']['gh_dose']

    def test_no_gh_dose_without_weight(self, client):
        """GH dose should be None without weight"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            # No weight
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['gh_dose'] is None


class TestMidParentalHeight:
    """Test mid-parental height calculations"""

    def test_mph_with_both_parent_heights(self, client):
        """MPH should be calculated with both parent heights"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'maternal_height': 165.0,
            'paternal_height': 180.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        mph = data['results']['mid_parental_height']
        assert mph is not None
        assert isinstance(mph, dict)
        assert mph['mid_parental_height'] is not None
        assert mph['target_range_lower'] is not None
        assert mph['target_range_upper'] is not None
        # MPH for male should be (165 + 180)/2 + 6.5 = 179
        assert abs(mph['mid_parental_height'] - 179.0) < 1.0

    def test_mph_for_female(self, client):
        """MPH calculation differs for females"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'maternal_height': 165.0,
            'paternal_height': 180.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        mph = data['results']['mid_parental_height']
        assert mph is not None
        # MPH for female should be (165 + 180)/2 - 6.5 = 166
        assert abs(mph['mid_parental_height'] - 166.0) < 1.0

    def test_no_mph_with_only_maternal_height(self, client):
        """MPH should be None with only one parent height"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'maternal_height': 165.0,
            # No paternal height
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['mid_parental_height'] is None

    def test_no_mph_with_only_paternal_height(self, client):
        """MPH should be None with only paternal height"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'height': 115.0,
            'paternal_height': 180.0,
            # No maternal height
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['mid_parental_height'] is None


class TestBMIPercentageMedian:
    """Test BMI percentage of median calculations"""

    def test_bmi_percentage_median_calculated(self, client):
        """BMI percentage median should be calculated when BMI is calculated"""
        payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            'height': 115.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        bmi = data['results']['bmi']
        assert bmi is not None
        assert 'percentage_median' in bmi
        assert bmi['percentage_median'] is not None
        assert isinstance(bmi['percentage_median'], (int, float))
        assert bmi['percentage_median'] > 0

    def test_no_bmi_percentage_without_weight_and_height(self, client):
        """BMI percentage median should be None without both weight and height"""
        payload = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-18',
            'weight': 20.0,
            # No height
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['results']['bmi'] is None


class TestCompleteCalculationWorkflow:
    """Integration tests for complete calculation workflows"""

    def test_preterm_with_all_measurements(self, client):
        """Preterm infant with complete measurements"""
        payload = {
            'sex': 'female',
            'birth_date': '2025-03-01',
            'measurement_date': '2026-01-18',
            'gestation_weeks': 30,
            'gestation_days': 4,
            'weight': 9.5,
            'height': 75.0,
            'ofc': 44.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Verify correction applied
        assert results['gestation_correction_applied'] is True
        assert results['corrected_age_years'] is not None

        # Verify measurements
        assert results['weight'] is not None
        assert results['height'] is not None
        assert results['bmi'] is not None
        assert results['ofc'] is not None

        # Verify BSA calculated
        assert results['bsa'] is not None
        assert results['bsa_method'] == 'Boyd'

        # Verify GH dose calculated
        assert results['gh_dose'] is not None

        # Verify no height velocity (no previous)
        assert results['height_velocity'] is None

    def test_term_child_with_all_optional_parameters(self, client):
        """Term child with all optional parameters"""
        payload = {
            'sex': 'male',
            'birth_date': '2018-06-15',
            'measurement_date': '2026-01-18',
            'weight': 28.0,
            'height': 130.0,
            'ofc': 53.0,
            'previous_measurements': [
                {
                    'date': '2025-01-18',
                    'height': 125.0
                }
            ],
            'maternal_height': 168.0,
            'paternal_height': 182.0,
            'reference': 'uk-who'
        }

        response = client.post('/calculate',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        results = data['results']

        # Verify no correction (term baby)
        assert results['gestation_correction_applied'] is False

        # Verify all measurements
        assert results['weight'] is not None
        assert results['height'] is not None
        assert results['bmi'] is not None
        assert results['ofc'] is not None

        # Verify height velocity calculated
        assert results['height_velocity'] is not None
        assert results['height_velocity']['value'] is not None

        # Verify previous height data
        assert results['previous_height'] is not None

        # Verify BSA and GH dose
        assert results['bsa'] is not None
        assert results['gh_dose'] is not None

        # Verify MPH
        assert results['mid_parental_height'] is not None
        assert results['mid_parental_height']['mid_parental_height'] is not None
