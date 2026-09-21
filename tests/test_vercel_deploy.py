"""
Test Vercel Deployment Configurations and Entrypoints
"""

import os
import json
import unittest
from starlette.testclient import TestClient

class TestVercelDeployment(unittest.TestCase):
    def test_requirements_file_exists_and_contains_deps(self):
        req_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
        self.assertTrue(os.path.exists(req_path), "requirements.txt must exist in root")
        with open(req_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("fastapi", content.lower())
        self.assertIn("uvicorn", content.lower())
        self.assertIn("pydantic", content.lower())

    def test_vercel_json_exists_and_valid(self):
        vercel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vercel.json")
        self.assertTrue(os.path.exists(vercel_path), "vercel.json must exist in root")
        with open(vercel_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("version"), 2)
        self.assertTrue(any(b.get("src") == "api/index.py" for b in data.get("builds", [])))
        self.assertTrue(any("api/index.py" in r.get("dest", "") for r in data.get("routes", [])))

    def test_api_index_entrypoint_and_routes(self):
        import api.index
        self.assertTrue(hasattr(api.index, "app"))
        client = TestClient(api.index.app)
        
        # Root static serving
        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)
        
        # CSS static asset
        res_css = client.get("/css/styles.css")
        self.assertEqual(res_css.status_code, 200)
        
        # JS static asset
        res_js = client.get("/js/app.js")
        self.assertEqual(res_js.status_code, 200)
        
        # API market endpoint
        res_market = client.get("/api/market?crop=Chilli")
        self.assertEqual(res_market.status_code, 200)
        market_data = res_market.json()
        self.assertIn("data", market_data)
        self.assertGreater(len(market_data["data"]), 0)

if __name__ == "__main__":
    unittest.main()
