"""
End-to-End API and Flow Test using TestClient (httpx)
"""

import unittest
from fastapi.testclient import TestClient
from app import app

class TestEndToEndKisanMitra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        # Reset profile before each test
        self.client.post("/api/profile/reset")

    def test_static_index_html_served(self):
        """Verify root URL serves the Chat-First HTML frontend."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("KisanMitra", res.text)
        self.assertIn("Let's set up your farm", res.text)
        self.assertIn("Ask KisanMitra about your farm...", res.text)
        self.assertIn("Where is my crop getting the highest price?", res.text)

    def test_complete_farmer_user_flow(self):
        """
        Simulate user flow:
        1. User opens website -> Profile uncompleted.
        2. User attempts to ask 'Where is my crop getting the highest price?'
        3. Form validation verifies required fields.
        4. User completes profile (Name: Ramesh Kumar, Location: Guntur, Crops: ['Tomato'], Farm size: '3 acres').
        5. Preserved question is processed by AI with personalized context applied!
        """
        # Step 1: Initial state
        res_profile = self.client.get("/api/profile")
        self.assertEqual(res_profile.status_code, 200)
        self.assertFalse(res_profile.json()["completed"])

        # Step 2 & 3: Save profile
        profile_data = {
            "name": "Ramesh Kumar",
            "location": "Guntur",
            "crops": ["Tomato"],
            "farm_size": "3 acres",
            "crop_variety": "Hybrid Red",
            "soil_type": "Red Loam",
            "irrigation_type": "Drip",
            "growth_stage": "Flowering / Fruiting",
            "completed": True
        }
        res_save = self.client.post("/api/profile", json=profile_data)
        self.assertEqual(res_save.status_code, 200)
        self.assertTrue(res_save.json()["profile"]["completed"])

        # Step 4: AI processes preserved query
        chat_req = {
            "message": "Where is my crop getting the highest price?",
            "profile": profile_data
        }
        res_chat = self.client.post("/api/chat", json=chat_req)
        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()

        # Verify AI personalized output
        self.assertEqual(chat_data["context_applied"]["crop"], "Tomato")
        self.assertEqual(chat_data["context_applied"]["location"], "Guntur")
        self.assertEqual(chat_data["context_applied"]["farmer"], "Ramesh Kumar")
        self.assertIn("Guntur", chat_data["reply"])
        self.assertIn("Tomato", chat_data["reply"])
        self.assertIn("Highest Price Market", chat_data["reply"])

    def test_tomato_price_today_query(self):
        """Test specific example from user specification: 'What is the tomato price today?'"""
        profile_data = {
            "name": "Suresh Patel",
            "location": "Guntur",
            "crops": ["Tomato"],
            "farm_size": "2 acres",
            "completed": True
        }
        self.client.post("/api/profile", json=profile_data)

        chat_req = {
            "message": "What is the tomato price today?",
            "profile": profile_data
        }
        res = self.client.post("/api/chat", json=chat_req)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_rates")
        self.assertIn("Tomato", data["reply"])
        self.assertIn("Live Mandi Rates", data["reply"])

if __name__ == "__main__":
    unittest.main()
