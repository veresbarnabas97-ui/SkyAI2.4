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
# FIGYELEM: A token nyilvános kódban való tárolása biztonsági kockázatot jelent!
TELEGRAM_BOT_TOKEN = '8486431467:AAEMJ87kuhbwzYl529ypndfD7LsrQ52Ekx4'
DB_NAME = 'skyai_users.db'
# ÚJ: ADMIN ID BEÁLLÍTÁSA (VeresBarnabas1)
ADMIN_USER_ID = 1979330363 

# --- STRATÉGIAILAG INTEGRÁLT FIZETÉSI LINKEK ---
FIAT_PAYMENT_URL = 'https://revolut.me/veresbarnabas1?currency=HUF&amount=15000' 
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
    
    # 1. Lépés: Hozzuk létre a táblát, ha még nem létezik (az alap sémával)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        join_date TEXT,
        subscription_status TEXT DEFAULT 'free',
        pro_expiry_date TEXT -- Ezzel a definícióval dolgozunk
    )
''')

    # 2. Lépés: Ellenőrizzük, hogy létezik-e a 'pro_expiry_date' oszlop.
    # Ez megoldja a "no such column" hibát, ha a felhasználó korábbi adatbázis fájlt használ.
    try:
        cursor.execute("SELECT pro_expiry_date FROM users LIMIT 1")
    except sqlite3.OperationalError:
        logger.warning("Hiányzó 'pro_expiry_date' oszlop észlelve. Frissítem a sémát.")
        # Ha a lekérdezés hibát dob, hozzáadjuk az oszlopot
        cursor.execute("ALTER TABLE users ADD COLUMN pro_expiry_date TEXT")

    conn.commit()
    conn.close()

def set_user_status(user_id, new_status, expiry_months=1):
    """Adminisztrátori funkció a felhasználó státuszának és lejárati idejének beállítására."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if new_status == 'pro':
        current_date = datetime.datetime.now()
        # Hónap hozzáadása (kb. 30 nap)
        expiry_date = current_date + datetime.timedelta(days=expiry_months * 30) 
        expiry_date_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE users SET subscription_status = ?, pro_expiry_date = ? WHERE user_id = ?',
            (new_status, expiry_date_str, user_id)
        )
        msg = f"A felhasználó (ID: {user_id}) PRO státusza beállítva {expiry_date_str} dátumig."
    else:
        # Ha 'free'-re állítunk, a pro_expiry_date-et nullázzuk
        cursor.execute(
            'UPDATE users SET subscription_status = ?, pro_expiry_date = NULL WHERE user_id = ?',
            (new_status, user_id)
        )
        msg = f"A felhasználó (ID: {user_id}) státusza 'free'-re állítva."

    conn.commit()
    conn.close()
    return msg


def check_user_status(user_id):
    """Ellenőrzi a felhasználó státuszát, beleértve a PRO tagság lejárati dátumát is."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Lekérjük a subscription_status-t ÉS a pro_expiry_date-et
    cursor.execute('SELECT subscription_status, pro_expiry_date FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return 'free'
        
    status, expiry_date_str = result

    # 1. Ha a státusz nem 'pro', akkor marad 'free'
    if status != 'pro':
        return 'free'
    
    # 2. Ha 'pro', ellenőrizzük a lejárati dátumot
    if expiry_date_str:
        try:
            expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d %H:%M:%S')
            
            # Ha a lejárati dátum ELMÚLT, a státusz visszakerül 'free'-re
            if expiry_date < datetime.datetime.now():
                # Automatikus visszaminősítés
                set_user_status(user_id, 'free') 
                return 'free'
            else:
                return 'pro' # Még aktív
        except ValueError:
            logger.error(f"Hiba a lejárati dátum formátumával: {expiry_date_str}")
            return 'free' # Hiba esetén biztonsági okokból free

    # Ha 'pro' státusz van, de nincs lejárati dátum (hiba), akkor free
    return 'free'

# --- PARANCSKEZELŐK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Adatbázisba mentés és/vagy státusz lekérdezése
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Frissítés: user_id mint kulcs, join_date formázott stringként
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)',
                    (user.id, user.username, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
    """
    Kiküldi az aktuális AI elemzést a felhasználó státuszának megfelelően.
    """
    user_id = update.effective_user.id
    status = check_user_status(user_id) # Felhasználói státusz lekérése
    
    # Adatok lekérése a felhasználói státusz alapján 
    # (A get_current_analysis() feltételezhetően a háttérben kezeli a FREE/PRO logikát, 
    # de a PRO-nál több adatot ad vissza.)
    data = get_current_analysis(status)
    
    # Eltávolítottam a hibaokozó, rossz helyen lévő 'btc_info' ellenőrzést, 
    # mivel az adatok a 'data' változóból kerülnek kinyerésre az alábbi logikában.
    
    if status == 'pro':
        msg = "🔍 **AKTÍV PRO SZIGNÁLOK (VALÓS IDEJŰ):**\n\n"
        
        # Ellenőrizzük, hogy van-e adat. Ha nincs, a data lehet egy üres szótár.
        if not data:
            msg += "Nincs elérhető adat. Kérjük, próbáld újra később vagy használd a /generateanalysis parancsot (ha admin vagy)."
        else:
            for pair, info in data.items():
                icon = "🟢" if info['trend'] == 'BULLISH' else "🔴" if info['trend'] == 'BEARISH' else "⚪"
                
                # Biztonságos hozzáférés a valószínűséghez, ha hiányzik az ai_analyzer-ből
                probability = info.get('probability', 'N/A') 
                level = info.get('level', 'Nincs szint')
                
                msg += f"{icon} **{pair}**: {info['trend']} ({probability})\n"
                msg += f"   └ {level}\n\n"
            
        keyboard = [[InlineKeyboardButton("🔙 Vissza a Főmenübe", callback_data='start_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    else: # FREE felhasználó ('Kezdő Sky')
        msg = "🔍 **Kezdő Sky Elemzés (Korlátozott):**\n\n"
        msg += "A SkyAI csak a fő kereskedési párt (BTC) mutatja a FREE csomagban. Nézd meg a mai legfontosabb elemzésünket:\n\n"
        
        # Csak BTC adat mutatása 
        # Feltételezzük, hogy a BTC/USDC a kulcs.
        btc_info = data.get('BTC/USDC', {'trend': 'Nincs adat', 'probability': '0%', 'level': 'Frissítés szükséges'})
        
        # A KeyErrors elkerülése érdekében most már a 'btc_info' objektumot használjuk:
        icon = "🟢" if btc_info.get('trend') == 'BULLISH' else "🔴" if btc_info.get('trend') == 'BEARISH' else "⚪"
        probability = btc_info.get('probability', 'N/A')
        trend = btc_info.get('trend', 'Nincs adat')
        level = btc_info.get('level', 'Frissítés szükséges')

        msg += f"{icon} **BTC/USDC**: {trend} ({probability})\n"
        msg += f"   └ {level}\n\n"
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
    # A hiba elkerülése érdekében átadtuk az is_command=True-t a korrigált send_analysis-nek
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

async def refresh_analysis_daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    """A JobQueue által hívott függvény a napi elemzés frissítésére."""
    # A szinkron update_daily_analysis() meghívása
    result_msg = update_daily_analysis()
    
    logger.info(f"Automatikus Elemzés Frissítés: {result_msg}")
    
    # Értesítés küldése az adminisztrátornak
    try:
          await context.bot.send_message(chat_id=ADMIN_USER_ID, text=f"✅ Napi elemzés frissítve. {result_msg}")
    except Exception as e:
          logger.error(f"Hiba az admin értesítésekor: {e}")

# Kézi indítás adminisztrátor számára a napi elemzés frissítésére. (NameError javítása)
async def admin_generate_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Kézi indítás adminisztrátor számára a napi elemzés frissítésére.
    """
    user = update.effective_user

    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ Nincs jogosultságod ehhez a parancshoz.")
        return

    await update.message.reply_text("⚙️ Elemzés generálása elindult...")
    
    # A szinkron update_daily_analysis() meghívása
    result_msg = update_daily_analysis()
    
    await update.message.reply_text(f"✅ Manuális elemzés frissítés befejezve:\n\n`{result_msg}`", parse_mode='Markdown')
    logger.info(f"Manuális Elemzés Frissítés: {result_msg}")

async def admin_set_pro_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin parancs a felhasználó PRO státuszának beállítására."""
    user = update.effective_user

    # Admin jogosultság ellenőrzése a beállított ID-vel
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ Nincs jogosultságod ehhez a parancshoz.")
        return

    # Parancs formátum ellenőrzése: /setpro <user_id> [hónapok száma]
    try:
        if len(context.args) < 1:
            raise IndexError("Hiányzó User ID.")
            
        target_user_id = int(context.args[0])
        expiry_months = int(context.args[1]) if len(context.args) > 1 else 1 # Alapértelmezés: 1 hónap
        
        result_msg = set_user_status(target_user_id, 'pro', expiry_months)
        await update.message.reply_text(f"✅ Sikeres beállítás:\n{result_msg}", parse_mode='Markdown')
        
        # Opcionálisan: Értesítés küldése a felhasználónak
        try:
              await context.bot.send_message(
                 chat_id=target_user_id, 
                 text="🥳 **Gratulálunk!** A SkyAI PRO előfizetésed aktiválva lett. Kereskedj valós idejű szignálokkal!\n\n/signals",
                 parse_mode='Markdown'
              )
        except Exception:
              await update.message.reply_text(f"⚠️ Hiba a felhasználó értesítésekor (ID: {target_user_id}).")

    except Exception:
        await update.message.reply_text(f"❌ Hibás formátum. Használd így: `/setpro <user_id> [hónap]`\nPl.: `/setpro 987654321 1`", parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Callback logika a főmenü irányítására
    if query.data == 'analysis':
        # send_analysis hívása gombnyomásból, itt nem parancsról van szó
        await send_analysis(update, context, is_command=False) 
    elif query.data == 'subscribe':
        await subscribe_message(update, context)
    elif query.data == 'help':
        await help_command(update, context) 
    elif query.data == 'start_menu':
        await start(update, context)

# ----------------- HIBÁK GRACEFUL KEZELÉSE -----------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logolja a hibát és küld egy értesítést az adminisztrátornak (ha lehetséges)."""
    logger.error("Az update %s hibát okozott: %s", update, context.error)
    
    # Próbáljuk meg elküldeni a hibaüzenetet az adminnak
    if ADMIN_USER_ID:
        error_message = f"🚨 **KRITIKUS HIBA A BOTBAN** 🚨\n\n"
        error_message += f"Függvény: {context.callback_name if hasattr(context, 'callback_name') else 'Nincs adat'}\n"
        error_message += f"Hiba: `{context.error}`\n\n"
        error_message += "Kérjük, ellenőrizd a bot logját."
        
        try:
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=error_message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Hiba az admin értesítésekor a fő hibakezelőben: {e}")

# --- FŐ PROGRAM ---

def main():
    print("A SkyAI Bot indul...")
    init_db() # Ez most már frissíti a sémát, ha szükséges
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # >>>>>>>>>>>>> JOBQUEUE (IDŐZÍTÉS) BEÁLLÍTÁSA <<<<<<<<<<<<<
    job_queue = application.job_queue
    
    if job_queue is None:
        logger.error("A JobQueue nincs telepítve. Kérjük, futtassa: pip install \"python-telegram-bot[job-queue]\"")
    else:
        # Beállítjuk a napi frissítést minden nap 09:00:00-kor
        job_queue.run_daily(
            refresh_analysis_daily, 
            time=datetime.time(hour=9, minute=0, second=0), 
            days=(0, 1, 2, 3, 4, 5, 6), 
            name='daily_analysis_update'
        )
        logger.info("Napi elemzés frissítés időzítve 09:00:00-ra.")
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Parancs Handlerek hozzáadása
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("signals", signals_command))
    application.add_handler(CommandHandler("pro", pro_command))
    application.add_handler(CommandHandler("generateanalysis", admin_generate_analysis)) # Admin parancs
    application.add_handler(CommandHandler("setpro", admin_set_pro_status)) # Admin parancs

    # Callback/Gomb Handlerek hozzáadása
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # 🌟 ÚJ: Hibakezelő hozzáadása
    application.add_error_handler(error_handler)


    print("A Bot sikeresen fut! (Nyomj Ctrl+C-t a leállításhoz)")
    application.run_polling()

if __name__ == '__main__':
    main()
