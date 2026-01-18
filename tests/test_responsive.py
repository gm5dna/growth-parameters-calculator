"""
Mobile Responsiveness Test Suite for Growth Parameters Calculator

Tests the app across various mobile device dimensions to ensure:
- Proper layout and element visibility
- Text readability (no overflow, proper sizing)
- Touch target sizes (minimum 44x44px)
- Form usability
- Chart rendering
- No horizontal scrolling
"""

import pytest
from playwright.sync_api import sync_playwright, Page, expect
import time


# Common mobile device viewports
MOBILE_DEVICES = {
    "iPhone SE": {"width": 375, "height": 667},  # Small phone
    "iPhone 12/13/14": {"width": 390, "height": 844},  # Modern iPhone
    "iPhone 14 Pro Max": {"width": 430, "height": 932},  # Large iPhone
    "Samsung Galaxy S20": {"width": 360, "height": 800},  # Small Android
    "Samsung Galaxy S21": {"width": 384, "height": 854},  # Medium Android
    "Pixel 5": {"width": 393, "height": 851},  # Google Pixel
    "Pixel 7 Pro": {"width": 412, "height": 915},  # Large Pixel
    "Small Android": {"width": 320, "height": 568},  # Minimum size
}


@pytest.fixture(scope="module")
def playwright_instance():
    """Initialize Playwright instance"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def browser(playwright_instance):
    """Launch browser with mobile emulation"""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


class TestMobileResponsiveness:
    """Test suite for mobile responsiveness"""

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_page_loads_without_horizontal_scroll(self, browser, base_url, device_name, viewport):
        """Test that page loads without horizontal scrolling"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Check for horizontal scrollbar
            scroll_width = page.evaluate("document.documentElement.scrollWidth")
            client_width = page.evaluate("document.documentElement.clientWidth")

            assert scroll_width <= client_width, \
                f"{device_name}: Horizontal scroll detected (scrollWidth: {scroll_width}, clientWidth: {client_width})"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_header_and_title_visible(self, browser, base_url, device_name, viewport):
        """Test that header and title are visible and properly sized"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Check h1 is visible
            h1 = page.locator("h1")
            expect(h1).to_be_visible()

            # Check that title doesn't overflow
            h1_box = h1.bounding_box()
            container_width = viewport["width"]

            assert h1_box["width"] < container_width - 40, \
                f"{device_name}: Title may be overflowing (width: {h1_box['width']}px)"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_mode_toggle_visible_and_functional(self, browser, base_url, device_name, viewport):
        """Test that mode toggle is visible and works"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Check mode toggle container is visible (not the hidden checkbox)
            mode_toggle_container = page.locator(".mode-toggle")
            expect(mode_toggle_container).to_be_visible()

            # Check mode text is visible
            mode_text = page.locator("#modeText")
            expect(mode_text).to_be_visible()

            # Test toggle functionality by clicking the visible slider
            initial_text = mode_text.text_content()
            page.locator(".slider").click()
            time.sleep(0.3)  # Wait for transition

            new_text = mode_text.text_content()
            assert initial_text != new_text, \
                f"{device_name}: Mode toggle doesn't update text"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_form_inputs_are_touch_friendly(self, browser, base_url, device_name, viewport):
        """Test that form inputs meet minimum touch target size (44px)"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Test main inputs
            inputs_to_test = [
                "#birth_date",
                "#measurement_date",
                "#weight",
                "#height",
            ]

            for input_selector in inputs_to_test:
                input_elem = page.locator(input_selector)
                box = input_elem.bounding_box()

                assert box["height"] >= 44, \
                    f"{device_name}: Input {input_selector} height {box['height']}px < 44px (not touch-friendly)"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_buttons_are_touch_friendly(self, browser, base_url, device_name, viewport):
        """Test that buttons meet minimum touch target size"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Test main buttons
            submit_btn = page.locator(".btn-submit")
            reset_btn = page.locator(".btn-reset")

            for btn in [submit_btn, reset_btn]:
                box = btn.bounding_box()
                assert box["height"] >= 44, \
                    f"{device_name}: Button height {box['height']}px < 44px"
                assert box["width"] >= 44, \
                    f"{device_name}: Button width {box['width']}px < 44px"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_radio_buttons_are_accessible(self, browser, base_url, device_name, viewport):
        """Test that radio buttons and labels are properly sized"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Test sex radio buttons
            male_radio = page.locator("#sex-male")
            female_radio = page.locator("#sex-female")

            for radio in [male_radio, female_radio]:
                expect(radio).to_be_visible()
                box = radio.bounding_box()
                assert box["width"] >= 20, \
                    f"{device_name}: Radio button too small (width: {box['width']}px)"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_disclaimer_renders_properly(self, browser, base_url, device_name, viewport):
        """Test that disclaimer is visible and doesn't overflow"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            disclaimer = page.locator("#disclaimer")
            expect(disclaimer).to_be_visible()

            box = disclaimer.bounding_box()
            container_width = viewport["width"]

            assert box["width"] <= container_width - 40, \
                f"{device_name}: Disclaimer overflowing"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_form_completes_successfully(self, browser, base_url, device_name, viewport):
        """Test that form can be filled and submitted on mobile"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Fill form
            page.locator("#sex-male").click()
            page.locator("#birth_date").fill("2020-01-01")
            page.locator("#measurement_date").fill("2023-01-01")
            page.locator("#weight").fill("15")
            page.locator("#height").fill("90")

            # Submit
            page.locator(".btn-submit").click()

            # Wait for results
            page.wait_for_selector("#results.show", timeout=10000)

            # Check results are visible
            results = page.locator("#results")
            expect(results).to_be_visible()

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_results_grid_layout(self, browser, base_url, device_name, viewport):
        """Test that results grid renders properly"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Fill and submit form
            page.locator("#sex-male").click()
            page.locator("#birth_date").fill("2020-01-01")
            page.locator("#measurement_date").fill("2023-01-01")
            page.locator("#weight").fill("15")
            page.locator("#height").fill("90")
            page.locator(".btn-submit").click()

            # Wait for results
            page.wait_for_selector("#results.show", timeout=10000)

            # Check result items don't overflow
            result_items = page.locator(".result-item").all()

            for item in result_items:
                if item.is_visible():
                    box = item.bounding_box()
                    container_width = viewport["width"]

                    assert box["width"] <= container_width - 40, \
                        f"{device_name}: Result item overflowing"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_chart_section_responsive(self, browser, base_url, device_name, viewport):
        """Test that chart section renders properly on mobile"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Fill and submit form
            page.locator("#sex-male").click()
            page.locator("#birth_date").fill("2020-01-01")
            page.locator("#measurement_date").fill("2023-01-01")
            page.locator("#weight").fill("15")
            page.locator("#height").fill("90")
            page.locator(".btn-submit").click()

            # Wait for results
            page.wait_for_selector("#results.show", timeout=10000)

            # Show charts
            show_charts_btn = page.locator("#showChartsBtn")
            expect(show_charts_btn).to_be_visible()
            show_charts_btn.click()

            # Wait for charts section
            page.wait_for_selector("#charts-section.show", timeout=5000)

            # Check chart tabs are visible
            chart_tabs = page.locator(".chart-tab").all()
            assert len(chart_tabs) > 0, f"{device_name}: No chart tabs found"

            # Check chart container
            chart_container = page.locator(".chart-container")
            expect(chart_container).to_be_visible()

            box = chart_container.bounding_box()
            container_width = viewport["width"]

            assert box["width"] <= container_width, \
                f"{device_name}: Chart container overflowing"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_text_readability(self, browser, base_url, device_name, viewport):
        """Test that text sizes are readable (minimum 14px for body text)"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            # Check various text elements
            elements_to_check = [
                ("label", 14),  # Labels should be at least 14px
                ('input[type="text"]', 14),  # Text inputs should be at least 14px
                ('input[type="number"]', 14),  # Number inputs should be at least 14px
                ('input[type="date"]', 14),  # Date inputs should be at least 14px
                (".disclaimer", 14),  # Disclaimer text
            ]

            for selector, min_size in elements_to_check:
                element = page.locator(selector).first
                if element.count() > 0:  # Check if element exists
                    font_size = element.evaluate("el => window.getComputedStyle(el).fontSize")
                    font_size_num = float(font_size.replace("px", ""))

                    assert font_size_num >= min_size, \
                        f"{device_name}: {selector} font size {font_size_num}px < {min_size}px"

        finally:
            context.close()

    @pytest.mark.parametrize("device_name,viewport", MOBILE_DEVICES.items())
    def test_footer_visible(self, browser, base_url, device_name, viewport):
        """Test that footer is visible and properly formatted"""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto(base_url, wait_until="networkidle")

            footer = page.locator(".footer")
            expect(footer).to_be_visible()

            # Check footer link is clickable
            footer_link = page.locator(".footer a")
            expect(footer_link).to_be_visible()

        finally:
            context.close()


class TestLayoutBreakpoints:
    """Test specific layout changes at breakpoints"""

    BASE_URL = "http://localhost:8080"

    def test_form_grid_layout_at_768px(self, browser):
        """Test that form switches to 2-column at 768px"""
        # Just below breakpoint (767px)
        context = browser.new_context(viewport={"width": 767, "height": 1024})
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle")

        form_grid = page.locator(".form-grid").first
        grid_columns = form_grid.evaluate(
            "el => window.getComputedStyle(el).gridTemplateColumns"
        )

        # Should be single column or auto
        assert "1fr 1fr" not in grid_columns, \
            "Form should be single column below 768px"

        context.close()

        # At breakpoint (768px)
        context = browser.new_context(viewport={"width": 768, "height": 1024})
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle")

        form_grid = page.locator(".form-grid").first
        grid_columns = form_grid.evaluate(
            "el => window.getComputedStyle(el).gridTemplateColumns"
        )

        # Should be two columns
        assert "1fr 1fr" in grid_columns or grid_columns.count("px") >= 2, \
            "Form should be two columns at 768px+"

        context.close()

    def test_result_grid_layout_at_600px(self, browser):
        """Test that results grid switches to 2-column at 600px"""
        # Below breakpoint (599px)
        context = browser.new_context(viewport={"width": 599, "height": 800})
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle")

        # Fill and submit form
        page.locator("#sex-male").click()
        page.locator("#birth_date").fill("2020-01-01")
        page.locator("#measurement_date").fill("2023-01-01")
        page.locator("#weight").fill("15")
        page.locator("#height").fill("90")
        page.locator(".btn-submit").click()
        page.wait_for_selector("#results.show", timeout=10000)

        result_grid = page.locator(".result-grid")
        grid_columns = result_grid.evaluate(
            "el => window.getComputedStyle(el).gridTemplateColumns"
        )

        # Should be single column
        columns_count = grid_columns.count("px") or grid_columns.count("fr")
        assert columns_count <= 1, \
            "Results should be single column below 600px"

        context.close()


def test_visual_regression_snapshot(browser):
    """Take screenshots at various sizes for manual visual inspection"""
    import os

    os.makedirs("test_screenshots", exist_ok=True)

    for device_name, viewport in MOBILE_DEVICES.items():
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        try:
            page.goto("http://localhost:8080", wait_until="networkidle")

            # Screenshot of form
            safe_name = device_name.replace(" ", "_").replace("/", "-")
            page.screenshot(path=f"test_screenshots/{safe_name}_form.png")

            # Fill and submit
            page.locator("#sex-male").click()
            page.locator("#birth_date").fill("2020-01-01")
            page.locator("#measurement_date").fill("2023-01-01")
            page.locator("#weight").fill("15")
            page.locator("#height").fill("90")
            page.locator(".btn-submit").click()
            page.wait_for_selector("#results.show", timeout=10000)

            # Screenshot of results
            page.screenshot(path=f"test_screenshots/{safe_name}_results.png")

        finally:
            context.close()


if __name__ == "__main__":
    print("Run with: pytest test_responsive.py -v")
    print("For screenshots: pytest test_responsive.py::test_visual_regression_snapshot -v")
