"""
Unit and Integration Tests for Chilli / Mirchi Variety Selection in KisanMitra
Validates:
- Secondary variety selection (341, Teja, Wonder Hot, Byadgi, etc.)
- Strict variety isolation (no cross-variety mixing)
- Zero fabrication enforcement (unavailable variety returns empty, no fallback substitution)
- Variety comparison side-by-side payload
- AI Chat variety awareness and comparison
"""

import unittest
from fastapi.testclient import TestClient
from app import app, query_market_data, reset_profile
from ai_agent import session_repo

class TestChilliVarietyFeature(unittest.TestCase):
    def setUp(self):
        reset_profile()
        session_repo.sessions.clear()
        self.client = TestClient(app)

    def test_chilli_all_varieties_list(self):
        """Selecting Chilli without specific variety provides supported variety options."""
        res = self.client.get("/api/market?crop=Chilli&date=Yesterday")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["crop"], "Chilli")
        self.assertEqual(data["variety_selected"], "all")
        self.assertIn("341", data["varieties"])
        self.assertIn("Teja", data["varieties"])
        self.assertIn("Wonder Hot", data["varieties"])
        self.assertIn("Byadgi", data["varieties"])
        self.assertIn("Guntur Sannam", data["varieties"])
        self.assertIn("Dry Chilli", data["varieties"])
        self.assertIn("Local / Other", data["varieties"])
        # Check comparison summary payload
        self.assertGreater(len(data["varieties_comparison"]), 0)

    def test_strict_341_variety_filtering(self):
        """When 341 is selected, only 341 records must be returned with zero cross-contamination."""
        res = self.client.get("/api/market?crop=Chilli&variety=341&date=Yesterday")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["crop"], "Chilli")
        self.assertEqual(data["variety_selected"], "341")
        self.assertEqual(data["display_title"], "CHILLI — 341")
        self.assertFalse(data["variety_unavailable"])

        # All records must strictly be 341
        self.assertGreater(len(data["data"]), 0)
        for item in data["data"]:
            self.assertEqual(item["variety"], "341", f"Found non-341 variety: {item['variety']}")
            self.assertEqual(item["crop"], "Chilli")

        # Must be strictly sorted descending by modal_price
        prices = [m["modal_price"] for m in data["data"]]
        self.assertEqual(prices, sorted(prices, reverse=True))

        # Highest price must be Guntur Mirchi Yard at 21,800
        highest = data["data"][0]
        self.assertEqual(highest["market"], "Guntur Mirchi Yard")
        self.assertEqual(highest["modal_price"], 21800)
        self.assertEqual(highest["variety"], "341")

        # History should be specific to 341
        self.assertIn("7D", data["history"])
        self.assertGreater(len(data["history"]["7D"]), 0)

    def test_strict_teja_variety_filtering(self):
        """When Teja is selected, only Teja records must be returned."""
        res = self.client.get("/api/market?crop=Chilli&variety=Teja&date=Yesterday")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["variety_selected"], "Teja")
        for item in data["data"]:
            self.assertEqual(item["variety"], "Teja")

    def test_zero_fabrication_rule(self):
        """If a variety has no data for market/date, state unavailable and do NOT substitute another variety."""
        res = self.client.get("/api/market?crop=Chilli&variety=NonExistentVariety&date=Yesterday")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["variety_unavailable"])
        self.assertEqual(len(data["data"]), 0, "Must not fabricate or substitute records for unavailable variety")

    def test_chat_yesterday_341_price(self):
        """Chat asking 'What was yesterday's 341 price?' should return 341 market ranking."""
        res = self.client.post("/api/chat", json={"message": "What was yesterday's 341 price?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_variety_rates")
        self.assertIn("341", data["reply"])
        self.assertIn("21,800", data["reply"])
        self.assertIn("Guntur Mirchi Yard", data["reply"])
        self.assertIn("Highest reported comparable price in the available data.", data["reply"])

    def test_chat_compare_two_varieties(self):
        """Chat asking 'Compare 341 and Teja' returns side-by-side comparison with spread."""
        res = self.client.post("/api/chat", json={"message": "Compare 341 and Teja"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_variety_comparison")
        self.assertIn("341", data["reply"])
        self.assertIn("Teja", data["reply"])
        self.assertIn("Price Difference", data["reply"])

    def test_chat_compare_all_chilli_varieties(self):
        """Chat asking 'Compare chilli varieties' returns overview of varieties."""
        res = self.client.post("/api/chat", json={"message": "Compare chilli varieties"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_variety_comparison")
        self.assertIn("341", data["reply"])
        self.assertIn("Teja", data["reply"])

    def test_chat_highest_price_for_341(self):
        """Chat asking 'Where is 341 selling at the highest price?' identifies top mandi."""
        res = self.client.post("/api/chat", json={"message": "Where is 341 selling at the highest price?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_variety_rates")
        self.assertIn("Guntur Mirchi Yard", data["reply"])
        self.assertIn("21,800", data["reply"])

if __name__ == "__main__":
    unittest.main()
