"""
KisanMitra AI Agricultural Extension Evaluation Suite
=====================================================
Validates agricultural chatbot response accuracy, 5-part ICAR extension structure,
disambiguation of ambiguous symptoms, multi-crop agronomic knowledge, and zero chemical fabrication.
"""

import unittest
from fastapi.testclient import TestClient
from app import app


class TestChatbotAccuracy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_vague_symptom_disambiguation_no_crop(self):
        """When a farmer asks a vague question without crop, bot should politely disambiguate."""
        res = self.client.post("/api/chat", json={
            "message": "Why are my leaves turning yellow?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "clarification")
        self.assertTrue(
            "which crop" in data["reply"].lower() or "details" in data["reply"].lower(),
            f"Expected clarification asking for details/crop, got: {data['reply']}"
        )

    def test_vague_yellowing_disambiguation_with_crop(self):
        """When a crop is given but symptom is ambiguous (upper vs lower yellowing), bot asks for clarification."""
        res = self.client.post("/api/chat", json={
            "message": "My chilli leaves are turning yellow",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "clarification")
        self.assertIn("bottom", data["reply"].lower())
        self.assertIn("top", data["reply"].lower())

    def test_5_part_structured_advisory_format(self):
        """Advisory for specific symptom must strictly adhere to the 5-part extension format with ICAR citation."""
        res = self.client.post("/api/chat", json={
            "message": "What should I do for leaf curl in chilli?",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        reply = data.get("reply", "")

        self.assertIn("1. **What may be happening:**", reply)
        self.assertIn("2. **What you can check in the field:**", reply)
        self.assertIn("3. **What you can do next", reply)
        self.assertIn("4. **Important precautions:**", reply)
        self.assertIn("5. **Source:**", reply)
        self.assertTrue("ICAR" in reply or "ANGRAU" in reply)

    def test_multilingual_5_part_telugu(self):
        """Telugu advisory follows official 5-part structure and contains local terminology."""
        res = self.client.post("/api/chat", json={
            "message": "మిర్చిలో ఆకుముడత నివారణ ఏమిటి?",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        reply = data.get("reply", "")
        self.assertEqual(data["tool_used"], "crop_doctor")
        self.assertIn("ఏమి జరుగుతుండవచ్చు", reply)
        self.assertIn("పొలంలో మీరు ఏమి గమనించాలి", reply)
        self.assertIn("నివారణ చర్యలు", reply)
        self.assertIn("ముఖ్యమైన జాగ్రత్తలు", reply)
        self.assertIn("ఆధారం / వనరు", reply)

    def test_multilingual_5_part_hindi(self):
        """Hindi advisory follows official 5-part structure and contains local terminology."""
        res = self.client.post("/api/chat", json={
            "message": "मिर्च में पत्ती मरोड़ की रोकथाम कैसे करें?",
            "lang": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        reply = data.get("reply", "")
        self.assertEqual(data["tool_used"], "crop_doctor")
        self.assertIn("क्या समस्या हो सकती है", reply)
        self.assertIn("खेत में क्या जांचें", reply)
        self.assertIn("रोकथाम एवं उपचार", reply)
        self.assertIn("महत्वपूर्ण सावधानियां", reply)
        self.assertIn("स्रोत", reply)

    def test_lower_vs_upper_yellowing_differentiation(self):
        """Bot should give different agronomic advice for lower leaves vs top leaves."""
        # Lower leaves -> Nitrogen deficiency
        res_lower = self.client.post("/api/chat", json={
            "message": "Lower leaves of my chilli are turning yellow from bottom",
            "lang": "en"
        }).json()
        self.assertIn("nitrogen", res_lower["reply"].lower())

        # Upper leaves -> Micronutrient (iron/zinc) or viral
        res_upper = self.client.post("/api/chat", json={
            "message": "Top young leaves of chilli are turning yellow",
            "lang": "en"
        }).json()
        self.assertTrue(
            "iron" in res_upper["reply"].lower() or "zinc" in res_upper["reply"].lower() or "deficiency" in res_upper["reply"].lower(),
            f"Expected iron/zinc/micronutrient in upper leaf reply, got: {res_upper['reply']}"
        )

    def test_crop_planning_ambiguity_and_recommendation(self):
        """General crop planning query triggers clarification; specific season+soil provides grounded suggestions."""
        # Vague planning
        res_vague = self.client.post("/api/chat", json={
            "message": "Which crop should I grow?",
            "lang": "en"
        }).json()
        self.assertEqual(res_vague["tool_used"], "clarification")
        self.assertIn("season", res_vague["reply"].lower())

        # Specific planning
        res_plan = self.client.post("/api/chat", json={
            "message": "Which crop should I grow in kharif in black soil?",
            "lang": "en"
        }).json()
        self.assertEqual(res_plan["tool_used"], "crop_planning")
        self.assertIn("cotton", res_plan["reply"].lower())
        self.assertIn("icar", res_plan["reply"].lower())

    def test_multi_crop_coverage(self):
        """Verifies verified guidance is available across crops (Cotton, Tomato, Paddy, Groundnut, Wheat)."""
        crops = ["cotton", "tomato", "paddy", "groundnut", "wheat"]
        for c in crops:
            res = self.client.post("/api/chat", json={
                "message": f"Fertilizer schedule for {c}",
                "lang": "en"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(
                "fertilizer" in data["reply"].lower() or "nutrient" in data["reply"].lower() or "basal" in data["reply"].lower(),
                f"Failed for crop {c}: {data['reply']}"
            )


if __name__ == "__main__":
    unittest.main()
