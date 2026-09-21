"""
Unit and Integration Tests for KisanMitra Advanced Multilingual Voice Assistant.
Tests:
- Spoken response (spoken_text) generation across all intent branches
- Mixed-language speech query parsing (Telugu + English, Hindi + English)
- Chilli variety ambiguity detection and prompt
- Spoken text cleanliness (no markdown formatting, concise summaries)
- Multilingual fidelity (Telugu, Hindi, English)
"""

import unittest
from fastapi.testclient import TestClient
from app import app

class TestVoiceAndAssistant(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_spoken_text_market_rates_en(self):
        """Test concise spoken_text for standard market rates in English."""
        res = self.client.post("/api/chat", json={
            "message": "What is the tomato price today?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("spoken_text", data)
        spoken = data["spoken_text"]
        self.assertTrue(len(spoken) > 10)
        self.assertIn("Tomato", spoken)
        self.assertIn("quintal", spoken)
        # Verify no markdown table artifacts in speech
        self.assertNotIn("|", spoken)
        self.assertNotIn("###", spoken)

    def test_spoken_text_market_rates_te(self):
        """Test Telugu spoken_text for market rates."""
        res = self.client.post("/api/chat", json={
            "message": "ఈరోజు టమోటా ధర ఎంత?",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("spoken_text", data)
        spoken = data["spoken_text"]
        self.assertIn("టమోటా", spoken)
        self.assertIn("క్వింటాల్", spoken)
        self.assertNotIn("|", spoken)

    def test_spoken_text_market_rates_hi(self):
        """Test Hindi spoken_text for market rates."""
        res = self.client.post("/api/chat", json={
            "message": "आज टमाटर का भाव क्या है?",
            "lang": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("spoken_text", data)
        spoken = data["spoken_text"]
        self.assertIn("टमाटर", spoken)
        self.assertIn("क्विंटल", spoken)
        self.assertNotIn("|", spoken)

    def test_mixed_language_te_en_chilli_341(self):
        """Test natural mixed Telugu-English voice query: 'Today mirchi 341 price entha?'"""
        res = self.client.post("/api/chat", json={
            "message": "Today mirchi 341 price entha?",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("341", spoken)
        self.assertIn("మిర్చి", spoken)
        self.assertNotIn("|", spoken)

    def test_mixed_language_tomato_price_entha(self):
        """Test mixed language query: 'Tomato price today entha?'"""
        res = self.client.post("/api/chat", json={
            "message": "Tomato price today entha?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("Tomato", spoken)
        self.assertTrue(len(spoken) > 0)

    def test_mixed_language_highest_mandi_comparator(self):
        """Test mixed query: 'Where is mirchi rate highest?'"""
        res = self.client.post("/api/chat", json={
            "message": "Where is mirchi rate highest?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("highest", spoken.lower())
        self.assertNotIn("|", spoken)

    def test_mixed_language_aaj_mirchi_rate_kitna(self):
        """Test Hindi mixed query: 'Aaj mirchi ka rate kitna hai?'"""
        res = self.client.post("/api/chat", json={
            "message": "Aaj mirchi ka rate kitna hai?",
            "lang": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertTrue(len(spoken) > 0)
        self.assertIn("मिर्च", spoken)

    def test_chilli_variety_ambiguity_detection(self):
        """When user asks for chilli price without variety, prompt to clarify (341 or Teja)."""
        res = self.client.post("/api/chat", json={
            "message": "What is the chilli price today?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        # Ambiguity check in speech
        self.assertIn("Did you mean 341 chilli or Teja chilli?", spoken)
        # Ambiguity note in visual reply
        self.assertIn("Did you mean 341 chilli or Teja", data["reply"])

    def test_chilli_variety_ambiguity_te(self):
        """Ambiguity clarification in Telugu when variety is unspecified."""
        res = self.client.post("/api/chat", json={
            "message": "ఈరోజు మిర్చి ధర ఎంత?",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("మీరు 341 మిర్చినా లేక తేజా మిర్చినా?", spoken)

    def test_chilli_variety_comparison_spoken(self):
        """Test spoken response when comparing chilli varieties."""
        res = self.client.post("/api/chat", json={
            "message": "Compare 341 and Teja chilli",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertTrue("spread of" in spoken or "Chilli" in spoken)
        self.assertNotIn("|", spoken)
        self.assertNotIn("###", spoken)

    def test_weather_spoken_summary(self):
        """Test spoken summary for weather / spray advisory."""
        res = self.client.post("/api/chat", json={
            "message": "What is the weather and spray advisory for my farm?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("conditions are", spoken)
        self.assertNotIn("|", spoken)

    def test_crop_doctor_spoken_summary(self):
        """Test spoken summary for crop remedies."""
        res = self.client.post("/api/chat", json={
            "message": "What spray should I use for leaf curl in chilli?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("neem oil", spoken.lower())
        self.assertNotIn("|", spoken)

    def test_photo_diagnosis_spoken_summary(self):
        """Test spoken summary for photo diagnosis."""
        res = self.client.post("/api/chat", json={
            "message": "Analyze this crop photo",
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("diagnosis complete", spoken.lower())

    def test_greeting_assistant_spoken(self):
        """Test spoken response for general greeting."""
        res = self.client.post("/api/chat", json={
            "message": "Hello KisanMitra",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        spoken = data.get("spoken_text", "")
        self.assertIn("KisanMitra", spoken)

if __name__ == "__main__":
    unittest.main()
