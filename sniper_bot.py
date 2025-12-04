import logging
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# --- KONFIGURÁCIÓ ---
TOKEN = '8332155247:AAHmYnKDhllMRHFepYqjZE29Pao3VdMc5UM' 

# !!! ITT A JAVÍTÁS A PONTOS REPO NÉVVEL:
DASHBOARD_LINK = "https://veresbarnabas97-ui.github.io/SkyAISniper/" 
# Mivel index.html a neve, elég a mappa linkje!

DATA_FILE = 'data_storage.json'

logging.basicConfig(format='%(asctime)s - SkyAI_SNIPER - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ADATOLVASÁS ---
def load_analysis():
    if not os.path.exists(DATA_FILE): return None
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

# --- HANDLEREK ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"🎯 **SKYAI SNIPER EGYSÉG**\n"
        f"Üdvözöllek, {user.first_name}!\n\n"
        "A rendszer készen áll. A Deep Scanner folyamatosan figyeli a MA(200) és Bollinger szalagokat.\n\n"
        "🔻 **PARANCSKÖZPONT:**"
    )
    keyboard = [
        [InlineKeyboardButton("📡 Deep Scan Futtatása", callback_data='run_scan')],
        [InlineKeyboardButton("🖥️ PRIVÁT TERMINÁL MEGNYITÁSA", url=DASHBOARD_LINK)],
        [InlineKeyboardButton("📘 Stratégia & Oktatás", callback_data='edu_menu')]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Elemzés folyamatban...")
    await asyncio.sleep(1) # Kamu töltés effekt
    
    data = load_analysis()
    if not data:
        await query.message.reply_text("⚠️ Hiba: Az AI motor (ai_analyzer.py) nem fut a szerveren.")
        return

    report = f"📡 **SkyAI Deep Scan Jelentés**\n🕒 {data.get('last_analysis_date')}\n\n"
    for pair, details in data["analyses"].items():
        icon = "🟢" if "BULLISH" in str(details) else "🔴"
        report += f"{icon} **{pair}**\n_{details.get('level')}_\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Vissza", callback_data='start_menu')]]
    await query.message.edit_text(report, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ... (A többi handler maradhat ugyanaz, mint előbb) ...

async def start_menu_callback(update, context): await start(update, context)
async def edu_handler(update, context): 
    # Egyszerűsített edu handler
    await update.callback_query.answer()
    await update.callback_query.message.edit_text("📘 **Oktatás:**\nCsak a 90%+ valószínűségű jelekre lépj be. Használd a dashboardot a megerősítéshez.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Vissza", callback_data='start_menu')]]), parse_mode='Markdown')

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(scan_handler, pattern='^run_scan$'))
    application.add_handler(CallbackQueryHandler(edu_handler, pattern='^edu_menu$'))
    application.add_handler(CallbackQueryHandler(start_menu_callback, pattern='^start_menu$'))
    application.run_polling()

if __name__ == '__main__':
    main()
