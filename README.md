# 🚀 SkyAI - Intelligens Kereskedési Asszisztens (Telegram Bot & Webes Felület)

![SkyAI Banner](https://img.shields.io/badge/Status-Aktív%20Kereskedelmi%20Verzió-brightgreen)
![Python Verzió](https://img.shields.io/badge/Python-3.10%2B-blue)
![Telegram Bot](https://img.shields.io/badge/Platform-Telegram-lightblue)

A **SkyAI** egy mesterséges intelligencia alapú platform, amelyet arra terveztek, hogy valós idejű kereskedési elemzéseket és szignálokat biztosítson a kriptovaluta piacokon. A projekt egy Telegram bot és egy kísérő statikus weboldal köré épül, amely egy logikus **Freemium** üzleti stratégia mentén működik.

---

## 💰 Üzleti Modell & Stratégia

A SkyAI két szintű hozzáférést biztosít:

| Szolgáltatási Szint | Leírás | Értékajánlat |
| :--- | :--- | :--- |
| **Kezdő Sky (FREE)** | Korlátozott, késleltetett elemzési hozzáférés. | Bevonja a felhasználót, minimalizálja a kezdeti kockázatot, **felhívja a figyelmet** a PRO-ra. Jelenleg **csak BTC/USDC** adatok láthatók. |
| **Pro Trader (PAID)** | Havi **15.000 Ft** díj ellenében korlátlan, valós idejű elemzés. | **Konverziós pont:** Teljes hozzáférés az összes piachoz (BTC, BNB, SOL, ETH, stb.) és részletes belépési/kilépési zónákhoz. |

### 🎯 Monetizációs Cél

A Telegram bot direkt **fizetési linkeket** tartalmaz (`/pro` parancs), így a FREE felhasználók azonnal fizető ügyfelekké konvertálhatók a FOMO (Fear of Missing Out) és a megbízható elemzések ígéretének köszönhetően.

---

## 🛠️ Telepítés és Beállítás

A projekt futtatásához Python 3.10 vagy újabb verzió szükséges.

### 1. Előfeltételek

* **Python:** A szükséges függőségek telepítése:
    ```bash
    pip install python-telegram-bot sqlite3
    ```
* **Telegram Bot Token:** Szerezz be egy tokent a @BotFather-től.

### 2. Konfiguráció

Készítsd el a `bot.py` fájlban a konfigurációt. **FONTOS:** Cseréld ki a placeholder értékeket a saját adataidra.

```python
# bot.py (Konfiguráció részlet)
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE' 

# Stratégiailag integrált fizetési linkek
FIAT_PAYMENT_URL = '[https://revolut.me/veresbarnabas1?currency=HUF&amount=15000](https://revolut.me/veresbarnabas1?currency=HUF&amount=15000)' 
CRYPTO_PAYMENT_URL = '[https://s.binance.com/LfcBZowU](https://s.binance.com/LfcBZowU)'
