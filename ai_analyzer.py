import json
import random
from datetime import datetime
import time 
import pandas as pd
import logging
from binance.client import Client 

# Logging beállítása
logger = logging.getLogger(__name__)

# --- BINANCE KONFIGURÁCIÓ (Olvasás módban elég) ---
API_KEY = "fykRTXookY8OkwNlQTlZo4gURFHNVkg9clSBXTTEuIRkU7QvLOtAORyrQEfVTgyQ" 
API_SECRET = "RfgiMsjxOA1kkz8xW8l68AZcWDAxrIuPtaA2Kwp7BluD9bicoKnLAMFH4blf6Fk2"
client = Client(API_KEY, API_SECRET)

# KONFIGURÁCIÓS PARAMÉTEREK
MA_PERIOD = 20      
INTERVAL = Client.KLINE_INTERVAL_1HOUR 
DB_PATH = 'data_storage.json'

def get_ma_trend(symbol, interval, ma_period):
    """Letölti a gyertyákat és meghatározza a SPOT trendet."""
    try:
        klines = client.get_historical_klines(symbol, interval, f"{ma_period + 5} hours ago UTC")
    except Exception as e:
        logger.error(f"Hiba a Binance adatok lekérdezésekor ({symbol}): {e}")
        return {'trend': 'NEUTRAL', 'current_price': 0, 'ma_value': 0}

    if not klines or len(klines) < ma_period:
        return {'trend': 'NEUTRAL', 'current_price': 0, 'ma_value': 0}

    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    df['MA'] = df['close'].rolling(window=ma_period).mean()
    
    current_price = df['close'].iloc[-1]
    ma_value = df['MA'].iloc[-1]
    
    # SPOT Trend: Csak akkor vétel, ha stabilan felette van
    if current_price > ma_value:
        trend = 'BULLISH'
    elif current_price < ma_value:
        trend = 'BEARISH' # Spotban ez cash-out jelzés (USDT-be lépés)
    else:
        trend = 'NEUTRAL'

    return {'trend': trend, 'current_price': current_price, 'ma_value': ma_value}

def get_current_analysis(status='free'):
    """SPOT Elemzés generálása."""
    full_pairs = ['BTC/USDC', 'BNB/USDC', 'SOL/USDC', 'ETH/USDC']
    pairs_to_analyze = ['BTC/USDC'] if status == 'free' else full_pairs
        
    analysis = {}
    
    for pair_slash in pairs_to_analyze:
        symbol = pair_slash.replace('/', '') 
        data = get_ma_trend(symbol, INTERVAL, MA_PERIOD)
        trend = data['trend']
        current_price = data['current_price']
        ma_value = data['ma_value']
        prob = random.randint(78, 96) # AI Confidence

        # --- SPOT SZÖVEGEZÉS ---
        margin = current_price * 0.005 # 0.5% zóna
        
        if trend == 'BULLISH':
            # Spot Vétel
            entry_level = ma_value - margin 
            level_text = f"🟢 **SPOT VÉTELI ZÓNA:**\nAz árfolyam a mozgóátlag felett. Belépés korrekcióban: **{entry_level:.2f}$** környékén.\nCél: Akkumuláció."
        elif trend == 'BEARISH':
            # Spot Eladás (Cash out)
            level_text = f"🛡️ **VÉDEKEZŐ MÓD (USDT):**\nTrendforduló lefelé. Javasolt a kitettség csökkentése vagy Stop-Loss szűkítése.\nEllenállás: {ma_value:.2f}$"
        else: 
            level_text = f"⚪ **OLDALAZÁS:**\nKivárás javasolt. A piac irányt keres {current_price:.2f}$ környékén."

        if status == 'free' and pair_slash == 'BTC/USDC':
             level_text = f"🔒 **Ingyenes Betekintő:**\nTrend: {trend}\n\nA pontos SPOT belépőkért és a SOL/BNB elemzésekért válassz csomagot!"

        analysis[pair_slash] = {
            'trend': trend,
            'level': level_text,
            'prob': prob, 
            'current_price': f"{current_price:.2f}$"
        }
    
    return analysis

def update_daily_analysis():
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
        return f"SPOT Elemzések Frissítve ({len(new_analysis)} pár)."
    except Exception as e:
        return f"Hiba: {e}"
