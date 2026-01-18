"""
Comprehensive Error Path Testing

Tests edge cases, boundary conditions, malformed inputs, and error scenarios
that are commonly missed in happy-path testing.
"""

import pytest
import json
from datetime import date, timedelta
from validation import ValidationError


class TestBoundaryConditions:
    """Test exact boundary values for all measurements"""

    def test_weight_at_exact_minimum(self, client):
        """Test weight at exact minimum boundary (0.1 kg)"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '0.1'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_weight_at_exact_maximum(self, client):
        """Test weight at exact maximum boundary (300 kg)"""
        data = {
            'birth_date': '2010-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '300'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_weight_just_below_minimum(self, client):
        """Test weight just below minimum boundary"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '0.09'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_weight_just_above_maximum(self, client):
        """Test weight just above maximum boundary"""
        data = {
            'birth_date': '2010-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '300.1'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_height_at_exact_minimum(self, client):
        """Test height at exact minimum boundary (10 cm)"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '10'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_height_at_exact_maximum(self, client):
        """Test height at exact maximum boundary (250 cm)"""
        data = {
            'birth_date': '2010-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '250'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_ofc_boundary_values(self, client):
        """Test OFC at boundary values"""
        # Minimum
        data_min = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'ofc': '10'
        }
        response = client.post('/calculate', json=data_min)
        assert response.status_code == 200

        # Maximum
        data_max = {
            'birth_date': '2010-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'ofc': '100'
        }
        response = client.post('/calculate', json=data_max)
        assert response.status_code == 200

    def test_gestation_at_minimum(self, client):
        """Test gestation at minimum boundary (22w0d)"""
        data = {
            'birth_date': '2023-10-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '5.0',
            'gestation_weeks': 22,
            'gestation_days': 0
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_gestation_at_maximum(self, client):
        """Test gestation at maximum boundary (44w6d)"""
        data = {
            'birth_date': '2023-10-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'weight': '6.0',
            'gestation_weeks': 44,
            'gestation_days': 6
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_gestation_below_minimum(self, client):
        """Test gestation below minimum (21w6d)"""
        data = {
            'birth_date': '2023-10-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '5.0',
            'gestation_weeks': 21,
            'gestation_days': 6
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_gestation_above_maximum(self, client):
        """Test gestation above maximum (45w0d)"""
        data = {
            'birth_date': '2023-10-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'weight': '6.0',
            'gestation_weeks': 45,
            'gestation_days': 0
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_age_at_maximum(self, client):
        """Test calculation at maximum age (25 years)"""
        birth_date = (date.today() - timedelta(days=25*365)).isoformat()
        data = {
            'birth_date': birth_date,
            'measurement_date': date.today().isoformat(),
            'sex': 'male',
            'height': '175'
        }
        response = client.post('/calculate', json=data)
        # May succeed or fail depending on reference limits
        assert response.status_code in [200, 400]


class TestInvalidInputTypes:
    """Test with wrong data types for fields"""

    def test_weight_as_boolean(self, client):
        """Test weight as boolean value"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': True
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_height_as_array(self, client):
        """Test height as array"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': [85, 90]
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_date_as_number(self, client):
        """Test date as numeric value"""
        data = {
            'birth_date': 20230115,
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_sex_as_number(self, client):
        """Test sex as numeric value"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 1,
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_sex_invalid_value(self, client):
        """Test sex with invalid value"""
        for invalid_sex in ['m', 'f', 'Male', 'MALE', 'other', '']:
            data = {
                'birth_date': '2023-01-15',
                'measurement_date': '2024-01-15',
                'sex': invalid_sex,
                'weight': '12.5'
            }
            response = client.post('/calculate', json=data)
            assert response.status_code == 400

    def test_reference_invalid_value(self, client):
        """Test with invalid reference"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            'reference': 'invalid-ref'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_measurements_as_objects(self, client):
        """Test measurements as objects instead of numbers"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': {'value': 12.5, 'unit': 'kg'}
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400


class TestMalformedRequests:
    """Test with malformed or unexpected request structures"""

    def test_empty_json_object(self, client):
        """Test with completely empty JSON"""
        response = client.post('/calculate', json={})
        assert response.status_code == 400

    def test_null_json(self, client):
        """Test with null JSON value"""
        response = client.post('/calculate', json=None)
        assert response.status_code == 400

    def test_json_with_null_values(self, client):
        """Test with null values for required fields"""
        data = {
            'birth_date': None,
            'measurement_date': None,
            'sex': None,
            'weight': None
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_array_instead_of_object(self, client):
        """Test sending array instead of object"""
        response = client.post(
            '/calculate',
            data=json.dumps(['birth_date', 'measurement_date']),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_deeply_nested_object(self, client):
        """Test with deeply nested JSON structure"""
        data = {
            'data': {
                'patient': {
                    'birth_date': '2023-01-15',
                    'sex': 'male'
                }
            }
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_extra_unexpected_fields(self, client):
        """Test with many unexpected extra fields"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            # Add many unexpected fields
            'extra1': 'value1',
            'extra2': 'value2',
            'script': '<script>alert("xss")</script>',
            'sql': "'; DROP TABLE users; --",
            'command': '$(rm -rf /)',
        }
        response = client.post('/calculate', json=data)
        # Should succeed but ignore extra fields
        assert response.status_code == 200

    def test_extremely_large_json(self, client):
        """Test with extremely large JSON payload"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            # Add large array
            'large_field': ['x' * 1000 for _ in range(100)]
        }
        response = client.post('/calculate', json=data)
        # Should handle gracefully
        assert response.status_code in [200, 400, 413]

    def test_circular_reference_in_json(self, client):
        """Test handling of data that could cause issues"""
        # JSON can't have circular refs, but test deeply nested
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            'nested': {'level1': {'level2': {'level3': {'level4': {'level5': {}}}}}}
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200


class TestUnicodeAndSpecialCharacters:
    """Test handling of unicode and special characters"""

    def test_unicode_in_sex_field(self, client):
        """Test unicode characters in sex field"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': '男',  # Chinese character for male
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_unicode_in_reference(self, client):
        """Test unicode in reference field"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            'reference': 'uk-who™®'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_sql_injection_attempts(self, client):
        """Test that SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE measurements; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        for malicious_input in malicious_inputs:
            data = {
                'birth_date': malicious_input,
                'measurement_date': '2024-01-15',
                'sex': 'male',
                'weight': '12.5'
            }
            response = client.post('/calculate', json=data)
            # Should reject invalid date format
            assert response.status_code == 400


class TestEdgeCaseCalculations:
    """Test edge cases in calculations"""

    def test_bmi_with_very_small_height(self, client):
        """Test BMI calculation doesn't divide by zero"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5',
            'height': '10'  # Minimum height
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        # BMI should be calculated without error
        assert 'bmi' in result['results'] or result['success'] is True

    def test_preterm_correction_at_boundary(self, client):
        """Test preterm correction at exactly 2 years"""
        # Birth date exactly 2 years ago
        birth_date = (date.today() - timedelta(days=730)).isoformat()
        data = {
            'birth_date': birth_date,
            'measurement_date': date.today().isoformat(),
            'sex': 'male',
            'weight': '12.5',
            'gestation_weeks': 32,
            'gestation_days': 0
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_measurement_on_birth_date_plus_one_day(self, client):
        """Test measurement on day after birth"""
        birth_date = '2024-01-15'
        measurement_date = '2024-01-16'
        data = {
            'birth_date': birth_date,
            'measurement_date': measurement_date,
            'sex': 'male',
            'weight': '3.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200

    def test_measurements_years_apart(self, client):
        """Test with measurements many years apart"""
        data = {
            'birth_date': '2000-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '165.0'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code in [200, 400]  # May exceed age limits

    def test_same_date_for_birth_and_measurement(self, client):
        """Test with same date for birth and measurement (should fail)"""
        same_date = '2024-01-15'
        data = {
            'birth_date': same_date,
            'measurement_date': same_date,
            'sex': 'male',
            'weight': '3.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_height_velocity_insufficient_interval(self, client):
        """Test height velocity with very short interval"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '105.0',
            'previous_measurements': [
                {
                    'date': '2024-01-10',  # Only 5 days ago
                    'height': 104.9
                }
            ]
        }
        response = client.post('/calculate', json=data)
        # Should succeed but may not calculate velocity
        assert response.status_code == 200

    def test_negative_height_velocity(self, client):
        """Test when height decreases (measurement error)"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '100.0',
            'previous_measurements': [
                {
                    'date': '2023-07-15',
                    'height': 105.0  # Previous height was higher
                }
            ]
        }
        response = client.post('/calculate', json=data)
        # Should succeed but velocity may be negative or not calculated
        assert response.status_code == 200

    def test_mph_with_extreme_parental_heights(self, client):
        """Test MPH with extreme parental heights"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '105.0',
            'maternal_height': '250',  # Extremely tall
            'paternal_height': '250'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
