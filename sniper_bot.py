import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# --- KONFIGURÁCIÓ ---
TOKEN = '8332155247:AAHmYnKDhllMRHFepYqjZE29Pao3VdMc5UM' # A te Tokened
DASHBOARD_LINK = "https://veresbarnabas97-ui.github.io/SkyAI/SkyAISniper.html" 
POOOLSE_LINK = "https://app.pooolse.com/join/7974"
DATA_FILE = 'data_storage.json'

# Logging beállítása
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- SEGÉDFÜGGVÉNYEK ---

def load_analysis():
    """Betölti a legfrissebb elemzést a JSON fájlból."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Hiba a JSON olvasásakor: {e}")
        return None

# --- COMMAND HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Főmenü"""
    user = update.effective_user
    text = (
        f"🎯 **SkyAI Sniper Egység - Online**\n"
        f"Üdvözöllek, {user.first_name}!\n\n"
        "A rendszer készen áll a Spot kereskedési jelek közvetítésére.\n"
        "A Deep Scanner folyamatosan figyeli a MA(200) és Bollinger szalagokat.\n\n"
        "Válassz parancsot:"
    )
    keyboard = [
        [InlineKeyboardButton("📡 Deep Scan Indítása (Elemzés)", callback_data='run_scan')],
        [InlineKeyboardButton("🖥️ Webes Dashboard", url=DASHBOARD_LINK)],
        [InlineKeyboardButton("📘 Oktatóanyagok", callback_data='edu_menu')],
        [InlineKeyboardButton("🤖 Pooolse Automatizálás", callback_data='pooolse_info')]
    ]
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kiolvassa az elemzést és elküldi"""
    query = update.callback_query
    await query.answer("Deep Scanner futtatása...")
    
    data = load_analysis()
    
    if not data or "analyses" not in data:
        await query.message.reply_text("⚠️ **Nincs elérhető friss elemzés.**\nKérlek, futtasd a háttérben az 'ai_analyzer.py'-t az adatok generálásához!")
        return

    # Elemzések formázása
    report = f"📡 **SkyAI Deep Scan Jelentés**\n📅 Dátum: {data.get('last_analysis_date', 'N/A')}\n\n"
    
    for pair, details in data["analyses"].items():
        trend_icon = "🟢" if "BULLISH" in str(details) or "Vétel" in str(details) else "🔴"
        report += f"{trend_icon} **{pair}**\nOutput: {details.get('level', 'N/A')}\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Vissza", callback_data='start_menu')]]
    await query.message.edit_text(report, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def edu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oktató menü"""
    query = update.callback_query
    await query.answer()
    text = "📘 **Tudásbázis**\nVálassz témát:"
    keyboard = [
        [InlineKeyboardButton("🔍 Mi az a Deep Scanner?", callback_data='edu_deepscan')],
        [InlineKeyboardButton("💰 Kistőkés Stratégia", callback_data='strat_lowcap')],
        [InlineKeyboardButton("🔙 Főmenü", callback_data='start_menu')]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Egyedi tartalmak megjelenítése"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    text = ""
    if data == 'edu_deepscan':
        text = (
            "🔍 **Deep Scanner Működése**\n\n"
            "Ez az algoritmus nem 'jósol', hanem mér.\n"
            "1. **MA(200):** Ha az ár ez alatt van, csak Short jeleket keresünk.\n"
            "2. **Squeeze:** Ha a Bollinger szalagok beszűkülnek, a volatilitás robbanása várható.\n"
        )
    elif data == 'strat_lowcap':
        text = (
            "💰 **Kistőkés Stratégia ($100-$1000)**\n\n"
            "1. **Türelem:** Csak a 90%+ valószínűségű jelekre lépj be.\n"
            "2. **Compound:** A profitot ne vedd ki, hanem forgasd vissza.\n"
            "3. **Eszközök:** Koncentrálj a top coinokra (SOL, BNB), kerüld a shitcoinokat."
        )
    elif data == 'pooolse_info':
        text = (
            "🤖 **Pooolse Integráció**\n\n"
            "Kösd össze a SkyAI jeleit a Pooolse botokkal.\n"
            "Ajánlott: **Spot Grid Bot** oldalazó piacon."
        )

    keyboard = [[InlineKeyboardButton("🔙 Vissza", callback_data='start_menu')]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# --- MAIN ---
def main():
    print("SkyAI Sniper Bot Indítása...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(scan_handler, pattern='^run_scan$'))
    application.add_handler(CallbackQueryHandler(edu_handler, pattern='^edu_menu$'))
    application.add_handler(CallbackQueryHandler(content_handler, pattern='^(edu_deepscan|strat_lowcap|pooolse_info)$'))
    application.add_handler(CallbackQueryHandler(start_menu_callback, pattern='^start_menu$'))

    application.run_polling()

if __name__ == '__main__':
    main()
