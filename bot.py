import logging
import sqlite3
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# --- KONFIGURÁCIÓ ---
TELEGRAM_BOT_TOKEN = '8486431467:AAEMJ87kuhbwzYl529ypndfD7LsrQ52Ekx4' # SkyAI_ProBot
ADMIN_USER_ID = 1979330363 

# WEB DASHBOARD URL-ek (A te GitHub Pages címed)
BASE_URL = "https://veresbarnabas97-ui.github.io/SkyAI2.4" 

DASHBOARD_LINKS = {
    'sniper': f"{BASE_URL}/SkyAISniper.html",
    'whale': f"{BASE_URL}/SkyAIWhale.html"
}

# TITKOS BOTOK LINKJEI
BOT_LINKS = {
    'sniper': 'https://t.me/SkyAISniper_Bot',
    'whale': 'https://t.me/SkyAIWhale_Bot'
}

PAYMENT_INFO = {
    'revolut_sniper': 'https://revolut.me/veresbarnabas1?currency=HUF&amount=15000',
    'revolut_whale': 'https://revolut.me/veresbarnabas1?currency=HUF&amount=45000',
    'binance': 'https://s.binance.com/LfcBZowU'
}

DB_NAME = 'skyai_users.db'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ADATBÁZIS ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, join_date TEXT, subscription_tier TEXT DEFAULT 'free', expiry_date TEXT)''')
    conn.commit()
    conn.close()

def update_tier(user_id, tier):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE users SET subscription_tier = ?, expiry_date = ? WHERE user_id = ?', (tier, expiry_str, user_id))
    conn.commit()
    conn.close()
    return expiry_str

def register_user(user):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)', (user.id, user.username, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# --- HANDLEREK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)
    
    text = (
        f"🌌 **Üdvözöllek a SkyAI Központban, {user.first_name}!**\n\n"
        "Ez a rendszer a **SPOT AI Botok** és a **Pooolse** ökoszisztéma belépési pontja.\n"
        "Itt aktiválhatod a hozzáférésedet a privát Dashboardokhoz és az AI szignálokhoz.\n\n"
        "🔻 **Válassz Csomagot:**"
    )
    keyboard = [
        [InlineKeyboardButton("🎯 SkyAI Sniper (Spot) - 15k Ft", callback_data='info_sniper')],
        [InlineKeyboardButton("🐋 SkyAI Whale (VIP) - 45k Ft", callback_data='info_whale')],
        [InlineKeyboardButton("🆘 Ügyfélszolgálat", url="https://t.me/VeresBarnabas1")]
    ]
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier = query.data.split('_')[1] 
    
    tier_name = "SNIPER" if tier == 'sniper' else "WHALE VIP"
    
    text = (
        f"💎 **SkyAI {tier_name} SPOT CSOMAG**\n\n"
        "Az előfizetés tartalma:\n"
        "1. **Privát Webes Dashboard** (Grafikonok + AI)\n"
        "2. **Titkos Telegram Bot** (Azonnali értesítések)\n"
        "3. **Pooolse Integráció** (Jövőbeli update)\n\n"
        "💳 **Fizetés:** Utalás után küldd el a bizonylatot ide: @VeresBarnabas1"
    )
    
    pay_link = PAYMENT_INFO[f'revolut_{tier}']
    
    keyboard = [
        [InlineKeyboardButton("💳 Fizetés (Revolut)", url=pay_link)],
        [InlineKeyboardButton("🪙 Fizetés (Binance Pay)", url=PAYMENT_INFO['binance'])],
        [InlineKeyboardButton("🔙 Vissza", callback_data='start')]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# --- ADMIN JÓVÁHAGYÁS ---
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_USER_ID: return

    try:
        target_id = int(context.args[0])
        tier = context.args[1].lower()
        if tier not in ['sniper', 'whale']: return

        expiry = update_tier(target_id, tier)
        
        web_dashboard = DASHBOARD_LINKS[tier]
        telegram_bot = BOT_LINKS[tier]

        msg = (
            f"✅ **FIZETÉS ELFOGADVA!**\n"
            f"Köszönjük a bizalmat. A SkyAI {tier.upper()} csomagod aktív.\n\n"
            "📦 **Itt vannak a titkos hozzáféréseid:**\n\n"
            f"🖥️ **1. Privát Webes Dashboard (Mentsd el!):**\n{web_dashboard}\n\n"
            f"🤖 **2. Titkos Értesítő Bot:**\n{telegram_bot}\n\n"
            "Jó kereskedést kíván a SkyAI & Pooolse csapata!"
        )

        await context.bot.send_message(chat_id=target_id, text=msg, parse_mode='Markdown')
        await update.message.reply_text(f"User {target_id} aktiválva. Linkek elküldve.")

    except Exception as e:
        await update.message.reply_text(f"Hiba: {e}")

def main():
    init_db()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CallbackQueryHandler(info_handler, pattern='^info_'))
    application.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    print("SkyAI Gatekeeper ProBot Indul...")
    application.run_polling()

if __name__ == '__main__':
    main()
