# Testing Guidelines

## Philosophy

Our testing strategy prioritizes:

1. **Reliability** - Tests should be deterministic and catch real bugs
2. **Maintainability** - Tests should be easy to understand and update
3. **Speed** - Tests should run quickly to encourage frequent execution
4. **Coverage** - Critical paths must be tested, but 100% coverage is not the goal

**Key Principle:** Write tests that provide value, not just to increase coverage numbers.

---

## Test Naming Conventions

### Test Files

- Backend: `test_<module_name>.py` (e.g., `test_validation.py`)
- Frontend: `<module_name>.test.js` (e.g., `validation.test.js`)
- Place tests in `tests/` directory, mirroring source structure

### Test Functions/Methods

Use descriptive names that explain what is being tested:

✅ **Good:**
```python
def test_weight_below_minimum_returns_validation_error()
def test_preterm_infant_receives_corrected_age()
def test_turner_syndrome_uses_correct_reference()
```

❌ **Bad:**
```python
def test_weight()
def test_case_1()
def test_error()
```

### Test Classes

Group related tests using classes with descriptive names:

```python
class TestCalculateEndpoint:
    """Tests for POST /calculate endpoint"""

class TestBoundaryConditions:
    """Tests for exact boundary values"""

class TestMidParentalHeight:
    """Tests for MPH calculation"""
```

---

## Test Structure

### AAA Pattern (Arrange-Act-Assert)

Always structure tests with clear sections:

```python
def test_infant_weight_calculation(client, valid_infant_data):
    """Test weight calculation for 1-year-old infant"""
    # Arrange - Set up test data
    data = valid_infant_data
    data['weight'] = '10.5'

    # Act - Execute the function being tested
    response = client.post('/calculate', json=data)

    # Assert - Verify the results
    assert response.status_code == 200
    result = response.get_json()
    assert result['success'] is True
    assert result['weight_data']['value'] == 10.5
```

### Given-When-Then (Alternative)

For more complex scenarios, use Given-When-Then:

```python
def test_preterm_correction_workflow(client):
    """Test complete preterm correction workflow"""
    # Given a preterm infant born at 32 weeks
    data = preterm_data(gestation_weeks=32, gestation_days=4)

    # When we calculate growth parameters
    response = client.post('/calculate', json=data)

    # Then we should receive corrected age data
    result = response.get_json()
    assert 'corrected_age_data' in result
    assert result['corrected_age_data'] is not None
```

---

## What to Test

### DO Test ✅

1. **Public API / Interfaces**
   - Endpoint inputs and outputs
   - Function parameters and return values
   - Component props and behavior

2. **Business Logic**
   - Calculations and transformations
   - Validation rules
   - Data processing

3. **Error Conditions**
   - Invalid inputs
   - Boundary values
   - Edge cases

4. **Integration Points**
   - API endpoint workflows
   - Database interactions (if applicable)
   - External library calls (rcpchgrowth)

5. **Critical Paths**
   - Most common user workflows
   - Security-critical operations
   - Data integrity checks

### DON'T Test ❌

1. **Implementation Details**
   - Private functions (test through public API)
   - Internal variable names
   - Code formatting

2. **Third-Party Libraries**
   - Don't test rcpchgrowth internals
   - Don't test Flask/React internals
   - Trust well-tested libraries

3. **Trivial Code**
   - Simple getters/setters
   - Obvious pass-throughs
   - Auto-generated code

4. **User Interface Details**
   - Exact pixel positions
   - Specific CSS values
   - Visual aesthetics (use E2E for layout)

---

## Test Types and When to Use Them

### Unit Tests

**Purpose:** Test individual functions/methods in isolation

**When to use:**
- Testing validation logic
- Testing calculations
- Testing data transformations

**Example:**
```python
def test_norm_cdf_at_zero():
    """Test CDF at z=0 returns 0.5"""
    result = norm_cdf(0)
    assert abs(result - 0.5) < 1e-7
```

**Characteristics:**
- Fast (< 100ms each)
- No external dependencies
- Deterministic results

### Integration Tests

**Purpose:** Test multiple components working together

**When to use:**
- Testing API endpoints
- Testing complete workflows
- Testing database interactions

**Example:**
```python
def test_complete_calculation_workflow(client):
    """Test full calculation from input to output"""
    data = infant_data()
    response = client.post('/calculate', json=data)

    assert response.status_code == 200
    result = response.get_json()
    assert_measurement_result(result['weight_data'], 'weight')
```

**Characteristics:**
- Slower than unit tests
- May involve HTTP requests
- Test realistic scenarios

### End-to-End Tests

**Purpose:** Test complete user workflows through the UI

**When to use:**
- Testing responsive design
- Testing cross-browser compatibility
- Testing critical user journeys

**Example:**
```python
def test_form_completes_successfully(page, base_url):
    """Test user can complete form on mobile"""
    page.goto(base_url)
    page.fill('#weight', '12.5')
    page.click('#calculate-btn')
    assert page.locator('.results').is_visible()
```

**Characteristics:**
- Slowest tests
- Most realistic
- Can be brittle

---

## Coverage Goals

### By Module Type

| Type | Target | Rationale |
|------|--------|-----------|
| Core logic (validation, calculations) | 100% | Critical for correctness |
| Business logic (models, utils) | 85-90% | High value, frequently used |
| API endpoints | 75-85% | Important but less critical |
| UI helpers | 60-70% | E2E tests cover most scenarios |
| Scripts with heavy DOM | 30-40% | E2E tests are more appropriate |

### Coverage is Not the Goal

**Good coverage ≠ Good tests**

Focus on:
- Testing critical paths thoroughly
- Testing edge cases and errors
- Testing what can actually break

Avoid:
- Writing tests just to hit coverage targets
- Testing trivial code
- Testing third-party code

---

## Test Data Best Practices

### Use Fixtures and Generators

✅ **Good:**
```python
def test_calculation(client, valid_infant_data):
    """Use fixture for common data"""
    response = client.post('/calculate', json=valid_infant_data)
    assert response.status_code == 200
```

❌ **Bad:**
```python
def test_calculation(client):
    """Inline data is harder to maintain"""
    data = {
        'birth_date': '2023-01-15',
        'measurement_date': '2024-01-15',
        'sex': 'male',
        'weight': '10.5',
        # ... 20 more lines
    }
    response = client.post('/calculate', json=data)
```

### Use Test Data Builders

✅ **Good:**
```python
def test_mph_calculation(client):
    """Build data using helpers"""
    data = infant_data()
    data = with_parental_heights(data, maternal_height='165', paternal_height='180')
    response = client.post('/calculate', json=data)
```

### Avoid Magic Numbers

✅ **Good:**
```python
MIN_WEIGHT = 0.1
MAX_WEIGHT = 300

def test_weight_at_minimum():
    assert validate_weight(MIN_WEIGHT) is True

def test_weight_below_minimum():
    assert validate_weight(MIN_WEIGHT - 0.01) is False
```

❌ **Bad:**
```python
def test_weight_validation():
    assert validate_weight(0.1) is True
    assert validate_weight(0.09) is False
```

---

## Mocking Guidelines

### When to Mock

✅ **Mock external services:**
- HTTP requests to external APIs
- Database calls (if applicable)
- File system operations
- Time-dependent code

✅ **Mock for isolation:**
- Testing error handling without triggering real errors
- Testing edge cases that are hard to reproduce

### When NOT to Mock

❌ **Don't mock:**
- Your own code (test the real thing)
- Simple data structures
- Well-tested libraries (rcpchgrowth)

### Example

```python
from unittest.mock import patch

def test_external_api_failure():
    """Test handling of external API failure"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = ConnectionError("API unavailable")

        result = fetch_external_data()

        assert result is None  # Graceful degradation
```

---

## Async Testing (JavaScript)

### Testing Promises

```javascript
test('fetches data successfully', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});
```

### Testing with Mock Timers

```javascript
jest.useFakeTimers();

test('debounce delays execution', () => {
  const mockFn = jest.fn();
  const debouncedFn = debounce(mockFn, 500);

  debouncedFn();
  expect(mockFn).not.toHaveBeenCalled();

  jest.advanceTimersByTime(500);
  expect(mockFn).toHaveBeenCalledTimes(1);
});
```

---

## Parametrized Tests

### Using pytest.mark.parametrize

✅ **Good for testing multiple inputs:**

```python
@pytest.mark.parametrize("weight,expected", [
    (0.1, True),    # Minimum
    (10.0, True),   # Normal
    (300, True),    # Maximum
    (0.05, False),  # Below minimum
    (350, False),   # Above maximum
])
def test_weight_validation(weight, expected):
    """Test weight validation with various inputs"""
    result = validate_weight(weight)
    assert result == expected
```

### Benefits
- Reduces code duplication
- Makes test cases explicit
- Easy to add new cases

---

## Test Maintenance

### Keeping Tests Up to Date

**When code changes:**
1. Run affected tests immediately
2. Update test assertions if behavior changed
3. Add tests for new code paths
4. Don't delete tests that still provide value

**Regular maintenance:**
- Review failing tests promptly
- Remove tests for deleted features
- Update test data when formats change
- Refactor tests when they become hard to understand

### Dealing with Flaky Tests

**If a test fails intermittently:**

1. **Investigate root cause:**
   - Timing issues? Add appropriate waits
   - Test ordering issues? Ensure tests are independent
   - External dependencies? Add better mocking

2. **Don't just re-run:**
   - Flaky tests erode confidence
   - Fix the root cause, don't ignore

3. **Last resort:**
   - Mark as flaky with `@pytest.mark.flaky`
   - Document the issue
   - Plan to fix properly

---

## Performance Testing

### Keep Tests Fast

**Unit tests:** < 100ms each
**Integration tests:** < 1 second each
**E2E tests:** < 30 seconds each

### Strategies for Speed

1. **Run in parallel:**
   ```bash
   pytest -n auto
   ```

2. **Use appropriate scope for fixtures:**
   ```python
   @pytest.fixture(scope="session")  # Created once
   @pytest.fixture(scope="module")   # Created per file
   @pytest.fixture(scope="function")  # Created per test (default)
   ```

3. **Skip slow tests during development:**
   ```python
   @pytest.mark.slow
   def test_comprehensive_e2e():
       pass
   ```

   ```bash
   pytest -m "not slow"
   ```

---

## Debugging Failed Tests

### Reading Test Output

```
FAILED tests/test_endpoints.py::test_calculate - AssertionError: assert 400 == 200
```

This tells you:
- File: `tests/test_endpoints.py`
- Test: `test_calculate`
- Failure: Expected 200, got 400

### Using Print Debugging

```python
def test_calculation(client):
    response = client.post('/calculate', json=data)

    # Print for debugging
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")

    assert response.status_code == 200
```

Run with `-s` to see print output:
```bash
pytest tests/test_file.py::test_calculation -s
```

### Using Debugger

```python
def test_calculation(client):
    import pdb; pdb.set_trace()  # Debugger breakpoint

    response = client.post('/calculate', json=data)
    assert response.status_code == 200
```

---

## CI/CD Integration

### Pre-commit Checks

Before committing, run:
```bash
# Quick smoke test
pytest tests/test_validation.py tests/test_calculations.py

# Full test suite (if time allows)
pytest
npm test
```

### Pull Request Requirements

All PRs must:
- Pass all existing tests
- Add tests for new functionality
- Maintain or improve coverage
- Have meaningful test names and docstrings

### Deployment Gates

Tests run automatically on push/PR:
- All backend tests must pass
- All frontend tests must pass
- Coverage must not decrease by > 5%

---

## Common Patterns and Examples

### Testing Error Responses

```python
def test_invalid_sex_returns_error(client):
    """Test that invalid sex value returns 400 error"""
    data = valid_calculation_data(sex='invalid')

    response = client.post('/calculate', json=data)

    assert_error_response(response, 400, 'sex')
```

### Testing with Multiple Scenarios

```python
@pytest.mark.parametrize("reference,expected_in_result", [
    ('uk-who', 'UK-WHO'),
    ('turners-syndrome', 'Turner'),
    ('trisomy-21', 'Trisomy'),
])
def test_reference_formatting(reference, expected_in_result):
    """Test reference names are formatted correctly"""
    formatted = format_reference(reference)
    assert expected_in_result in formatted
```

### Testing Workflows

```python
def test_complete_infant_assessment(client):
    """Test complete workflow for infant growth assessment"""
    # Step 1: Calculate growth parameters
    calc_data = infant_data()
    calc_response = client.post('/calculate', json=calc_data)
    assert calc_response.status_code == 200

    # Step 2: Get chart data
    chart_data = chart_data_request('weight', 'male')
    chart_response = client.post('/chart-data', json=chart_data)
    assert chart_response.status_code == 200

    # Step 3: Export to PDF
    pdf_data = {'results': calc_response.get_json()}
    pdf_response = client.post('/export-pdf', json=pdf_data)
    assert_pdf_response(pdf_response)
```

---

## Anti-Patterns to Avoid

### ❌ Testing Implementation Instead of Behavior

```python
# BAD - Tests internal implementation
def test_calculation_uses_correct_formula():
    assert calculator._internal_formula == "x * y / z"

# GOOD - Tests behavior
def test_calculation_returns_correct_result():
    result = calculator.calculate(10, 5, 2)
    assert result == 25
```

### ❌ Overly Complex Test Setup

```python
# BAD - Too much setup
def test_something():
    # 50 lines of setup
    result = do_thing()
    assert result == expected

# GOOD - Use fixtures
def test_something(prepared_data):
    result = do_thing(prepared_data)
    assert result == expected
```

### ❌ Testing Multiple Things in One Test

```python
# BAD
def test_everything():
    assert validate_weight(10) is True
    assert validate_height(100) is True
    assert validate_ofc(48) is True
    # ... 20 more assertions

# GOOD - Separate tests
def test_weight_validation():
    assert validate_weight(10) is True

def test_height_validation():
    assert validate_height(100) is True
```

### ❌ Brittle Tests

```python
# BAD - Breaks if order changes
def test_results():
    results = get_results()
    assert results[0] == 'weight'
    assert results[1] == 'height'

# GOOD - Tests behavior, not order
def test_results():
    results = get_results()
    assert 'weight' in results
    assert 'height' in results
```

---

## Resources

- **pytest docs:** https://docs.pytest.org/
- **Jest docs:** https://jestjs.io/
- **Testing best practices:** https://testingjavascript.com/
- **Test-driven development:** https://martinfowler.com/bliki/TestDrivenDevelopment.html

---

**Remember:** Tests are code too. Keep them clean, maintainable, and valuable.

**Last Updated:** January 2026
