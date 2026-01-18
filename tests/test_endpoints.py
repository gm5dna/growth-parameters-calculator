"""
Comprehensive Endpoint Testing for Growth Parameters Calculator

Tests all API endpoints with:
- Success cases (happy path)
- Error cases (malformed input, missing fields, invalid data)
- Edge cases (boundary values, extreme inputs)
- Validation scenarios
"""

import pytest
import json
from datetime import date, timedelta


class TestCalculateEndpoint:
    """Test suite for POST /calculate endpoint"""

    def test_calculate_with_weight_only(self, client):
        """Test successful calculation with only weight measurement"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'results' in result
        assert result['results']['weight'] is not None

    def test_calculate_with_height_only(self, client):
        """Test successful calculation with only height measurement"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '85.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'results' in result
        assert result['results']['height'] is not None

    def test_calculate_with_ofc_only(self, client):
        """Test successful calculation with only OFC measurement"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'ofc': '48.2'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'results' in result
        assert result['results']['ofc'] is not None

    def test_calculate_with_all_measurements(self, client):
        """Test successful calculation with all measurements"""
        data = {
            'birth_date': '2020-06-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'weight': '18.5',
            'height': '105.2',
            'ofc': '50.5',
            'reference': 'uk-who'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'weight' in result['results']
        assert 'height' in result['results']
        assert 'ofc' in result['results']
        assert 'bmi' in result['results']

    def test_calculate_with_parental_heights(self, client):
        """Test calculation with parental heights for MPH"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '105.0',
            'maternal_height': '165',
            'paternal_height': '180'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'mid_parental_height' in result['results']
        assert result['results']['mid_parental_height'] is not None

    def test_calculate_preterm_with_gestation(self, client):
        """Test calculation for preterm infant with gestation correction"""
        data = {
            'birth_date': '2023-10-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '5.8',
            'height': '60.5',
            'gestation_weeks': 32,
            'gestation_days': 4
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'corrected_age_years' in result['results']

    def test_calculate_with_previous_measurements(self, client):
        """Test calculation with previous measurements for velocity"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '105.0',
            'weight': '18.0',
            'previous_measurements': [
                {
                    'date': '2023-07-15',
                    'weight': 16.5,
                    'height': 100.0
                }
            ]
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_calculate_with_bone_age(self, client):
        """Test calculation with bone age assessment"""
        data = {
            'birth_date': '2014-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '145.0',
            'weight': '40.0',
            'bone_age_assessments': [
                {
                    'assessment_date': '2024-01-15',
                    'bone_age_years': 9,
                    'bone_age_months': 6
                }
            ]
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_calculate_turner_syndrome_reference(self, client):
        """Test calculation with Turner syndrome reference"""
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '95.0',
            'weight': '15.5',
            'reference': 'turners-syndrome'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    # Error cases

    def test_calculate_malformed_json(self, client):
        """Test endpoint with malformed JSON"""
        response = client.post(
            '/calculate',
            data='not valid json{',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_calculate_missing_birth_date(self, client):
        """Test endpoint without birth_date field"""
        data = {
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_missing_measurement_date(self, client):
        """Test endpoint without measurement_date field"""
        data = {
            'birth_date': '2023-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_missing_sex(self, client):
        """Test endpoint without sex field"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_no_measurements(self, client):
        """Test endpoint without any measurements"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
        assert 'at least one measurement' in result['error'].lower()

    def test_calculate_invalid_date_format(self, client):
        """Test endpoint with invalid date format"""
        data = {
            'birth_date': '15-01-2023',  # Wrong format
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_future_birth_date(self, client):
        """Test endpoint with future birth date"""
        future_date = (date.today() + timedelta(days=30)).isoformat()
        data = {
            'birth_date': future_date,
            'measurement_date': date.today().isoformat(),
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_measurement_before_birth(self, client):
        """Test endpoint with measurement date before birth"""
        data = {
            'birth_date': '2024-01-15',
            'measurement_date': '2023-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_invalid_sex_value(self, client):
        """Test endpoint with invalid sex value"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'invalid',
            'weight': '12.5'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_negative_weight(self, client):
        """Test endpoint with negative weight"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '-5.0'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_excessive_weight(self, client):
        """Test endpoint with excessively high weight"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '500.0'  # Unrealistic
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400

    def test_calculate_weight_as_string(self, client):
        """Test endpoint with non-numeric weight"""
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': 'not a number'
        }
        response = client.post('/calculate', json=data)
        assert response.status_code == 400


class TestChartDataEndpoint:
    """Test suite for POST /chart-data endpoint"""

    def test_chart_data_height_male(self, client):
        """Test chart data for height, male"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'height',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'centiles' in result
        assert len(result['centiles']) > 0

    def test_chart_data_weight_female(self, client):
        """Test chart data for weight, female"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'weight',
            'sex': 'female'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'centiles' in result

    def test_chart_data_bmi_male(self, client):
        """Test chart data for BMI, male"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'bmi',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_chart_data_ofc_female(self, client):
        """Test chart data for OFC, female"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'ofc',
            'sex': 'female'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_chart_data_turner_syndrome(self, client):
        """Test chart data for Turner syndrome reference"""
        data = {
            'reference': 'turners-syndrome',
            'measurement_method': 'height',
            'sex': 'female'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_chart_data_trisomy_21(self, client):
        """Test chart data for Trisomy 21 reference"""
        data = {
            'reference': 'trisomy-21',
            'measurement_method': 'height',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    # Error cases

    def test_chart_data_missing_measurement_method(self, client):
        """Test chart data without measurement_method"""
        data = {
            'reference': 'uk-who',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 400

    def test_chart_data_missing_sex(self, client):
        """Test chart data without sex"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'height'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 400

    def test_chart_data_invalid_measurement_method(self, client):
        """Test chart data with invalid measurement_method"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'invalid',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 400

    def test_chart_data_invalid_reference(self, client):
        """Test chart data with invalid reference"""
        data = {
            'reference': 'invalid-reference',
            'measurement_method': 'height',
            'sex': 'male'
        }
        response = client.post('/chart-data', json=data)
        assert response.status_code == 400


class TestExportPDFEndpoint:
    """Test suite for POST /export-pdf endpoint"""

    def test_export_pdf_success(self, client):
        """Test successful PDF export with valid data"""
        # First get calculation results
        calc_data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '18.5',
            'height': '105.2'
        }
        calc_response = client.post('/calculate', json=calc_data)
        assert calc_response.status_code == 200
        calc_result = calc_response.get_json()

        # Now export to PDF
        pdf_data = {
            'results': calc_result['results'],
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-15',
                'measurement_date': '2024-01-15',
                'reference': 'uk-who'
            }
        }
        response = client.post('/export-pdf', json=pdf_data)
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'

    def test_export_pdf_with_minimal_data(self, client):
        """Test PDF export with minimal calculation data"""
        calc_data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'weight': '12.0'
        }
        calc_response = client.post('/calculate', json=calc_data)
        calc_result = calc_response.get_json()

        pdf_data = {
            'results': calc_result['results'],
            'patient_info': {
                'sex': 'female',
                'birth_date': '2023-01-15',
                'measurement_date': '2024-01-15',
                'reference': 'uk-who'
            }
        }
        response = client.post('/export-pdf', json=pdf_data)
        assert response.status_code == 200

    def test_export_pdf_missing_results(self, client):
        """Test PDF export without results data"""
        response = client.post('/export-pdf', json={})
        assert response.status_code == 400

    def test_export_pdf_malformed_data(self, client):
        """Test PDF export with malformed results"""
        pdf_data = {
            'results': 'not a valid result object'
        }
        response = client.post('/export-pdf', json=pdf_data)
        assert response.status_code in [400, 500]


class TestRootEndpoint:
    """Test suite for GET / endpoint"""

    def test_root_returns_html(self, client):
        """Test that root endpoint returns HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data

    def test_root_contains_title(self, client):
        """Test that root page contains app title"""
        response = client.get('/')
        assert response.status_code == 200
        # Should contain some reference to growth or calculator
        assert b'growth' in response.data.lower() or b'calculator' in response.data.lower()
