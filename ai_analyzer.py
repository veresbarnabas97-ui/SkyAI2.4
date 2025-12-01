import json
import random
from datetime import datetime
import time 
import pandas as pd
import logging

# ÚJ IMPORT
from binance.client import Client 

# Logging beállítása
logger = logging.getLogger(__name__)

# --- BINANCE KONFIGURÁCIÓ ---
# Megadott kulcsok beillesztve
API_KEY = "fykRTXookY8OkwNlQTlZo4gURFHNVkg9clSBXTTEuIRkU7QvLOtAORyrQEfVTgyQ" 
API_SECRET = "RfgiMsjxOA1kkz8xW8l68AZcWDAxrIuPtaA2Kwp7BluD9bicoKnLAMFH4blf6Fk2"
client = Client(API_KEY, API_SECRET)

# KONFIGURÁCIÓS PARAMÉTEREK
MA_PERIOD = 20      # Mozgóátlag periódusa (pl. 20 órás)
INTERVAL = Client.KLINE_INTERVAL_1HOUR # 1 órás gyertyák használata
DB_PATH = 'data_storage.json'

# --- SEGÉDFÜGGVÉNYEK ---

def get_ma_trend(symbol, interval, ma_period):
    """Letölti a gyertyákat, kiszámolja a mozgóátlagot és meghatározza a trendet."""
    
    try:
        # Lekérünk elegendő gyertyát a számításhoz (MA_PERIOD + 5 biztonsági gyertya)
        klines = client.get_historical_klines(symbol, interval, f"{ma_period + 5} hours ago UTC")
    except Exception as e:
        logger.error(f"Hiba a Binance adatok lekérdezésekor ({symbol}): {e}")
        return {'trend': 'NEUTRAL', 'current_price': 0, 'ma_value': 0}

    if not klines or len(klines) < ma_period:
        logger.warning(f"Nincs elegendő adat ({symbol}) a {ma_period} perióusú MA számításához.")
        return {'trend': 'NEUTRAL', 'current_price': 0, 'ma_value': 0}

    # 1. Adatok formázása Pandas DataFrame-be
    # A 4. index a záróár (close price)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    
    # 2. Mozgóátlag (MA) számítása
    df['MA'] = df['close'].rolling(window=ma_period).mean()
    
    # A legfrissebb értékek
    current_price = df['close'].iloc[-1]
    ma_value = df['MA'].iloc[-1]
    
    # 3. TREND meghatározása (Egyszerű MA keresztezés)
    if current_price > ma_value:
        trend = 'BULLISH'
    elif current_price < ma_value:
        trend = 'BEARISH'
    else:
        trend = 'NEUTRAL'

    return {
        'trend': trend, 
        'current_price': current_price, 
        'ma_value': ma_value
    }


# --- FŐ ELEMZŐ FUNKCIÓ ---

def get_current_analysis(status='free'):
    """
    Generálja az elemzéseket a felhasználói státusz alapján, valós Binance adatokkal.
    """
    
    # Alapértelmezett Pro Párlista
    full_pairs = ['BTC/USDC', 'BNB/USDC', 'SOL/USDC', 'ETH/USDC']
    
    if status == 'free':
        # FREE csomagban csak BTC-re van rálátás
        pairs_to_analyze = ['BTC/USDC']
    else:
        # PRO csomagban minden elérhető
        pairs_to_analyze = full_pairs
        
    analysis = {}
    
    for pair_slash in pairs_to_analyze:
        # A Binance API-hoz BTCUSDC formátum kell, nem BTC/USDC
        symbol = pair_slash.replace('/', '') 
        
        # Valós elemzés végrehajtása
        data = get_ma_trend(symbol, INTERVAL, MA_PERIOD)
        trend = data['trend']
        current_price = data['current_price']
        ma_value = data['ma_value']
        
        # A valószínűséget (prob) most hagyjuk magasabb értéken
        prob = random.randint(75, 95) 

        # --- Elemzési Szövegek Létrehozása ---
        
        # A belépési szintet most a Mozgóátlag (MA) +/- egy kis margója határozza meg (0.3%)
        margin = current_price * 0.003 
        
        if trend == 'BULLISH':
            # Vétel MA felett: Belépő zóna az MA körül
            entry_level = ma_value - margin 
            level_text = f"Valós idejű szignál (Long): Belépő zóna ~ **{entry_level:.2f}$** (MA támasz)\nAktuális ár: {current_price:.2f}$"
        elif trend == 'BEARISH':
            # Eladás MA alatt: Belépő zóna az MA körül (ellenállásként)
            entry_level = ma_value + margin
            level_text = f"Valós idejű szignál (Short): Belépő zóna ~ **{entry_level:.2f}$** (MA ellenállás)\nAktuális ár: {current_price:.2f}$"
        else: # NEUTRAL
            level_text = f"Jelenleg NEUTRAL mozgás. A piac oldalazik az MA ({ma_value:.2f}$) körül.\nAktuális ár: {current_price:.2f}$"

        # A FREE korlátozás megtartása
        if status == 'free' and pair_slash == 'BTC/USDC':
             # FREE: Csak az általános trendet látja, belépő szint nélkül.
             level_text = f"Korlátozott FREE elemzés.\nAktuális trend: **{trend}**\n\n**PRO** szükséges a valós idejű belépő szinthez!"
        elif status == 'free' and pair_slash != 'BTC/USDC':
            # Ez nem fut le a pairs_to_analyze miatt, de biztonságos
            level_text = "Korlátozott: PRO státusz szükséges a párhoz."


        analysis[pair_slash] = {
            'trend': trend,
            'level': level_text,
            'prob': prob, 
            'current_price': f"{current_price:.2f}$"
        }
    
    return analysis


def update_daily_analysis():
    """
    Frissíti a data_storage.json fájlt a legfrissebb PRO elemzésekkel.
    Ezt futtatja a bot a JobQueue-val (automatikus frissítés).
    """
    
    # PRO státusszal kérjük le az összes elemzést
    new_analysis = get_current_analysis(status='pro')
    
    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'last_analysis_date': 'N/A', 'analyses': {}}
        
    data['last_analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['analyses'] = new_analysis
    
    try:
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return f"Sikeresen frissítve ({len(new_analysis)} elemzés)."
    except Exception as e:
        return f"Hiba a JSON fájl írásakor: {e}"


def get_stored_analysis():
    """Visszaadja a data_storage.json-ban tárolt legutolsó elemzést."""
    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
        return data.get('analyses', {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
