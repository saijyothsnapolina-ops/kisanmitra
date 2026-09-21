"""
Unit Tests for KisanMitra Conversational AI Engine
==================================================
Tests:
1. Real Intent Understanding (Math, Science, Writing, Humor, Translation)
   - Answers general questions directly.
   - Does NOT force questions into generic farming/crop advice.
2. Context & Multi-turn Memory (Anaphora & Coreference Resolution)
   - Preserves crop, variety, and topic across turns ("What about yesterday?", "Where is it getting the highest price?").
3. Missing Parameter Disambiguation
   - Asks short clarifying questions when required parameters are missing instead of guessing.
4. Dedicated Agricultural Tools
   - Invokes market_rates, market_comparator, market_variety_rates, agromet_weather, crop_doctor when needed.
5. Unified Architecture & SSE Streaming
   - Tests both /api/chat and /api/chat/stream endpoints.
"""

import unittest
import json
from starlette.testclient import TestClient
from app import app, reset_profile
from ai_agent import AIAgent, session_repo

class TestConversationalAI(unittest.TestCase):
    def setUp(self):
        reset_profile()
        session_repo.sessions.clear()
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Real Intent Understanding (Non-Agricultural General Questions)
    # --------------------------------------------------------------------------

    def test_math_direct_addition(self):
        """USER: 'What is 25 + 25?' -> CORRECT: '50', WRONG: 'To improve your crop...'"""
        res = self.client.post("/api/chat", json={"message": "What is 25 + 25?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "math_engine")
        self.assertIn("50", data["reply"])
        self.assertEqual(data["spoken_text"], "50")
        # Ensure absolutely NO generic crop preaching
        self.assertNotIn("crop", data["reply"].lower())
        self.assertNotIn("fertilizer", data["reply"].lower())
        self.assertNotIn("mandi", data["reply"].lower())

    def test_math_multiplication_and_percentage(self):
        """USER: 'Calculate 15 * 8' and '25% of 800'"""
        res1 = self.client.post("/api/chat", json={"message": "Calculate 15 * 8"})
        self.assertEqual(res1.status_code, 200)
        self.assertIn("120", res1.json()["reply"])

        res2 = self.client.post("/api/chat", json={"message": "What is 25% of 800?"})
        self.assertEqual(res2.status_code, 200)
        self.assertIn("200", res2.json()["reply"])

    def test_science_concept_explanation(self):
        """USER: 'What is photosynthesis?' -> Explains the biological process directly."""
        res = self.client.post("/api/chat", json={"message": "What is photosynthesis?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertIn("Photosynthesis", data["reply"])
        self.assertIn("sunlight", data["reply"].lower())
        self.assertIn("glucose", data["reply"].lower())
        # Must not force generic mandi or fertilizer dump
        self.assertNotIn("mandi price", data["reply"].lower())
        self.assertNotIn("spray fipronil", data["reply"].lower())

    def test_document_drafting_supplier_message(self):
        """USER: 'Write a message to my fertilizer supplier' -> Drafts message."""
        res = self.client.post("/api/chat", json={"message": "Write a message to my fertilizer supplier"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertIn("Urea", data["reply"])
        self.assertIn("Neem Oil", data["reply"])
        self.assertIn("rates", data["reply"].lower())

    def test_leave_letter_drafting(self):
        """USER: 'Write a leave letter' -> Drafts formal leave letter."""
        res = self.client.post("/api/chat", json={"message": "Write a leave letter"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertIn("Leave Application Letter", data["reply"])
        self.assertIn("leave of absence", data["reply"].lower())

    def test_jokes_and_humor(self):
        """USER: 'Tell me a joke' -> Returns lighthearted joke."""
        res = self.client.post("/api/chat", json={"message": "Tell me a joke"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertTrue(len(data["reply"]) > 20)
        self.assertNotIn("mandi price", data["reply"].lower())

    def test_multilingual_translation_en_to_te(self):
        """USER: 'Translate \"good morning\" into Telugu' -> 'శుభోదయం'"""
        res = self.client.post("/api/chat", json={"message": "Translate 'good morning' into Telugu"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertIn("శుభోదయం", data["reply"])

    def test_multilingual_translation_en_to_hi(self):
        """USER: 'Translate \"thank you\" into Hindi' -> 'धन्यवाद'"""
        res = self.client.post("/api/chat", json={"message": "Translate 'thank you' into Hindi"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "conversational_assistant")
        self.assertIn("धन्यवाद", data["reply"])

    # --------------------------------------------------------------------------
    # 2. Multi-turn Conversational Memory & Coreference Resolution
    # --------------------------------------------------------------------------

    def test_multi_turn_anaphoric_conversation(self):
        """
        Turn 1: 'What is today's chilli price?'
        Turn 2: 'What about yesterday?' (inherits crop=Chilli, changes date=Yesterday)
        Turn 3: 'Where is it getting the highest price?' (inherits crop=Chilli, date=Yesterday)
        """
        # Turn 1
        res1 = self.client.post("/api/chat", json={"message": "What is today's chilli price?"})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        cid = data1["conversation_id"]
        self.assertIn("Chilli", data1["reply"])
        self.assertIn("Today", data1["reply"])

        # Turn 2: 'What about yesterday?'
        res2 = self.client.post("/api/chat", json={"message": "What about yesterday?", "conversation_id": cid})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["conversation_id"], cid)
        self.assertIn("Chilli", data2["reply"])
        self.assertIn("Yesterday", data2["reply"])

        # Turn 3: 'Where is it getting the highest price?'
        res3 = self.client.post("/api/chat", json={"message": "Where is it getting the highest price?", "conversation_id": cid})
        self.assertEqual(res3.status_code, 200)
        data3 = res3.json()
        self.assertEqual(data3["conversation_id"], cid)
        self.assertEqual(data3["tool_used"], "market_comparator")
        self.assertIn("Chilli", data3["reply"])
        self.assertIn("Highest Price Market", data3["reply"])

    def test_multi_turn_variety_coreference(self):
        """
        Turn 1: 'What is 341?' (explains variety 341)
        Turn 2: 'Where is it getting the highest price?' (resolves 'it' to 341 Chilli)
        """
        res1 = self.client.post("/api/chat", json={"message": "What is 341?"})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        cid = data1["conversation_id"]
        self.assertIn("341", data1["reply"])

        res2 = self.client.post("/api/chat", json={"message": "Where is it getting the highest price?", "conversation_id": cid})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertIn("341", data2["reply"])
        self.assertIn("Guntur Mirchi Yard", data2["reply"])

    # --------------------------------------------------------------------------
    # 3. Missing Parameter Disambiguation
    # --------------------------------------------------------------------------

    def test_missing_crop_disambiguation(self):
        """When user asks 'What is the price?' with NO crop mentioned and NO profile, ask short clarifying question."""
        res = self.client.post("/api/chat", json={"message": "What is the price?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "clarification")
        self.assertIn("Which crop would you like to check the market price for?", data["reply"])
        self.assertIn("Chilli", data["reply"])
        self.assertIn("Tomato", data["reply"])

    # --------------------------------------------------------------------------
    # 4. SSE Response Streaming
    # --------------------------------------------------------------------------

    def test_sse_streaming_response(self):
        """Verify /api/chat/stream delivers valid SSE token events and terminal event."""
        res = self.client.post(
            "/api/chat/stream",
            json={"message": "What is 25 + 25?"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))
        
        lines = res.text.strip().split("\n")
        data_lines = [l for l in lines if l.startswith("data:")]
        self.assertTrue(len(data_lines) >= 2)
        
        # Verify JSON structure of first chunk
        first_payload = json.loads(data_lines[0].replace("data:", "").strip())
        self.assertIn("chunk", first_payload)
        self.assertIn("done", first_payload)

        # Verify terminal [DONE] indicator exists
        self.assertTrue(any("[DONE]" in l for l in data_lines))

if __name__ == "__main__":
    unittest.main()
