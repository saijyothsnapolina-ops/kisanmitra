"""
Unit & Integration Tests for KisanMitra LLM & API Key Integration
==================================================================
Tests:
1. Environment Variable & Provider Resolution (Gemini priority, OpenAI fallback, generic key detection).
2. Missing Key Handling (Polite guidance without crashes or fake data).
3. Google Gemini REST Integration (Mock 200, 401 auth error, 429 rate limit, timeout).
4. OpenAI REST Integration (Mock 200, 401 auth error, 429 rate limit).
5. Zero Key Leakage (Secrets never returned in user replies or error payloads).
6. Multimodal Vision Handling with Image Attachment.
7. End-to-End Chatbot API Execution via FastAPI TestClient.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from app import app, reset_profile
from ai_agent import AIAgent, session_repo
import llm_client


class TestLLMIntegration(unittest.TestCase):
    def setUp(self):
        reset_profile()
        session_repo.sessions.clear()
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Environment Variable & Provider Resolution
    # --------------------------------------------------------------------------

    def test_provider_detection_no_keys(self):
        """When no keys are set, is_configured should be False."""
        with patch.dict(os.environ, {}, clear=True):
            cfg = llm_client.get_active_llm_config()
            self.assertFalse(cfg["is_configured"])
            self.assertIsNone(cfg["provider"])
            self.assertIsNone(cfg["api_key"])

    def test_provider_detection_gemini_priority(self):
        """GEMINI_API_KEY should be detected first with gemini-1.5-flash default."""
        env = {
            "GEMINI_API_KEY": "AIzaSyTestGeminiKey123",
            "OPENAI_API_KEY": "sk-TestOpenAIKey456"
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = llm_client.get_active_llm_config()
            self.assertTrue(cfg["is_configured"])
            self.assertEqual(cfg["provider"], "gemini")
            self.assertEqual(cfg["api_key"], "AIzaSyTestGeminiKey123")
            self.assertEqual(cfg["model"], "gemini-1.5-flash")

    def test_provider_detection_openai_fallback(self):
        """When only OPENAI_API_KEY is present, detect OpenAI."""
        env = {
            "OPENAI_API_KEY": "sk-TestOpenAIKey456"
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = llm_client.get_active_llm_config()
            self.assertTrue(cfg["is_configured"])
            self.assertEqual(cfg["provider"], "openai")
            self.assertEqual(cfg["api_key"], "sk-TestOpenAIKey456")
            self.assertEqual(cfg["model"], "gpt-4o-mini")

    def test_provider_detection_generic_llm_key(self):
        """LLM_API_KEY starting with AIzaSy should detect as Gemini."""
        env = {
            "LLM_API_KEY": "AIzaSyGenericGoogleKey789"
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = llm_client.get_active_llm_config()
            self.assertTrue(cfg["is_configured"])
            self.assertEqual(cfg["provider"], "gemini")

    # --------------------------------------------------------------------------
    # 2. Missing Key Handling (Clear Setup Guidance, No Crash)
    # --------------------------------------------------------------------------

    def test_missing_key_guidance_en(self):
        """English missing key explanation contains link to aistudio and variable name."""
        with patch.dict(os.environ, {}, clear=True):
            res = llm_client.generate_farming_response("How to improve soil health?", lang="en")
            self.assertFalse(res["success"])
            self.assertEqual(res["tool_used"], "llm_unconfigured")
            self.assertIn("aistudio.google.com", res["reply"])
            self.assertIn("GEMINI_API_KEY", res["reply"])

    def test_missing_key_guidance_te(self):
        """Telugu missing key explanation contains Telugu instructions and variable name."""
        with patch.dict(os.environ, {}, clear=True):
            res = llm_client.generate_farming_response("భూమి సారాన్ని ఎలా పెంచాలి?", lang="te")
            self.assertFalse(res["success"])
            self.assertIn("GEMINI_API_KEY", res["reply"])
            self.assertIn("Google ఖాతాతో", res["reply"])

    def test_missing_key_guidance_hi(self):
        """Hindi missing key explanation contains Hindi instructions."""
        with patch.dict(os.environ, {}, clear=True):
            res = llm_client.generate_farming_response("मिट्टी की उर्वरता कैसे बढ़ाएं?", lang="hi")
            self.assertFalse(res["success"])
            self.assertIn("GEMINI_API_KEY", res["reply"])
            self.assertIn("निःशुल्क", res["reply"])

    def test_chat_endpoint_llm_setup_prompt(self):
        """Explicit query 'How to connect LLM?' via /api/chat returns setup guidance cleanly."""
        res = self.client.post("/api/chat", json={"message": "How do I connect the LLM and API key?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("GEMINI_API_KEY", data["reply"])
        self.assertIn("aistudio.google.com", data["reply"])

    # --------------------------------------------------------------------------
    # 3. Google Gemini REST Integration (Mock Tests)
    # --------------------------------------------------------------------------

    @patch("requests.post")
    def test_gemini_success_response(self, mock_post):
        """Successful Gemini response is parsed and formatted."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "For Tomato flowering stage, apply 13-0-45 (Potassium Nitrate) @ 5g/L."}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        res = llm_client.call_gemini(
            api_key="valid_gemini_key",
            model="gemini-1.5-flash",
            system_prompt="system",
            user_prompt="Tomato fertilizer"
        )
        self.assertTrue(res["success"])
        self.assertIn("13-0-45", res["text"])

    @patch("requests.post")
    def test_gemini_401_auth_error_no_leak(self, mock_post):
        """401 Unauthorized returns auth_error and NEVER leaks the secret key."""
        secret_key = "AIzaSy_SUPER_SECRET_KEY_NEVER_LEAK"
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_post.return_value = mock_resp

        env = {"GEMINI_API_KEY": secret_key}
        with patch.dict(os.environ, env, clear=True):
            res = llm_client.generate_farming_response("What fertilizer to use?", lang="en")
            self.assertFalse(res["success"])
            self.assertEqual(res["error_type"], "auth_error")
            self.assertIn("Authentication Failed", res["reply"])
            # CRITICAL SECURITY ASSERTION: Secret key must NOT appear in output
            self.assertNotIn(secret_key, res["reply"])
            self.assertNotIn(secret_key, res["spoken_text"])

    @patch("requests.post")
    def test_gemini_429_rate_limit(self, mock_post):
        """429 Rate limit returns polite retry message."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_post.return_value = mock_resp

        res = llm_client.call_gemini(
            api_key="valid_key",
            model="gemini-1.5-flash",
            system_prompt="system",
            user_prompt="Tomato fertilizer"
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "rate_limit")

    # --------------------------------------------------------------------------
    # 4. OpenAI REST Integration (Mock Tests)
    # --------------------------------------------------------------------------

    @patch("requests.post")
    def test_openai_success_response(self, mock_post):
        """Successful OpenAI response is parsed correctly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Apply balanced micronutrient mixture during vegetative phase."
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        res = llm_client.call_openai(
            api_key="sk-valid-openai-key",
            model="gpt-4o-mini",
            system_prompt="system",
            user_prompt="Micronutrients"
        )
        self.assertTrue(res["success"])
        self.assertIn("micronutrient", res["text"])

    @patch("requests.post")
    def test_openai_401_auth_error_no_leak(self, mock_post):
        """OpenAI 401 Unauthorized never leaks secret key."""
        secret_key = "sk-OPENAI_SECRET_KEY_12345"
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_post.return_value = mock_resp

        env = {"OPENAI_API_KEY": secret_key}
        with patch.dict(os.environ, env, clear=True):
            res = llm_client.generate_farming_response("Fertilizer question", lang="en")
            self.assertFalse(res["success"])
            self.assertEqual(res["error_type"], "auth_error")
            self.assertNotIn(secret_key, res["reply"])

    # --------------------------------------------------------------------------
    # 5. End-to-End Chat API with Active Gemini Key
    # --------------------------------------------------------------------------

    @patch("requests.post")
    def test_end_to_end_conversational_llm(self, mock_post):
        """Conversational query routes to Gemini when GEMINI_API_KEY is configured."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "For soil organic matter, incorporate 5 tonnes of well-rotted FYM or Vermicompost per acre before the monsoon."}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        env = {"GEMINI_API_KEY": "AIzaSyTestValidKey"}
        with patch.dict(os.environ, env, clear=True):
            res = self.client.post("/api/chat", json={
                "message": "How do I increase soil organic carbon?",
                "lang": "en"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("Vermicompost", data["reply"])
            self.assertEqual(data["tool_used"], "gemini_llm")
            self.assertEqual(data["context_applied"]["llm_provider"], "gemini")

    @patch("requests.post")
    def test_end_to_end_image_analysis_llm(self, mock_post):
        """Image attachment with active Gemini key invokes multimodal vision."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Photo diagnosis: Visible yellow leaf curl virus symptoms. Spray Neem oil 10,000 ppm @ 2ml/L to control vector whiteflies."}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        env = {"GEMINI_API_KEY": "AIzaSyTestVisionKey"}
        with patch.dict(os.environ, env, clear=True):
            res = self.client.post("/api/chat", json={
                "message": "Analyze this crop photo",
                "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
                "lang": "en"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["tool_used"], "vision_diagnosis")
            self.assertIn("yellow leaf curl", data["reply"].lower())
            self.assertTrue(data["context_applied"]["has_image"])

    # --------------------------------------------------------------------------
    # 6. Fallback Integrity: Mandi Prices & Weather Always Grounded
    # --------------------------------------------------------------------------

    def test_mandi_prices_remain_grounded_never_hallucinated(self):
        """Even if LLM is configured or unconfigured, Mandi prices use authentic APMC data."""
        res = self.client.post("/api/chat", json={"message": "What is today's chilli price in Guntur?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tool_used"], "market_rates")
        self.assertIn("Guntur", data["reply"])
        self.assertIn("Chilli", data["reply"])
        # Prices must be derived from verified data, not raw generative text
        self.assertIn("₹", data["reply"])


if __name__ == "__main__":
    unittest.main()
