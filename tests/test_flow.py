"""
Unit and Integration Tests for KisanMitra Chat-First User Flow & AI Agent
Tests FastAPI endpoint handlers directly for fast, dependency-free execution.
"""

import unittest
from fastapi import HTTPException
from app import (
    FarmerProfile,
    ChatRequest,
    get_profile,
    update_profile,
    reset_profile,
    get_market_prices,
    get_weather,
    process_chat
)

class TestKisanMitraFlow(unittest.TestCase):
    def setUp(self):
        # Reset profile to uncompleted initial state
        reset_profile()

    def test_initial_profile_state(self):
        """Initial experience should reflect uncompleted profile."""
        profile = get_profile()
        self.assertFalse(profile.completed)
        self.assertEqual(profile.name, "")

    def test_profile_validation_required_fields(self):
        """Test required fields: Name, Location, at least 1 Crop, Farm size."""
        # 1. Missing Name
        with self.assertRaises(HTTPException) as cm:
            update_profile(FarmerProfile(
                name="",
                location="Guntur",
                crops=["Tomato"],
                farm_size="3 acres"
            ))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Farmer name is required", cm.exception.detail)

        # 2. Missing Location
        with self.assertRaises(HTTPException) as cm:
            update_profile(FarmerProfile(
                name="Ramesh Kumar",
                location="",
                crops=["Tomato"],
                farm_size="3 acres"
            ))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Farm location is required", cm.exception.detail)

        # 3. Missing Crops
        with self.assertRaises(HTTPException) as cm:
            update_profile(FarmerProfile(
                name="Ramesh Kumar",
                location="Guntur",
                crops=[],
                farm_size="3 acres"
            ))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("At least one main crop is required", cm.exception.detail)

        # 4. Missing Farm Size
        with self.assertRaises(HTTPException) as cm:
            update_profile(FarmerProfile(
                name="Ramesh Kumar",
                location="Guntur",
                crops=["Tomato"],
                farm_size=""
            ))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Farm size is required", cm.exception.detail)

    def test_successful_profile_submission_with_optional_fields_skipped(self):
        """Profile completes successfully with only required fields, optional skipped."""
        p = FarmerProfile(
            name="Ramesh Kumar",
            location="Guntur",
            crops=["Tomato"],
            farm_size="3 acres",
            # Optional fields left empty
            crop_variety="",
            soil_type="",
            irrigation_type="",
            growth_stage=""
        )
        res = update_profile(p)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["profile"].completed)
        self.assertEqual(res["profile"].name, "Ramesh Kumar")

        # Verify via get_profile()
        saved = get_profile()
        self.assertTrue(saved.completed)
        self.assertEqual(saved.name, "Ramesh Kumar")
        self.assertEqual(saved.location, "Guntur")
        self.assertEqual(saved.crops, ["Tomato"])

    def test_ai_personalization_highest_price(self):
        """AI must use farmer profile location & crop for 'Where is my crop getting the highest price?'"""
        profile = FarmerProfile(
            name="Ramesh Kumar",
            location="Guntur",
            crops=["Tomato"],
            farm_size="3 acres",
            crop_variety="Hybrid Red",
            soil_type="Red Loam",
            irrigation_type="Drip",
            growth_stage="Flowering",
            completed=True
        )
        update_profile(profile)

        # Send chat message without specifying crop or location explicitly
        req = ChatRequest(
            message="Where is my crop getting the highest price?",
            profile=profile
        )
        data = process_chat(req)
        self.assertEqual(data["tool_used"], "market_comparator")
        self.assertEqual(data["context_applied"]["crop"], "Tomato")
        self.assertEqual(data["context_applied"]["location"], "Guntur")
        self.assertIn("Tomato", data["reply"])
        self.assertIn("Ramesh Kumar", data["reply"])
        self.assertIn("Guntur", data["reply"])
        self.assertIn("Highest Price Market", data["reply"])

    def test_market_and_weather_endpoints(self):
        """Test auxiliary data endpoints for market and weather."""
        res_market = get_market_prices(crop="Tomato")
        self.assertEqual(res_market["status"], "success")
        self.assertGreater(len(res_market["data"]), 0)

        res_weather = get_weather(location="Guntur")
        self.assertEqual(res_weather["status"], "success")
        self.assertIn("temp", res_weather["data"])
        self.assertEqual(len(res_weather["forecast_5_days"]), 5)

if __name__ == "__main__":
    unittest.main()
