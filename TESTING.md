# Testing Documentation

## Overview

This document provides comprehensive guidance for running, writing, and maintaining tests for the Growth Parameters Calculator.

**Current Test Coverage:**
- Backend (Python): 70%+ overall coverage
- Frontend (JavaScript): 60%+ coverage for testable modules
- Total Tests: 336+ automated tests
- E2E Tests: 99 Playwright responsive tests

---

## Quick Start

### Backend Tests (Python/Pytest)

```bash
# Run all backend tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_endpoints.py

# Run specific test
pytest tests/test_endpoints.py::TestCalculateEndpoint::test_calculate_with_weight_only

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

### Frontend Tests (JavaScript/Jest)

```bash
# Install dependencies first
npm install

# Run all JavaScript tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (re-runs on file changes)
npm run test:watch

# Run with verbose output
npm run test:verbose
```

### E2E Tests (Playwright)

```bash
# Run all E2E tests (auto-starts server)
pytest tests/test_responsive.py

# Run accessibility tests
pytest tests/test_accessibility.py

# Run specific device test
pytest tests/test_responsive.py -k "iPhone"
```

---

## Test Structure

### Directory Layout

```
tests/
├── conftest.py                 # Pytest configuration & fixtures
├── helpers/
│   ├── __init__.py
│   ├── test_data.py           # Reusable test data generators
│   └── assertions.py          # Custom assertion helpers
│
├── js/                        # JavaScript tests (Jest)
│   ├── setup.js              # Jest configuration
│   ├── validation.test.js    # 39 validation tests
│   ├── clipboard.test.js     # 38 clipboard tests
│   └── script.test.js        # 31 script tests
│
├── test_validation.py         # Backend validation (100% coverage)
├── test_calculations.py       # Calculation logic (100% coverage)
├── test_endpoints.py          # API endpoints (42 tests)
├── test_models.py             # Model functions (39 tests)
├── test_utils.py              # Utility functions (47 tests)
├── test_error_paths.py        # Error scenarios (58 tests)
├── test_rate_limiting.py      # Rate limiting (7 tests)
├── test_workflows.py          # Integration tests (22 tests)
├── test_accessibility.py      # A11y tests (13 tests)
├── test_responsive.py         # Responsive E2E (99 tests)
├── test_copy_feature.py       # Copy feature tests
├── test_pdf_export.py         # PDF export tests
└── ...
```

---

## Coverage Targets

### Current Coverage by Module

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| validation.py | 100% | 100% | ✅ Excellent |
| calculations.py | 100% | 100% | ✅ Excellent |
| models.py | 90%+ | 90% | ✅ Excellent |
| utils.py | 85%+ | 85% | ✅ Excellent |
| app.py | 75%+ | 75% | ✅ Good |
| pdf_utils.py | 65%+ | 65% | ✅ Good |
| validation.js | 90%+ | 90% | ✅ Excellent |
| clipboard.js | 85%+ | 85% | ✅ Excellent |
| script.js | 35%+ | 35% | ✅ Good* |
| **OVERALL** | **70%+** | **70%** | ✅ **Target Met** |

*script.js target is intentionally lower due to heavy DOM manipulation requiring E2E tests

### Viewing Coverage Reports

#### Backend Coverage (Python)
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html
```

#### Frontend Coverage (JavaScript)
```bash
# Generate coverage report
npm run test:coverage

# Open in browser
open coverage-js/index.html
```

---

## Running Specific Test Types

### Unit Tests Only

```bash
# Backend unit tests
pytest tests/test_validation.py tests/test_calculations.py tests/test_models.py tests/test_utils.py

# Frontend unit tests
npm test -- validation.test.js clipboard.test.js
```

### Integration Tests Only

```bash
pytest tests/test_workflows.py tests/test_endpoints.py
```

### Error Path Tests

```bash
pytest tests/test_error_paths.py -v
```

### By Test Marker

```bash
# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"

# Run only E2E tests
pytest -m e2e
```

---

## Writing New Tests

### Using Test Data Generators

```python
from tests.helpers.test_data import infant_data, with_parental_heights

def test_infant_calculation(client):
    """Test calculation for infant"""
    data = infant_data(age_months=12)
    response = client.post('/calculate', json=data)
    assert response.status_code == 200

def test_with_mph(client):
    """Test with mid-parental height"""
    data = infant_data()
    data = with_parental_heights(data, maternal_height='165', paternal_height='180')
    response = client.post('/calculate', json=data)
    # ... assertions
```

### Using Custom Assertions

```python
from tests.helpers.assertions import (
    assert_valid_response,
    assert_measurement_result,
    assert_mph_data
)

def test_measurement(client, valid_infant_data):
    """Test using custom assertions"""
    response = client.post('/calculate', json=valid_infant_data)

    assert_valid_response(response, 200)
    result = response.get_json()

    assert_measurement_result(result['weight_data'], 'weight')
    assert_measurement_result(result['height_data'], 'height')
```

### Using Fixtures

```python
def test_with_fixtures(client, valid_infant_data, assert_valid_response):
    """Test using pytest fixtures"""
    response = client.post('/calculate', json=valid_infant_data)
    result = assert_valid_response(response)

    assert result['success'] is True
```

---

## Test Data Generators Reference

Available in `tests/helpers/test_data.py`:

- `valid_calculation_data(**overrides)` - Base valid calculation data
- `infant_data(**overrides)` - Infant (0-2 years)
- `child_data(age_years=5, **overrides)` - Child (2-12 years)
- `preterm_data(gestation_weeks=32, **overrides)` - Preterm infant
- `turner_syndrome_data(**overrides)` - Turner syndrome patient
- `with_parental_heights(data, maternal, paternal)` - Add MPH data
- `with_previous_measurement(data, months_ago=6)` - Add velocity data
- `with_bone_age(data, years, months=0)` - Add bone age
- `extreme_sds_data(sds_target=-5.0)` - Generate extreme values
- `chart_data_request(method, sex, reference)` - Chart data request
- `malformed_data_examples()` - Collection of invalid data
- `boundary_values()` - Boundary value test cases

**Quick Access:**
- `quick_infant()` - 1 year old
- `quick_child()` - 5 years old
- `quick_preterm()` - 32 weeks gestation

---

## Custom Assertions Reference

Available in `tests/helpers/assertions.py`:

- `assert_valid_response(response, status=200)` - Valid HTTP response
- `assert_error_response(response, status=400, contains=None)` - Error response
- `assert_measurement_result(data, type)` - Measurement structure
- `assert_age_result(data)` - Age data structure
- `assert_chart_data(data)` - Chart data structure
- `assert_mph_data(data)` - Mid-parental height data
- `assert_pdf_response(response)` - PDF response
- `assert_corrected_age_data(data)` - Corrected age for preterm
- `assert_bsa_data(data)` - Body surface area data
- `assert_height_velocity_data(data)` - Height velocity data
- `assert_success_with_measurements(response, *types)` - Multiple measurements
- `assert_warning_present(response, warning_text)` - Warning messages

---

## Continuous Integration

Tests run automatically on:
- Every push to main branch
- Every pull request
- Pre-deployment (via Render)

### CI Requirements

All tests must pass before deployment:
```bash
# This is what CI runs:
pytest --cov=. --cov-report=term-missing
npm test
```

### Pre-commit Hooks

Optionally set up pre-commit hooks:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/test_validation.py tests/test_calculations.py
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Troubleshooting

### Common Issues

#### 1. E2E Tests Fail with "Connection Refused"

**Problem:** Playwright tests can't connect to server

**Solution:** The `live_server` fixture should auto-start the server. If it fails:
```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill existing process
kill -9 <PID>

# Re-run tests
pytest tests/test_responsive.py
```

#### 2. JavaScript Tests Fail with "Cannot find module"

**Problem:** Node dependencies not installed

**Solution:**
```bash
npm install
npm test
```

#### 3. Coverage Report Missing Modules

**Problem:** Some files not included in coverage

**Solution:** Check `.coveragerc` and ensure files are not excluded

#### 4. Tests Pass Locally But Fail in CI

**Problem:** Environment differences

**Solution:**
- Check Python version (must be 3.12.8)
- Check dependency versions in requirements-dev.txt
- Review CI logs for specific errors

#### 5. Rate Limiting Tests Skip

**Problem:** Flask-Limiter not installed

**Solution:**
```bash
pip install Flask-Limiter
```

This is expected - rate limiting tests gracefully skip if not available.

#### 6. Accessibility Tests Skip

**Problem:** axe-playwright not installed

**Solution:**
```bash
pip install axe-playwright
```

---

## Performance Considerations

### Running Tests Faster

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Skip slow E2E tests during development
pytest -m "not e2e"

# Run only fast unit tests
pytest tests/test_validation.py tests/test_calculations.py
```

### Test Execution Time

Approximate execution times:
- Unit tests (backend): ~2-5 seconds
- Unit tests (frontend): ~3-8 seconds
- Integration tests: ~5-10 seconds
- E2E responsive tests: ~2-3 minutes (99 tests across 8 devices)
- Full test suite: ~3-5 minutes

---

## Adding New Tests

### Step-by-Step Process

1. **Identify what to test**
   - New feature? → Add integration test + unit tests
   - Bug fix? → Add regression test
   - Refactoring? → Ensure existing tests pass

2. **Choose test location**
   - New endpoint → `test_endpoints.py`
   - Validation logic → `test_validation.py` or `tests/js/validation.test.js`
   - Calculation → `test_calculations.py`
   - Utility function → `test_utils.py`
   - Complete workflow → `test_workflows.py`

3. **Write test using patterns**
   ```python
   def test_descriptive_name(client, valid_infant_data):
       """Docstring explaining what is being tested"""
       # Arrange
       data = valid_infant_data
       data['weight'] = '12.5'

       # Act
       response = client.post('/calculate', json=data)

       # Assert
       assert response.status_code == 200
       result = response.get_json()
       assert result['success'] is True
   ```

4. **Run test to verify**
   ```bash
   pytest tests/test_file.py::test_descriptive_name -v
   ```

5. **Check coverage**
   ```bash
   pytest --cov=module_under_test --cov-report=term-missing
   ```

---

## Test Maintenance

### Regular Maintenance Tasks

- **Weekly:** Review test failures, update fixtures if data formats change
- **Monthly:** Review coverage reports, identify gaps
- **Quarterly:** Update test dependencies, review test performance

### Updating Tests After Code Changes

When you modify code:
1. Run affected tests immediately
2. Update test assertions if API changed
3. Add new tests for new code paths
4. Ensure coverage doesn't decrease

### Deprecating Old Tests

When removing features:
1. Remove associated tests
2. Check for orphaned fixtures
3. Update coverage expectations

---

## Additional Resources

- **pytest documentation:** https://docs.pytest.org/
- **Jest documentation:** https://jestjs.io/docs/getting-started
- **Playwright documentation:** https://playwright.dev/python/
- **Coverage.py documentation:** https://coverage.readthedocs.io/

---

## Getting Help

If you encounter issues with tests:

1. Check this documentation
2. Review test file docstrings
3. Look at existing similar tests for patterns
4. Check CI logs for specific error messages
5. Consult `documentation/TESTING_GUIDELINES.md` for best practices

---

**Last Updated:** January 2026
**Maintainer:** Development Team
