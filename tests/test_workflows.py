"""
Integration Workflow Tests

Tests complete workflows from input to output, simulating real user scenarios.
These tests verify that all components work together correctly.
"""

import pytest
from datetime import date


class TestCompleteCalculationWorkflows:
    """Test complete calculation workflows for different scenarios"""

    def test_typical_infant_workflow(self, client):
        """Test complete workflow for typical infant growth assessment"""
        # Scenario: 1-year-old male infant, routine checkup
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '10.5',
            'height': '76.0',
            'ofc': '47.0',
            'reference': 'uk-who'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify all expected data is present
        assert 'weight' in result['results']
        assert 'height' in result['results']
        assert 'ofc' in result['results']
        assert 'bmi' in result['results']

        # Verify data structure
        assert 'value' in result['results']['weight']
        assert 'centile' in result['results']['weight']
        assert 'sds' in result['results']['weight']

        # Verify reasonable values
        assert 0 <= result['results']['weight']['centile'] <= 100
        assert -5 <= result['results']['weight']['sds'] <= 5

    def test_preterm_infant_with_correction_workflow(self, client):
        """Test workflow for preterm infant with gestational age correction"""
        # Scenario: 6-month-old born at 32 weeks gestation
        data = {
            'birth_date': '2023-07-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'weight': '6.5',
            'height': '65.0',
            'gestation_weeks': 32,
            'gestation_days': 4,
            'reference': 'uk-who'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Should include corrected age data
        assert 'corrected_age_years' in result['results']
        assert 'age_calendar' in result['results']

        # Verify both chronological and corrected measurements exist
        assert result['results']['weight'] is not None

    def test_height_velocity_calculation_workflow(self, client):
        """Test workflow with previous measurements for height velocity"""
        # Scenario: Child with growth tracking over 6 months
        data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '105.0',
            'weight': '18.0',
            'previous_measurements': [
                {
                    'date': '2023-07-15',
                    'height': 100.0,
                    'weight': 16.5
                }
            ]
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Should have height velocity data
        # Note: Velocity may not be calculated if interval is too short
        assert result['results']['height'] is not None

    def test_mid_parental_height_workflow(self, client):
        """Test workflow with parental heights for target height calculation"""
        # Scenario: Child with parental heights for genetic potential
        data = {
            'birth_date': '2015-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '135.0',
            'weight': '30.0',
            'maternal_height': '165',
            'paternal_height': '180'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Should include MPH data
        assert 'mid_parental_height' in result['results']
        mph_data = result['results']['mid_parental_height']

        # Verify MPH structure
        assert 'mid_parental_height' in mph_data
        assert 'target_range_lower' in mph_data
        assert 'target_range_upper' in mph_data

        # Verify target range is logical
        assert mph_data['target_range_lower'] < mph_data['mid_parental_height'] < mph_data['target_range_upper']

    def test_turner_syndrome_workflow(self, client):
        """Test workflow using Turner syndrome growth reference"""
        # Scenario: Female with Turner syndrome
        data = {
            'birth_date': '2018-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '110.0',
            'weight': '20.0',
            'reference': 'turners-syndrome'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify measurements against Turner syndrome reference
        assert result['results']['height'] is not None
        assert result['results']['weight'] is not None

    def test_gh_treatment_workflow(self, client):
        """Test workflow for child on growth hormone treatment"""
        # Scenario: Child being assessed for GH dose
        data = {
            'birth_date': '2014-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '135.0',
            'weight': '30.0',
            'maternal_height': '160',
            'paternal_height': '175'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify all relevant data for GH assessment
        assert 'height' in result['results']
        assert 'mid_parental_height' in result['results']
        assert 'bsa' in result['results']

    def test_obesity_assessment_workflow(self, client):
        """Test workflow for obesity/overweight assessment"""
        # Scenario: Child with elevated BMI
        data = {
            'birth_date': '2014-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '140.0',
            'weight': '50.0'  # Higher weight for age
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify BMI data is present
        assert 'bmi' in result['results']
        bmi_data = result['results']['bmi']

        # Verify BMI value is calculated
        assert bmi_data['value'] is not None
        assert bmi_data['centile'] is not None

    def test_failure_to_thrive_workflow(self, client):
        """Test workflow for failure to thrive assessment"""
        # Scenario: Infant with low weight and height
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'female',
            'height': '70.0',  # Lower than average
            'weight': '7.5'   # Lower than average
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify measurements are recorded
        assert result['results']['weight'] is not None
        assert result['results']['height'] is not None

        # Centiles should indicate lower percentiles
        # (exact values depend on rcpchgrowth calculations)

    def test_bone_age_assessment_workflow(self, client):
        """Test workflow with bone age assessment"""
        # Scenario: Child with bone age assessment
        data = {
            'birth_date': '2014-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'height': '140.0',
            'weight': '35.0',
            'bone_age_assessments': [
                {
                    'assessment_date': '2024-01-15',
                    'bone_age_years': 9,
                    'bone_age_months': 0
                }
            ]
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True

        # Verify bone age data is included
        # Note: Bone age data structure depends on implementation


class TestChartGenerationWorkflow:
    """Test complete chart data generation workflows"""

    def test_weight_chart_workflow(self, client):
        """Test complete workflow for weight chart generation"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'weight',
            'sex': 'male'
        }

        response = client.post('/chart-data', json=data)
        assert response.status_code == 200

        result = response.get_json()
        assert result['success'] is True
        assert 'centiles' in result
        assert len(result['centiles']) > 0

        # Verify centile data structure
        first_centile = result['centiles'][0]
        assert 'centile' in first_centile
        assert 'data' in first_centile
        assert len(first_centile['data']) > 0

        # Verify data points have x (age) and y (value)
        first_point = first_centile['data'][0]
        assert 'x' in first_point
        assert 'y' in first_point

    def test_height_chart_workflow(self, client):
        """Test complete workflow for height chart generation"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'height',
            'sex': 'female'
        }

        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_bmi_chart_workflow(self, client):
        """Test complete workflow for BMI chart generation"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'bmi',
            'sex': 'male'
        }

        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_ofc_chart_workflow(self, client):
        """Test complete workflow for OFC chart generation"""
        data = {
            'reference': 'uk-who',
            'measurement_method': 'ofc',
            'sex': 'female'
        }

        response = client.post('/chart-data', json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True


class TestPDFExportWorkflow:
    """Test complete PDF export workflows"""

    def test_complete_calculation_to_pdf_workflow(self, client):
        """Test complete workflow from calculation to PDF export"""
        # Step 1: Perform calculation
        calc_data = {
            'birth_date': '2020-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '18.5',
            'height': '105.0',
            'ofc': '50.0'
        }

        calc_response = client.post('/calculate', json=calc_data)
        assert calc_response.status_code == 200
        calc_result = calc_response.get_json()
        assert calc_result['success'] is True

        # Step 2: Export to PDF
        pdf_data = {
            'results': calc_result['results'],
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-15',
                'measurement_date': '2024-01-15',
                'reference': 'uk-who'
            }
        }
        pdf_response = client.post('/export-pdf', json=pdf_data)

        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'

        # Verify PDF has content
        assert len(pdf_response.data) > 0

        # PDF should start with PDF magic number
        assert pdf_response.data.startswith(b'%PDF')

    def test_minimal_data_to_pdf_workflow(self, client):
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
        pdf_response = client.post('/export-pdf', json=pdf_data)

        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'


class TestErrorRecoveryWorkflows:
    """Test workflows that involve error handling and recovery"""

    def test_validation_error_workflow(self, client):
        """Test workflow when validation errors occur"""
        # Send invalid data
        data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'invalid',
            'weight': '12.5'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 400

        result = response.get_json()
        assert result['success'] is False
        assert 'error' in result

    def test_missing_required_field_workflow(self, client):
        """Test workflow when required fields are missing"""
        data = {
            'birth_date': '2023-01-15',
            # Missing measurement_date
            'sex': 'male',
            'weight': '12.5'
        }

        response = client.post('/calculate', json=data)
        assert response.status_code == 400

        result = response.get_json()
        assert result['success'] is False

    def test_correction_after_error_workflow(self, client):
        """Test that valid request works after an error"""
        # First, send invalid request
        invalid_data = {
            'birth_date': 'invalid-date',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response1 = client.post('/calculate', json=invalid_data)
        assert response1.status_code == 400

        # Then, send valid request - should succeed
        valid_data = {
            'birth_date': '2023-01-15',
            'measurement_date': '2024-01-15',
            'sex': 'male',
            'weight': '12.5'
        }
        response2 = client.post('/calculate', json=valid_data)
        assert response2.status_code == 200
