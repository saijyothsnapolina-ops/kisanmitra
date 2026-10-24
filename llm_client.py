"""
KisanMitra LLM Integration Client
Handles secure, zero-dependency communication with LLM providers (Google Gemini, OpenAI).
Includes robust error handling for missing keys, 401/403 authentication failures,
429 rate limits, and network timeouts without leaking secrets.
"""

import os
import re
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("kisanmitra.llm")


def load_env_file(filepath: Optional[str] = None) -> None:
    """
    Safely load key-value pairs from a .env file into os.environ
    without overwriting existing environment variables and without extra dependencies.
    """
    if not filepath:
        candidate_paths = [
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(__file__), ".env"),
            os.path.join(os.path.dirname(__file__), "..", ".env"),
        ]
        for p in candidate_paths:
            if os.path.isfile(p):
                filepath = p
                break

    if not filepath or not os.path.isfile(filepath):
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'").strip()
                    # Do not overwrite if already set in environment
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")


# Automatically attempt to load .env on module import
load_env_file()


def get_active_llm_config() -> Dict[str, Any]:
    """
    Detect the active LLM provider and API key from environment variables.
    Priority order:
    1. GEMINI_API_KEY or GOOGLE_API_KEY (Recommended: Free tier, high multilingual capability)
    2. OPENAI_API_KEY
    3. LLM_API_KEY (Auto-detects format)
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip() and not gemini_key.strip().startswith("your_"):
        return {
            "provider": "gemini",
            "api_key": gemini_key.strip(),
            "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            "is_configured": True
        }

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip() and not openai_key.strip().startswith("your_"):
        return {
            "provider": "openai",
            "api_key": openai_key.strip(),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "is_configured": True
        }

    generic_key = os.getenv("LLM_API_KEY")
    if generic_key and generic_key.strip() and not generic_key.strip().startswith("your_"):
        # Auto-detect if key is Google or OpenAI
        if generic_key.startswith("AIzaSy"):
            return {
                "provider": "gemini",
                "api_key": generic_key.strip(),
                "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                "is_configured": True
            }
        else:
            return {
                "provider": "openai",
                "api_key": generic_key.strip(),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "is_configured": True
            }

    return {
        "provider": None,
        "api_key": None,
        "model": None,
        "is_configured": False
    }


def build_system_prompt(lang: str = "en", farm_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Builds the agricultural system prompt grounding the AI in Indian farming knowledge,
    safe pesticide guidelines, and respectful multilingual tone.
    """
    context_str = ""
    if farm_context:
        crop = farm_context.get("crop", "")
        variety = farm_context.get("variety", "")
        location = farm_context.get("location", "")
        soil = farm_context.get("soil_type", "")
        stage = farm_context.get("growth_stage", "")

        parts = []
        if crop:
            parts.append(f"Primary Crop: {crop}" + (f" ({variety})" if variety else ""))
        if location:
            parts.append(f"Location: {location}")
        if soil:
            parts.append(f"Soil Type: {soil}")
        if stage:
            parts.append(f"Crop Stage: {stage}")

        if parts:
            context_str = "\nFarmer's Farm Context:\n- " + "\n- ".join(parts) + "\n"

    lang_instruction = {
        "te": "Respond in simple, clear, respectful Telugu (తెలుగు). Use natural agricultural vocabulary familiar to Andhra Pradesh and Telangana farmers.",
        "hi": "Respond in simple, clear, respectful Hindi (हिंदी). Use practical agricultural terminology familiar to Indian farmers.",
        "en": "Respond in simple, clear, practical English formatted cleanly with bullet points."
    }.get(lang, "Respond in the language requested by the user (Telugu, Hindi, or English).")

    return f"""You are KisanMitra (కిసాన్ మిత్ర / किसानमित्र), an intelligent and compassionate AI agricultural companion designed for Indian farmers.

Role and Principles:
1. Provide practical, field-proven agricultural guidance covering crop health, pest & disease identification, organic treatments, soil fertility, irrigation scheduling, and agronomic best practices.
2. Grounded and Truthful:
   - DO NOT fabricate fake market prices or false weather predictions. If asked about today's mandi price or live weather, provide general market wisdom and kindly advise the farmer to check the KisanMitra 'Market Prices' or 'Weather' tab for certified live APMC/IMD figures.
3. Pest & Disease Safety:
   - Prioritize Integrated Pest Management (IPM) and bio-pesticides (e.g., Neem oil / NSKE 5%, Trichoderma) first.
   - When suggesting chemical interventions, state standard approved dosages per liter of water (e.g., Fipronil 5% SC @ 2 ml/L) and include a brief safety reminder (wear mask/gloves, avoid spraying during high wind or midday heat).
4. Tone & Style:
   - Respectful, encouraging, concise, and structured (use bullet points and clear headings).
   - {lang_instruction}
{context_str}"""


def call_gemini(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    image_base64: Optional[str] = None,
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Calls Google Gemini REST API using standard requests.
    Supports multimodal vision when image_base64 is provided.
    """
    import requests

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Build parts
    parts: List[Dict[str, Any]] = []

    if image_base64:
        clean_base64 = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", image_base64.strip())
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": clean_base64
            }
        })

    parts.append({"text": user_prompt})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
            "topP": 0.8
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                return {"success": True, "text": text}
            return {"success": False, "error_type": "empty_response", "message": "No response generated by model."}

        elif response.status_code in [401, 403]:
            return {
                "success": False,
                "error_type": "auth_error",
                "status_code": response.status_code,
                "message": "Invalid or unauthorized API key. Please check your GEMINI_API_KEY in .env or Vercel settings."
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error_type": "rate_limit",
                "status_code": 429,
                "message": "Gemini API rate limit reached. Please wait a moment and try again."
            }
        else:
            return {
                "success": False,
                "error_type": "api_error",
                "status_code": response.status_code,
                "message": f"Gemini API returned HTTP status {response.status_code}."
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "timeout",
            "message": "Request to Gemini API timed out after 15 seconds."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error_type": "connection_error",
            "message": "Unable to connect to Gemini API. Please check your internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "unexpected_error",
            "message": f"Unexpected error while calling Gemini API: {type(e).__name__}"
        }


def call_openai(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    image_base64: Optional[str] = None,
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Calls OpenAI Chat Completions API using standard requests.
    """
    import requests

    endpoint = "https://api.openai.com/v1/chat/completions"

    user_content: Any = user_prompt
    if image_base64:
        clean_base64 = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", image_base64.strip())
        data_uri = f"data:image/jpeg;base64,{clean_base64}"
        user_content = [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": data_uri}}
        ]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "").strip()
                return {"success": True, "text": text}
            return {"success": False, "error_type": "empty_response", "message": "No response generated by model."}

        elif response.status_code in [401, 403]:
            return {
                "success": False,
                "error_type": "auth_error",
                "status_code": response.status_code,
                "message": "Invalid or unauthorized OpenAI API key. Please check your OPENAI_API_KEY."
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error_type": "rate_limit",
                "status_code": 429,
                "message": "OpenAI API rate limit or quota exceeded. Please check your account usage."
            }
        else:
            return {
                "success": False,
                "error_type": "api_error",
                "status_code": response.status_code,
                "message": f"OpenAI API returned HTTP status {response.status_code}."
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "timeout",
            "message": "Request to OpenAI API timed out after 15 seconds."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error_type": "connection_error",
            "message": "Unable to connect to OpenAI API. Please check your internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "unexpected_error",
            "message": f"Unexpected error while calling OpenAI API: {type(e).__name__}"
        }


def format_missing_key_guidance(lang: str = "en") -> Dict[str, str]:
    """
    Returns polite, clear guidance explaining that the LLM is not yet configured,
    and provides exact step-by-step instructions for adding the free Gemini API key.
    """
    if lang == "te":
        reply = (
            "⚠️ **AI లాంగ్వేజ్ మోడల్ ఇంకా అనుసంధానం చేయబడలేదు.**\n\n"
            "కిసాన్ మిత్ర పూర్తి సామర్థ్యంతో వ్యవసాయ సలహాలు అందించడానికి ఉచిత **Google Gemini API Key** అవసరం.\n\n"
            "**కీని ఎలా సెటప్ చేయాలి:**\n"
            "1. [aistudio.google.com](https://aistudio.google.com/) లో మీ Google ఖాతాతో లాగిన్ అయి ఉచిత API Key పొందండి (క్రెడిట్ కార్డ్ అవసరం లేదు).\n"
            "2. మీ ప్రాజెక్ట్ `.env` ఫైల్‌లో లేదా Vercel Environment Variables లో `GEMINI_API_KEY=మీ_కీ` జోడించండి.\n"
            "3. సర్వర్‌ను రీస్టార్ట్ చేయండి.\n\n"
            "💡 *గమనిక: అప్పటివరకు మార్కెట్ ధరలు, వాతావరణం, మరియు నిల్వ చేసిన పంట సలహాలు సాధారణంగా పనిచేస్తాయి.*"
        )
        spoken = "AI భాషా మోడల్ API కీ ఇంకా సెటప్ కాలేదు. దయచేసి .env ఫైల్‌లో జెమిని API కీని జోడించండి."
    elif lang == "hi":
        reply = (
            "⚠️ **एआई भाषा मॉडल अभी कॉन्फ़िगर नहीं किया गया है।**\n\n"
            "किसानमित्र से उन्नत कृषि सलाह प्राप्त करने के लिए निःशुल्क **Google Gemini API Key** की आवश्यकता है।\n\n"
            "**एपीआई की (API Key) कैसे सेट करें:**\n"
            "1. [aistudio.google.com](https://aistudio.google.com/) पर जाकर फ्री API Key बनाएं (क्रेडिट कार्ड की आवश्यकता नहीं)।\n"
            "2. अपने `.env` फाइल में या Vercel Environment Variables में `GEMINI_API_KEY=आपकी_कुंजी` जोड़ें।\n"
            "3. सर्वर को पुनः आरंभ करें।\n\n"
            "💡 *नोट: तब तक लाइव मंडी भाव, मौसम और स्थानीय डेटा सामान्य रूप से उपलब्ध रहेंगे।*"
        )
        spoken = "एआई एपीआई कुंजी अभी सेट नहीं है। कृपया .env में जेमिनी एपीआई की जोड़ें।"
    else:
        reply = (
            "⚠️ **AI Language Model API Key Not Configured.**\n\n"
            "To enable live generative farming advice and conversational reasoning, configure a free **Google Gemini API Key**.\n\n"
            "**Quick Setup Steps:**\n"
            "1. Get a free API key at [aistudio.google.com](https://aistudio.google.com/) (100% free, no credit card required).\n"
            "2. Add `GEMINI_API_KEY=your_key_here` to your `.env` file or Vercel Project Settings (`Environment Variables`).\n"
            "3. Restart the server.\n\n"
            "💡 *Note: Mandi market prices, agro-weather, and built-in diagnostic tools remain fully functional.*"
        )
        spoken = "AI API key is not yet configured. Please set GEMINI_API_KEY in your environment variables."

    return {"reply": reply, "spoken_text": spoken}


def generate_farming_response(
    user_prompt: str,
    lang: str = "en",
    farm_context: Optional[Dict[str, Any]] = None,
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    High-level entry point to generate a farming response from the active LLM.
    Handles:
    - Key detection (fallback to missing key guidance)
    - Multimodal support (if image provided)
    - Provider execution (Gemini / OpenAI)
    - Clean error handling (auth, rate limits, timeouts)
    """
    config = get_active_llm_config()

    if not config["is_configured"]:
        guidance = format_missing_key_guidance(lang)
        return {
            "success": False,
            "reply": guidance["reply"],
            "spoken_text": guidance["spoken_text"],
            "tool_used": "llm_unconfigured",
            "provider": None
        }

    system_prompt = build_system_prompt(lang=lang, farm_context=farm_context)
    provider = config["provider"]
    api_key = config["api_key"]
    model = config["model"]

    if provider == "gemini":
        result = call_gemini(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            image_base64=image_base64
        )
    elif provider == "openai":
        result = call_openai(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            image_base64=image_base64
        )
    else:
        guidance = format_missing_key_guidance(lang)
        return {
            "success": False,
            "reply": guidance["reply"],
            "spoken_text": guidance["spoken_text"],
            "tool_used": "llm_unconfigured",
            "provider": None
        }

    if result.get("success"):
        text = result.get("text", "").strip()
        # Create a concise spoken version (first 1-2 sentences without markdown)
        clean_text = re.sub(r"[\*#_`]", "", text)
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", clean_text) if s.strip()]
        spoken = ". ".join(sentences[:2]) + "." if sentences else clean_text[:120]

        return {
            "success": True,
            "reply": text,
            "spoken_text": spoken,
            "tool_used": f"{provider}_llm",
            "provider": provider,
            "model": model
        }
    else:
        # Handle specific error scenarios gracefully
        err_type = result.get("error_type")
        msg = result.get("message", "AI service encountered an error.")

        if err_type == "auth_error":
            if lang == "te":
                reply = "❌ **API Key ప్రమాణీకరణ విఫలమైంది.**\n\nఅందించిన API కీ చెల్లనిది లేదా గడువు ముగిసింది. దయచేసి `.env` లేదా Vercel లో `GEMINI_API_KEY` సరిగ్గా కాన్ఫిగర్ చేయబడిందో లేదో తనిఖీ చేయండి."
                spoken = "API కీ చెల్లనిది. దయచేసి మీ కాన్ఫిగరేషన్ తనిఖీ చేయండి."
            elif lang == "hi":
                reply = "❌ **एपीआई प्रमाणीकरण विफल रहा।**\n\nप्रदान की गई एपीआई कुंजी अमान्य या समाप्त हो गई है। कृपया `.env` या Vercel में `GEMINI_API_KEY` की जांच करें।"
                spoken = "एपीआई कुंजी अमान्य है। कृपया अपनी कॉन्फ़िगरेशन जांचें।"
            else:
                reply = "❌ **API Authentication Failed.**\n\nThe configured API key is invalid or unauthorized. Please verify your `GEMINI_API_KEY` in `.env` or Vercel Project Settings."
                spoken = "API authentication failed. Please verify your configured API key."

        elif err_type == "rate_limit":
            if lang == "te":
                reply = "⏳ **API అభ్యర్థనల పరిమితి దాటింది.**\n\nప్రస్తుతం AI సర్వర్లు ఎక్కువ రద్దీతో ఉన్నాయి. దయచేసి కాసేపటి తర్వాత మళ్లీ ప్రయత్నించండి."
                spoken = "API అభ్యర్థనల పరిమితి దాటింది. దయచేసి కాసేపటి తర్వాత ప్రయత్నించండి."
            elif lang == "hi":
                reply = "⏳ **एपीआई सीमा समाप्त हो गई है।**\n\nवर्तमान में एआई सर्वर व्यस्त हैं। कृपया कुछ क्षण बाद पुनः प्रयास करें।"
                spoken = "एपीआई सीमा समाप्त हो गई है। कृपया कुछ देर बाद प्रयास करें।"
            else:
                reply = "⏳ **AI Rate Limit Reached.**\n\nThe AI model is currently experiencing high request volume. Please wait a moment and try again."
                spoken = "AI rate limit reached. Please wait a moment and try again."

        elif err_type in ["timeout", "connection_error"]:
            if lang == "te":
                reply = "🌐 **నెట్‌వర్క్ కనెక్షన్ లోపం.**\n\nAI సర్వర్ స్పందించడానికి ఎక్కువ సమయం పట్టింది. దయచేసి మీ ఇంటర్నెట్ కనెక్షన్ తనిఖీ చేసి మళ్లీ ప్రయత్నించండి."
                spoken = "నెట్‌వర్క్ కనెక్షన్ సమస్య. దయచేసి మళ్లీ ప్రయత్నించండి."
            elif lang == "hi":
                reply = "🌐 **नेटवर्क कनेक्शन त्रुटि।**\n\nएआई सर्वर से संपर्क नहीं हो सका। कृपया अपना इंटरनेट कनेक्शन जांचें और पुनः प्रयास करें।"
                spoken = "नेटवर्क कनेक्शन समस्या। कृपया पुनः प्रयास करें।"
            else:
                reply = "🌐 **AI Service Connection Error.**\n\nUnable to reach the AI model service. Please check your internet connectivity and try again."
                spoken = "Connection error. Please check your network and try again."

        else:
            reply = f"⚠️ **AI Service Notice:** {msg}"
            spoken = "AI service notice. Please try again."

        return {
            "success": False,
            "reply": reply,
            "spoken_text": spoken,
            "tool_used": f"{provider}_error",
            "error_type": err_type
        }
