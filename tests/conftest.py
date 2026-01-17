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
