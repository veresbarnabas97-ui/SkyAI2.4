import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
import sqlite3
import datetime
# Importáljuk az AI elemző modult
from ai_analyzer import get_current_analysis, update_daily_analysis 
import logging

# --- LOGGING BEÁLLÍTÁSA ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 1. KONSTANSOK ÉS KULCSOK ---

# A Telegram bot kulcsa (a megadott érték)
TELEGRAM_BOT_TOKEN = '8486431467:AAEMJ87kuhbwzYl529ypndfD7LsrQ52Ekx4'

# A Pro Trader csomag adatai (Weboldalhoz igazítva)
PRO_TRADER_PACK = "Pro Trader"
SUBSCRIPTION_DURATION_DAYS = 30

# FIAT Fizetési Link (Revolut)
REVOLUT_PAY_LINK = "https://revolut.me/veresbarnabas1?currency=HUF&amount=15000"
REVOLUT_PRICE = "15.000 Ft" 

# KRIPTO Fizetési Link (Binance Pay)
BINANCE_PAY_LINK = "https://s.binance.com/d3nJiY9L"
BINANCE_PRICE = "50 USDT" 

# A bot által támogatott fő kripto párok (Markets szekcióból)
CRYPTO_PAIRS = ['BTC/USDC', 'BNB/USDC', 'SOL/USDC'] 

# Adatbázis fájl
DB_NAME = 'skyai_users.db'


# --- 2. ADATBÁZIS KEZELÉS ---

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            subscription_end_date TEXT DEFAULT '1970-01-01'
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Adatbázis inicializálva.")

def get_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_end_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_subscription(user_id, duration_days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    data = get_user_data(user_id)
    now_date = datetime.datetime.now()
    
    if data and data[0]:
        try:
            end_date_from_db = datetime.datetime.strptime(data[0], '%Y-%m-%d')
            start_date = end_date_from_db if end_date_from_db > now_date else now_date
        except ValueError:
            start_date = now_date
    else:
        start_date = now_date
        
    new_end_date = (start_date + datetime.timedelta(days=duration_days)).strftime('%Y-%m-%d')
    
    cursor.execute("""
        INSERT INTO users (user_id, subscription_end_date) 
        VALUES (?, ?) 
        ON CONFLICT(user_id) 
        DO UPDATE SET subscription_end_date = ?
    """, (user_id, new_end_date, new_end_date)) 
    conn.commit()
    conn.close()
    logger.info(f"Előfizetés frissítve {user_id} felhasználó számára {new_end_date} dátumig.")
    return new_end_date

# --- 3. COMMAND KEZELŐK (Fő funkciók) ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A /start parancs."""
    user = update.effective_user
    await update.message.reply_html(
        f"**👋 Üdvözlünk, {user.first_name} a SkyAI {PRO_TRADER_PACK} botban!**\n\n"
        "Mesterséges intelligencia által generált valós idejű kereskedési jelzések a tiéd. A **Pro Trader** csomag 30 napra 15.000 Ft/50 USDT.\n\n"
        "👉 Nyomd meg a **/menu** gombot a fizetési opciók megtekintéséhez.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{PRO_TRADER_PACK} Menü 💰", callback_data='show_menu')]])
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Megjeleníti az előfizetési menüt a Pro Trader csomaghoz."""
    chat_id = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton(f"💳 Revolut Pay ({REVOLUT_PRICE})", url=REVOLUT_PAY_LINK)],
        [InlineKeyboardButton(f"🪙 Binance Pay ({BINANCE_PRICE})", url=BINANCE_PAY_LINK)],
        [InlineKeyboardButton("✅ Fizettem / Hosszabbítás", callback_data='payment_check')],
        [InlineKeyboardButton("❓ Előfizetés státusz", callback_data='show_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"**Válassz fizetési módot a {PRO_TRADER_PACK} csomaghoz (30 napra):**\n"
             f"Kérlek, az utalás után használd a 'Fizettem' gombot a gyors rögzítéshez.",
        reply_markup=reply_markup
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Megjeleníti a felhasználó előfizetési státuszát."""
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    today = datetime.datetime.now()
    
    if not data or datetime.datetime.strptime(data[0], '%Y-%m-%d') <= today:
        status_message = "❌ **INAKTÍV ELŐFIZETÉS.** A Pro Trader csomag elemzéseihez kérlek, fizess elő a /menu paranccsal."
    else:
        end_date_str = data[0]
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        status_message = (
            f"✅ **{PRO_TRADER_PACK} CSOMAG AKTÍV!**\n"
            f"Lejárat dátuma: **{end_date_str}**\n"
            f"Hátra van: {(end_date - today).days + 1} nap."
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=status_message)

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Megjeleníti a napi AI elemzést (CSAK aktív előfizetőknek)."""
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    
    # Előfizetés ellenőrzése
    if not data or datetime.datetime.strptime(data[0], '%Y-%m-%d') <= datetime.datetime.now():
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="🚫 **Hozzáférés megtagadva.**\nAz AI elemzések csak aktív előfizetők számára elérhetők. /menu"
        )
        return
        
    # Elemzések lekérése a modulból (valós AI vagy szimulált adat)
    analysis_data = get_current_analysis()
    
    if not analysis_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ **Hiba az adatok lekérésekor.** Kérjük, próbálja újra később."
        )
        return

    # Elemzések formázása
    analysis_date = analysis_data['last_analysis_date']
    report = [f"📈 **SKYAI {PRO_TRADER_PACK} JELZÉS ({analysis_date})**\n"]
    
    # A weboldalon szereplő párokat jelenítjük meg
    for pair in CRYPTO_PAIRS:
        if pair in analysis_data['analyses']:
            analysis = analysis_data['analyses'][pair]
            report.append(f"--- **{pair}:** ---")
            report.append(f"**Trend:** {analysis['trend']}")
            report.append(f"**Kulcs szint/Javaslat:** {analysis['level']}")
    
    analysis_report = '\n\n'.join(report)
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text=analysis_report)


# --- 4. CALLBACK KEZELŐK (Inline gombok) ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kezeli az inline gombok megnyomását."""
    query = update.callback_query
    await query.answer()

    if query.data == 'show_menu':
        await menu_command(update, context)
        
    elif query.data == 'show_status':
        await status_command(update, context)

    elif query.data == 'payment_check':
        # Manuális ellenőrzési kérelem indítása
        keyboard = [
            [InlineKeyboardButton("Igen, megtörtént a fizetés!", callback_data='confirm_subscription')],
            [InlineKeyboardButton("Vissza a menübe", callback_data='show_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="**🏦 Fizetés Ellenőrzése**\n\n"
                 "Mivel a fizetés manuális (Revolut/Binance Pay), rögzítenünk kell a kérésed. Kérlek, nyomd meg az alábbi gombot, ha az utalás elindult, és várj az adminisztrátor jóváhagyására.",
            reply_markup=reply_markup
        )
        
    elif query.data == 'confirm_subscription':
        user_id = query.from_user.id
        
        await context.bot.send_message(
            chat_id=user_id,
            text="**⏳ Előfizetés aktiválás folyamatban...**\n\n"
                 "Rögzítettük a fizetési szándékodat. Értesítünk, amint a fizetés beérkezését követően az admin aktiválta az előfizetésedet!\n"
                 "Ez általában 1-6 órát vesz igénybe. Használd a /status parancsot az ellenőrzéshez."
        )
        logger.info(f"Új fizetési kérelem érkezett: {user_id}")


# --- 5. ADMIN FUNKCIÓK ---

async def activate_sub_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ADMIN: Előfizetés manuális aktiválása (a fizetés ellenőrzése után futtatva)
    Használat: /activatesub <user_id> <napok>
    """
    try:
        target_user_id = int(context.args[0])
        duration = int(context.args[1])
        new_end_date = update_subscription(target_user_id, duration)
        
        await update.message.reply_text(f"✅ Sikeresen aktiválva: Felhasználó ID: {target_user_id}, Lejárat: {new_end_date}")
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 **ELŐFIZETÉS AKTIVÁLVA!**\n"
                 f"Hozzáférsz a SkyAI elemzésekhez **{new_end_date}** dátumig. Használd a /analysis parancsot!"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Hibás formátum. Használat: /activatesub <user_id> <napok>")
    except Exception as e:
        await update.message.reply_text(f"❌ Hiba történt: {e}")

async def generate_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ADMIN: Kézzel indítja a napi elemzés generálását/frissítését
    """
    await update.message.reply_text("⏳ Napi AI elemzés generálása/frissítése indult...")
    
    if update_daily_analysis():
        await update.message.reply_text("✅ A napi AI elemzés sikeresen frissítve lett!")
    else:
        await update.message.reply_text("❌ Hiba történt a frissítés közben.")

# --- 6. FŐ FUTTATHATÓ KÓD ---

def main():
    """A bot fő funkcióinak beállítása és futtatása."""
    
    init_db()
    if not get_current_analysis():
        update_daily_analysis() # Adatok előállítása az első futtatáskor
        
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Felhasználói parancsok
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("analysis", analysis_command))
    
    # Admin parancsok
    application.add_handler(CommandHandler("activatesub", activate_sub_command))
    application.add_handler(CommandHandler("generateanalysis", generate_analysis_command))
    
    # Inline gomb kezelő
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("SkyAI Bot fut...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
