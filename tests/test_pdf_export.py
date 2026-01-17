"""
Tests for PDF export functionality

Tests the PDF generation endpoint and utilities
"""

import pytest
import json
from io import BytesIO
from datetime import datetime
import base64


class TestPDFExportEndpoint:
    """Test the /export-pdf endpoint"""

    def test_export_pdf_success_minimal_data(self, client):
        """Test PDF export with minimal required data"""
        payload = {
            'results': {
                'age': {
                    'years': 6,
                    'months': 0,
                    'days': 16,
                    'corrected_decimal_age': 6.04
                },
                'measurements': {
                    'weight': {
                        'value': 20.0,
                        'centile': 36.77,
                        'sds': -0.3
                    }
                }
            },
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-01',
                'measurement_date': '2026-01-17',
                'reference': 'uk-who'
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        assert len(response.data) > 0

        # Verify PDF header (PDF files start with %PDF-)
        assert response.data[:5] == b'%PDF-'

    def test_export_pdf_success_complete_data(self, client):
        """Test PDF export with all measurements and parameters"""
        payload = {
            'results': {
                'age': {
                    'years': 6,
                    'months': 0,
                    'days': 16,
                    'corrected_decimal_age': 6.04
                },
                'measurements': {
                    'weight': {
                        'value': 20.0,
                        'centile': 36.77,
                        'sds': -0.3
                    },
                    'height': {
                        'value': 120.0,
                        'centile': 78.2,
                        'sds': 0.8
                    },
                    'bmi': {
                        'value': 13.9,
                        'centile': 7.54,
                        'sds': -1.4
                    },
                    'ofc': {
                        'value': 51.0,
                        'centile': 7.72,
                        'sds': -1.4
                    }
                },
                'height_velocity': {
                    'height_velocity_cm_year': 1.2
                },
                'bsa': {
                    'boyd': 0.82,
                    'dubois': 0.81,
                    'mosteller': 0.80
                },
                'gh_dose': {
                    'daily_dose_mg': 0.80
                },
                'mph': {
                    'mph_cm': 178.0,
                    'target_range_min': 167.9,
                    'target_range_max': 187.5
                },
                'warnings': [
                    'Height below 0.4th centile',
                    'Weight SDS outside typical range'
                ]
            },
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-01',
                'measurement_date': '2026-01-17',
                'reference': 'uk-who'
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        assert len(response.data) > 0

    def test_export_pdf_with_chart_images(self, client):
        """Test PDF export with chart images"""
        # Create a simple 1x1 pixel PNG in base64
        # This is a minimal valid PNG
        test_png_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

        payload = {
            'results': {
                'age': {
                    'years': 6,
                    'months': 0,
                    'days': 16,
                    'corrected_decimal_age': 6.04
                },
                'measurements': {
                    'weight': {
                        'value': 20.0,
                        'centile': 36.77,
                        'sds': -0.3
                    }
                }
            },
            'patient_info': {
                'sex': 'female',
                'birth_date': '2020-01-01',
                'measurement_date': '2026-01-17',
                'reference': 'uk-who'
            },
            'chart_images': {
                'height': f'data:image/png;base64,{test_png_base64}',
                'weight': f'data:image/png;base64,{test_png_base64}'
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'

    def test_export_pdf_missing_data(self, client):
        """Test PDF export with missing required data"""
        # Missing patient_info
        payload = {
            'results': {
                'age': {'years': 6, 'months': 0, 'days': 16},
                'measurements': {'weight': {'value': 20.0}}
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Missing required data' in data['error']

    def test_export_pdf_missing_results(self, client):
        """Test PDF export with missing results"""
        payload = {
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-01',
                'measurement_date': '2026-01-17',
                'reference': 'uk-who'
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_export_pdf_no_data(self, client):
        """Test PDF export with no data"""
        response = client.post('/export-pdf',
                                data=json.dumps({}),
                                content_type='application/json')

        assert response.status_code == 400

    def test_export_pdf_invalid_json(self, client):
        """Test PDF export with invalid JSON"""
        response = client.post('/export-pdf',
                                data='invalid json',
                                content_type='application/json')

        assert response.status_code in [400, 500]

    def test_export_pdf_filename_format(self, client):
        """Test PDF export filename contains timestamp"""
        payload = {
            'results': {
                'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
                'measurements': {'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3}}
            },
            'patient_info': {
                'sex': 'male',
                'birth_date': '2020-01-01',
                'measurement_date': '2026-01-17',
                'reference': 'uk-who'
            }
        }

        response = client.post('/export-pdf',
                                data=json.dumps(payload),
                                content_type='application/json')

        assert response.status_code == 200

        # Check Content-Disposition header for filename
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'growth-report-' in content_disposition
        assert '.pdf' in content_disposition


class TestPDFUtilities:
    """Test PDF generation utilities"""

    def test_pdf_generator_initialization(self):
        """Test GrowthReportPDF initialization"""
        from pdf_utils import GrowthReportPDF

        results = {
            'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
            'measurements': {
                'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3}
            }
        }
        patient_info = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'reference': 'uk-who'
        }

        pdf_gen = GrowthReportPDF(results, patient_info)
        assert pdf_gen.results == results
        assert pdf_gen.patient_info == patient_info
        assert pdf_gen.chart_images == {}

    def test_pdf_generation_returns_buffer(self):
        """Test that PDF generation returns a BytesIO buffer"""
        from pdf_utils import GrowthReportPDF

        results = {
            'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
            'measurements': {
                'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3}
            }
        }
        patient_info = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'reference': 'uk-who'
        }

        pdf_gen = GrowthReportPDF(results, patient_info)
        buffer = pdf_gen.generate()

        assert isinstance(buffer, BytesIO)
        assert buffer.tell() == 0  # Should be at beginning
        assert len(buffer.getvalue()) > 0

    def test_pdf_contains_valid_pdf_header(self):
        """Test that generated PDF has valid PDF header"""
        from pdf_utils import GrowthReportPDF

        results = {
            'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
            'measurements': {
                'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3}
            }
        }
        patient_info = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'reference': 'uk-who'
        }

        pdf_gen = GrowthReportPDF(results, patient_info)
        buffer = pdf_gen.generate()
        pdf_data = buffer.getvalue()

        assert pdf_data[:5] == b'%PDF-'

    def test_pdf_with_all_measurements(self):
        """Test PDF generation with all measurement types"""
        from pdf_utils import GrowthReportPDF

        results = {
            'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
            'measurements': {
                'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3},
                'height': {'value': 120.0, 'centile': 78.2, 'sds': 0.8},
                'bmi': {'value': 13.9, 'centile': 7.54, 'sds': -1.4},
                'ofc': {'value': 51.0, 'centile': 7.72, 'sds': -1.4}
            }
        }
        patient_info = {
            'sex': 'female',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'reference': 'uk90'
        }

        pdf_gen = GrowthReportPDF(results, patient_info)
        buffer = pdf_gen.generate()

        assert len(buffer.getvalue()) > 0

    def test_pdf_with_warnings(self):
        """Test PDF generation with warnings"""
        from pdf_utils import GrowthReportPDF

        results = {
            'age': {'years': 6, 'months': 0, 'days': 16, 'corrected_decimal_age': 6.04},
            'measurements': {
                'weight': {'value': 20.0, 'centile': 36.77, 'sds': -0.3}
            },
            'warnings': [
                'Height below 0.4th centile',
                'Weight SDS outside typical range'
            ]
        }
        patient_info = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'reference': 'uk-who'
        }

        pdf_gen = GrowthReportPDF(results, patient_info)
        buffer = pdf_gen.generate()

        assert len(buffer.getvalue()) > 0


class TestPDFIntegration:
    """Integration tests for PDF export feature"""

    def test_full_calculation_to_pdf_workflow(self, client):
        """Test complete workflow from calculation to PDF export"""
        # Step 1: Perform calculation
        calc_payload = {
            'sex': 'male',
            'birth_date': '2020-01-01',
            'measurement_date': '2026-01-17',
            'weight': 20.0,
            'height': 120.0,
            'reference': 'uk-who'
        }

        calc_response = client.post('/calculate',
                                     data=json.dumps(calc_payload),
                                     content_type='application/json')

        assert calc_response.status_code == 200
        calc_data = json.loads(calc_response.data)
        assert calc_data['success'] is True

        # Step 2: Export results to PDF
        pdf_payload = {
            'results': calc_data['results'],
            'patient_info': {
                'sex': calc_payload['sex'],
                'birth_date': calc_payload['birth_date'],
                'measurement_date': calc_payload['measurement_date'],
                'reference': calc_payload['reference']
            }
        }

        pdf_response = client.post('/export-pdf',
                                    data=json.dumps(pdf_payload),
                                    content_type='application/json')

        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'
        assert len(pdf_response.data) > 0
        assert pdf_response.data[:5] == b'%PDF-'
