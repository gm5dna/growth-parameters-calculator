"""
Basic tests for Copy Results feature
Tests clipboard button visibility and basic functionality
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import time


class TestCopyFeature:
    """Test suite for copy results functionality"""

    BASE_URL = "http://localhost:8080"

    def test_copy_button_exists_when_results_shown(self):
        """Test that copy button appears when results are displayed"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(self.BASE_URL, wait_until="networkidle")

                # Copy button should not be visible initially (no results)
                results = page.locator("#results")
                assert not results.is_visible()

                # Fill form and submit
                page.locator("#sex-male").click()
                page.locator("#birth_date").fill("2020-01-01")
                page.locator("#measurement_date").fill("2023-01-01")
                page.locator("#weight").fill("15")
                page.locator("#height").fill("90")
                page.locator(".btn-submit").click()

                # Wait for results
                page.wait_for_selector("#results.show", timeout=10000)

                # Copy button should be visible now
                copy_btn = page.locator("#copyResultsBtn")
                expect(copy_btn).to_be_visible()

                # Button should have correct text
                expect(copy_btn.locator(".text")).to_have_text("Copy")

            finally:
                browser.close()

    def test_copy_button_click_shows_toast(self):
        """Test that clicking copy button shows toast (success or graceful failure in headless)"""
        with sync_playwright() as p:
            # Grant clipboard permissions
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()

            try:
                page.goto(self.BASE_URL, wait_until="networkidle")

                # Submit form to get results
                page.locator("#sex-male").click()
                page.locator("#birth_date").fill("2020-01-01")
                page.locator("#measurement_date").fill("2023-01-01")
                page.locator("#weight").fill("15")
                page.locator("#height").fill("90")
                page.locator(".btn-submit").click()

                page.wait_for_selector("#results.show", timeout=10000)

                # Click copy button
                page.locator("#copyResultsBtn").click()

                # Wait a bit for async clipboard operation
                time.sleep(0.5)

                # Toast should appear (either success or error)
                toast = page.locator("#copyToast")
                expect(toast).to_be_visible()

                # Toast should have the "show" class
                assert toast.evaluate("el => el.classList.contains('show')")

                # Check if it's success or error (clipboard may fail in headless)
                is_success = toast.evaluate("el => el.classList.contains('success')")
                is_error = toast.evaluate("el => el.classList.contains('error')")

                assert is_success or is_error, "Toast should have either success or error class"

            finally:
                context.close()
                browser.close()

    def test_copy_button_mobile_responsive(self):
        """Test that copy button is mobile responsive"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 375, "height": 667})
            page = context.new_page()

            try:
                page.goto(self.BASE_URL, wait_until="networkidle")

                # Submit form
                page.locator("#sex-male").click()
                page.locator("#birth_date").fill("2020-01-01")
                page.locator("#measurement_date").fill("2023-01-01")
                page.locator("#weight").fill("15")
                page.locator("#height").fill("90")
                page.locator(".btn-submit").click()

                page.wait_for_selector("#results.show", timeout=10000)

                # Copy button should be visible and full-width on mobile
                copy_btn = page.locator("#copyResultsBtn")
                expect(copy_btn).to_be_visible()

                # Check button is full width (or close to viewport width)
                box = copy_btn.bounding_box()
                # On mobile, button should take significant width (allowing for padding)
                assert box["width"] > 290, f"Button width {box['width']}px too narrow for mobile"

            finally:
                context.close()
                browser.close()

    def test_clipboard_manager_formats(self):
        """Test that ClipboardManager is available and has expected formats"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(self.BASE_URL, wait_until="networkidle")

                # Check that clipboardManager is available
                has_manager = page.evaluate("typeof clipboardManager !== 'undefined'")
                assert has_manager, "clipboardManager not found in global scope"

                # Check available formats
                formats = page.evaluate("Object.keys(clipboardManager.formats)")
                assert 'plain' in formats
                assert 'compact' in formats
                assert 'markdown' in formats
                assert 'json' in formats

            finally:
                browser.close()

    def test_extract_results_data_function(self):
        """Test that extractResultsData function works correctly"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(self.BASE_URL, wait_until="networkidle")

                # Submit form
                page.locator("#sex-male").click()
                page.locator("#birth_date").fill("2020-01-01")
                page.locator("#measurement_date").fill("2023-01-01")
                page.locator("#weight").fill("15")
                page.locator("#height").fill("90")
                page.locator(".btn-submit").click()

                page.wait_for_selector("#results.show", timeout=10000)

                # Call extractResultsData
                data = page.evaluate("extractResultsData()")

                # Check extracted data structure
                assert data is not None
                assert 'sex' in data
                assert data['sex'] == 'male'
                assert 'age' in data
                assert 'weight' in data
                assert 'height' in data

                # Weight should have value, centile, sds
                if data['weight']:
                    assert 'value' in data['weight']
                    assert 'centile' in data['weight']
                    assert 'sds' in data['weight']

            finally:
                browser.close()


def test_toast_auto_dismisses():
    """Test that toast notification auto-dismisses"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:8080", wait_until="networkidle")

            # Submit form
            page.locator("#sex-male").click()
            page.locator("#birth_date").fill("2020-01-01")
            page.locator("#measurement_date").fill("2023-01-01")
            page.locator("#weight").fill("15")
            page.locator("#height").fill("90")
            page.locator(".btn-submit").click()

            page.wait_for_selector("#results.show", timeout=10000)

            # Click copy button
            page.locator("#copyResultsBtn").click()

            # Toast should be visible
            time.sleep(0.5)
            toast = page.locator("#copyToast")
            assert toast.evaluate("el => el.classList.contains('show')")

            # Wait for auto-dismiss (3 seconds)
            time.sleep(3.5)

            # Toast should be hidden
            assert not toast.evaluate("el => el.classList.contains('show')")

        finally:
            browser.close()


if __name__ == "__main__":
    print("Run with: pytest test_copy_feature.py -v")
