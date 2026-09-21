"""
Comprehensive Production-Grade Tests for KisanMitra:
=====================================================
1. Exact User Location Resolution & Haversine Nearby Mandis
2. Profile-Controlled Personalization ("What should I do today?")
3. Contextual Multi-turn Coreference & Topic Tracking
4. Automatic Multilingual & Transliterated Language Detection
5. Speech Normalization & Agricultural Phonetic Correction
6. Unified Voice Assistant Constraints (1-3 sentences spoken, full visual on screen)
"""

import unittest
from starlette.testclient import TestClient
from app import app, reset_profile, FarmerProfile, LocationContext
from ai_agent import AIAgent, session_repo, AgriculturalTools

class TestProductionGradeAI(unittest.TestCase):
    def setUp(self):
        reset_profile()
        session_repo.sessions.clear()
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Exact User Location Resolution & Haversine Nearest Mandis
    # --------------------------------------------------------------------------

    def test_location_resolve_guntur(self):
        """Coordinates around Guntur Mirchi Yard should resolve to Guntur and Guntur Mirchi Yard."""
        res = self.client.post("/api/location/resolve", json={
            "latitude": 16.3067,
            "longitude": 80.4365,
            "accuracy": 15
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["district"], "Guntur")
        self.assertEqual(data["state"], "Andhra Pradesh")
        self.assertEqual(data["nearest_market"], "Guntur Mirchi Yard")
        self.assertLess(data["nearest_distance_km"], 5.0)

    def test_location_resolve_warangal(self):
        """Coordinates around Warangal Mandi should resolve to Warangal."""
        res = self.client.post("/api/location/resolve", json={
            "latitude": 17.9689,
            "longitude": 79.5941,
            "accuracy": 10
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["district"], "Warangal")
        self.assertEqual(data["state"], "Telangana")
        self.assertEqual(data["nearest_market"], "Warangal Mandi")
        self.assertLess(data["nearest_distance_km"], 5.0)

    def test_nearby_markets_api(self):
        """GET /api/market/nearby should list mandis ordered by distance."""
        res = self.client.get("/api/market/nearby?latitude=16.3067&longitude=80.4365&crop=Chilli&max_km=200")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("mandis", data)
        self.assertTrue(len(data["mandis"]) > 0)
        # Verify ordering by distance
        distances = [m["distance_km"] for m in data["mandis"]]
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(data["mandis"][0]["market"], "Guntur Mirchi Yard")

    # --------------------------------------------------------------------------
    # 2. Profile-Controlled Personalization ("What should I do today?")
    # --------------------------------------------------------------------------

    def test_personalized_guidance_with_full_profile(self):
        """If profile has Chilli 341 at Flowering in Guntur with Drip, answer must tailor specifically."""
        profile_data = {
            "name": "Jyothsna",
            "location": "Guntur",
            "crops": ["Chilli"],
            "crop_varieties": ["341"],
            "growth_stage": "Flowering",
            "irrigation_type": "Drip Irrigation",
            "soil_type": "Black Cotton",
            "farm_size": "4 Acres"
        }
        res = self.client.post("/api/chat", json={
            "message": "What should I do today?",
            "profile": profile_data
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "personalized_guidance")
        reply = data["reply"]
        # Verify key personalized advice points
        self.assertIn("Chilli (341)", reply)
        self.assertIn("Flowering", reply)
        self.assertTrue("Thrips" in reply or "thrips" in reply.lower())
        self.assertTrue("13-0-45" in reply or "Potassium Nitrate" in reply)
        # Voice spoken text is concise (1-3 sentences)
        self.assertTrue(len(data["spoken_text"].split(".")) <= 4)
        self.assertIn("341", data["spoken_text"])

    def test_personalized_guidance_in_telugu(self):
        """Telugu query 'ఈరోజు ఏమి చేయాలి' with Chilli 341 flowering profile."""
        profile_data = {
            "name": "రైతు",
            "location": "గుంటూరు",
            "crops": ["Chilli"],
            "crop_varieties": ["341"],
            "growth_stage": "పూత దశ",
            "irrigation_type": "డ్రిప్"
        }
        res = self.client.post("/api/chat", json={
            "message": "ఈరోజు ఏమి చేయాలి?",
            "profile": profile_data,
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["detected_language"], "te")
        self.assertIn("341", data["reply"])
        self.assertTrue("పూత" in data["reply"] or "తామర" in data["reply"])

    def test_guidance_missing_profile_requests_details(self):
        """If profile has no crops, politely and specifically asks for crop & stage."""
        res = self.client.post("/api/chat", json={
            "message": "What should I do today?",
            "profile": None
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("crop", data["reply"].lower())
        self.assertIn("growth stage", data["reply"].lower())

    # --------------------------------------------------------------------------
    # 3. Contextual Multi-Turn Coreference Resolution
    # --------------------------------------------------------------------------

    def test_multi_turn_coreference_flow(self):
        """
        Turn 1: 'Chilli prices in Guntur'
        Turn 2: 'And yesterday?'
        Turn 3: 'What about 341?'
        Turn 4: 'Where was it getting the highest price?'
        """
        conv_id = "test_coref_conv_42"

        # Turn 1
        t1 = self.client.post("/api/chat", json={
            "message": "Chilli prices in Guntur",
            "conversation_id": conv_id
        }).json()
        self.assertIn("Guntur", t1["reply"])
        self.assertIn("Chilli", t1["reply"])

        # Turn 2
        t2 = self.client.post("/api/chat", json={
            "message": "And yesterday?",
            "conversation_id": conv_id
        }).json()
        self.assertIn("Yesterday", t2["reply"])
        self.assertIn("Chilli", t2["reply"])

        # Turn 3
        t3 = self.client.post("/api/chat", json={
            "message": "What about 341?",
            "conversation_id": conv_id
        }).json()
        self.assertIn("341", t3["reply"])

        # Turn 4
        t4 = self.client.post("/api/chat", json={
            "message": "Where was it getting the highest price?",
            "conversation_id": conv_id
        }).json()
        self.assertEqual(t4["tool_used"], "market_variety_rates")
        self.assertIn("341", t4["reply"])
        self.assertIn("Guntur Mirchi Yard", t4["reply"])

    # --------------------------------------------------------------------------
    # 4. Automatic Language Detection (Telugu, Hindi, English, Transliterated)
    # --------------------------------------------------------------------------

    def test_language_detection_native_telugu(self):
        res = self.client.post("/api/chat", json={"message": "ఈరోజు మిర్చి ధర ఎంత?"})
        self.assertEqual(res.json()["detected_language"], "te")

    def test_language_detection_native_hindi(self):
        res = self.client.post("/api/chat", json={"message": "आज मिर्च का भाव क्या है?"})
        self.assertEqual(res.json()["detected_language"], "hi")

    def test_language_detection_transliterated_telugu(self):
        """Transliterated Tenglish speech: 'Today mirchi 341 price entha?'"""
        res = self.client.post("/api/chat", json={"message": "Today mirchi 341 price entha?"})
        self.assertEqual(res.json()["detected_language"], "te")

    def test_language_detection_transliterated_hindi(self):
        """Transliterated Hinglish speech: 'aaj tamatar ka bhav kya hai?'"""
        res = self.client.post("/api/chat", json={"message": "aaj tamatar ka bhav kya hai?"})
        self.assertEqual(res.json()["detected_language"], "hi")

    def test_language_detection_english(self):
        res = self.client.post("/api/chat", json={"message": "What is the tomato price today?"})
        self.assertEqual(res.json()["detected_language"], "en")

    # --------------------------------------------------------------------------
    # 5. Speech Normalization & Phonetic Correction
    # --------------------------------------------------------------------------

    def test_speech_normalization(self):
        """Ensure ASR numbers like 'three forty one' and phonetics 'trips' are normalized."""
        norm1 = AIAgent.normalize_agricultural_speech("Today three forty one price in guntur")
        self.assertIn("341", norm1)

        norm2 = AIAgent.normalize_agricultural_speech("trips medicine for chilli")
        self.assertIn("thrips", norm2)

        norm3 = AIAgent.normalize_agricultural_speech("theja mirchi rate")
        self.assertIn("teja", norm3)

    # --------------------------------------------------------------------------
    # 6. Unified Voice Assistant Constraints
    # --------------------------------------------------------------------------

    def test_spoken_text_conciseness(self):
        """Voice spoken text must be strictly 1-3 short sentences while reply has full details."""
        res = self.client.post("/api/chat", json={
            "message": "Chilli prices in Guntur"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data["spoken_text"]
        self.assertTrue(len(spoken) > 0)
        # Count sentences
        sentence_count = len([s for s in spoken.replace("!", ".").replace("?", ".").split(".") if s.strip()])
        self.assertLessEqual(sentence_count, 3)
        # Visual reply has full markdown
        self.assertTrue(len(data["reply"]) > len(spoken))

if __name__ == "__main__":
    unittest.main()
