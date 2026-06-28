import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

load_dotenv()
from google import genai
from google.genai import types

# Teri purani calculation file se functions import ho rahe hain
from api.numerology_engine import (
    calculate_numerology,
    calculate_name_number,
    check_compatibility
)

app = FastAPI(title="Matrix Astro Full-Stack API")

# Frontend integration ke liye CORS enable kiya
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🧮 PURE PYTHON VEDIC RASHI ENGINE ---
RASHI_ALPHABETS = {
    "Aries (Mesh)": {"letters": ["A", "L", "E", "I", "O"], "ruler": "Mars (Mangal)", "lucky_num": 9},
    "Taurus (Vrishabha)": {"letters": ["B", "V", "U", "W"], "ruler": "Venus (Shukra)", "lucky_num": 6},
    "Gemini (Mithun)": {"letters": ["K", "CH", "G", "Q", "R"], "ruler": "Mercury (Budh)", "lucky_num": 5},
    "Cancer (Kark)": {"letters": ["DD", "H"], "ruler": "Moon (Chandra)", "lucky_num": 2},
    "Leo (Simha)": {"letters": ["M", "TT"], "ruler": "Sun (Surya)", "lucky_num": 1},
    "Virgo (Kanya)": {"letters": ["P", "T", "N", "SHA"], "ruler": "Mercury (Budh)", "lucky_num": 5},
    "Libra (Tula)": {"letters": ["R", "T"], "ruler": "Venus (Shukra)", "lucky_num": 6},
    "Scorpio (Vrishchik)": {"letters": ["N", "Y"], "ruler": "Mars (Mangal)", "lucky_num": 9},
    "Sagittarius (Dhanu)": {"letters": ["BH", "DH", "PH", "F"], "ruler": "Jupiter (Guru)", "lucky_num": 3},
    "Capricorn (Makar)": {"letters": ["KH", "J"], "ruler": "Saturn (Shani)", "lucky_num": 8},
    "Aquarius (Kumbh)": {"letters": ["G", "S", "SH"], "ruler": "Saturn (Shani)", "lucky_num": 8},
    "Pisces (Meen)": {"letters": ["D", "CH", "Z", "TH"], "ruler": "Jupiter (Guru)", "lucky_num": 3}
}

def calculate_rashi_internal(date_str, time_str):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        ref_date = datetime(2000, 1, 1, 0, 0)
        diff_days = (dt - ref_date).total_seconds() / 86400.0
        moon_cycle = 27.321661
        degrees = ((diff_days % moon_cycle) / moon_cycle) * 360.0
        rashi_idx = int(degrees / 30) % 12
        rashi_names = list(RASHI_ALPHABETS.keys())
        return {"rashi": rashi_names[rashi_idx], "details": RASHI_ALPHABETS[rashi_names[rashi_idx]]}
    except:
        return None

# --- 📑 DATA SCHEMAS ---
class FreeInput(BaseModel):
    name: str
    dob: str

class PremiumInput(BaseModel):
    name: str
    dob: str
    birth_time: str
    birth_place: str

@app.get("/")
def home():
    return {"status": "ONLINE", "message": "Astro Core API is running perfectly!"}


# =====================================================================
# 1. 🔥 FREE ENDPOINT: CRUNCHED & SHORT (Max 150 words)
# =====================================================================
@app.post("/predict")
def get_free_prediction(user_data: FreeInput):
    mool_bhag = calculate_numerology(user_data.dob)
    if mool_bhag is None:
        raise HTTPException(status_code=400, detail="DOB format galat hai!")
    
    name_num = calculate_name_number(user_data.name)
    num_data = {"Moolank": mool_bhag["Moolank"], "Bhagyank": mool_bhag["Bhagyank"], "Name_Number": name_num}
    comp_data = check_compatibility(num_data["Moolank"], num_data["Bhagyank"], num_data["Name_Number"])
    
    # SYSTEM PROMPT: AI ko strict order ki chhota aur teekha bolo
    FREE_SYSTEM_INSTRUCTION = """
    ROLE: You are a brutally honest Astro-Numerologist.
    TONE: Raw Hindi-English (Hinglish), witty, and ultra-punchy.
    
    CRITICAL RULE: Keep the total response strictly UNDER 150 words. Do NOT write long paragraphs. 
    Structure the response into exactly 3 quick, blunt bullet points:
    1. THE CORE PROBLEM: Tell them directly why their Name Number clashes with their Moolank/Bhagyank.
    2. THE CONSEQUENCE: Warn them how this clash is blocking their peace, money, or career right now.
    3. THE LOCKOUT: Tell them bluntly that the solution (remedy, rashi alphabets, lucky letters) is locked inside the Premium Report.
    
    End exactly at the cliffhanger. No solutions or remedies here.
    """
    
    user_context = f"Subject Name: {user_data.name}, DOB: {user_data.dob}, Moolank: {num_data['Moolank']}, Bhagyank: {num_data['Bhagyank']}, Name Number: {num_data['Name_Number']}. Status: {comp_data['status']}."
    
    try:
        # ⚠️ YAHAN APNI ASLI GEMINI API KEY PASTE KARNA
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=user_context,
            config=types.GenerateContentConfig(
                system_instruction=FREE_SYSTEM_INSTRUCTION, 
                temperature=0.85
            )
        )
        return {
            "user_info": {"name": user_data.name, "dob": user_data.dob}, 
            "numerology": num_data, 
            "compatibility": comp_data, 
            "raw_prediction": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# 2. 💎 PREMIUM ENDPOINT: DETAILED CAREER & NAME DECRYPTION (500+ words)
# =====================================================================
@app.post("/predict-premium")
def get_premium_prediction(user_data: PremiumInput):
    mool_bhag = calculate_numerology(user_data.dob)
    if mool_bhag is None:
        raise HTTPException(status_code=400, detail="DOB format galat hai!")
    
    name_num = calculate_name_number(user_data.name)
    num_data = {"Moolank": mool_bhag["Moolank"], "Bhagyank": mool_bhag["Bhagyank"], "Name_Number": name_num}
    
    rashi_data = calculate_rashi_internal(user_data.dob, user_data.birth_time)
    if rashi_data is None:
        raise HTTPException(status_code=400, detail="Birth Time input invalid hai.")
        
    # 🔥 FIXED SYSTEM PROMPT: Now strictly includes Career, Job Sector, and Financial Timeline!
    PREMIUM_SYSTEM_INSTRUCTION = """
    ROLE: You are an Elite Premium Astro-Numerologist, Cybernetic Career Forecaster & Quantum Consultant. 
    TONE: Deeply analytical, authoritative, sharp, and highly detailed Hinglish.
    
    CRITICAL RULE: This is a PAID premium report. The response must be highly DETAILED and exhaustive (around 500-600 words). 
    Break down the analysis into 4 clear, structured sections using professional neon headers:
    
    1. 📊 VEDIC MATRIX & QUANTUM ENERGY: Explain their Rashi, Nakshatra lord, and how their birth place and time coordinates affect their core personality.
    2. 💼 LIFEPATH & CAREER MATRIX (CAREER & JOB FOCUS): Detailed breakdown of their ideal Career Paths. Specify whether they are made for Technical Jobs (AI/ML, Software, Engineering), Government Sectors, Corporate Management, or Freelance Businesses. Tell them which specific job roles will bring the maximum money and when their high-growth financial timeline starts.
    3. 🔢 NUMEROLOGY & NAME MISMATCH: Detail the hidden connection between Moolank and Bhagyank, and explain why their current name creates a toxic obstacle in their Job/Business growth.
    4. ⚡ 3 PREMIUM NAME SUGGESTIONS FOR SUCCESS: Provide 3 ultra-modern, powerful names suited for high-growth tech/corporate sectors. For EACH name, explicitly show the Chaldean letter-by-letter math (e.g., A(1)+Y(1)...) to prove it equals their Target Lucky Number.
    
    Keep the tone extremely futuristic, hacker-style, and highly technical. Use neon themes in description.
    """
    
    # Pass all variables including birth_place to the context
    premium_context = f"""
    Current Name: {user_data.name}
    Calculated Janm Rashi: {rashi_data['rashi']}
    Rashi Ruler Planet: {rashi_data['details']['ruler']}
    Target Lucky Number for New Name: {rashi_data['details']['lucky_num']}
    Allowed Starting Letters: {', '.join(rashi_data['details']['letters'])}
    Moolank: {num_data['Moolank']}, Bhagyank: {num_data['Bhagyank']}
    Birth Time: {user_data.birth_time}
    Birth Place: {user_data.birth_place}
    """
    
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=premium_context,
            config=types.GenerateContentConfig(
                system_instruction=PREMIUM_SYSTEM_INSTRUCTION, 
                temperature=0.6  # Math aur analytics ekdum stable rakhne ke liye
            )
        )
        return {
            "vedic_metrics": {
                "rashi": rashi_data["rashi"],
                "ruler_planet": rashi_data["details"]["ruler"],
                "lucky_letters": rashi_data["details"]["letters"],
                "target_lucky_number": rashi_data["details"]["lucky_num"]
            },
            "premium_recommendation": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))