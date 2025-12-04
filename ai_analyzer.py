import json
import time
import random
from datetime import datetime

# Ha van Binance API-d, ide írd be, és állítsd a TEST_MODE-ot False-ra
TEST_MODE = True 
DATA_FILE = 'data_storage.json'

def generate_market_data():
    """Generálja a profi elemzést a Bot számára"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Elemzési sablonok, hogy változatos legyen
    btc_scenarios = [
        {
            "trend": "STRONG BULLISH",
            "level": "Az árfolyam sikeresen áttörte a $95k ellenállást. A MA(50) keresztezte az MA(200)-at (Golden Cross). Következő célár: $98,500. Vételi zóna: $94,800."
        },
        {
            "trend": "NEUTRAL / SIDEWAYS",
            "level": "Oldalazás a $92k - $94k sávban. Bollinger szalagok beszűkültek. Nagy elmozdulás várható. Javaslat: Várakozás a kitörésre."
        }
    ]
    
    sol_scenarios = [
        {
            "trend": "BULLISH",
            "level": "Erős vételi volumen érkezett. Az RSI 60-as szinten, még van tér felfelé. Célár: $215."
        }
    ]

    # Kiválasztunk egyet véletlenszerűen (szimuláció)
    btc_data = random.choice(btc_scenarios)
    sol_data = random.choice(sol_scenarios)

    data = {
        "last_analysis_date": timestamp,
        "analyses": {
            "BTC/USDC": btc_data,
            "SOL/USDC": sol_data,
            "BNB/USDC": {
                "trend": "BEARISH",
                "level": "Gyengeség jelei a napi grafikonon. MA(200) alatt vagyunk. Eladási nyomás $650 környékén. Javaslat: Short vagy távolmaradás."
            }
        }
    }
    
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[AI ENGINE] Elemzés frissítve: {data['last_analysis_date']}")

if __name__ == "__main__":
    print("SkyAI Deep Scanner Engine Indítása...")
    while True:
        analysis = generate_market_data()
        save_data(analysis)
        # 1 percet vár a következő frissítésig
        time.sleep(60)
