"""
Unit tests for market_service.py
Validates zero-fabrication rules, variety isolation, dynamic ranking, and normalized records.
"""

import unittest
from market_service import (
    MarketService,
    getLatestMarketPrices,
    getMarketPricesByDate,
    getHighestPriceMarket,
    getLowestPriceMarket,
    compareMarketPrices,
    getMarketPriceSpread,
    getMarketPriceHistory,
    normalizeRecord
)

class TestMarketService(unittest.TestCase):

    def test_variety_341_isolation(self):
        """When 341 is requested, all records must strictly be 341."""
        res = getMarketPricesByDate("Chilli", date="Yesterday", variety="341")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["variety_selected"], "341")
        self.assertFalse(res["variety_unavailable"])
        self.assertGreater(len(res["data"]), 0)
        for rec in res["data"]:
            self.assertEqual(rec["variety"], "341")

    def test_strict_descending_sorting(self):
        """Records must be sorted from highest modal price to lowest modal price."""
        res = getMarketPricesByDate("Chilli", date="Yesterday", variety="341")
        prices = [r["modal_price"] for r in res["data"]]
        self.assertEqual(prices, sorted(prices, reverse=True))
        # Top rank must have rank 1
        self.assertEqual(res["data"][0]["rank"], 1)

    def test_highest_price_market_for_341(self):
        """Highest reported price for 341 must be Guntur Mirchi Yard at 21,800."""
        highest = getHighestPriceMarket("Chilli", variety="341", date="Yesterday")
        self.assertIsNotNone(highest)
        self.assertEqual(highest["market"], "Guntur Mirchi Yard")
        self.assertEqual(highest["modalPrice"], 21800.0)
        self.assertIn("Highest reported comparable price", highest["note"])

    def test_zero_fabrication_unsupported_variety(self):
        """Unsupported variety must return empty data and variety_unavailable = True."""
        res = getMarketPricesByDate("Chilli", date="Yesterday", variety="UnrealVariety999")
        self.assertTrue(res["variety_unavailable"])
        self.assertEqual(len(res["data"]), 0)

    def test_spread_calculation(self):
        """Spread must correctly calculate difference and percentage between highest and lowest."""
        spread = getMarketPriceSpread("Chilli", variety="341", date="Yesterday")
        self.assertEqual(spread["highest_price"], 21800)
        self.assertEqual(spread["lowest_price"], 19900)
        self.assertEqual(spread["difference"], 1900)
        self.assertAlmostEqual(spread["percentage_difference"], 9.55, places=2)

    def test_price_history_without_interpolation(self):
        """Price history must return authentic records for 7D, 30D, 3M, 1Y."""
        hist = getMarketPriceHistory("Chilli", variety="341")
        self.assertIn("7D", hist)
        self.assertIn("30D", hist)
        self.assertIn("3M", hist)
        self.assertIn("1Y", hist)
        self.assertEqual(len(hist["7D"]), 7)
        self.assertEqual(hist["7D"][-1]["price"], 21800)

    def test_normalize_record_format(self):
        """Normalized record must conform to required schema."""
        raw = {
            "crop": "Chilli",
            "variety": "341",
            "market": "Guntur Mirchi Yard",
            "district": "Guntur",
            "state": "Andhra Pradesh",
            "min_price": 19500,
            "max_price": 23200,
            "modal_price": 21800,
            "arrivals": "340 Tonnes",
            "date": "22 Sep 2026"
        }
        norm = normalizeRecord(raw)
        self.assertEqual(norm["crop"], "Chilli")
        self.assertEqual(norm["variety"], "341")
        self.assertEqual(norm["modalPrice"], 21800.0)
        self.assertEqual(norm["unit"], "₹/Quintal")

if __name__ == "__main__":
    unittest.main()
