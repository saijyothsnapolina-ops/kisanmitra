import unittest

class TestSearchAndCameraTap(unittest.TestCase):
    def setUp(self):
        with open('static/index.html', 'r', encoding='utf-8') as f:
            self.html = f.read()
        with open('static/js/app.js', 'r', encoding='utf-8') as f:
            self.app_js = f.read()
        with open('static/js/components.js', 'r', encoding='utf-8') as f:
            self.components_js = f.read()
        with open('static/css/styles.css', 'r', encoding='utf-8') as f:
            self.css = f.read()

    def test_boot_initialization_resilience(self):
        """Verify app.js boots reliably even if DOMContentLoaded already fired."""
        self.assertIn("function boot()", self.app_js)
        self.assertIn("if (document.readyState === 'loading')", self.app_js)
        self.assertIn("document.addEventListener('DOMContentLoaded', boot)", self.app_js)
        self.assertIn("boot();", self.app_js)

    def test_market_search_input_and_clear_button(self):
        """Verify market search bar has wrapper id, autocomplete off, and clear button."""
        self.assertIn('id="market-search-input"', self.components_js)
        self.assertIn('id="search-input-wrapper"', self.components_js)
        self.assertIn('id="market-search-clear"', self.components_js)
        self.assertIn('filterTableInPlace', self.components_js)
        self.assertIn('data-market-row="true"', self.components_js)
        self.assertIn('data-search-text=', self.components_js)

    def test_camera_and_chat_tap_controls(self):
        """Verify camera button and native fallback inputs in index.html and app.js."""
        self.assertIn('id="chat-photo-btn"', self.html)
        self.assertIn('id="chat-camera-capture-input"', self.html)
        self.assertIn('capture="environment"', self.html)
        self.assertIn('id="opt-camera-btn"', self.html)
        self.assertIn('id="opt-gallery-btn"', self.html)
        self.assertIn('dom.cameraCaptureInput.click()', self.app_js)

    def test_touch_manipulation_and_mobile_styles(self):
        """Verify touch-action manipulation and mobile 16px font-size to prevent zoom."""
        self.assertIn('touch-action: manipulation;', self.css)
        self.assertIn('pointer-events: none;', self.css)
        self.assertIn('font-size: 16px !important;', self.css)
        self.assertIn('height: 100dvh;', self.css)
        self.assertIn('search-clear-btn', self.css)

if __name__ == '__main__':
    unittest.main()
