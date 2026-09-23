"""
Tests for KISANMITRA - Core Two Problems:
1. Location Separation (Farm Location independent from Device Location, Zero Fake Defaults)
2. Conversational Memory (Crop -> Yesterday -> 341 -> Highest Market), Strict Variety Isolation,
   General Questions without forced agriculture, and Telugu default only when uncertain.
"""

import unittest
from fastapi.testclient import TestClient
from app import app, reset_profile, get_profile, FarmerProfile, update_profile
from ai_agent import AIAgent, session_repo

class TestCoreTwoProblems(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        reset_profile()

    # ==========================================================================
    # 1. Location Separation Tests
    # ==========================================================================

    def test_location_search_autocomplete(self):
        """Search endpoint must return matching Indian agricultural villages, mandals, districts."""
        res = self.client.get("/api/location/search?q=cherla").json()
        self.assertEqual(res["status"], "success")
        self.assertTrue(len(res["data"]) > 0)
        top = res["data"][0]
        self.assertIn("Cherla", top["display_name"])
        self.assertIn("Bhadradri Kothagudem", top["display_name"])
        self.assertIn("Telangana", top["display_name"])

    def test_farm_location_independent_from_device_location(self):
        """
        Farm location must be saved independently and NEVER overwritten by GPS device location updates.
        """
        # 1. User sets Farm Location: Cherla, Bhadradri Kothagudem, Telangana
        farm_res = self.client.post("/api/location/farm", json={
            "farm_location": "Cherla, Bhadradri Kothagudem, Telangana",
            "farm_location_details": {
                "village": "Cherla",
                "district": "Bhadradri Kothagudem",
                "state": "Telangana"
            }
        }).json()
        self.assertEqual(farm_res["status"], "success")
        self.assertEqual(farm_res["farm_location"], "Cherla, Bhadradri Kothagudem, Telangana")

        # 2. User device GPS detects Guntur, Andhra Pradesh
        device_res = self.client.post("/api/location/device", json={
            "latitude": 16.3067,
            "longitude": 80.4365,
            "district": "Guntur",
            "state": "Andhra Pradesh"
        }).json()
        self.assertEqual(device_res["status"], "success")
        self.assertEqual(device_res["device_location"]["district"], "Guntur")
        # Farm location MUST remain Cherla!
        self.assertEqual(device_res["farm_location"], "Cherla, Bhadradri Kothagudem, Telangana")

        # Verify profile state
        prof = get_profile()
        self.assertEqual(prof.farm_location, "Cherla, Bhadradri Kothagudem, Telangana")
        self.assertEqual(prof.device_location.district, "Guntur")

    def test_location_routing_query_rules(self):
        """
        Test routing rules:
        - Explicit query location -> overrides all
        - 'here' / 'around me' -> device location (Guntur)
        - 'my farm' -> farm location (Cherla)
        """
        # Set farm in Cherla and device in Guntur
        self.client.post("/api/location/farm", json={"farm_location": "Cherla, Bhadradri Kothagudem, Telangana"})
        self.client.post("/api/location/device", json={
            "latitude": 16.3067, "longitude": 80.4365, "district": "Guntur", "state": "Andhra Pradesh"
        })

        # 1. Explicit location in query overrides all
        res1 = self.client.post("/api/chat", json={"message": "Weather in Warangal", "lang": "en"}).json()
        self.assertIn("Warangal", res1["reply"])

        # 2. 'here' routes to device location (Guntur)
        res2 = self.client.post("/api/chat", json={"message": "What is the weather here?", "lang": "en"}).json()
        self.assertIn("Guntur", res2["reply"])

        # 3. 'my farm' routes to farm location (Cherla)
        res3 = self.client.post("/api/chat", json={"message": "Weather at my farm", "lang": "en"}).json()
        self.assertIn("Cherla", res3["reply"])

    def test_nearby_markets_from_farm_vs_device(self):
        """Nearby markets should calculate road distance from farm or device coordinates."""
        # Farm in Cherla, Device in Guntur
        self.client.post("/api/location/farm", json={"farm_location": "Cherla, Bhadradri Kothagudem, Telangana"})
        self.client.post("/api/location/device", json={
            "latitude": 16.3067, "longitude": 80.4365, "district": "Guntur", "state": "Andhra Pradesh"
        })

        # Query near device ("markets near me")
        res_device = self.client.post("/api/chat", json={"message": "Which mandi is near me for chilli?", "lang": "en"}).json()
        self.assertEqual(res_device["tool_used"], "nearby_mandis")
        self.assertIn("Guntur Mirchi Yard", res_device["reply"])

        # Query near farm ("markets near my farm")
        res_farm = self.client.post("/api/chat", json={"message": "Which mandi is near my farm for chilli?", "lang": "en"}).json()
        self.assertEqual(res_farm["tool_used"], "nearby_mandis")
        self.assertIn("Khammam APMC", res_farm["reply"])

    # ==========================================================================
    # 2. Multi-turn Coreference Memory (Crop -> Yesterday -> 341 -> Highest)
    # ==========================================================================

    def test_multi_turn_coreference_memory_sequence(self):
        """
        Validates the exact sequence:
        Turn 1: 'Chilli' -> Active crop becomes Chilli
        Turn 2: 'What about yesterday?' -> Date becomes Yesterday, crop remains Chilli
        Turn 3: '341' -> Variety becomes 341, crop remains Chilli
        Turn 4: 'Where is it getting the highest price?' -> Targets Chilli 341 Yesterday highest market
        """
        conv_id = "test-coref-seq-1"

        # Turn 1: Chilli
        res1 = self.client.post("/api/chat", json={
            "message": "Chilli prices",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertIn("Chilli", res1["reply"])
        session = session_repo.get_or_create(conv_id)
        self.assertEqual(session.active_crop, "Chilli")

        # Turn 2: What about yesterday?
        res2 = self.client.post("/api/chat", json={
            "message": "What about yesterday?",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertIn("Chilli", res2["reply"])
        self.assertEqual(session.active_crop, "Chilli")
        self.assertEqual(session.active_date, "Yesterday")

        # Turn 3: 341
        res3 = self.client.post("/api/chat", json={
            "message": "341",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertIn("341", res3["reply"])
        self.assertEqual(session.active_crop, "Chilli")
        self.assertEqual(session.active_variety, "341")

        # Turn 4: Where is it getting the highest price?
        res4 = self.client.post("/api/chat", json={
            "message": "Where is it getting the highest price?",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertIn("341", res4["reply"])
        self.assertIn("Guntur Mirchi Yard", res4["reply"])
        self.assertIn("₹21,800", res4["reply"])

    # ==========================================================================
    # 3. Strict Variety Isolation & Non-Fabrication
    # ==========================================================================

    def test_strict_variety_isolation_341_teja(self):
        """341 queries must only return 341 benchmarks; Teja queries must only return Teja benchmarks."""
        res_341 = self.client.post("/api/chat", json={"message": "341 chilli price yesterday", "lang": "en"}).json()
        self.assertIn("341", res_341["reply"])
        self.assertIn("₹22,100", res_341["reply"])

        res_teja = self.client.post("/api/chat", json={"message": "Teja chilli price yesterday", "lang": "en"}).json()
        self.assertIn("Teja", res_teja["reply"])
        self.assertIn("₹22,500", res_teja["reply"])

    # ==========================================================================
    # 4. General Questions Answered Directly (No Forced Agriculture)
    # ==========================================================================

    def test_math_evaluation_direct_answer(self):
        """Math expressions must be calculated directly without agricultural boilerplate."""
        res = self.client.post("/api/chat", json={"message": "What is 25% of 800?", "lang": "en"}).json()
        self.assertEqual(res["tool_used"], "math_engine")
        self.assertIn("200", res["reply"])
        self.assertNotIn("chilli", res["reply"].lower())
        self.assertNotIn("mandi", res["reply"].lower())

    def test_science_explanation_direct_answer(self):
        """Science questions like photosynthesis must be answered directly."""
        res = self.client.post("/api/chat", json={"message": "What is photosynthesis?", "lang": "en"}).json()
        self.assertEqual(res["tool_used"], "conversational_assistant")
        self.assertIn("glucose", res["reply"].lower())
        self.assertIn("oxygen", res["reply"].lower())
        self.assertNotIn("mandi", res["reply"].lower())

    def test_geography_capital_direct_answer(self):
        """General geography queries must be answered directly."""
        res = self.client.post("/api/chat", json={"message": "What is the capital of France?", "lang": "en"}).json()
        self.assertEqual(res["tool_used"], "conversational_assistant")
        self.assertIn("Paris", res["reply"])
        self.assertNotIn("mandi", res["reply"].lower())

    def test_general_knowledge_sky_blue(self):
        """Science curiosity questions must explain Rayleigh scattering directly."""
        res = self.client.post("/api/chat", json={"message": "Why is the sky blue?", "lang": "en"}).json()
        self.assertEqual(res["tool_used"], "conversational_assistant")
        self.assertIn("Rayleigh", res["reply"])
        self.assertNotIn("fertilizer", res["reply"].lower())

    def test_writing_draft_direct_answer(self):
        """Drafting requests must create clean letter templates without forcing farming advice."""
        res = self.client.post("/api/chat", json={"message": "Write a leave letter", "lang": "en"}).json()
        self.assertEqual(res["tool_used"], "conversational_assistant")
        self.assertIn("Application for Leave", res["reply"])

    # ==========================================================================
    # 5. Language Detection (Telugu Default ONLY when Uncertain)
    # ==========================================================================

    def test_language_detection_clear_english(self):
        """Clear English query must be detected as 'en' and answered in English."""
        res = self.client.post("/api/chat", json={"message": "What is photosynthesis?"}).json()
        self.assertEqual(res["detected_language"], "en")
        self.assertIn("Photosynthesis", res["reply"])

    def test_language_detection_mixed_telugu_english(self):
        """Mixed Telugu-English farmer speech must be detected as 'te' and answered in Telugu."""
        res = self.client.post("/api/chat", json={"message": "ninnatiki eroju mirchi price entha?"}).json()
        self.assertEqual(res["detected_language"], "te")
        self.assertIn("ధర", res["reply"])

    def test_language_detection_mixed_hindi_english(self):
        """Mixed Hindi-English farmer speech must be detected as 'hi' and answered in Hindi."""
        res = self.client.post("/api/chat", json={"message": "aaj mirchi ka rate kitna hai?"}).json()
        self.assertEqual(res["detected_language"], "hi")
        self.assertIn("भाव", res["reply"])

    def test_language_detection_uncertain_defaults_to_telugu(self):
        """When language detection is ambiguous or uncertain, it must default to Telugu."""
        # Isolated number / symbols
        lang = AIAgent.detect_language("12345")
        self.assertEqual(lang, "te")

        lang2 = AIAgent.detect_language("???")
        self.assertEqual(lang2, "te")

        lang3 = AIAgent.detect_language("")
        self.assertEqual(lang3, "te")

    # ==========================================================================
    # 6. Unified Voice Assistant Constraints
    # ==========================================================================

    def test_voice_spoken_text_bounds(self):
        """Spoken text must be bounded (1-3 sentences), clean for TTS without markdown tables."""
        res = self.client.post("/api/chat", json={"message": "341 chilli price in Guntur", "lang": "en"}).json()
        spoken = res.get("spoken_text", "")
        self.assertTrue(len(spoken) > 0)
        self.assertNotIn("|", spoken)
        self.assertNotIn("###", spoken)
        sentences = [s for s in spoken.split(".") if s.strip()]
        self.assertTrue(1 <= len(sentences) <= 3)

    # ==========================================================================
    # 7. Saved Profile Crop Default Context, Turn Override, & Empty Profile
    # ==========================================================================

    def test_saved_profile_crop_as_default_context(self):
        """
        If farmer has selected a crop in Profile (Main Crop = Chilli, Variety = 341, Farm Location = Cherla),
        then asking 'Today price entha?' must naturally resolve to Chilli 341 for Today.
        """
        # Save profile
        self.client.post("/api/profile", json={
            "name": "Ramesh",
            "farm_location": "Cherla, Bhadradri Kothagudem, Telangana",
            "crops": ["Chilli"],
            "crop_variety": "341",
            "farm_size": "3 Acres"
        })

        res = self.client.post("/api/chat", json={
            "message": "Today price entha?",
            "conversation_id": "test-prof-crop-1"
        }).json()

        self.assertEqual(res["tool_used"], "market_variety_rates")
        self.assertEqual(res.get("context_applied", {}).get("crop"), "Chilli")
        self.assertEqual(res.get("context_applied", {}).get("variety"), "341")
        self.assertEqual(res.get("context_applied", {}).get("date"), "Today")
        self.assertIn("341", res["reply"])

    def test_turn_override_and_preservation_sequence(self):
        """
        Validates:
        Turn 1: 'Today price entha?' with Profile (Chilli, 341) -> Chilli 341 Today
        Turn 2: 'What is tomato price today?' -> Tomato explicitly overrides saved Chilli, variety resets
        Turn 3: 'What about yesterday?' -> Tomato preserved for Yesterday
        """
        conv_id = "test-override-seq"
        self.client.post("/api/profile", json={
            "name": "Ramesh",
            "farm_location": "Cherla, Bhadradri Kothagudem, Telangana",
            "crops": ["Chilli"],
            "crop_variety": "341",
            "farm_size": "3 Acres"
        })

        # Turn 1
        res1 = self.client.post("/api/chat", json={
            "message": "Today price entha?",
            "conversation_id": conv_id
        }).json()
        self.assertEqual(res1["tool_used"], "market_variety_rates")
        self.assertEqual(res1.get("context_applied", {}).get("crop"), "Chilli")
        self.assertEqual(res1.get("context_applied", {}).get("variety"), "341")
        self.assertEqual(res1.get("context_applied", {}).get("date"), "Today")

        # Turn 2: Tomato overrides Chilli
        res2 = self.client.post("/api/chat", json={
            "message": "What is tomato price today?",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertEqual(res2["tool_used"], "market_rates")
        self.assertEqual(res2.get("context_applied", {}).get("crop"), "Tomato")
        self.assertEqual(res2.get("context_applied", {}).get("variety"), "All")
        self.assertEqual(res2.get("context_applied", {}).get("date"), "Today")

        # Turn 3: What about yesterday? (preserves Tomato context)
        res3 = self.client.post("/api/chat", json={
            "message": "What about yesterday?",
            "conversation_id": conv_id,
            "lang": "en"
        }).json()
        self.assertEqual(res3["tool_used"], "market_rates")
        self.assertEqual(res3.get("context_applied", {}).get("crop"), "Tomato")
        self.assertEqual(res3.get("context_applied", {}).get("variety"), "All")
        self.assertEqual(res3.get("context_applied", {}).get("date"), "Yesterday")

    def test_empty_profile_asks_clarification(self):
        """
        New user with an empty Profile must NOT default to Tomato or Chilli.
        AI agent must ask for clarification on which crop to check.
        """
        self.client.post("/api/profile/reset")

        res = self.client.post("/api/chat", json={
            "message": "Today price entha?",
            "conversation_id": "test-empty-prof",
            "profile": {
                "name": "",
                "farm_location": "",
                "crops": [],
                "crop_variety": "",
                "farm_size": "",
                "completed": False
            }
        }).json()

        self.assertEqual(res["tool_used"], "clarification")
        self.assertIn("మీరు ఏ పంట ధర గురించి తెలుసుకోవాలనుకుంటున్నారు?", res["reply"])
        self.assertNotIn("Chilli", res.get("context_applied", {}).get("crop", ""))

    def test_greeting_automation_message_with_profile(self):
        """
        Chatbot automated greeting/welcome message must adapt to the user's profile:
        - Uses farmer's name (Ramesh)
        - Tailors to saved crop (Chilli / మిర్చి), variety (341), farm location (Cherla)
        - Suggested actions dynamically target Chilli (341) prices, farm weather, Chilli crop care
        - NEVER assumes Tomato or any fixed crop
        """
        self.client.post("/api/profile", json={
            "name": "Ramesh",
            "farm_location": "Cherla, Bhadradri Kothagudem, Telangana",
            "crops": ["Chilli"],
            "crop_variety": "341",
            "farm_size": "3 Acres"
        })

        # Test greeting in Telugu
        res_te = self.client.post("/api/chat", json={
            "message": "నమస్కారం",
            "conversation_id": "test-greeting-prof-te",
            "lang": "te"
        }).json()
        self.assertEqual(res_te["tool_used"], "welcome_bot")
        self.assertIn("Ramesh", res_te["reply"])
        self.assertIn("మిర్చి", res_te["reply"])
        self.assertIn("341", res_te["reply"])
        self.assertIn("Cherla", res_te["reply"])
        self.assertNotIn("టమోటా", res_te["reply"])
        self.assertTrue(any("మిర్చి" in act for act in res_te["suggested_actions"]))

        # Test greeting in English
        res_en = self.client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": "test-greeting-prof-en",
            "lang": "en"
        }).json()
        self.assertEqual(res_en["tool_used"], "welcome_bot")
        self.assertIn("Ramesh", res_en["reply"])
        self.assertIn("Chilli", res_en["reply"])
        self.assertIn("341", res_en["reply"])
        self.assertIn("Cherla", res_en["reply"])
        self.assertNotIn("Tomato", res_en["reply"])
        self.assertTrue(any("Chilli" in act for act in res_en["suggested_actions"]))

    def test_greeting_automation_message_with_empty_profile(self):
        """
        Chatbot automated greeting for an empty profile:
        - Clean neutral greeting
        - No hardcoded assumption of Tomato or Chilli
        - Useful general farming suggested actions
        """
        self.client.post("/api/profile/reset")

        res = self.client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": "test-greeting-empty",
            "profile": {
                "name": "",
                "farm_location": "",
                "crops": [],
                "crop_variety": "",
                "farm_size": "",
                "completed": False
            },
            "lang": "en"
        }).json()
        self.assertEqual(res["tool_used"], "welcome_bot")
        self.assertNotIn("Tomato", res["reply"])
        self.assertNotIn("Chilli", res["reply"])
        self.assertIn("KisanMitra", res["reply"])
        self.assertEqual(res["suggested_actions"], ["💰 Check Market Prices", "🌦️ Today's Weather", "🌱 Crop Health Advice"])

if __name__ == "__main__":
    unittest.main()


