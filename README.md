# 🌾 KisanMitra - AI Farming Companion

KisanMitra is an intelligent AI agricultural companion designed for farmers across India. It features a modern **Chat-First** user flow where farmers immediately engage with the AI chatbot without upfront onboarding friction, with profile setup deferred until their first interaction.

---

## 🌟 Key Flow & UX Highlights

### 1. Initial Experience (Chat-First)
- Farmers land **directly on the AI chatbot screen**.
- The profile form is **never shown upfront** or as a blocking modal on page load.
- Farmers see the greeting, example questions, and quick actions:
  - 💰 **Market Prices**
  - 📈 **Price History**
  - 📍 **Compare Markets**
  - 🌦️ **Weather**
  - 🌱 **Crop Help**
  - 📷 **Analyze Crop Photo**
- Farmers immediately understand KisanMitra's capabilities before providing any personal details.

### 2. Profile Trigger & Query Preservation
- When an un-profiled farmer attempts to send their first chat message or tap a quick action:
  1. The interaction is **not sent to the AI yet**.
  2. The query is **safely preserved** in application state (`state.pendingMessage`).
  3. A friendly modal opens:
     > *"Before we start 🌾*  
     > *Tell me a little about your farm so I can give you more relevant information."*
  4. The modal displays a reassurance banner indicating their question is preserved and will be answered immediately after completion.

### 3. Profile Validation & Completion
- **Required Fields**:
  - Farmer Name
  - Location (Village, District, State)
  - Main Crop / Crops (with tap chips + custom input)
  - Farm Size (e.g. 3 Acres)
- **Optional Fields** (collapsible accordion; can be skipped without blocking):
  - Crop Variety
  - Soil Type
  - Irrigation Type
  - Current Crop Growth Stage
- Upon submission:
  - Profile is saved (`profileCompleted: true`).
  - Modal closes and farmer returns to the chatbot.
  - **The preserved question executes automatically! The farmer never has to re-type the question.**

### 4. Returning Farmers
- Returning farmers with a completed profile are never prompted with the setup modal.
- Messages send instantly with personalized farm context.
- Farmers can view and update their profile anytime from **Profile → Edit Profile**.

### 5. Secondary Profile Section & Main Navigation
Main navigation dock provides access to:
- 🤖 **Chat** (Default / Primary)
- 💰 **Market** (Live Mandi APMC rates, price ranges, arrivals, and trends)
- 🌦️ **Weather** (5-day agro-weather forecast with spraying/irrigation advisories)
- 🌱 **My Crops** (Stage-wise agronomy guidance and pest alerts)
- 👤 **Profile** (View profile, Edit profile, update farm size/crops, and Reset Profile Demo Mode)

### 6. AI Personalization Engine
Once the profile is completed, the AI assistant automatically incorporates the farmer's profile context:
- Query: *"Where is my crop getting the highest price?"*
  - Recognizes `crop = Tomato` and `location = Guntur` from farmer profile.
  - Compares nearby APMC markets (Guntur APMC, Vijayawada Mandi, Tenali Market Yard, Kolar APMC).
  - Highlights the highest price market and estimates net revenue gains for their farm size.

---

## 🚀 Running KisanMitra

### Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `pydantic`

### Start the Server
```bash
python app.py
```
Or with uvicorn:
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at:
```
http://localhost:8000
```

### Running Tests
```bash
python -m unittest tests/test_flow.py tests/test_e2e.py
```
