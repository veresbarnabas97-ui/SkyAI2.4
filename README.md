# SkyAI

# 🌌 SkyAI Systems | Professional AI Trading Ecosystem

![SkyAI Banner](https://via.placeholder.com/1200x300/050507/00f0ff?text=SkyAI+Systems+%7C+Precision+%26+Dominance)
> *„Lásd, amit mások nem. Cselekedj, mielőtt mások mozdulnának.”*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Telegram API](https://img.shields.io/badge/Telegram-Bot_API-0088cc?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Status](https://img.shields.io/badge/System-ONLINE-success?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)]()

## 📜 Projekt Leírás

A **SkyAI** egy elit szintű, mesterséges intelligenciával vezérelt kereskedési ökoszisztéma. A projekt célja, hogy érzelemmentes, tisztán matematikai alapú **Spot jelekkel** támogassa a modern kereskedőket a kriptovaluta piacon.

A rendszer nem csupán egy bot, hanem egy **többrétegű hálózat**, amely a felhasználó tőkéjéhez és kockázatvállalási profiljához igazodik: a gyors, precíziós műveletektől (**Sniper**) a stratégiai piaci dominanciáig (**Whale**).

## 🚀 Architektúra és Modulok

A rendszer egy központi "Kapuőr" (Gatekeeper) egységből és két titkosított, zártkörű alrendszerből áll.

### 🛡️ SkyAI ProBot (The Gatekeeper)
A publikus belépési pont. Kezeli a felhasználói jogosultságokat, a fizetéseket és az adminisztrációt.
- **Funkció:** Beléptetés, Auth, Adminisztráció.
- **Hozzáférés:** Publikus.

---

### 🎯 SkyAI Sniper (Agilis Vadász)
A "Tőkeépítő" modul. Kistőkével rendelkező, agilis kereskedők számára, akik a gyors piaci mozgásokat keresik.
- **Fókusz:** Sebesség és Precizitás.
- **Eszközök:** BTC, SOL, BNB, ETH.
- **Idősík:** 15m / 1H.
- **Stílus:** `Neon Cyan` - High Frequency Spot.

---

### 🐋 SkyAI Whale (Stratégiai Dominancia)
A "Belső Kör". Nagy tőkeáttétellel dolgozó partnerek számára, akik a makro trendeket lovagolják meg.
- **Fókusz:** Trendkövetés és Vagyonvédelem.
- **Eszközök:** Teljes piaci lefedettség + Makro elemzések.
- **Idősík:** 4H / 1D / 1W.
- **Stílus:** `Neon Purple` - Institutional Grade.

## 🛠️ Technológiai Háttér

A projekt modern, robusztus technológiákra épül a maximális rendelkezésre állás érdekében:

* **Core:** Python 3.10+ (AsyncIO)
* **Interface:** `python-telegram-bot` (v20+)
* **Database:** SQLite3 (Felhasználói szintek és lejárati idők kezelése)
* **Data Analysis:** Pandas, NumPy (Szignál generálás)
* **Payment Integration:** Binance Pay & Revolut API integráció

## 💻 Telepítés és Futtatás

A fejlesztői környezet beállítása:

```bash
# 1. Repository klónozása
git clone [https://github.com/VeresBarnabas97-ui/SkyAI.git](https://github.com/VeresBarnabas97-ui/SkyAI.git)

# 2. Könyvtárba lépés
cd SkyAI

# 3. Függőségek telepítése
pip install -r requirements.txt

# 4. Tokenek konfigurálása (secrets)
# Hozd létre a .env fájlt vagy állítsd be a változókat a bot.py-ban.
