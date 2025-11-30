import json
import datetime
import random

# Az elemzéseket tároló fájl neve
DATA_FILE = 'data_storage.json'
# Ezek a párok fognak szerepelni az elemzésben
CRYPTO_PAIRS = ['BTC/USDC', 'BNB/USDC', 'SOL/USDC'] 

def fetch_live_data(pair: str) -> dict:
    """Szimulálja az élő piaci adatok lekérését (pl. Binance API-ról)."""
    # Éles környezetben itt történne a valós tőzsdei API hívás.
    return {"volume": random.randint(1000, 5000), "price_change": round(random.uniform(-0.05, 0.05), 4)}

def generate_analysis(pair: str, data: dict) -> dict:
    """Szimulálja az AI elemzést a kapott adatok alapján."""
    
    # Egyszerű logikai alapú szimuláció
    change = data["price_change"]
    
    if change > 0.02:
        trend = "Erős Bullish lendület. Várhatóan folytatódik a drágulás. (LONG)"
        level = f"Következő ellenállás: magasan van, de figyelni kell az 5% feletti napi zárásra."
    elif change < -0.02:
        trend = "Figyelmeztető jelzések. Az eladói nyomás növekszik a piacon. (SHORT)"
        level = f"Kritikus támasz: valószínűleg tesztelni fogja az előző aljat."
    else:
        trend = "Konszolidációs időszak. Kereskedési tartományon belüli mozgás várható."
        level = f"Oldalazás: Várhatóan a jelenlegi ár +/- 2% tartományban marad. (VÁRAKOZÁS)"
        
    return {"trend": trend, "level": level}

def update_daily_analysis():
    """Létrehozza a napi elemzéseket és elmenti a JSON fájlba."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    new_analyses = {}
    
    for pair in CRYPTO_PAIRS:
        live_data = fetch_live_data(pair)
        analysis_result = generate_analysis(pair, live_data)
        new_analyses[pair] = analysis_result

    # Elmentjük az új adatokat a JSON fájlba
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                "last_analysis_date": today,
                "analyses": new_analyses
            }, f, indent=2)
        print(f"✅ Sikeresen frissítve a napi elemzés: {today}")
        return True
    except Exception as e:
        print(f"❌ Hiba történt az elemzés mentésekor: {e}")
        return False

def get_current_analysis():
    """Lekéri az utolsó elemzést a JSON fájlból."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"❌ Hiba: Az {DATA_FILE} JSON fájl hibás.")
        return None

if __name__ == '__main__':
    # Ezt a funkciót kell naponta egyszer futtatni!
    update_daily_analysis()
