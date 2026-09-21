"""
Tests for Mobile Access & QR Share functionality in KisanMitra.
Verifies network-info endpoint, PWA mobile meta tags, mobile share modal,
multilingual translations, and responsive mobile controls.
"""

import unittest
import os
import json
import re
from fastapi.testclient import TestClient
from app import app, get_local_ip, get_public_url


class TestMobileShare(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_network_info_endpoint(self):
        """Verify /api/network-info returns correct network URLs and QR endpoint."""
        res = self.client.get("/api/network-info")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("local_ip", data)
        self.assertIn("port", data)
        self.assertIn("local_url", data)
        self.assertIn("public_url", data)
        self.assertIn("preferred_url", data)
        self.assertIn("qr_code_url", data)
        self.assertIn("has_https", data)

        # Validate IP format
        ip_parts = data["local_ip"].split(".")
        self.assertEqual(len(ip_parts), 4, "Local IP must be valid IPv4")

        # Validate URLs
        self.assertTrue(data["local_url"].startswith("http://"))
        self.assertTrue(str(data["port"]) in data["local_url"])
        self.assertTrue(data["public_url"].startswith("https://"))
        self.assertTrue(data["has_https"])
        self.assertTrue("api.qrserver.com" in data["qr_code_url"])

    def test_mobile_pwa_meta_tags_in_index_html(self):
        """Verify HTML includes standard mobile app meta tags for phone browsers."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.text

        self.assertIn('name="viewport"', html)
        self.assertIn('name="theme-color"', html)
        self.assertIn('name="mobile-web-app-capable"', html)
        self.assertIn('name="apple-mobile-web-app-capable"', html)
        self.assertIn('name="apple-mobile-web-app-title"', html)

    def test_mobile_share_modal_markup(self):
        """Verify index.html contains all mobile share elements."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Header and sidebar triggers
        self.assertIn('id="header-mobile-share-btn"', html)
        self.assertIn('id="sidebar-mobile-share-btn"', html)

        # Modal elements
        self.assertIn('id="mobile-share-modal"', html)
        self.assertIn('id="mobile-share-close-btn"', html)
        self.assertIn('id="mobile-qr-img"', html)
        self.assertIn('id="public-url-input"', html)
        self.assertIn('id="copy-public-url-btn"', html)
        self.assertIn('id="open-public-url-btn"', html)
        self.assertIn('id="local-url-input"', html)
        self.assertIn('id="copy-local-url-btn"', html)
        self.assertIn('id="open-local-url-btn"', html)

    def test_mobile_share_multilingual_translations(self):
        """Verify translations dictionary includes translations for EN, TE, and HI."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        trans_file = os.path.join(base_dir, "static", "js", "translations.js")
        with open(trans_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check English
        self.assertIn('openOnMobile: "Open on Mobile"', content)
        self.assertIn('mobileModalTitle: "Open on Mobile Phone"', content)

        # Check Telugu
        self.assertIn('openOnMobile: "మొబైల్‌లో తెరవండి"', content)
        self.assertIn('mobileModalTitle: "మీ మొబైల్ ఫోన్‌లో తెరవండి"', content)

        # Check Hindi
        self.assertIn('openOnMobile: "मोबाइल पर खोलें"', content)
        self.assertIn('mobileModalTitle: "अपने मोबाइल पर किसानमित्र खोलें"', content)

    def test_api_js_get_network_info(self):
        """Verify api.js defines getNetworkInfo."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        api_file = os.path.join(base_dir, "static", "js", "api.js")
        with open(api_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("async getNetworkInfo()", content)
        self.assertIn("/network-info", content)

    def test_css_mobile_share_styles(self):
        """Verify styles.css contains rules for mobile share card and buttons."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        css_file = os.path.join(base_dir, "static", "css", "styles.css")
        with open(css_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".header-mobile-share-btn", content)
        self.assertIn(".mobile-share-card", content)
        self.assertIn(".qr-preview-box", content)
        self.assertIn(".qr-code-img", content)
        self.assertIn(".mobile-link-card", content)


if __name__ == "__main__":
    unittest.main()
