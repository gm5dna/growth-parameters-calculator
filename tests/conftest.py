"""
Pytest configuration and fixtures for testing
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import app as flask_app

    # Set testing configuration
    flask_app.config['TESTING'] = True

    yield flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


def _run_flask_server():
    """Run Flask server in subprocess - top-level function for pickling"""
    from app import app
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)


@pytest.fixture(scope="session")
def live_server():
    """
    Start Flask server in background for E2E tests

    This fixture automatically starts the Flask development server
    on localhost:8080 for Playwright/E2E tests, eliminating the need
    to manually start the server before running tests.
    """
    import multiprocessing
    import time
    import requests

    # Start server in background process
    server_process = multiprocessing.Process(target=_run_flask_server, daemon=True)
    server_process.start()

    # Wait for server to be ready (max 15 seconds)
    server_url = 'http://localhost:8080'
    for attempt in range(30):
        try:
            response = requests.get(server_url, timeout=1)
            if response.status_code == 200:
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(0.5)
    else:
        # Server didn't start in time
        server_process.terminate()
        server_process.join(timeout=5)
        raise RuntimeError("Flask server failed to start within 15 seconds")

    yield server_url

    # Cleanup: terminate server process
    server_process.terminate()
    server_process.join(timeout=5)
    if server_process.is_alive():
        server_process.kill()


@pytest.fixture(scope="session")
def base_url(live_server):
    """
    Provide base URL for E2E tests

    This fixture depends on live_server to ensure the Flask app
    is running before tests execute.
    """
    return live_server


# ============================================================================
# Comprehensive Test Data Fixtures
# ============================================================================

@pytest.fixture
def valid_infant_data():
    """Valid data for 1-year-old infant"""
    return {
        'birth_date': '2023-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '10.5',
        'height': '76.0',
        'ofc': '47.0'
    }


@pytest.fixture
def valid_child_data():
    """Valid data for 4-year-old child"""
    return {
        'birth_date': '2020-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'female',
        'weight': '18.0',
        'height': '105.0'
    }


@pytest.fixture
def preterm_data():
    """Valid data for preterm infant"""
    return {
        'birth_date': '2023-10-01',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '5.8',
        'height': '65.0',
        'gestation_weeks': 32,
        'gestation_days': 4
    }


@pytest.fixture
def recent_dates():
    """Generate recent dates for testing"""
    from datetime import date, timedelta
    today = date.today()
    return {
        'today': today.isoformat(),
        'yesterday': (today - timedelta(days=1)).isoformat(),
        'one_week_ago': (today - timedelta(days=7)).isoformat(),
        'one_month_ago': (today - timedelta(days=30)).isoformat(),
        'six_months_ago': (today - timedelta(days=180)).isoformat(),
        'one_year_ago': (today - timedelta(days=365)).isoformat()
    }


@pytest.fixture
def future_date():
    """Generate a future date for validation testing"""
    from datetime import date, timedelta
    return (date.today() + timedelta(days=30)).isoformat()


@pytest.fixture
def mock_measurement():
    """Mock measurement result structure"""
    return {
        'value': 12.5,
        'centile': 50.2,
        'sds': 0.05
    }


# ============================================================================
# Helper Function Fixtures
# ============================================================================

@pytest.fixture
def assert_valid_response():
    """Fixture providing response validation helper"""
    def _assert_valid(response, expected_status=200):
        assert response.status_code == expected_status
        if expected_status == 200:
            result = response.get_json()
            assert result is not None
            return result
        return None
    return _assert_valid


@pytest.fixture
def assert_error_response():
    """Fixture providing error response validation helper"""
    def _assert_error(response, expected_status=400):
        assert response.status_code == expected_status
        result = response.get_json()
        assert result is not None
        assert result.get('success') is False
        assert 'error' in result
        return result
    return _assert_error


@pytest.fixture
def assert_measurement_result():
    """Fixture providing measurement validation helper"""
    def _assert_measurement(measurement_data, measurement_type):
        assert measurement_data is not None
        assert 'value' in measurement_data
        assert 'centile' in measurement_data
        assert 'sds' in measurement_data

        centile = measurement_data['centile']
        if centile is not None:
            assert 0 <= centile <= 100

        sds = measurement_data['sds']
        if sds is not None:
            assert -10 <= sds <= 10

        return measurement_data
    return _assert_measurement


@pytest.fixture
def assert_age_result():
    """Fixture providing age validation helper"""
    def _assert_age(age_data):
        assert age_data is not None
        assert 'decimal_age' in age_data
        assert 'calendar_age' in age_data
        assert 0 <= age_data['decimal_age'] <= 25
        return age_data
    return _assert_age


@pytest.fixture
def assert_chart_data():
    """Fixture providing chart data validation helper"""
    def _assert_chart(chart_data):
        assert isinstance(chart_data, list)
        assert len(chart_data) > 0

        first_centile = chart_data[0]
        assert 'centile' in first_centile
        assert 'data' in first_centile
        assert isinstance(first_centile['data'], list)

        if len(first_centile['data']) > 0:
            first_point = first_centile['data'][0]
            assert 'x' in first_point
            assert 'y' in first_point

        return chart_data
    return _assert_chart
