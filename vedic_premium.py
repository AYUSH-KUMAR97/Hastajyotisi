from datetime import datetime

# Rashi aur unke Vedic Lucky Alphabets (Same as before)
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

def calculate_rashi(date_str, time_str, lat=0.0, lon=0.0):
    """
    Pure Python approximation matrix based on Ephemeris cycles.
    Bina kisi external C-library (pyswisseph) ke smoothly chalega.
    """
    dt = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
    
    # Ek standard reference date (Epoch) jahan Moon ki position pata ho
    # Moon cycle lagbhag 27.3 days ki hoti hai
    ref_date = datetime(2000, 1, 1, 0, 0)
    diff_days = (dt - ref_date).total_seconds() / 86400.0
    
    # Moon ki positions calculate karna (Approximation logic)
    moon_cycle = 27.321661
    position_in_cycle = (diff_days % moon_cycle) / moon_cycle
    degrees = position_in_cycle * 360.0
    
    # 12 rashiyon mein divide karna (30 degree each)
    rashi_idx = int(degrees / 30) % 12
    
    rashi_names = list(RASHI_ALPHABETS.keys())
    detected_rashi = rashi_names[rashi_idx]
    
    return {
        "rashi": detected_rashi,
        "details": RASHI_ALPHABETS[detected_rashi]
    }

if __name__ == "__main__":
    # Test run
    res = calculate_rashi("29-11-2007", "14:30")
    print(f"Approximated Rashi: {res['rashi']}")
    print(f"Letters: {res['details']['letters']}")