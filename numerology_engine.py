import os
from google import genai
from google.genai import types
def sum_digits_until_single(number):
    """Digits ko tab tak jodta hai jab tak single digit (1-9) na mil jaye."""
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number

def calculate_numerology(dob_str):
    """DOB (DD-MM-YYYY) se dynamic Moolank aur Bhagyank nikalta hai."""
    try:
        day, month, year = dob_str.split('-')
    except ValueError:
        return None

    moolank = sum_digits_until_single(int(day))
    full_dob_digits = day + month + year
    total_sum = sum(int(digit) for digit in full_dob_digits)
    bhagyank = sum_digits_until_single(total_sum)

    return {
        "Moolank": moolank,
        "Bhagyank": bhagyank
    }

# Chaldean Mapping Dictionary
CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

def calculate_name_number(name_str):
    """Dynamic name string se Chaldean Name Number nikalta hai."""
    cleaned_name = name_str.upper().replace(" ", "")
    total_sum = 0
    for char in cleaned_name:
        if char in CHALDEAN_MAP:
            total_sum += CHALDEAN_MAP[char]
    return sum_digits_until_single(total_sum)

# Enemy Mapping
ENEMY_MAP = {
    1: [8], 2: [4, 7, 8], 3: [6], 4: [1, 2, 9], 5: [],
    6: [3], 7: [1, 2], 8: [1, 2, 4, 9], 9: [4, 8]
}

def check_compatibility(moolank, bhagyank, name_number):
    """Calculated dynamic numbers ke beech dushmani check karta hai."""
    conflicts = []
    if name_number in ENEMY_MAP.get(moolank, []):
        conflicts.append(f"Name Number ({name_number}) aur Moolank ({moolank}) aapas mein dushman hain.")
    if name_number in ENEMY_MAP.get(bhagyank, []):
        conflicts.append(f"Name Number ({name_number}) aur Bhagyank ({bhagyank}) aapas mein dushman hain.")

    if conflicts:
        return {
            "status": "DUSHMANI (Anti-Number)",
            "details": conflicts,
            "advice": "Bhai, is bande ke naam ki spelling badalna zaroori hai, luck block ho raha hai."
        }
    else:
        return {
            "status": "DOSTI YA NEUTRAL",
            "details": ["Naam aur DOB mein koi bada 36 ka aakda nahi hai. Sab sahi hai."],
            "advice": "Spelling ekdum perfect hai, koi badlaav ki zaroorat nahi hai."
        }

def generate_ai_prompt(user_name, dob, numerology_data, compatibility_data):
    """Dynamic data ko prompt frame mein convert karta hai."""
    system_instruction = """
    ROLE: You are an elite, raw, and brutally honest Vedic & Numerology Astrologer. 
    TONE: Use raw Hindi-English (Hinglish). Be direct, witty, and slightly blunt. Strictly NO sugarcoating. 
    INSTRUCTION: Read the calculated numerology and compatibility data of the user. Give a highly detailed future prediction, career advice (Job vs Business), and name compatibility reality check based ONLY on the provided numbers. Do not hallucinate or invent new planetary configurations.
    """
    
    user_context = f"""
    --- USER ASTRO DATA ---
    User Name: {user_name}
    Date of Birth: {dob}
    Moolank: {numerology_data['Moolank']}
    Bhagyank: {numerology_data['Bhagyank']}
    Name Number: {numerology_data['Name_Number']}
    
    Compatibility Status: {compatibility_data['status']}
    Compatibility Details: {', '.join(compatibility_data['details'])}
    Core Advice: {compatibility_data['advice']}
    -----------------------
    
    Bhai, ab is bande ka full detail mein bhavishya batao. Career, Paisa, Persona, aur Name change ki real advice do.
    """
    return {"system_instruction": system_instruction, "user_context": user_context}


# --- 🔥 LIVE USER INPUT & AI GENERATION ---
if __name__ == "__main__":
    print("=== WELCOME TO AI ASTROLOGY ENGINE ===")
    
    # User se live data lena
    user_name = input("Apna Full Name daalo: ")
    user_dob = input("Apna DOB daalo (Format: DD-MM-YYYY, jaise 29-11-2007): ")
    
    # 1. Dynamic Calculations
    mool_bhag = calculate_numerology(user_dob)
    
    if mool_bhag is None:
        print("Bhai, DOB format galat hai! Program ko firse chalao.")
    else:
        name_num = calculate_name_number(user_name)
        
        num_data = {
            "Moolank": mool_bhag["Moolank"],
            "Bhagyank": mool_bhag["Bhagyank"],
            "Name_Number": name_num
        }
        
        # 2. Dynamic Compatibility Check
        comp_data = check_compatibility(num_data["Moolank"], num_data["Bhagyank"], num_data["Name_Number"])
        
        # 3. Dynamic Prompt Generation
        final_prompt = generate_ai_prompt(user_name, user_dob, num_data, comp_data)
        
        print("\n[AI Connecting...] Kundali aur Numbers ka sach nikala jaa raha hai...\n")
        
        # 4. Gemini API Connection
        # Yeh automatically OS se GEMINI_API_KEY utha lega
        try:
            client = genai.Client(api_key="AQ.Ab8RN6L1LlITdJKIeylaoZ34J_dLWK48nrOTkrqbkXeudDyBPw")
            
            # Hum use kar rahe hain gemini-2.5-flash jo ki fast aur accurate hai
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=final_prompt["user_context"],
                config=types.GenerateContentConfig(
                    system_instruction=final_prompt["system_instruction"],
                    temperature=0.7 # Thoda creative aur witty rakhne ke liye
                )
            )
            
            print("================ 🔮 BINA SUGARCOATING WALA BHAVISHYA ================\n")
            print(response.text)
            print("\n====================================================================")
            
        except Exception as e:
            print(f"Bhai, API connect karne mein dikkat aayi: {e}")
            print("Check karo ki GEMINI_API_KEY terminal mein sahi se set hai ya nahi.")