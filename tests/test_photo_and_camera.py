"""
Automated Unit and Integration Tests for KisanMitra Camera & Crop Photo Diagnostic Engine.
Tests:
- Photo diagnosis across different crops (Chilli, Tomato, Cotton, Paddy)
- Actionable chemical and organic treatment plans
- Spoken text generation across English, Telugu, and Hindi
- Formatting cleanliness (no markdown artifacts in audio summaries)
- Image payload validation and context application
"""

import unittest
from fastapi.testclient import TestClient
from app import app

# Minimal 1x1 dummy PNG in base64
DUMMY_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

class TestPhotoAndCamera(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_photo_diagnosis_chilli_en(self):
        """Test crop photo diagnosis for Chilli in English."""
        res = self.client.post("/api/chat", json={
            "message": "Analyze this chilli leaf photo",
            "image": DUMMY_IMAGE,
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "vision_diagnosis")
        self.assertIn("Thrips Infestation", data["reply"])
        self.assertIn("Fipronil", data["reply"])
        self.assertIn("Neem Oil", data["reply"])
        # Check spoken audio summary
        spoken = data.get("spoken_text", "")
        self.assertTrue(len(spoken) > 10)
        self.assertIn("Chilli", spoken)
        self.assertNotIn("###", spoken)
        self.assertNotIn("|", spoken)

    def test_photo_diagnosis_tomato_te(self):
        """Test crop photo diagnosis for Tomato in Telugu."""
        res = self.client.post("/api/chat", json={
            "message": "ఈ టమోటా ఆకు ఫోటోను విశ్లేషించండి",
            "image": DUMMY_IMAGE,
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "vision_diagnosis")
        self.assertIn("టమోటా", data["reply"])
        self.assertIn("మాంకోజెబ్", data["reply"])
        spoken = data.get("spoken_text", "")
        self.assertIn("టమోటా", spoken)
        self.assertIn("మాంకోజెబ్", spoken)

    def test_photo_diagnosis_cotton_hi(self):
        """Test crop photo diagnosis for Cotton in Hindi."""
        res = self.client.post("/api/chat", json={
            "message": "कपास के पत्तों की फोटो जांच करें",
            "image": DUMMY_IMAGE,
            "lang": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "vision_diagnosis")
        self.assertIn("कपास", data["reply"])
        self.assertIn("रस चूसक कीट", data["reply"])
        spoken = data.get("spoken_text", "")
        self.assertIn("कपास", spoken)

    def test_photo_diagnosis_paddy_en(self):
        """Test crop photo diagnosis for Paddy in English."""
        res = self.client.post("/api/chat", json={
            "message": "Paddy crop disease photo",
            "image": DUMMY_IMAGE,
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "vision_diagnosis")
        self.assertIn("Blast", data["reply"])
        self.assertIn("Tricyclazole", data["reply"])
        spoken = data.get("spoken_text", "")
        self.assertIn("Paddy", spoken)

    def test_photo_without_text_defaults_to_diagnosis(self):
        """Test uploading a photo with empty text query."""
        res = self.client.post("/api/chat", json={
            "message": "",
            "image": DUMMY_IMAGE,
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "vision_diagnosis")
        self.assertTrue(len(data["reply"]) > 50)
        self.assertTrue(len(data["spoken_text"]) > 20)

    def test_photo_diagnosis_action_chips(self):
        """Test suggested action chips returned with photo diagnosis."""
        res = self.client.post("/api/chat", json={
            "message": "Check my plant photo",
            "image": DUMMY_IMAGE,
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        actions = data.get("suggested_actions", [])
        self.assertTrue(len(actions) >= 2)

if __name__ == "__main__":
    unittest.main()
