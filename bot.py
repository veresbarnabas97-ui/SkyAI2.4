import logging
import sqlite3
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
# Feltételezzük, hogy az ai_analyzer.py már a módosított formában van
from ai_analyzer import get_current_analysis, update_daily_analysis 

# --- KONFIGURÁCIÓ ---
TELEGRAM_BOT_TOKEN = '8486431467:AAEMJ87kuhbwzYl529ypndfD7LsrQ52Ekx4'
DB_NAME = 'skyai_users.db'

# --- STRATÉGIAILAG INTEGRÁLT FIZETÉSI LINKEK ---
FIAT_PAYMENT_URL = 'https://revolut.me/veresbarnabas1?currency=HUF&amount=15000' # A 1500000-t feltételeztem 15000 Ft-nak (1500000 Ft irreálisan magas)
CRYPTO_PAYMENT_URL = 'https://s.binance.com/LfcBZowU' 

# Logging beállítása
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ADATBÁZIS & SEGÉDFÜGGVÉNYEK ---

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            subscription_status TEXT DEFAULT 'free',  # Alapértelmezett: 'free'
            join_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def check_user_status(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT subscription_status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'free'

# --- PARANCSKEZELŐK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Adatbázisba mentés és/vagy státusz lekérdezése
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)',
                   (user.id, user.username, datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    status = check_user_status(user.id)
    status_emoji = "💎 PRO" if status == 'pro' else "🆓 FREE"

    welcome_msg = (
        f"Üdvözöllek {user.first_name} a SkyAI Rendszerben! 🤖\n\n"
        "Én egy mesterséges intelligencia alapú kereskedési asszisztens vagyok.\n"
        f"Jelenlegi státuszod: **{status_emoji}**\n\n"
        "Mit szeretnél tenni?"
    )

    keyboard = [
        [InlineKeyboardButton("📊 AI Szignálok", callback_data='analysis')],
        [InlineKeyboardButton("💎 Előfizetés (Pro Csomag)", callback_data='subscribe')],
        [InlineKeyboardButton("ℹ️ Segítség & Támogatás", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Ha CallbackQuery-ből érkezik, az üzenet szerkesztése
    if update.callback_query:
        await context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=welcome_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    # Ha CommandHandler-ből érkezik, új üzenet küldése
    else:
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def send_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command=False):
    """Közös funkció a /signals parancshoz és az 'analysis' callback-hez."""
    user_id = update.effective_user.id
    status = check_user_status(user_id)
    
    # Adatok lekérése a felhasználói státusz alapján (ami az ai_analyzer.py-ban kezeli a FREE/PRO logikát)
    data = get_current_analysis(status)
    
    if status == 'pro':
        msg = "🔍 **AKTÍV PRO SZIGNÁLOK (VALÓS IDEJŰ):**\n\n"
        for pair, info in data.items():
            icon = "🟢" if info['trend'] == 'BULLISH' else "🔴" if info['trend'] == 'BEARISH' else "⚪"
            msg += f"{icon} **{pair}**: {info['trend']} ({info['probability']})\n"
            msg += f"   └ {info['level']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Vissza a Főmenübe", callback_data='start_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    else: # FREE felhasználó ('Kezdő Sky')
        msg = "🔍 **Kezdő Sky Elemzés (Korlátozott):**\n\n"
        msg += "A SkyAI csak a fő kereskedési párt (BTC) mutatja a FREE csomagban. Nézd meg a mai legfontosabb elemzésünket:\n\n"
        
        # Csak BTC adat mutatása 
        btc_info = data.get('BTC/USDC', {'trend': 'Nincs adat', 'probability': '0%', 'level': 'Frissítés szükséges'})
        icon = "🟢" if btc_info['trend'] == 'BULLISH' else "🔴" if btc_info['trend'] == 'BEARISH' else "⚪"
        msg += f"{icon} **BTC/USDC**: {btc_info['trend']} ({btc_info['probability']})\n"
        msg += f"   └ {btc_info['level']}\n\n"
        msg += "**Több kereskedési lehetőségért és részletesebb belépőkért frissíts PRO-ra!**\n\n"
        
        keyboard = [[InlineKeyboardButton("💎 PRO-ra Frissítés", callback_data='subscribe')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    if is_command:
        # Üzenet küldése parancs esetén
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        # Üzenet szerkesztése gombnyomás esetén
        await context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_analysis(update, context, is_command=True)

async def subscribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command=False):
    """Közös funkció a /pro parancshoz és a 'subscribe' callback-hez."""
    
    # A Revolut linket korrigáltam 15000 HUF-ra, feltételezve, hogy havi 15.000 Ft az ár
    msg = (
        "💎 **SkyAI PRO TRADER CSOMAG**\n\n"
        "Ár: **15.000 Ft / hó**\n"
        "Előnyök: Valós idejű szignálok, Korlátlan eszköz (BTC, BNB, SOL, ETH), Részletes belépő/kilépő zónák.\n\n"
        "--- **Fizetési Opciók** ---\n\n"
        "**1. FIAT (Revolut)**: A leggyorsabb. A fizetés után vedd fel a kapcsolatot a támogatással az aktiválásért.\n"
        "**2. KRIPTO (Binance Pay)**: Kényelmes kriptós fizetés. Kérjük, küldd el a fizetési bizonylatot a támogatásnak.\n"
    )

    keyboard = [
        [InlineKeyboardButton("💳 Revolut Fizetés (15.000 HUF)", url=FIAT_PAYMENT_URL)],
        [InlineKeyboardButton("🪙 Kripto Fizetés (Binance Pay)", url=CRYPTO_PAYMENT_URL)],
        [InlineKeyboardButton("ℹ️ Támogatás (Aktiválás/Segítség): @VeresBarnabas1", url="https://t.me/VeresBarnabas1")],
        [InlineKeyboardButton("🔙 Vissza a Főmenübe", callback_data='start_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_command:
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def pro_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await subscribe_message(update, context, is_command=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "**SkyAI Támogatás & Segítség**\n\n"
        "Parancsok:\n"
        "/start - Főmenü indítása\n"
        "/signals - Aktuális AI elemzések megtekintése\n"
        "/pro - Előfizetési információk és fizetési linkek\n\n"
        "**Személyes támogatásért kérjük, vedd fel a kapcsolatot:**\n"
    )
    keyboard = [[InlineKeyboardButton("🧑‍💻 Támogatás: @VeresBarnabas1", url="https://t.me/VeresBarnabas1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kezeljük azt, hogy honnan hívták (parancs vagy gomb)
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    elif hasattr(update, 'callback_query') and update.callback_query:
         await context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def admin_generate_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin parancs a napi elemzés frissítésének szimulálására."""
    result_msg = update_daily_analysis()
    await update.message.reply_text(f"Admin Művelet:\n{result_msg}", parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Callback logika a főmenü irányítására
    if query.data == 'analysis':
        await send_analysis(update, context)
    elif query.data == 'subscribe':
        await subscribe_message(update, context)
    elif query.data == 'help':
        await help_command(update, context) 
    elif query.data == 'start_menu':
        await start(update, context)


# --- FŐ PROGRAM ---
def main():
    print("A SkyAI Bot indul...")
    init_db()
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Parancs Handlerek hozzáadása
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("signals", signals_command))
    application.add_handler(CommandHandler("pro", pro_command))
    application.add_handler(CommandHandler("generateanalysis", admin_generate_analysis)) # Admin parancs

    # Callback/Gomb Handlerek hozzáadása
    application.add_handler(CallbackQueryHandler(button_handler))

    print("A Bot sikeresen fut! (Nyomj Ctrl+C-t a leállításhoz)")
    application.run_polling()

if __name__ == '__main__':
    main()
