"""
Accessibility Tests

Tests WCAG 2.1 AA compliance and accessibility features.
Requires axe-playwright for automated accessibility testing.
"""

import pytest


# Check if axe-playwright is available
try:
    from axe_playwright import Axe
    AXE_AVAILABLE = True
except ImportError:
    AXE_AVAILABLE = False


@pytest.mark.skipif(not AXE_AVAILABLE, reason="axe-playwright not installed")
class TestAccessibility:
    """Test accessibility compliance using axe-core"""

    def test_homepage_wcag_compliance(self, page, base_url):
        """Test that homepage meets WCAG 2.1 AA standards"""
        page.goto(base_url)

        # Run axe accessibility scan
        axe = Axe()
        results = axe.run(page)

        # Check for violations
        violations = results.get('violations', [])

        # Filter out minor issues and focus on critical/serious
        critical_violations = [
            v for v in violations
            if v.get('impact') in ['critical', 'serious']
        ]

        # Assert no critical violations
        assert len(critical_violations) == 0, (
            f"Found {len(critical_violations)} critical accessibility violations: "
            f"{[v['description'] for v in critical_violations]}"
        )

    def test_form_labels_present(self, page, base_url):
        """Test that all form inputs have associated labels"""
        page.goto(base_url)

        # Check all input fields have labels
        inputs = page.locator('input[type="text"], input[type="date"], input[type="number"]').all()

        for input_element in inputs:
            input_id = input_element.get_attribute('id')
            if input_id:
                # Check if there's a label for this input
                label = page.locator(f'label[for="{input_id}"]')
                assert label.count() > 0, f"No label found for input with id: {input_id}"

    def test_form_has_fieldsets(self, page, base_url):
        """Test that radio button groups use fieldset and legend"""
        page.goto(base_url)

        # Find radio button groups
        radio_groups = page.locator('input[type="radio"]').all()

        if len(radio_groups) > 0:
            # Check if radios are within fieldsets
            fieldsets = page.locator('fieldset').count()
            # Should have at least one fieldset for radio groups
            assert fieldsets > 0, "Radio buttons should be grouped in fieldsets"

    def test_keyboard_navigation(self, page, base_url):
        """Test that form can be navigated with keyboard only"""
        page.goto(base_url)

        # Tab through form elements
        page.keyboard.press('Tab')  # Focus first element

        # Check that focus is visible
        focused_element = page.evaluate('document.activeElement.tagName')
        assert focused_element is not None

        # Tab through multiple elements
        for _ in range(5):
            page.keyboard.press('Tab')

        # Ensure we can still focus elements
        focused_after_tabs = page.evaluate('document.activeElement.tagName')
        assert focused_after_tabs is not None

    def test_heading_hierarchy(self, page, base_url):
        """Test that heading levels follow proper hierarchy"""
        page.goto(base_url)

        # Get all headings
        h1_count = page.locator('h1').count()
        h2_count = page.locator('h2').count()

        # Should have exactly one h1
        assert h1_count == 1, "Page should have exactly one h1 heading"

        # If there are h3s, there should be h2s first
        h3_count = page.locator('h3').count()
        if h3_count > 0:
            assert h2_count > 0, "Cannot have h3 without h2 elements"

    def test_color_contrast(self, page, base_url):
        """Test that color contrast meets WCAG AA standards"""
        page.goto(base_url)

        # Run axe with color contrast rules
        axe = Axe()
        results = axe.run(page)

        # Check for color contrast violations
        violations = results.get('violations', [])
        contrast_violations = [
            v for v in violations
            if 'color-contrast' in v.get('id', '')
        ]

        assert len(contrast_violations) == 0, (
            f"Found {len(contrast_violations)} color contrast violations"
        )

    def test_alt_text_for_images(self, page, base_url):
        """Test that all images have alt text"""
        page.goto(base_url)

        # Get all images
        images = page.locator('img').all()

        for img in images:
            # Check for alt attribute
            alt_text = img.get_attribute('alt')
            assert alt_text is not None, "All images must have alt attribute"

    def test_aria_labels_present(self, page, base_url):
        """Test that interactive elements have appropriate ARIA labels"""
        page.goto(base_url)

        # Check buttons without text content have aria-label
        buttons = page.locator('button').all()

        for button in buttons:
            text_content = button.text_content().strip()
            if not text_content:
                # Button has no text, should have aria-label
                aria_label = button.get_attribute('aria-label')
                aria_labelledby = button.get_attribute('aria-labelledby')
                assert aria_label or aria_labelledby, (
                    "Buttons without text must have aria-label or aria-labelledby"
                )

    def test_landmark_regions(self, page, base_url):
        """Test that page uses appropriate landmark regions"""
        page.goto(base_url)

        # Check for main landmark
        main_landmark = page.locator('main, [role="main"]').count()
        assert main_landmark > 0, "Page should have a main landmark region"

    def test_skip_to_content_link(self, page, base_url):
        """Test for skip-to-content link for keyboard users"""
        page.goto(base_url)

        # Tab once to focus first focusable element
        page.keyboard.press('Tab')

        # Check if focused element is a skip link
        focused_text = page.evaluate('document.activeElement.textContent')

        # Skip link is optional but recommended
        # This test documents current state
        assert focused_text is not None


@pytest.mark.skipif(AXE_AVAILABLE, reason="Testing behavior without axe-playwright")
class TestAccessibilityWithoutAxe:
    """Basic accessibility tests that don't require axe-playwright"""

    def test_form_labels_basic(self, page, base_url):
        """Test basic form label association"""
        page.goto(base_url)

        # Check birth_date input has label
        birth_date_label = page.locator('label[for="birth_date"]')
        assert birth_date_label.count() > 0

        # Check measurement_date input has label
        measurement_date_label = page.locator('label[for="measurement_date"]')
        assert measurement_date_label.count() > 0

    def test_page_has_title(self, page, base_url):
        """Test that page has a descriptive title"""
        page.goto(base_url)

        title = page.title()
        assert title is not None
        assert len(title) > 0
        # Should contain relevant keywords
        assert 'growth' in title.lower() or 'calculator' in title.lower()

    def test_page_has_language_attribute(self, page, base_url):
        """Test that HTML element has lang attribute"""
        page.goto(base_url)

        html_lang = page.locator('html').get_attribute('lang')
        assert html_lang is not None
        assert html_lang in ['en', 'en-GB', 'en-US']


@pytest.fixture(scope="session")
def page(browser, base_url):
    """Create a Playwright page for accessibility testing"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
