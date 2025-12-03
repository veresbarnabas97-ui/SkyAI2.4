import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# --- KONFIGURÁCIÓ ---
# SkyAIWhale_Bot Token (A te saját tokened)
TOKEN = '8414813040:AAGNNWePEdixbhBC2-JEd-riObEcjGX6iIs'

# Linkek (Győződj meg róla, hogy a GitHub Pages címed helyes!)
DASHBOARD_LINK = "https://veresbarnabas97-ui.github.io/SkyAI2.4/SkyAIWhale.html" 
POOOLSE_LINK = "https://app.pooolse.com/join/7974"
BCBLOOM_LINK = "https://blockchainbloom.com"

# Logging beállítása
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- HANDLEREK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Főmenü és Üdvözlés"""
    user = update.effective_user
    text = (
        f"🐋 **Üdvözlöm a SkyAI Whale Központban, {user.first_name}.**\n\n"
        "Ez a felület a stratégiai vagyonkezelés és a piaci információszerzés privát csatornája.\n\n"
        "📰 **Mai Fókusz:** Intézményi tőkeáramlás és ETF adatok.\n"
        "🛡️ **SkyAI Státusz:** A 'Vault' (Széf) aktív. Kérjük, csatlakoztassa tárcáját a webes terminálon a teljes hozzáféréshez.\n\n"
        "Válasszon az alábbi lehetőségek közül:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔐 VIP Vault Megnyitása", url=DASHBOARD_LINK)],
        [InlineKeyboardButton("📰 Napi SkyAI Elemzés", callback_data='daily_intel')],
        [InlineKeyboardButton("💰 Wallet Csatlakoztatása (Info)", callback_data='wallet_help')],
        [InlineKeyboardButton("🤖 Pooolse Vagyonkezelés", url=POOOLSE_LINK)]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def daily_intel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Napi Piaci Gyorselemzés"""
    query = update.callback_query
    await query.answer()
    text = (
        "📰 **Napi SkyAI Intelligence Report**\n\n"
        "**Főcím:** Intézményi Rekordok az ETF Piacon\n\n"
        "**Részletek:** A BlackRock és a Fidelity vásárlói nyomása ellensúlyozza a rövid távú eladói oldalt. A piac szerkezete bullish.\n\n"
        "🔮 **SkyAI Vélemény:** Akkumuláció (Felhalmozás) zajlik. A bálnák nem adnak el. Ez a legjobb időszak a portfólió bővítésére.\n\n"
        "👉 *A teljes elemzésért és a részletes grafikonokért lépjen be a Vault-ba.*"
    )
    keyboard = [[InlineKeyboardButton("🔙 Vissza a Menübe", callback_data='start_menu')]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def wallet_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Segítség a Wallet Csatlakoztatáshoz"""
    query = update.callback_query
    await query.answer()
    text = (
        "💼 **Hogyan csatlakoztassa tárcáját?**\n\n"
        "A SkyAI Whale oldal a **Web3** technológiát használja a biztonságos azonosításhoz.\n\n"
        "1. Nyissa meg a **VIP Vault** oldalt (felső gomb).\n"
        "2. Kattints a **'Csatlakozás'** vagy **'Connect'** gombra a jobb felső sarokban.\n"
        "3. Válassza ki a **Trust Wallet** vagy **Phantom** opciót.\n"
        "4. A rendszer automatikusan feloldja a zárolt tartalmakat.\n\n"
        "🔒 *A kapcsolat csak olvasási jogot kér (Read-Only) az egyenleg megjelenítéséhez. A tőkéje biztonságban van.*"
    )
    keyboard = [[InlineKeyboardButton("🔙 Vissza a Menübe", callback_data='start_menu')]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Visszatérés a főmenübe"""
    await start(update, context)

# --- MAIN ---

def main():
    print("SkyAI Whale Bot Indítása...")
    application = Application.builder().token(TOKEN).build()

    # Parancsok
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # Gombnyomások kezelése
    application.add_handler(CallbackQueryHandler(daily_intel_handler, pattern='^daily_intel$'))
    application.add_handler(CallbackQueryHandler(wallet_help_handler, pattern='^wallet_help$'))
    application.add_handler(CallbackQueryHandler(start_menu_callback, pattern='^start_menu$'))

    application.run_polling()

if __name__ == '__main__':
    main()
