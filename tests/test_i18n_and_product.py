"""
Comprehensive Tests for KisanMitra Product Redesign & Multilingual (i18n) Engine
Validates:
1. Neutral zero-prefilled profile initial state.
2. Authentic multilingual salutations (English, Telugu, Hindi) for blank and named profiles.
3. Multilingual AI Chat responses across all functional branches (Rates, Variety comparison,
   Zero fabrication notices, Highest price comparator, Agro-weather, Crop health).
4. APMC Market API variety isolation and canonical crop matching.
"""

import unittest
from fastapi.testclient import TestClient
from app import app, reset_profile, get_profile, FarmerProfile, update_profile

class TestI18nAndProductRedesign(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        reset_profile()

    def test_initial_neutral_profile_state(self):
        """Initial state must be completely uncompleted and contain NO pre-filled name."""
        profile = get_profile()
        self.assertFalse(profile.completed, "Profile should not be marked completed on fresh start")
        self.assertEqual(profile.name, "", "Farmer name must be blank initially, no fake identity like Ramesh Kumar")
        self.assertEqual(profile.location, "")
        self.assertEqual(profile.crops, [])
        self.assertEqual(profile.farm_size, "")

    def test_authentic_salutations_blank_and_named(self):
        """Test respectful salutations in English, Telugu, and Hindi."""
        # 1. Blank name salutations
        res_en = self.client.post("/api/chat", json={"message": "Hello KisanMitra", "lang": "en"}).json()
        self.assertIn("Farmer", res_en["reply"])

        res_te = self.client.post("/api/chat", json={"message": "నమస్కారం", "lang": "te"}).json()
        self.assertIn("రైతు గారు", res_te["reply"])

        res_hi = self.client.post("/api/chat", json={"message": "नमस्ते", "lang": "hi"}).json()
        self.assertIn("किसान भाई", res_hi["reply"])

        # 2. Named farmer salutations
        named_profile = FarmerProfile(
            name="వెంకటేశ్వర్లు",
            location="Guntur",
            crops=["Chilli"],
            farm_size="4 acres",
            completed=True
        )
        update_profile(named_profile)

        res_te_named = self.client.post("/api/chat", json={
            "message": "నమస్కారం",
            "lang": "te",
            "profile": named_profile.model_dump()
        }).json()
        self.assertIn("వెంకటేశ్వర్లు గారు", res_te_named["reply"])

        named_profile_hi = FarmerProfile(
            name="सुरेश कुमार",
            location="Guntur",
            crops=["Tomato"],
            farm_size="2 acres",
            completed=True
        )
        res_hi_named = self.client.post("/api/chat", json={
            "message": "नमस्ते",
            "lang": "hi",
            "profile": named_profile_hi.model_dump()
        }).json()
        self.assertIn("सुरेश कुमार जी", res_hi_named["reply"])

    def test_multilingual_mandi_rates_tomato(self):
        """Mandi price inquiries should return authentic localized text with live APMC benchmarks."""
        # English
        res_en = self.client.post("/api/chat", json={"message": "What is the tomato price today?", "lang": "en"}).json()
        self.assertEqual(res_en["tool_used"], "market_rates")
        self.assertIn("Live Mandi Rates", res_en["reply"])
        self.assertIn("Narasaraopet Yard", res_en["reply"])

        # Telugu
        res_te = self.client.post("/api/chat", json={"message": "ఈరోజు టమోటా ధర ఎంత?", "lang": "te"}).json()
        self.assertEqual(res_te["tool_used"], "market_rates")
        self.assertIn("మార్కెట్ యార్డ్ తాజా ధరలు", res_te["reply"])
        self.assertIn("టమోటా", res_te["reply"])
        self.assertIn("క్వింటాల్", res_te["reply"])

        # Hindi
        res_hi = self.client.post("/api/chat", json={"message": "आज टमाटर का भाव क्या है?", "lang": "hi"}).json()
        self.assertEqual(res_hi["tool_used"], "market_rates")
        self.assertIn("ताजा मंडी भाव", res_hi["reply"])
        self.assertIn("टमाटर", res_hi["reply"])
        self.assertIn("क्विंटल", res_hi["reply"])

    def test_multilingual_variety_comparison(self):
        """Comparing Chilli varieties should work and translate across all three languages."""
        # English
        res_en = self.client.post("/api/chat", json={"message": "Compare 341 and Teja", "lang": "en"}).json()
        self.assertEqual(res_en["tool_used"], "market_variety_comparison")
        self.assertIn("Variety Comparison: Chilli 341 vs. Chilli Teja", res_en["reply"])
        self.assertIn("Price Difference", res_en["reply"])

        # Telugu
        res_te = self.client.post("/api/chat", json={"message": "341 మరియు తేజ మిర్చి రకాలను పోల్చండి", "lang": "te"}).json()
        self.assertEqual(res_te["tool_used"], "market_variety_comparison")
        self.assertIn("మిర్చి రకాల పోలిక: 341 vs. Teja", res_te["reply"])
        self.assertIn("ధర వ్యత్యాసం", res_te["reply"])
        self.assertIn("మోడల్ బెంచ్‌మార్క్ ధర", res_te["reply"])

        # Hindi
        res_hi = self.client.post("/api/chat", json={"message": "341 और तेजा किस्मों की तुलना करें", "lang": "hi"}).json()
        self.assertEqual(res_hi["tool_used"], "market_variety_comparison")
        self.assertIn("मिर्च किस्मों की तुलना: 341 बनाम Teja", res_hi["reply"])
        self.assertIn("भाव का अंतर", res_hi["reply"])
        self.assertIn("मोडल बेंचमार्क भाव", res_hi["reply"])

    def test_multilingual_zero_fabrication_unsupported_variety(self):
        """Asking for an unsupported variety must return an explicit non-fabrication notice in the requested language."""
        # Telugu
        res_te = self.client.post("/api/chat", json={"message": "వండర్ హాట్ ధర ఎంత?", "lang": "te"}).json()
        self.assertEqual(res_te["tool_used"], "market_variety_rates")
        self.assertIn("Wonder Hot", res_te["reply"])

        # Test non-existent variety via direct query or API
        res_unavail_te = self.client.get("/api/market?crop=Chilli&variety=NonExistent&date=Yesterday")
        self.assertTrue(res_unavail_te.json()["variety_unavailable"])
        self.assertEqual(len(res_unavail_te.json()["data"]), 0)

    def test_multilingual_highest_price_comparator(self):
        """Highest price query must rank mandis descending and return in requested language."""
        p = FarmerProfile(name="Kiran", location="Guntur", crops=["Chilli"], farm_size="5 acres", completed=True)
        update_profile(p)

        # Telugu
        res_te = self.client.post("/api/chat", json={
            "message": "నా మిర్చి పంటకు అత్యధిక ధర ఎక్కడ వస్తుంది?",
            "lang": "te",
            "profile": p.model_dump()
        }).json()
        self.assertEqual(res_te["tool_used"], "market_comparator")
        self.assertIn("అత్యధిక ధర గల మార్కెట్", res_te["reply"])
        self.assertIn("Guntur", res_te["reply"])

        # Hindi
        res_hi = self.client.post("/api/chat", json={
            "message": "मेरी मिर्च की फसल का सबसे अधिक भाव कहां मिलेगा?",
            "lang": "hi",
            "profile": p.model_dump()
        }).json()
        self.assertEqual(res_hi["tool_used"], "market_comparator")
        self.assertIn("उच्चतम भाव देने वाली मंडी", res_hi["reply"])

    def test_multilingual_agro_weather_advisory(self):
        """Weather advisory query should give actionable agricultural guidance in target language."""
        # Telugu
        res_te = self.client.post("/api/chat", json={"message": "ఈరోజు మందులు పిచికారీ చేయవచ్చా?", "lang": "te"}).json()
        self.assertEqual(res_te["tool_used"], "agromet_weather")
        self.assertIn("వ్యవసాయ వాతావరణం", res_te["reply"])
        self.assertIn("పిచికారీ సూచన", res_te["reply"])

        # Hindi
        res_hi = self.client.post("/api/chat", json={"message": "क्या आज स्प्रे करना सुरक्षित है?", "lang": "hi"}).json()
        self.assertEqual(res_hi["tool_used"], "agromet_weather")
        self.assertIn("कृषि मौसम", res_hi["reply"])
        self.assertIn("छिड़काव परामर्श", res_hi["reply"])

    def test_multilingual_crop_health_doctor(self):
        """Crop doctor query should diagnose and advise in target language."""
        # Telugu
        res_te = self.client.post("/api/chat", json={"message": "మిర్చి ఆకులు ముడుచుకుపోతున్నాయి, పరిష్కారం చెప్పండి", "lang": "te"}).json()
        self.assertEqual(res_te["tool_used"], "crop_doctor")
        self.assertIn("పంట సంరక్షణ", res_te["reply"])
        self.assertIn("నివారణ", res_te["reply"])

        # Hindi
        res_hi = self.client.post("/api/chat", json={"message": "मिर्च के पत्ते मुड़ रहे हैं, उपाय बताएं", "lang": "hi"}).json()
        self.assertEqual(res_hi["tool_used"], "crop_doctor")
        self.assertIn("फसल प्रबंधन", res_hi["reply"])
        self.assertIn("रोकथाम", res_hi["reply"])

if __name__ == "__main__":
    unittest.main()
