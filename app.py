"""
KisanMitra Backend Server
FastAPI server providing Chatbot AI, APMC Mandi Market data, Agro-Weather, Crop Advisories,
and Farmer Profile Management with Chat-First deferral flow.
"""

import os
import json
import re
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_agent import AIAgent
import market_service

app = FastAPI(title="KisanMitra AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent file storage for farmer profile (file-based or in-memory fallback)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
PROFILE_FILE = os.path.join(DATA_DIR, "farmer_profile.json")

class LocationContext(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    nearest_market: Optional[str] = None
    nearest_distance_km: Optional[float] = None
    captured_at: Optional[float] = None

class FarmerProfile(BaseModel):
    name: str = ""
    farm_location: str = ""
    farm_location_details: Optional[Dict[str, Any]] = None
    location: str = ""
    device_location: Optional[LocationContext] = None
    gps_location: Optional[LocationContext] = None
    main_crop: Optional[str] = ""
    crops: List[str] = []
    farm_size: str = ""
    crop_variety: Optional[str] = ""
    crop_varieties: List[str] = []
    soil_type: Optional[str] = ""
    irrigation_type: Optional[str] = ""
    growth_stage: Optional[str] = ""
    sowing_date: Optional[str] = ""
    preferred_language: Optional[str] = "te"
    completed: bool = False

def load_profile() -> FarmerProfile:
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return FarmerProfile(**data)
        except Exception:
            pass
    return FarmerProfile()

def save_profile_to_disk(profile: FarmerProfile):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile.model_dump(), f, indent=2)
    except Exception:
        pass

# In-memory working copy
current_profile = load_profile()

# ----------------- Mandi Market Benchmark Data -----------------
MANDI_PRICES = [
    # --- TOMATO (Yesterday: 22 Sep 2026) ---
    {"market": "Narasaraopet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 3200, "modal_price": 3500, "max_price": 3700, "unit": "₹/Quintal", "trend": "up", "change": "+₹250", "change_pct": "+7.69%", "arrivals": "75 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:30 PM"},
    {"market": "Guntur APMC", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 3100, "modal_price": 3400, "max_price": 3650, "unit": "₹/Quintal", "trend": "up", "change": "+₹300", "change_pct": "+9.68%", "arrivals": "140 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Vijayawada Mandi", "district": "Krishna", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 2950, "modal_price": 3250, "max_price": 3450, "unit": "₹/Quintal", "trend": "up", "change": "+₹150", "change_pct": "+4.84%", "arrivals": "110 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 7:15 PM"},
    {"market": "Tenali Market Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Desi / Local", "min_price": 2800, "modal_price": 3180, "max_price": 3350, "unit": "₹/Quintal", "trend": "stable", "change": "+₹40", "change_pct": "+1.27%", "arrivals": "50 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:45 PM"},
    {"market": "Chilakaluripet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Desi / Local", "min_price": 2700, "modal_price": 2950, "max_price": 3150, "unit": "₹/Quintal", "trend": "stable", "change": "-₹50", "change_pct": "-1.67%", "arrivals": "40 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},

    # --- TOMATO (Today: 23 Sep 2026) ---
    {"market": "Guntur APMC", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 3150, "modal_price": 3450, "max_price": 3700, "unit": "₹/Quintal", "trend": "up", "change": "+₹50", "change_pct": "+1.47%", "arrivals": "145 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:00 AM"},
    {"market": "Narasaraopet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 3250, "modal_price": 3520, "max_price": 3750, "unit": "₹/Quintal", "trend": "up", "change": "+₹20", "change_pct": "+0.57%", "arrivals": "80 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 7:00 AM"},
    {"market": "Vijayawada Mandi", "district": "Krishna", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Hybrid Red", "min_price": 3000, "modal_price": 3280, "max_price": 3500, "unit": "₹/Quintal", "trend": "up", "change": "+₹30", "change_pct": "+0.92%", "arrivals": "115 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 7:15 AM"},
    {"market": "Tenali Market Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Desi / Local", "min_price": 2850, "modal_price": 3200, "max_price": 3400, "unit": "₹/Quintal", "trend": "stable", "change": "+₹20", "change_pct": "+0.63%", "arrivals": "55 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:45 AM"},
    {"market": "Chilakaluripet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Tomato", "variety": "Desi / Local", "min_price": 2750, "modal_price": 2980, "max_price": 3200, "unit": "₹/Quintal", "trend": "stable", "change": "+₹30", "change_pct": "+1.02%", "arrivals": "45 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:15 AM"},

    # --- CHILLI — VARIETY: 341 (Yesterday: 22 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "341", "min_price": 19500, "modal_price": 21800, "max_price": 23200, "unit": "₹/Quintal", "trend": "up", "change": "+₹600", "change_pct": "+2.83%", "arrivals": "340 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 7:00 PM"},
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 19000, "modal_price": 21200, "max_price": 22600, "unit": "₹/Quintal", "trend": "up", "change": "+₹400", "change_pct": "+1.92%", "arrivals": "220 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:30 PM"},
    {"market": "Enumamula Yard", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 18500, "modal_price": 20800, "max_price": 22100, "unit": "₹/Quintal", "trend": "stable", "change": "+₹150", "change_pct": "+0.73%", "arrivals": "180 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:45 PM"},
    {"market": "Khammam APMC", "district": "Khammam", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 18200, "modal_price": 20400, "max_price": 21700, "unit": "₹/Quintal", "trend": "stable", "change": "+₹100", "change_pct": "+0.49%", "arrivals": "160 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Narasaraopet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "341", "min_price": 17800, "modal_price": 19900, "max_price": 21200, "unit": "₹/Quintal", "trend": "down", "change": "-₹200", "change_pct": "-1.00%", "arrivals": "95 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},

    # --- CHILLI — VARIETY: 341 (Today: 23 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "341", "min_price": 19800, "modal_price": 22100, "max_price": 23500, "unit": "₹/Quintal", "trend": "up", "change": "+₹300", "change_pct": "+1.38%", "arrivals": "360 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:00 AM"},
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 19200, "modal_price": 21400, "max_price": 22800, "unit": "₹/Quintal", "trend": "up", "change": "+₹200", "change_pct": "+0.94%", "arrivals": "230 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:30 AM"},
    {"market": "Enumamula Yard", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 18700, "modal_price": 21000, "max_price": 22300, "unit": "₹/Quintal", "trend": "up", "change": "+₹200", "change_pct": "+0.96%", "arrivals": "190 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:45 AM"},
    {"market": "Khammam APMC", "district": "Khammam", "state": "Telangana", "crop": "Chilli", "variety": "341", "min_price": 18400, "modal_price": 20600, "max_price": 21900, "unit": "₹/Quintal", "trend": "up", "change": "+₹200", "change_pct": "+0.98%", "arrivals": "170 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 7:00 AM"},
    {"market": "Narasaraopet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "341", "min_price": 18000, "modal_price": 20100, "max_price": 21400, "unit": "₹/Quintal", "trend": "up", "change": "+₹200", "change_pct": "+1.01%", "arrivals": "100 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 7:15 AM"},

    # --- CHILLI — VARIETY: Teja (Yesterday: 22 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Teja", "min_price": 20500, "modal_price": 22500, "max_price": 24000, "unit": "₹/Quintal", "trend": "up", "change": "+₹500", "change_pct": "+2.27%", "arrivals": "450 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 7:00 PM"},
    {"market": "Khammam APMC", "district": "Khammam", "state": "Telangana", "crop": "Chilli", "variety": "Teja", "min_price": 19800, "modal_price": 21900, "max_price": 23400, "unit": "₹/Quintal", "trend": "up", "change": "+₹400", "change_pct": "+1.86%", "arrivals": "280 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:30 PM"},
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "Teja", "min_price": 19500, "modal_price": 21400, "max_price": 22900, "unit": "₹/Quintal", "trend": "stable", "change": "+₹200", "change_pct": "+0.94%", "arrivals": "210 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Enumamula Yard", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "Teja", "min_price": 19000, "modal_price": 20900, "max_price": 22400, "unit": "₹/Quintal", "trend": "stable", "change": "+₹100", "change_pct": "+0.48%", "arrivals": "170 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:45 PM"},

    # --- CHILLI — VARIETY: Teja (Today: 23 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Teja", "min_price": 20800, "modal_price": 22800, "max_price": 24200, "unit": "₹/Quintal", "trend": "up", "change": "+₹300", "change_pct": "+1.33%", "arrivals": "470 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:00 AM"},
    {"market": "Khammam APMC", "district": "Khammam", "state": "Telangana", "crop": "Chilli", "variety": "Teja", "min_price": 20000, "modal_price": 22100, "max_price": 23600, "unit": "₹/Quintal", "trend": "up", "change": "+₹200", "change_pct": "+0.91%", "arrivals": "290 Tonnes", "date": "23 Sep 2026", "date_iso": "2026-09-23", "date_label": "Today", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Today, 6:30 AM"},

    # --- CHILLI — VARIETY: Wonder Hot (Yesterday: 22 Sep 2026) ---
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "Wonder Hot", "min_price": 17200, "modal_price": 18800, "max_price": 20200, "unit": "₹/Quintal", "trend": "stable", "change": "+₹150", "change_pct": "+0.80%", "arrivals": "210 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:30 PM"},
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Wonder Hot", "min_price": 16900, "modal_price": 18400, "max_price": 19800, "unit": "₹/Quintal", "trend": "stable", "change": "+₹100", "change_pct": "+0.55%", "arrivals": "180 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Enumamula Yard", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "Wonder Hot", "min_price": 16400, "modal_price": 17900, "max_price": 19300, "unit": "₹/Quintal", "trend": "down", "change": "-₹100", "change_pct": "-0.56%", "arrivals": "140 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},

    # --- CHILLI — VARIETY: Byadgi (Yesterday: 22 Sep 2026) ---
    {"market": "Byadgi Mandi", "district": "Haveri", "state": "Karnataka", "crop": "Chilli", "variety": "Byadgi", "min_price": 24000, "modal_price": 26500, "max_price": 28500, "unit": "₹/Quintal", "trend": "up", "change": "+₹800", "change_pct": "+3.11%", "arrivals": "320 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:45 PM"},
    {"market": "Haveri APMC", "district": "Haveri", "state": "Karnataka", "crop": "Chilli", "variety": "Byadgi", "min_price": 23500, "modal_price": 25800, "max_price": 27600, "unit": "₹/Quintal", "trend": "up", "change": "+₹500", "change_pct": "+1.98%", "arrivals": "210 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Byadgi", "min_price": 23000, "modal_price": 25100, "max_price": 27000, "unit": "₹/Quintal", "trend": "stable", "change": "+₹200", "change_pct": "+0.80%", "arrivals": "160 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},

    # --- CHILLI — VARIETY: Guntur Sannam (Yesterday: 22 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Guntur Sannam", "min_price": 16000, "modal_price": 17500, "max_price": 18800, "unit": "₹/Quintal", "trend": "up", "change": "+₹300", "change_pct": "+1.74%", "arrivals": "190 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:15 PM"},
    {"market": "Chilakaluripet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Guntur Sannam", "min_price": 15400, "modal_price": 16900, "max_price": 18100, "unit": "₹/Quintal", "trend": "stable", "change": "+₹100", "change_pct": "+0.60%", "arrivals": "120 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:45 PM"},
    {"market": "Narasaraopet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Guntur Sannam", "min_price": 15000, "modal_price": 16400, "max_price": 17600, "unit": "₹/Quintal", "trend": "down", "change": "-₹100", "change_pct": "-0.61%", "arrivals": "85 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:15 PM"},

    # --- CHILLI — VARIETY: Dry Chilli (Yesterday: 22 Sep 2026) ---
    {"market": "Guntur Mirchi Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Dry Chilli", "min_price": 17800, "modal_price": 19500, "max_price": 21000, "unit": "₹/Quintal", "trend": "stable", "change": "+₹150", "change_pct": "+0.78%", "arrivals": "260 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Chilli", "variety": "Dry Chilli", "min_price": 17400, "modal_price": 19100, "max_price": 20500, "unit": "₹/Quintal", "trend": "stable", "change": "+₹100", "change_pct": "+0.53%", "arrivals": "175 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},

    # --- CHILLI — VARIETY: Local / Other (Yesterday: 22 Sep 2026) ---
    {"market": "Chilakaluripet Yard", "district": "Palnadu", "state": "Andhra Pradesh", "crop": "Chilli", "variety": "Local / Other", "min_price": 14500, "modal_price": 16000, "max_price": 17200, "unit": "₹/Quintal", "trend": "stable", "change": "0", "change_pct": "0.0%", "arrivals": "60 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"},

    # --- COTTON (Yesterday: 22 Sep 2026) ---
    {"market": "Guntur APMC", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Cotton", "variety": "Medium Staple (Shankar-6)", "min_price": 6800, "modal_price": 7450, "max_price": 7700, "unit": "₹/Quintal", "trend": "up", "change": "+₹180", "change_pct": "+2.47%", "arrivals": "160 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Adilabad Yard", "district": "Adilabad", "state": "Telangana", "crop": "Cotton", "variety": "Long Staple", "min_price": 6700, "modal_price": 7300, "max_price": 7550, "unit": "₹/Quintal", "trend": "up", "change": "+₹120", "change_pct": "+1.67%", "arrivals": "190 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},
    {"market": "Warangal Mandi", "district": "Warangal", "state": "Telangana", "crop": "Cotton", "variety": "Medium Staple (Shankar-6)", "min_price": 6600, "modal_price": 7150, "max_price": 7400, "unit": "₹/Quintal", "trend": "stable", "change": "+₹50", "change_pct": "+0.70%", "arrivals": "140 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"},
    {"market": "Bhainsa APMC", "district": "Nirmal", "state": "Telangana", "crop": "Cotton", "variety": "Medium Staple", "min_price": 6500, "modal_price": 7000, "max_price": 7250, "unit": "₹/Quintal", "trend": "stable", "change": "0", "change_pct": "0.0%", "arrivals": "85 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 4:45 PM"},

    # --- PADDY (Yesterday: 22 Sep 2026) ---
    {"market": "Tenali Market Yard", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Paddy", "variety": "BPT-5204 (Samba)", "min_price": 2300, "modal_price": 2450, "max_price": 2600, "unit": "₹/Quintal", "trend": "stable", "change": "+₹20", "change_pct": "+0.82%", "arrivals": "350 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:30 PM"},
    {"market": "Miryalaguda APMC", "district": "Nalgonda", "state": "Telangana", "crop": "Paddy", "variety": "Common (Fine)", "min_price": 2250, "modal_price": 2400, "max_price": 2550, "unit": "₹/Quintal", "trend": "stable", "change": "0", "change_pct": "0.0%", "arrivals": "420 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Nellore Mandi", "district": "SPSR Nellore", "state": "Andhra Pradesh", "crop": "Paddy", "variety": "BPT-5204 (Samba)", "min_price": 2200, "modal_price": 2350, "max_price": 2500, "unit": "₹/Quintal", "trend": "stable", "change": "+₹10", "change_pct": "+0.43%", "arrivals": "280 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},
    {"market": "Suryapet Yard", "district": "Suryapet", "state": "Telangana", "crop": "Paddy", "variety": "RNR-15048", "min_price": 2150, "modal_price": 2280, "max_price": 2420, "unit": "₹/Quintal", "trend": "stable", "change": "-₹20", "change_pct": "-0.87%", "arrivals": "190 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"},

    # --- ONION (Yesterday: 22 Sep 2026) ---
    {"market": "Kurnool Mandi", "district": "Kurnool", "state": "Andhra Pradesh", "crop": "Onion", "variety": "Red Medium", "min_price": 1600, "modal_price": 1950, "max_price": 2300, "unit": "₹/Quintal", "trend": "down", "change": "-₹80", "change_pct": "-3.94%", "arrivals": "140 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 7:00 PM"},
    {"market": "Hyderabad Bowenpally", "district": "Hyderabad", "state": "Telangana", "crop": "Onion", "variety": "Red Medium", "min_price": 1550, "modal_price": 1900, "max_price": 2250, "unit": "₹/Quintal", "trend": "down", "change": "-₹50", "change_pct": "-2.56%", "arrivals": "310 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:15 PM"},
    {"market": "Solapur Yard", "district": "Solapur", "state": "Maharashtra", "crop": "Onion", "variety": "Nashik Red", "min_price": 1450, "modal_price": 1820, "max_price": 2150, "unit": "₹/Quintal", "trend": "down", "change": "-₹100", "change_pct": "-5.21%", "arrivals": "480 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:45 PM"},
    {"market": "Mahbubnagar Mandi", "district": "Mahbubnagar", "state": "Telangana", "crop": "Onion", "variety": "Local White", "min_price": 1400, "modal_price": 1750, "max_price": 2050, "unit": "₹/Quintal", "trend": "down", "change": "-₹60", "change_pct": "-3.31%", "arrivals": "110 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"},

    # --- MAIZE (Yesterday: 22 Sep 2026) ---
    {"market": "Nizamabad Yard", "district": "Nizamabad", "state": "Telangana", "crop": "Maize", "variety": "Yellow Hybrid", "min_price": 1950, "modal_price": 2250, "max_price": 2400, "unit": "₹/Quintal", "trend": "up", "change": "+₹70", "change_pct": "+3.21%", "arrivals": "260 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Davanagere Mandi", "district": "Davanagere", "state": "Karnataka", "crop": "Maize", "variety": "Yellow Hybrid", "min_price": 1900, "modal_price": 2180, "max_price": 2350, "unit": "₹/Quintal", "trend": "stable", "change": "+₹30", "change_pct": "+1.40%", "arrivals": "310 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},
    {"market": "Guntur APMC", "district": "Guntur", "state": "Andhra Pradesh", "crop": "Maize", "variety": "Local White", "min_price": 1850, "modal_price": 2120, "max_price": 2280, "unit": "₹/Quintal", "trend": "stable", "change": "0", "change_pct": "0.0%", "arrivals": "120 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"},

    # --- GROUNDNUT (Yesterday: 22 Sep 2026) ---
    {"market": "Kurnool Mandi", "district": "Kurnool", "state": "Andhra Pradesh", "crop": "Groundnut", "variety": "Bold / Pods", "min_price": 5900, "modal_price": 6650, "max_price": 7100, "unit": "₹/Quintal", "trend": "up", "change": "+₹150", "change_pct": "+2.31%", "arrivals": "175 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 6:00 PM"},
    {"market": "Anantapur APMC", "district": "Anantapur", "state": "Andhra Pradesh", "crop": "Groundnut", "variety": "Bold / Pods", "min_price": 5800, "modal_price": 6480, "max_price": 6950, "unit": "₹/Quintal", "trend": "stable", "change": "+₹50", "change_pct": "+0.78%", "arrivals": "210 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:30 PM"},
    {"market": "Kadiri Yard", "district": "Sri Sathya Sai", "state": "Andhra Pradesh", "crop": "Groundnut", "variety": "TMV-2", "min_price": 5700, "modal_price": 6350, "max_price": 6800, "unit": "₹/Quintal", "trend": "stable", "change": "0", "change_pct": "0.0%", "arrivals": "140 Tonnes", "date": "22 Sep 2026", "date_iso": "2026-09-22", "date_label": "Yesterday", "source": "Agmarknet APMC Daily Report (Demo)", "freshness": "DEMO APMC DATA", "updated": "Yesterday, 5:00 PM"}
]

HISTORICAL_PRICE_DATA = {
    "Tomato": {
        "7D": [
            {"date": "16 Sep", "price": 3100, "market": "Narasaraopet"},
            {"date": "17 Sep", "price": 3150, "market": "Narasaraopet"},
            {"date": "18 Sep", "price": 3220, "market": "Guntur APMC"},
            {"date": "19 Sep", "price": 3310, "market": "Guntur APMC"},
            {"date": "20 Sep", "price": 3380, "market": "Narasaraopet"},
            {"date": "21 Sep", "price": 3440, "market": "Narasaraopet"},
            {"date": "22 Sep", "price": 3500, "market": "Narasaraopet"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 2650, "market": "Guntur APMC"},
            {"date": "31 Aug", "price": 2800, "market": "Guntur APMC"},
            {"date": "07 Sep", "price": 3050, "market": "Narasaraopet"},
            {"date": "14 Sep", "price": 3200, "market": "Narasaraopet"},
            {"date": "21 Sep", "price": 3440, "market": "Narasaraopet"},
            {"date": "22 Sep", "price": 3500, "market": "Narasaraopet"}
        ],
        "3M": [
            {"date": "Jul", "price": 2100, "market": "Regional APMC"},
            {"date": "Aug", "price": 2650, "market": "Regional APMC"},
            {"date": "Sep", "price": 3500, "market": "Regional APMC"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 1900, "market": "APMC Benchmark"},
            {"date": "Jan '26", "price": 2200, "market": "APMC Benchmark"},
            {"date": "Apr '26", "price": 2450, "market": "APMC Benchmark"},
            {"date": "Jul '26", "price": 2700, "market": "APMC Benchmark"},
            {"date": "Sep '26", "price": 3500, "market": "APMC Benchmark"}
        ]
    },
    "Chilli": {
        "7D": [
            {"date": "16 Sep", "price": 20400, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "17 Sep", "price": 20600, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "18 Sep", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "19 Sep", "price": 20950, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "20 Sep", "price": 21050, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "21 Sep", "price": 21100, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "22 Sep", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 19200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "31 Aug", "price": 19800, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "07 Sep", "price": 20400, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "14 Sep", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "22 Sep", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"}
        ],
        "3M": [
            {"date": "Jul", "price": 18500, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "Aug", "price": 19800, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "Sep", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 17200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "Jan '26", "price": 18400, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "Apr '26", "price": 19200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
            {"date": "Sep '26", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"}
        ],
        "all": {
            "7D": [
                {"date": "16 Sep", "price": 20400, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "17 Sep", "price": 20600, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "18 Sep", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "19 Sep", "price": 20950, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "20 Sep", "price": 21050, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "21 Sep", "price": 21100, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"},
                {"date": "22 Sep", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "Chilli Benchmark"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 19200, "market": "Guntur Mirchi Yard"},
                {"date": "31 Aug", "price": 19800, "market": "Guntur Mirchi Yard"},
                {"date": "07 Sep", "price": 20400, "market": "Guntur Mirchi Yard"},
                {"date": "14 Sep", "price": 20800, "market": "Guntur Mirchi Yard"},
                {"date": "22 Sep", "price": 21200, "market": "Guntur Mirchi Yard"}
            ],
            "3M": [
                {"date": "Jul", "price": 18500, "market": "Guntur Mirchi Yard"},
                {"date": "Aug", "price": 19800, "market": "Guntur Mirchi Yard"},
                {"date": "Sep", "price": 21200, "market": "Guntur Mirchi Yard"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 17200, "market": "Guntur Mirchi Yard"},
                {"date": "Jan '26", "price": 18400, "market": "Guntur Mirchi Yard"},
                {"date": "Apr '26", "price": 19200, "market": "Guntur Mirchi Yard"},
                {"date": "Sep '26", "price": 21200, "market": "Guntur Mirchi Yard"}
            ]
        },
        "341": {
            "7D": [
                {"date": "16 Sep", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "17 Sep", "price": 21000, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "18 Sep", "price": 21200, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "19 Sep", "price": 21350, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "20 Sep", "price": 21500, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "21 Sep", "price": 21650, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "22 Sep", "price": 21800, "market": "Guntur Mirchi Yard", "variety": "341"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 19600, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "31 Aug", "price": 20200, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "07 Sep", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "14 Sep", "price": 21300, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "22 Sep", "price": 21800, "market": "Guntur Mirchi Yard", "variety": "341"}
            ],
            "3M": [
                {"date": "Jul", "price": 18900, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "Aug", "price": 20100, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "Sep", "price": 21800, "market": "Guntur Mirchi Yard", "variety": "341"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 17800, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "Jan '26", "price": 18900, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "Apr '26", "price": 19800, "market": "Guntur Mirchi Yard", "variety": "341"},
                {"date": "Sep '26", "price": 21800, "market": "Guntur Mirchi Yard", "variety": "341"}
            ]
        },
        "Teja": {
            "7D": [
                {"date": "16 Sep", "price": 21400, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "17 Sep", "price": 21600, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "18 Sep", "price": 21850, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "19 Sep", "price": 22000, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "20 Sep", "price": 22150, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "21 Sep", "price": 22300, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "22 Sep", "price": 22500, "market": "Guntur Mirchi Yard", "variety": "Teja"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 20100, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "31 Aug", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "07 Sep", "price": 21400, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "14 Sep", "price": 21900, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "22 Sep", "price": 22500, "market": "Guntur Mirchi Yard", "variety": "Teja"}
            ],
            "3M": [
                {"date": "Jul", "price": 19400, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "Aug", "price": 20800, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "Sep", "price": 22500, "market": "Guntur Mirchi Yard", "variety": "Teja"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 18200, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "Jan '26", "price": 19500, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "Apr '26", "price": 20600, "market": "Guntur Mirchi Yard", "variety": "Teja"},
                {"date": "Sep '26", "price": 22500, "market": "Guntur Mirchi Yard", "variety": "Teja"}
            ]
        },
        "Wonder Hot": {
            "7D": [
                {"date": "16 Sep", "price": 18100, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "17 Sep", "price": 18250, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "18 Sep", "price": 18400, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "19 Sep", "price": 18500, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "20 Sep", "price": 18600, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "21 Sep", "price": 18700, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "22 Sep", "price": 18800, "market": "Warangal Mandi", "variety": "Wonder Hot"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 17200, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "31 Aug", "price": 17600, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "07 Sep", "price": 18000, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "14 Sep", "price": 18400, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "22 Sep", "price": 18800, "market": "Warangal Mandi", "variety": "Wonder Hot"}
            ],
            "3M": [
                {"date": "Jul", "price": 16500, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "Aug", "price": 17500, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "Sep", "price": 18800, "market": "Warangal Mandi", "variety": "Wonder Hot"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 15800, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "Jan '26", "price": 16600, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "Apr '26", "price": 17400, "market": "Warangal Mandi", "variety": "Wonder Hot"},
                {"date": "Sep '26", "price": 18800, "market": "Warangal Mandi", "variety": "Wonder Hot"}
            ]
        },
        "Byadgi": {
            "7D": [
                {"date": "16 Sep", "price": 25200, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "17 Sep", "price": 25400, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "18 Sep", "price": 25700, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "19 Sep", "price": 25950, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "20 Sep", "price": 26100, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "21 Sep", "price": 26300, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "22 Sep", "price": 26500, "market": "Byadgi Mandi", "variety": "Byadgi"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 23800, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "31 Aug", "price": 24500, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "07 Sep", "price": 25100, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "14 Sep", "price": 25800, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "22 Sep", "price": 26500, "market": "Byadgi Mandi", "variety": "Byadgi"}
            ],
            "3M": [
                {"date": "Jul", "price": 22500, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "Aug", "price": 24200, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "Sep", "price": 26500, "market": "Byadgi Mandi", "variety": "Byadgi"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 21000, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "Jan '26", "price": 22600, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "Apr '26", "price": 24100, "market": "Byadgi Mandi", "variety": "Byadgi"},
                {"date": "Sep '26", "price": 26500, "market": "Byadgi Mandi", "variety": "Byadgi"}
            ]
        },
        "Guntur Sannam": {
            "7D": [
                {"date": "16 Sep", "price": 16800, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "17 Sep", "price": 16950, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "18 Sep", "price": 17100, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "19 Sep", "price": 17200, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "20 Sep", "price": 17350, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "21 Sep", "price": 17400, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "22 Sep", "price": 17500, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"}
            ],
            "30D": [
                {"date": "24 Aug", "price": 15800, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "31 Aug", "price": 16200, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "07 Sep", "price": 16600, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "14 Sep", "price": 17000, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "22 Sep", "price": 17500, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"}
            ],
            "3M": [
                {"date": "Jul", "price": 15200, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "Aug", "price": 16200, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "Sep", "price": 17500, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"}
            ],
            "1Y": [
                {"date": "Oct '25", "price": 14500, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "Jan '26", "price": 15300, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "Apr '26", "price": 16100, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"},
                {"date": "Sep '26", "price": 17500, "market": "Guntur Mirchi Yard", "variety": "Guntur Sannam"}
            ]
        }
    },
    "Cotton": {
        "7D": [
            {"date": "16 Sep", "price": 7180, "market": "Guntur APMC"},
            {"date": "17 Sep", "price": 7220, "market": "Guntur APMC"},
            {"date": "18 Sep", "price": 7300, "market": "Guntur APMC"},
            {"date": "19 Sep", "price": 7350, "market": "Guntur APMC"},
            {"date": "20 Sep", "price": 7390, "market": "Guntur APMC"},
            {"date": "21 Sep", "price": 7410, "market": "Guntur APMC"},
            {"date": "22 Sep", "price": 7450, "market": "Guntur APMC"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 6800, "market": "Guntur APMC"},
            {"date": "31 Aug", "price": 6950, "market": "Guntur APMC"},
            {"date": "07 Sep", "price": 7100, "market": "Guntur APMC"},
            {"date": "14 Sep", "price": 7250, "market": "Guntur APMC"},
            {"date": "22 Sep", "price": 7450, "market": "Guntur APMC"}
        ],
        "3M": [
            {"date": "Jul", "price": 6600, "market": "Guntur APMC"},
            {"date": "Aug", "price": 6950, "market": "Guntur APMC"},
            {"date": "Sep", "price": 7450, "market": "Guntur APMC"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 6400, "market": "Guntur APMC"},
            {"date": "Jan '26", "price": 6700, "market": "Guntur APMC"},
            {"date": "Apr '26", "price": 6900, "market": "Guntur APMC"},
            {"date": "Sep '26", "price": 7450, "market": "Guntur APMC"}
        ]
    },
    "Paddy": {
        "7D": [
            {"date": "16 Sep", "price": 2420, "market": "Tenali Market Yard"},
            {"date": "17 Sep", "price": 2430, "market": "Tenali Market Yard"},
            {"date": "18 Sep", "price": 2435, "market": "Tenali Market Yard"},
            {"date": "19 Sep", "price": 2440, "market": "Tenali Market Yard"},
            {"date": "20 Sep", "price": 2445, "market": "Tenali Market Yard"},
            {"date": "21 Sep", "price": 2445, "market": "Tenali Market Yard"},
            {"date": "22 Sep", "price": 2450, "market": "Tenali Market Yard"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 2380, "market": "Tenali Market Yard"},
            {"date": "31 Aug", "price": 2400, "market": "Tenali Market Yard"},
            {"date": "07 Sep", "price": 2415, "market": "Tenali Market Yard"},
            {"date": "14 Sep", "price": 2430, "market": "Tenali Market Yard"},
            {"date": "22 Sep", "price": 2450, "market": "Tenali Market Yard"}
        ],
        "3M": [
            {"date": "Jul", "price": 2320, "market": "APMC Benchmark"},
            {"date": "Aug", "price": 2390, "market": "APMC Benchmark"},
            {"date": "Sep", "price": 2450, "market": "APMC Benchmark"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 2200, "market": "APMC Benchmark"},
            {"date": "Jan '26", "price": 2280, "market": "APMC Benchmark"},
            {"date": "Apr '26", "price": 2350, "market": "APMC Benchmark"},
            {"date": "Sep '26", "price": 2450, "market": "APMC Benchmark"}
        ]
    },
    "Onion": {
        "7D": [
            {"date": "16 Sep", "price": 2100, "market": "Kurnool Mandi"},
            {"date": "17 Sep", "price": 2050, "market": "Kurnool Mandi"},
            {"date": "18 Sep", "price": 2020, "market": "Kurnool Mandi"},
            {"date": "19 Sep", "price": 1990, "market": "Kurnool Mandi"},
            {"date": "20 Sep", "price": 1970, "market": "Kurnool Mandi"},
            {"date": "21 Sep", "price": 1960, "market": "Kurnool Mandi"},
            {"date": "22 Sep", "price": 1950, "market": "Kurnool Mandi"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 2300, "market": "Kurnool Mandi"},
            {"date": "31 Aug", "price": 2240, "market": "Kurnool Mandi"},
            {"date": "07 Sep", "price": 2150, "market": "Kurnool Mandi"},
            {"date": "14 Sep", "price": 2050, "market": "Kurnool Mandi"},
            {"date": "22 Sep", "price": 1950, "market": "Kurnool Mandi"}
        ],
        "3M": [
            {"date": "Jul", "price": 2100, "market": "Kurnool Mandi"},
            {"date": "Aug", "price": 2400, "market": "Kurnool Mandi"},
            {"date": "Sep", "price": 1950, "market": "Kurnool Mandi"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 1600, "market": "Kurnool Mandi"},
            {"date": "Jan '26", "price": 1750, "market": "Kurnool Mandi"},
            {"date": "Apr '26", "price": 2000, "market": "Kurnool Mandi"},
            {"date": "Sep '26", "price": 1950, "market": "Kurnool Mandi"}
        ]
    },
    "Maize": {
        "7D": [
            {"date": "16 Sep", "price": 2150, "market": "Nizamabad Yard"},
            {"date": "17 Sep", "price": 2180, "market": "Nizamabad Yard"},
            {"date": "18 Sep", "price": 2190, "market": "Nizamabad Yard"},
            {"date": "19 Sep", "price": 2210, "market": "Nizamabad Yard"},
            {"date": "20 Sep", "price": 2220, "market": "Nizamabad Yard"},
            {"date": "21 Sep", "price": 2240, "market": "Nizamabad Yard"},
            {"date": "22 Sep", "price": 2250, "market": "Nizamabad Yard"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 2050, "market": "Nizamabad Yard"},
            {"date": "31 Aug", "price": 2100, "market": "Nizamabad Yard"},
            {"date": "07 Sep", "price": 2140, "market": "Nizamabad Yard"},
            {"date": "14 Sep", "price": 2190, "market": "Nizamabad Yard"},
            {"date": "22 Sep", "price": 2250, "market": "Nizamabad Yard"}
        ],
        "3M": [
            {"date": "Jul", "price": 1980, "market": "APMC Benchmark"},
            {"date": "Aug", "price": 2090, "market": "APMC Benchmark"},
            {"date": "Sep", "price": 2250, "market": "APMC Benchmark"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 1850, "market": "APMC Benchmark"},
            {"date": "Jan '26", "price": 1950, "market": "APMC Benchmark"},
            {"date": "Apr '26", "price": 2080, "market": "APMC Benchmark"},
            {"date": "Sep '26", "price": 2250, "market": "APMC Benchmark"}
        ]
    },
    "Groundnut": {
        "7D": [
            {"date": "16 Sep", "price": 6480, "market": "Kurnool Mandi"},
            {"date": "17 Sep", "price": 6510, "market": "Kurnool Mandi"},
            {"date": "18 Sep", "price": 6550, "market": "Kurnool Mandi"},
            {"date": "19 Sep", "price": 6590, "market": "Kurnool Mandi"},
            {"date": "20 Sep", "price": 6610, "market": "Kurnool Mandi"},
            {"date": "21 Sep", "price": 6630, "market": "Kurnool Mandi"},
            {"date": "22 Sep", "price": 6650, "market": "Kurnool Mandi"}
        ],
        "30D": [
            {"date": "24 Aug", "price": 6200, "market": "Kurnool Mandi"},
            {"date": "31 Aug", "price": 6320, "market": "Kurnool Mandi"},
            {"date": "07 Sep", "price": 6450, "market": "Kurnool Mandi"},
            {"date": "14 Sep", "price": 6550, "market": "Kurnool Mandi"},
            {"date": "22 Sep", "price": 6650, "market": "Kurnool Mandi"}
        ],
        "3M": [
            {"date": "Jul", "price": 6100, "market": "APMC Benchmark"},
            {"date": "Aug", "price": 6350, "market": "APMC Benchmark"},
            {"date": "Sep", "price": 6650, "market": "APMC Benchmark"}
        ],
        "1Y": [
            {"date": "Oct '25", "price": 5800, "market": "APMC Benchmark"},
            {"date": "Jan '26", "price": 6050, "market": "APMC Benchmark"},
            {"date": "Apr '26", "price": 6250, "market": "APMC Benchmark"},
            {"date": "Sep '26", "price": 6650, "market": "APMC Benchmark"}
        ]
    }
}

# ----------------- Weather & Advisory Data -----------------
WEATHER_DATA = {
    "Guntur": {"temp": "29°C", "condition": "Partly Cloudy", "humidity": "72%", "rain_chance": "30%", "wind": "12 km/h S", "advisory": "Favorable spray window before 11:00 AM. Avoid evening pesticide application due to 30% rain likelihood."},
    "Krishna": {"temp": "31°C", "condition": "Partly Cloudy", "humidity": "74%", "rain_chance": "25%", "wind": "14 km/h SE", "advisory": "Optimal conditions for harvesting early vegetables. Maintain scheduled drip irrigation."},
    "default": {"temp": "29°C", "condition": "Partly Cloudy", "humidity": "72%", "rain_chance": "30%", "wind": "12 km/h", "advisory": "Favorable spray window before 11:00 AM. Maintain balanced soil moisture."}
}

# ----------------- Profile Endpoints -----------------

@app.get("/api/profile")
def get_profile():
    return current_profile

@app.post("/api/profile")
def update_profile(profile_data: FarmerProfile):
    # Required field validation
    if not profile_data.name.strip():
        raise HTTPException(status_code=400, detail="Farmer name is required.")
    
    # Synchronize farm_location and location
    if profile_data.farm_location.strip() and not profile_data.location.strip():
        profile_data.location = profile_data.farm_location.strip()
    elif profile_data.location.strip() and not profile_data.farm_location.strip():
        profile_data.farm_location = profile_data.location.strip()

    if not profile_data.farm_location.strip() and not profile_data.location.strip():
        raise HTTPException(status_code=400, detail="Farm location is required.")
    if not profile_data.crops or len([c for c in profile_data.crops if c.strip()]) == 0:
        raise HTTPException(status_code=400, detail="At least one main crop is required.")
    if not profile_data.farm_size.strip():
        raise HTTPException(status_code=400, detail="Farm size is required.")

    global current_profile
    current_profile = profile_data
    current_profile.completed = True
    save_profile_to_disk(current_profile)
    return {"status": "success", "message": "Farmer profile saved successfully", "profile": current_profile}

@app.post("/api/profile/reset")
def reset_profile():
    global current_profile
    current_profile = FarmerProfile()
    current_profile.completed = False
    save_profile_to_disk(current_profile)
    return {"status": "success", "message": "Profile reset to blank for first-time onboarding test.", "profile": current_profile}

class FarmLocationUpdateRequest(BaseModel):
    farm_location: str
    farm_location_details: Optional[Dict[str, Any]] = None

@app.post("/api/location/farm")
def update_farm_location(req: FarmLocationUpdateRequest):
    """Save or update farm location independently from device location."""
    global current_profile
    if not req.farm_location.strip():
        raise HTTPException(status_code=400, detail="Farm location cannot be empty.")
    current_profile.farm_location = req.farm_location.strip()
    current_profile.location = req.farm_location.strip()
    if req.farm_location_details:
        current_profile.farm_location_details = req.farm_location_details
    save_profile_to_disk(current_profile)
    return {
        "status": "success",
        "message": "Farm location updated successfully",
        "farm_location": current_profile.farm_location,
        "profile": current_profile
    }

@app.post("/api/location/device")
def update_device_location(loc: LocationContext):
    """Update current device location from GPS. NEVER overwrites farm location."""
    global current_profile
    current_profile.device_location = loc
    current_profile.gps_location = loc
    # Strictly preserve farm_location
    save_profile_to_disk(current_profile)
    return {
        "status": "success",
        "message": "Device location updated",
        "device_location": loc,
        "farm_location": current_profile.farm_location
    }

@app.get("/api/location/search")
def search_locations_endpoint(q: str = ""):
    """Search agricultural locations across India (village, mandal, district, state)."""
    results = market_service.search_locations(q)
    return {"status": "success", "count": len(results), "data": results}

# ----------------- Market & Weather Services & Endpoints -----------------

def get_historical_data_for(crop: str, variety: Optional[str] = None):
    crop_data = HISTORICAL_PRICE_DATA.get(crop, HISTORICAL_PRICE_DATA.get("Tomato", {}))
    if variety and variety.strip().lower() not in ["all", "all chilli", "all varieties", ""]:
        v_clean = variety.strip().lower()
        for k, v in crop_data.items():
            if k.lower() == v_clean or v_clean in k.lower():
                return v
    if "all" in crop_data and isinstance(crop_data["all"], dict):
        return crop_data["all"]
    return crop_data

def query_market_data(
    crop: Optional[str] = None, 
    location: Optional[str] = None,
    date: Optional[str] = None,
    variety: Optional[str] = None
):
    selected_crop = crop.capitalize() if crop else "Tomato"
    for k in ["Tomato", "Chilli", "Cotton", "Paddy", "Onion", "Maize", "Groundnut"]:
        if k.lower() == selected_crop.lower():
            selected_crop = k
            break
    else:
        selected_crop = "Tomato"

    # All records for this crop
    matching_crop_records = [
        m for m in MANDI_PRICES 
        if selected_crop.lower() in m["crop"].lower()
    ]
    if not matching_crop_records:
        matching_crop_records = [m for m in MANDI_PRICES if m["crop"] == "Tomato"]
        selected_crop = "Tomato"

    # Varieties available for this crop
    available_varieties = sorted(list({m["variety"] for m in matching_crop_records if m.get("variety")}))

    # Filter by date if specified (default: 'yesterday' or 'all')
    results = matching_crop_records
    date_clean = (date or "Yesterday").strip().lower()
    if date_clean in ["yesterday", "22 sep", "22 sep 2026", "2026-09-22"]:
        results = [m for m in results if m.get("date_label", "").lower() == "yesterday" or "22 sep" in m.get("date", "").lower()]
    elif date_clean in ["today", "23 sep", "23 sep 2026", "2026-09-23"]:
        results = [m for m in results if m.get("date_label", "").lower() == "today" or "23 sep" in m.get("date", "").lower()]
    elif date_clean in ["last 7 days", "all"]:
        results = matching_crop_records

    # Filter by variety if specified and not 'all'
    variety_unavailable = False
    requested_variety = None
    if variety and variety.strip().lower() not in ["all", "all chilli", "all varieties", ""]:
        requested_variety = variety.strip()
        var_filtered = [
            m for m in results 
            if requested_variety.lower() == m.get("variety", "").lower() or requested_variety.lower() in m.get("variety", "").lower()
        ]
        if not var_filtered:
            # ZERO FABRICATION: Do NOT substitute with another variety!
            results = []
            variety_unavailable = True
        else:
            results = var_filtered

    # Filter by location if specified
    if location and location.strip().lower() not in ["all", "all markets", ""]:
        loc_lower = location.strip().lower()
        direct_matches = [
            m for m in results 
            if loc_lower in m["market"].lower() or loc_lower in m["district"].lower() or loc_lower in m["state"].lower() or
               m["market"].lower() in loc_lower or m["district"].lower() in loc_lower
        ]
        if direct_matches:
            results = direct_matches
        else:
            # Check village/mandal mapped to district, state, or nearest mandi
            from market_service import search_locations
            loc_matches = search_locations(loc_lower, limit=1)
            if loc_matches:
                top_m = loc_matches[0]
                dist = (top_m.get("district") or "").lower()
                st = (top_m.get("state") or "").lower()
                nm = (top_m.get("nearest_market") or "").lower()
                geo_matches = [
                    m for m in results 
                    if (nm and nm in m["market"].lower()) or (dist and dist in m["district"].lower()) or (st and st in m["state"].lower())
                ]
                if geo_matches:
                    results = geo_matches


    # Deterministic sorting: Modal Price DESCENDING, secondary sort by Market name ASCENDING
    sorted_results = sorted(results, key=lambda x: (-x["modal_price"], x["market"]))

    # Add dynamic rank attribute (1-indexed)
    ranked_results = []
    for rank, item in enumerate(sorted_results, 1):
        item_copy = dict(item)
        item_copy["rank"] = rank
        ranked_results.append(item_copy)

    # Spread calculations
    if ranked_results:
        highest_market = ranked_results[0]
        lowest_market = ranked_results[-1]
        diff = highest_market["modal_price"] - lowest_market["modal_price"]
        pct_diff = round((diff / lowest_market["modal_price"]) * 100, 2) if lowest_market["modal_price"] > 0 else 0
        spread_data = {
            "highest_price": highest_market["modal_price"],
            "highest_market": highest_market["market"],
            "highest_district": highest_market["district"],
            "lowest_price": lowest_market["modal_price"],
            "lowest_market": lowest_market["market"],
            "lowest_district": lowest_market["district"],
            "difference": diff,
            "percentage_difference": pct_diff
        }
    else:
        spread_data = {
            "highest_price": 0,
            "highest_market": None,
            "highest_district": None,
            "lowest_price": 0,
            "lowest_market": None,
            "lowest_district": None,
            "difference": 0,
            "percentage_difference": 0
        }

    # Varieties comparison summary (for optional 'Compare Varieties' feature)
    varieties_comparison = []
    comparison_date_label = date_clean if date_clean in ["today", "yesterday"] else "yesterday"
    date_records_for_crop = [m for m in matching_crop_records if m.get("date_label", "").lower() == comparison_date_label]
    for var_name in available_varieties:
        var_items = [m for m in date_records_for_crop if m.get("variety", "").lower() == var_name.lower()]
        if var_items:
            best = max(var_items, key=lambda x: x["modal_price"])
            varieties_comparison.append({
                "variety": var_name,
                "crop": selected_crop,
                "modal_price": best["modal_price"],
                "min_price": best["min_price"],
                "max_price": best["max_price"],
                "market": best["market"],
                "district": best["district"],
                "date": best["date"],
                "arrivals": best["arrivals"],
                "trend": best.get("trend", "stable")
            })

    varieties_comparison = sorted(varieties_comparison, key=lambda x: -x["modal_price"])

    history = get_historical_data_for(selected_crop, requested_variety)

    display_title = f"{selected_crop.upper()} — {requested_variety}" if (requested_variety and not variety_unavailable) else selected_crop.upper()

    return {
        "status": "success",
        "crop": selected_crop,
        "variety_selected": requested_variety or "all",
        "display_title": display_title,
        "date_selected": date or "Yesterday",
        "data": ranked_results,
        "all_records": matching_crop_records,
        "spread": spread_data,
        "varieties": available_varieties,
        "varieties_comparison": varieties_comparison,
        "history": history,
        "variety_unavailable": variety_unavailable,
        "source": "Agmarknet APMC Daily Report (Demo)",
        "freshness": "DEMO APMC DATA"
    }

@app.get("/api/market")
def get_market_prices(
    crop: Optional[str] = None, 
    location: Optional[str] = None,
    date: Optional[str] = None,
    variety: Optional[str] = None
):
    return query_market_data(crop, location, date, variety)

@app.get("/api/market/latest")
def get_latest_market_endpoint(
    crop: Optional[str] = "Chilli",
    variety: Optional[str] = None,
    location: Optional[str] = None
):
    return market_service.getLatestMarketPrices(crop=crop or "Chilli", variety=variety, location=location)

@app.get("/api/market/highest")
def get_highest_market_endpoint(
    crop: Optional[str] = "Chilli",
    variety: Optional[str] = None,
    date: Optional[str] = "Yesterday"
):
    highest = market_service.getHighestPriceMarket(crop=crop or "Chilli", variety=variety, date=date or "Yesterday")
    if not highest:
        return {"status": "unavailable", "message": "Price data currently unavailable"}
    return {"status": "success", "data": highest}

@app.get("/api/market/compare")
def get_compare_market_endpoint(
    crop: Optional[str] = "Chilli",
    variety: Optional[str] = None,
    date: Optional[str] = "Yesterday"
):
    return market_service.compareMarketPrices(crop=crop or "Chilli", variety=variety, date=date or "Yesterday")

@app.get("/api/market/spread")
def get_spread_market_endpoint(
    crop: Optional[str] = "Chilli",
    variety: Optional[str] = None,
    date: Optional[str] = "Yesterday"
):
    return market_service.getMarketPriceSpread(crop=crop or "Chilli", variety=variety, date=date or "Yesterday")

@app.get("/api/market/history")
def get_history_market_endpoint(
    crop: Optional[str] = "Chilli",
    variety: Optional[str] = None,
    range: Optional[str] = "7D"
):
    return market_service.getMarketPriceHistory(crop=crop or "Chilli", variety=variety, range_key=range)

@app.get("/api/weather")
def get_weather(location: Optional[str] = None):
    loc_key = "default"
    if location:
        for key in WEATHER_DATA:
            if key.lower() in location.lower():
                loc_key = key
                break
    loc_display = location.strip() if (location and location.strip()) else "Farm Location"
    return {
        "status": "success",
        "location": loc_display,
        "data": WEATHER_DATA.get(loc_key, WEATHER_DATA["default"]),
        "forecast_5_days": [
            {"day": "Today", "temp": "29°C / 23°C", "condition": "Partly Cloudy", "rain": "30%", "icon": "⛅"},
            {"day": "Tomorrow", "temp": "31°C / 24°C", "condition": "Sunny with clouds", "rain": "20%", "icon": "🌤️"},
            {"day": "Day 3", "temp": "28°C / 22°C", "condition": "Scattered Showers", "rain": "65%", "icon": "🌧️"},
            {"day": "Day 4", "temp": "27°C / 22°C", "condition": "Rain & Thunder", "rain": "80%", "icon": "⛈️"},
            {"day": "Day 5", "temp": "30°C / 23°C", "condition": "Clear Sky", "rain": "15%", "icon": "☀️"},
        ]
    }

CROP_ADVISORIES = {
    "Chilli": {
        "pest": "Thrips & Mites (Sucking Pests) causing upward leaf curling and yellowing",
        "solution": "1. Spray Neem Oil (10,000 ppm) @ 2 ml/L as organic deterrent.\n2. In severe infestation, spray Fipronil 5% SC @ 2 ml/L or Acetamiprid 20% SP @ 0.5 g/L.",
        "chemical": "Fipronil 5% SC @ 2 ml/L or Acetamiprid 20% SP @ 0.5 g/L on lower leaf surface",
        "organic": "Neem Oil (10,000 ppm) @ 2 ml/L or Verticillium lecanii @ 5 g/L in evening",
        "fertilizer": "Apply 0:52:34 @ 5 g/L with micronutrient Boron to prevent flower drop."
    },
    "Tomato": {
        "pest": "Tomato Leaf Curl Virus (transmitted by Whiteflies) and Early Blight",
        "solution": "1. Install yellow sticky traps (15-20 traps/acre).\n2. Spray Neem formulation (10,000 ppm) @ 2 ml/L or Imidacloprid 17.8% SL @ 0.5 ml/L.",
        "chemical": "Imidacloprid 17.8% SL @ 0.5 ml/L or Cyantraniliprole 10.26% OD @ 1.8 ml/L",
        "organic": "Neem Oil @ 2 ml/L or microbial spray of Beauveria bassiana",
        "fertilizer": "Apply 19:19:19 @ 5 g/L + Calcium Nitrate @ 2 g/L for fruit firmness."
    },
    "Cotton": {
        "pest": "Pink Bollworm and Whitefly",
        "solution": "1. Install Pheromone traps @ 5/acre.\n2. Spray Neem seed kernel extract (NSKE 5%) or Chlorantraniliprole 18.5% SC @ 0.3 ml/L.",
        "chemical": "Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L",
        "organic": "NSKE 5% or Trichogramma egg parasitoids release",
        "fertilizer": "Foliar spray of 2% DAP or Potassium Nitrate (13:0:45) @ 10 g/L."
    },
    "Rice": {
        "pest": "Stem Borer and Leaf Folder",
        "solution": "1. Release Trichogramma japonicum @ 40,000/acre.\n2. Spray Cartap Hydrochloride 50% SP @ 2 g/L or Chlorantraniliprole 0.4% GR.",
        "chemical": "Cartap Hydrochloride 50% SP @ 2 g/L or Chlorantraniliprole 18.5% SC @ 0.3 ml/L",
        "organic": "Azadirachtin 1% @ 2 ml/L or Pseudomonas fluorescens @ 2.5 kg/ha",
        "fertilizer": "Top dress Urea @ 25 kg/acre with Potash (MOP) @ 15 kg/acre at panicle initiation."
    }
}

@app.get("/api/crops")
def get_crop_advisories(crop: Optional[str] = None):
    farm_crops = [
        {
            "crop": "Rice",
            "icon": "🌾",
            "variety": "BPT-5204 (Samba Mahsuri)",
            "growth_stage": "Vegetative Stage",
            "health_status": "Healthy",
            "planting_date": "10 Aug 2026 (41 days ago)",
            "area": "1.5 Acres",
            "current_alert": "Monitor water depth at 2-3 cm. No blast symptoms detected.",
            "irrigation": "Maintain shallow standing water during active tillering.",
            "nutrients": "Apply second split of Nitrogen (Urea @ 25 kg/acre) this week."
        },
        {
            "crop": "Chilli",
            "icon": "🌶️",
            "variety": "Teja Deluxe",
            "growth_stage": "Flowering Stage",
            "health_status": "Needs attention",
            "planting_date": "25 Jul 2026 (57 days ago)",
            "area": "1.0 Acre",
            "current_alert": "Thrips and mite surveillance needed; slight leaf curl observed.",
            "irrigation": "Light alternate day drip irrigation; avoid pooling around stems.",
            "nutrients": "Spray 0:52:34 @ 5g/L with micronutrient Boron to prevent flower drop."
        },
        {
            "crop": "Tomato",
            "icon": "🍅",
            "variety": "Hybrid US-440",
            "growth_stage": "Fruiting Stage",
            "health_status": "Healthy",
            "planting_date": "05 Aug 2026 (46 days ago)",
            "area": "0.5 Acre",
            "current_alert": "Fruit borer pheromone traps operational. Fruit setting is excellent.",
            "irrigation": "Regular drip at 4 liters/plant every alternate morning.",
            "nutrients": "Potassium Nitrate (13:0:45) fertigation @ 2kg/acre for fruit sizing."
        }
    ]
    if crop:
        filtered = [c for c in farm_crops if crop.lower() in c["crop"].lower()]
        if filtered:
            return {"status": "success", "data": filtered}
    return {"status": "success", "data": farm_crops}

# ----------------- Location & Proximity Services -----------------

class LocationResolveRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None

@app.post("/api/location/resolve")
def resolve_location(req: LocationResolveRequest):
    """Resolve browser GPS coordinates to official APMC district and nearby markets."""
    res = market_service.resolve_coordinates_to_district(req.latitude, req.longitude)
    if req.accuracy is not None:
        res["accuracy"] = req.accuracy
    res["captured_at"] = time.time()
    res["status"] = "success"
    res["data"] = dict(res)
    return res

@app.get("/api/market/nearby")
def get_nearby_markets(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    crop: Optional[str] = None,
    max_km: float = 250.0
):
    """List APMC markets ranked by physical distance from coordinates."""
    actual_lat = latitude if latitude is not None else lat
    actual_lon = longitude if longitude is not None else lon
    if actual_lat is None or actual_lon is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude coordinates are required.")
    mandis = market_service.find_nearby_mandis(actual_lat, actual_lon, crop=crop, max_km=max_km)
    return {"status": "success", "count": len(mandis), "data": mandis, "mandis": mandis}

# ----------------- AI Chat & Personalization Engine -----------------

class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None
    action: Optional[str] = None
    profile: Optional[FarmerProfile] = None
    lang: Optional[str] = "en"
    conversation_id: Optional[str] = None
    location: Optional[LocationContext] = None
    device_location: Optional[LocationContext] = None
    farm_location: Optional[str] = None

def resolve_chat_profile(req_profile: Optional[FarmerProfile], req_farm_loc: Optional[str]) -> FarmerProfile:
    """Seamlessly preserve farmer's saved profile crops and location across chat turns."""
    if req_profile and (req_profile.crops or req_profile.main_crop):
        profile = req_profile.model_copy()
    elif current_profile and (current_profile.crops or current_profile.main_crop):
        profile = current_profile.model_copy()
    elif req_profile:
        profile = req_profile.model_copy()
    else:
        profile = current_profile or load_profile()

    if req_farm_loc and not profile.farm_location:
        profile.farm_location = req_farm_loc
    if profile.farm_location and not profile.location:
        profile.location = profile.farm_location
    elif profile.location and not profile.farm_location:
        profile.farm_location = profile.location

    return profile

@app.post("/api/chat")
def process_chat(req: ChatRequest):
    profile = resolve_chat_profile(req.profile, req.farm_location)

    device_loc = req.device_location or req.location
    device_loc_dict = device_loc.model_dump() if device_loc else (profile.device_location.model_dump() if getattr(profile, "device_location", None) else None)
    farm_loc_str = profile.farm_location or profile.location or ""

    return AIAgent.process(
        message=req.message,
        conversation_id=req.conversation_id,
        image_base64=req.image,
        profile=profile,
        lang=req.lang or "te",
        location=device_loc_dict,
        device_location=device_loc_dict,
        farm_location=farm_loc_str
    )

@app.post("/api/chat/stream")
async def process_chat_stream(req: ChatRequest):
    profile = resolve_chat_profile(req.profile, req.farm_location)

    device_loc = req.device_location or req.location
    device_loc_dict = device_loc.model_dump() if device_loc else (profile.device_location.model_dump() if getattr(profile, "device_location", None) else None)
    farm_loc_str = profile.farm_location or profile.location or ""

    return StreamingResponse(
        AIAgent.process_stream(
            message=req.message,
            conversation_id=req.conversation_id,
            image_base64=req.image,
            profile=profile,
            lang=req.lang or "te",
            location=device_loc_dict,
            device_location=device_loc_dict,
            farm_location=farm_loc_str
        ),
        media_type="text/event-stream"
    )


# ----------------- Network & Mobile Access Info -----------------
import socket

def get_local_ip() -> str:
    """Detect local IPv4 address on the current network interface."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

TUNNEL_INFO_FILE = os.path.join(DATA_DIR, "tunnel_info.json")

def get_public_url() -> str:
    """Retrieve public HTTPS tunnel or Vercel production URL if available."""
    env_url = os.environ.get("PUBLIC_URL") or os.environ.get("TUNNEL_URL")
    if env_url:
        return env_url.strip()

    # Automatically detect Vercel production domain
    vercel_url = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL") or os.environ.get("VERCEL_URL")
    if vercel_url:
        v = vercel_url.strip()
        return v if v.startswith("http") else f"https://{v}"
    if os.path.exists(TUNNEL_INFO_FILE):
        try:
            with open(TUNNEL_INFO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("public_url"):
                    return data["public_url"].strip()
        except Exception:
            pass
    return "https://d7558ae162cd6a.lhr.life"

@app.get("/api/network-info")
def get_network_info():
    """Provides local Wi-Fi and public HTTPS tunnel endpoints for mobile access."""
    local_ip = get_local_ip()
    port = 8000
    local_url = f"http://{local_ip}:{port}"
    pub_url = get_public_url()
    preferred_url = pub_url if pub_url else local_url
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={preferred_url}"

    return {
        "local_ip": local_ip,
        "port": port,
        "local_url": local_url,
        "public_url": pub_url,
        "preferred_url": preferred_url,
        "qr_code_url": qr_code_url,
        "has_https": bool(pub_url and pub_url.startswith("https://"))
    }

# Mount static files for the frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(FRONTEND_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
