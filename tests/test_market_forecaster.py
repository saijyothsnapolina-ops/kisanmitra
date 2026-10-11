"""
Unit and Integration Tests for APMC Mandi Price Forecaster:
===========================================================
1. Numerical Linear Algebra Routines (Matrix multiplication, inversion, Gauss-Jordan)
2. Agricultural Feature Engineering (Lags, rolling momentum, velocity)
3. Regularized Ridge Auto-Regression Fitting & Weights
4. Multi-Step Horizon Forecasts & 95% Confidence Intervals
5. Academic Walk-Forward Cross-Validation Metrics (MAE, RMSE, MAPE, Directional Accuracy)
6. REST API Endpoint: GET /api/market/forecast
7. Conversational AI Agent Multi-Lingual Integration (EN, TE, HI)
"""

import unittest
from starlette.testclient import TestClient
from app import app, FarmerProfile, reset_profile
from ai_agent import AIAgent, session_repo, AgriculturalTools
from market_forecaster import (
    matrix_transpose,
    matrix_multiply,
    matrix_inverse,
    matrix_vector_multiply,
    vector_dot,
    PriceFeatureExtractor,
    APMCPriceForecaster,
    generate_market_forecast
)
from market_service import MarketService, getMarketPriceForecast


class TestMarketForecaster(unittest.TestCase):
    def setUp(self):
        reset_profile()
        session_repo.sessions.clear()
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Numerical Linear Algebra Routines
    # --------------------------------------------------------------------------

    def test_matrix_transpose(self):
        A = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        At = matrix_transpose(A)
        self.assertEqual(len(At), 3)
        self.assertEqual(len(At[0]), 2)
        self.assertEqual(At[0][0], 1.0)
        self.assertEqual(At[2][1], 6.0)

    def test_matrix_multiply(self):
        A = [[1.0, 2.0], [3.0, 4.0]]
        B = [[2.0, 0.0], [1.0, 2.0]]
        C = matrix_multiply(A, B)
        # Row 0: 1*2 + 2*1 = 4; 1*0 + 2*2 = 4
        # Row 1: 3*2 + 4*1 = 10; 3*0 + 4*2 = 8
        self.assertEqual(C[0][0], 4.0)
        self.assertEqual(C[0][1], 4.0)
        self.assertEqual(C[1][0], 10.0)
        self.assertEqual(C[1][1], 8.0)

    def test_matrix_inverse_identity(self):
        A = [[4.0, 7.0], [2.0, 6.0]]
        A_inv = matrix_inverse(A)
        prod = matrix_multiply(A, A_inv)
        # Product should be identity matrix
        self.assertAlmostEqual(prod[0][0], 1.0, places=6)
        self.assertAlmostEqual(prod[0][1], 0.0, places=6)
        self.assertAlmostEqual(prod[1][0], 0.0, places=6)
        self.assertAlmostEqual(prod[1][1], 1.0, places=6)

    # --------------------------------------------------------------------------
    # 2. Agricultural Feature Engineering
    # --------------------------------------------------------------------------

    def test_feature_extraction(self):
        norm_series = [-1.0, -0.5, 0.0, 0.5, 1.0]
        feats = PriceFeatureExtractor.extract_features_at(norm_series, 3)
        self.assertIsNotNone(feats)
        self.assertEqual(len(feats), 6)
        # bias = 1.0
        self.assertEqual(feats[0], 1.0)
        # lag1 = norm_series[2] = 0.0
        self.assertEqual(feats[1], 0.0)
        # lag2 = norm_series[1] = -0.5
        self.assertEqual(feats[2], -0.5)
        # lag3 = norm_series[0] = -1.0
        self.assertEqual(feats[3], -1.0)
        # velocity = lag1 - lag2 = 0.0 - (-0.5) = 0.5
        self.assertEqual(feats[5], 0.5)

    # --------------------------------------------------------------------------
    # 3. Ridge Regression Fitting & Recursive Multi-Step Forecast
    # --------------------------------------------------------------------------

    def test_forecaster_fit_and_horizon(self):
        prices = [21000.0, 21200.0, 21350.0, 21500.0, 21650.0, 21800.0, 21950.0]
        model = APMCPriceForecaster(lambda_reg=0.5)
        model.fit(prices)

        self.assertIsNotNone(model.weights)
        self.assertEqual(len(model.weights), 6)
        self.assertGreater(model.residual_variance, 0.0)

        # 7-day forecast
        forecast = model.forecast_horizon(horizon_days=7)
        self.assertEqual(len(forecast), 7)

        for step in forecast:
            self.assertIn("predicted_modal_price", step)
            self.assertIn("lower_bound_95", step)
            self.assertIn("upper_bound_95", step)
            self.assertIn("trend", step)
            # Confidence interval bounds sanity
            self.assertLessEqual(step["lower_bound_95"], step["predicted_modal_price"])
            self.assertGreaterEqual(step["upper_bound_95"], step["predicted_modal_price"])
            # Reasonable price range for agricultural produce
            self.assertGreater(step["predicted_modal_price"], 10000.0)
            self.assertLess(step["predicted_modal_price"], 35000.0)

    # --------------------------------------------------------------------------
    # 4. Academic Walk-Forward Cross-Validation Metrics
    # --------------------------------------------------------------------------

    def test_academic_metrics_evaluation(self):
        prices = [21000.0, 21200.0, 21350.0, 21500.0, 21650.0, 21800.0, 21950.0]
        model = APMCPriceForecaster(lambda_reg=0.5)
        model.fit(prices)
        metrics = model.metrics

        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("mape_pct", metrics)
        self.assertIn("directional_accuracy_pct", metrics)
        self.assertIn("validation_method", metrics)

        # Metrics must be non-negative and reasonable
        self.assertGreaterEqual(metrics["mae"], 0.0)
        self.assertGreaterEqual(metrics["rmse"], 0.0)
        self.assertGreaterEqual(metrics["mape_pct"], 0.0)
        self.assertLess(metrics["mape_pct"], 10.0)  # Low error on smooth trends
        self.assertGreaterEqual(metrics["directional_accuracy_pct"], 50.0)

    # --------------------------------------------------------------------------
    # 5. High-Level Agricultural Report Generation
    # --------------------------------------------------------------------------

    def test_generate_market_forecast_report(self):
        report = generate_market_forecast("Chilli", variety="341", market="Guntur Mirchi Yard", horizon_days=7)
        self.assertEqual(report["crop"], "Chilli")
        self.assertEqual(report["variety"], "341")
        self.assertEqual(report["market"], "Guntur Mirchi Yard")
        self.assertIn("forecast_series", report)
        self.assertEqual(len(report["forecast_series"]), 7)
        self.assertIn("advisory", report)
        self.assertIn("en", report["advisory"])
        self.assertIn("te", report["advisory"])
        self.assertIn("hi", report["advisory"])
        self.assertIn("model_metadata", report)
        self.assertEqual(report["model_metadata"]["algorithm"], "Regularized Auto-Regressive Ridge Linear Regression (L2)")

    # --------------------------------------------------------------------------
    # 6. REST API Endpoint: GET /api/market/forecast
    # --------------------------------------------------------------------------

    def test_forecast_api_endpoint(self):
        res = self.client.get("/api/market/forecast?crop=Chilli&variety=341&horizon=7")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["crop"], "Chilli")
        self.assertEqual(data["variety"], "341")
        self.assertEqual(len(data["forecast_series"]), 7)
        self.assertIn("model_metadata", data)
        self.assertIn("evaluation_metrics", data["model_metadata"])

    def test_forecast_api_tomato(self):
        res = self.client.get("/api/market/forecast?crop=Tomato&horizon=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["crop"], "Tomato")
        self.assertEqual(len(data["forecast_series"]), 5)

    # --------------------------------------------------------------------------
    # 7. Conversational AI Agent Multi-Lingual Query Routing
    # --------------------------------------------------------------------------

    def test_conversational_forecast_english(self):
        profile = FarmerProfile(name="Jyothsna", crops=["Chilli"], crop_varieties=["341"], farm_location="Cherla")
        res = AIAgent.process("Will chilli 341 price increase next week?", profile=profile, session_id="test-forecaster-en")
        self.assertEqual(res["tool_used"], "market_price_forecast")
        reply = res["reply"]
        self.assertIn("7-Day APMC Mandi Price Forecast", reply)
        self.assertIn("Ridge Regression", reply)
        self.assertIn("Mean Absolute Error", reply)
        spoken = res["spoken_text"]
        # Spoken text should be concise (1-3 sentences)
        self.assertLessEqual(len([s for s in spoken.split(".") if s.strip()]), 3)

    def test_conversational_forecast_telugu(self):
        profile = FarmerProfile(name="Jyothsna", crops=["Chilli"], crop_varieties=["341"], farm_location="Cherla")
        res = AIAgent.process("వచ్చే వారం మిర్చి ధర పెరుగుతుందా?", profile=profile, session_id="test-forecaster-te")
        self.assertEqual(res["tool_used"], "market_price_forecast")
        reply = res["reply"]
        self.assertIn("ధరల అంచనా", reply)
        self.assertIn("క్వింటాల్", reply)
        spoken = res["spoken_text"]
        self.assertIn("మిర్చి", spoken)

    def test_conversational_forecast_hindi(self):
        profile = FarmerProfile(name="Jyothsna", crops=["Chilli"], crop_varieties=["341"], farm_location="Cherla")
        res = AIAgent.process("क्या अगले हफ्ते मिर्च का भाव बढ़ेगा?", profile=profile, session_id="test-forecaster-hi")
        self.assertEqual(res["tool_used"], "market_price_forecast")
        reply = res["reply"]
        self.assertIn("पूर्वानुमान", reply)
        spoken = res["spoken_text"]
        self.assertIn("मिर्च", spoken)

    # --------------------------------------------------------------------------
    # 8. Edge Cases & Boundary Conditions
    # --------------------------------------------------------------------------

    def test_forecaster_constant_prices_edge_case(self):
        """Constant prices (zero variance) should not cause division by zero or NaN."""
        prices = [20000.0, 20000.0, 20000.0, 20000.0, 20000.0]
        model = APMCPriceForecaster(lambda_reg=0.5)
        model.fit(prices)
        forecast = model.forecast_horizon(horizon_days=3)
        self.assertEqual(len(forecast), 3)
        for step in forecast:
            self.assertFalse(any(isinstance(v, float) and (v != v) for v in step.values()))  # No NaN
            self.assertAlmostEqual(step["predicted_modal_price"], 20000.0, delta=500.0)

    def test_forecaster_minimal_series_edge_case(self):
        """Very short price series (< 4 points) should fall back safely without error."""
        prices = [22000.0, 22100.0]
        model = APMCPriceForecaster(lambda_reg=0.5)
        model.fit(prices)
        forecast = model.forecast_horizon(horizon_days=3)
        self.assertEqual(len(forecast), 3)
        self.assertGreater(forecast[0]["predicted_modal_price"], 0.0)

    def test_forecast_api_clamped_horizon_edge_case(self):
        """Negative or zero horizon should be clamped to default 7 without error."""
        res_zero = self.client.get("/api/market/forecast?crop=Chilli&horizon=0")
        self.assertEqual(res_zero.status_code, 200)
        self.assertEqual(len(res_zero.json()["forecast_series"]), 7)

        res_neg = self.client.get("/api/market/forecast?crop=Chilli&horizon=-10")
        self.assertEqual(res_neg.status_code, 200)
        self.assertEqual(len(res_neg.json()["forecast_series"]), 7)

    def test_forecast_api_empty_crop_edge_case(self):
        """Empty crop query parameter should default safely to Chilli."""
        res = self.client.get("/api/market/forecast?crop=")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["crop"], "Chilli")

    def test_conversational_forecast_mixed_telugu_english(self):
        """Transliterated mixed farmer phrasing should route to market_price_forecast."""
        profile = FarmerProfile(name="Jyothsna", crops=["Chilli"], crop_varieties=["341"], farm_location="Cherla")
        res = AIAgent.process("Chilli 341 dhara peruguthunda next week?", profile=profile, session_id="test-mixed-lang")
        self.assertEqual(res["tool_used"], "market_price_forecast")


if __name__ == "__main__":
    unittest.main()
