import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# --- KONFIGURÁCIÓ ---
# SkyAISniper_Bot Token (Amit megadtál)
TOKEN = '8332155247:AAHmYnKDhllMRHFepYqjZE29Pao3VdMc5UM'

# A te GitHub Pages linked a Sniper Dashboardhoz
DASHBOARD_LINK = "https://veresbarnabas97-ui.github.io/SkyAI/SkyAISniper.html" 
POOOLSE_LINK = "https://app.pooolse.com/join/7974"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- MENÜK ÉS ÜZENETEK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Főmenü és Üdvözlés"""
    user = update.effective_user
    
    text = (
        f"🎯 **Üdvözöllek a SkyAI Sniper Egységben, {user.first_name}!**\n\n"
        "Ez a bot a te személyes stratégiai központod. Itt nem csak jeleket kapsz, hanem megtanulod, hogyan használd a **Deep Scanner** technológiát a tőkéd növelésére.\n\n"
        "📉 **Fókusz:** SPOT kereskedés\n"
        "⚡ **Stílus:** Agilis, Precíz, Biztonságos\n\n"
        "Miben segíthetek ma?"
    )

    keyboard = [
        [InlineKeyboardButton("🖥️ Webes Terminál (Élő Scanner)", url=DASHBOARD_LINK)],
        [InlineKeyboardButton("📘 Mi az a Deep Scanner?", callback_data='edu_deepscan')],
        [InlineKeyboardButton("💰 Stratégia Kistőkével", callback_data='strat_lowcap')],
        [InlineKeyboardButton("🤖 Pooolse Bot Ajánló", callback_data='pooolse_info')],
        [InlineKeyboardButton("🆘 Kapcsolat", url="https://t.me/VeresBarnabas1")]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def education_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deep Scanner Oktató Anyag"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "📘 **A SkyAI Deep Scanner Technológiája**\n\n"
        "A legtöbb kezdő ott rontja el, hogy csak az árat nézi. A Deep Scanner a piac **mélységét** vizsgálja.\n\n"
        "🔍 **Mit figyelünk valós időben?**\n"
        "1. **MA(200) - A Bálna Vonal:** Ha az árfolyam ez alatt van, TILOS a Spot vétel. Ez a mi védelmi pajzsunk a medvepiac ellen.\n"
        "2. **MA(25) & MA(75):** A rövid távú trendek keresztezései. Itt lépünk be (Sniper Entry).\n"
        "3. **Bollinger Szalagok:** Amikor a szalagok 'összenyomódnak' (Squeeze), az vihar előtti csendet jelent. Ilyenkor készülünk a robbanásra.\n\n"
        "💡 *A Webes Terminálon ezeket az adatokat látod másodperc alapú frissítéssel.*"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Vissza a Menübe", callback_data='start_menu')]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def strategy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kistőkés Stratégia Tervező"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "💰 **Sniper Stratégia: Építkezés Kistőkével ($100 - $1000)**\n\n"
        "Nem kell milliókkal kezdened. A titok a **Kamatos Kamat** és a **Fegyelem**.\n\n"
        "📋 **A Terv:**\n"
        "1. **Ne kapkodj:** Csak akkor lépj, ha a Deep Scanner 90%+ valószínűséget jelez (Zöld zóna).\n"
        "2. **DCA (Dollar Cost Averaging):** Ha van rá lehetőséged, heti/havi szinten utalj be kisebb összeget (pl. $20-$50). Ez kisimítja a beszállóidat.\n"
        "3. **Take Profit:** Ne legyél mohó. Ha megvan a 3-5% profit egy Spot pozíción, zárd le, vagy húzd fel a Stop-Loss-t.\n\n"
        "🚀 *Cél: A tőke megduplázása biztonságos lépésekkel, nem szerencsejátékkal.*"
    )
    
    keyboard = [
        [InlineKeyboardButton("Hogyan automatizáljam? (Pooolse)", callback_data='pooolse_info')],
        [InlineKeyboardButton("🔙 Vissza", callback_data='start_menu')]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def pooolse_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pooolse Integráció és Bot Ajánló"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "🤖 **SkyAI x Pooolse: Automatizált Profit**\n\n"
        "A SkyAI megadja a jelet, a Pooolse pedig végrehajtja. Ez a tökéletes párosítás, ha nincs időd a gép előtt ülni.\n\n"
        "🛠️ **Ajánlott Botok Sniper Tagoknak:**\n"
        "🔹 **Spot Grid Bot:** Oldalazó piacon (amikor a Scanner 'Neutral'-t jelez). Kicsi, de biztos profitot termel a hullámzásokból.\n"
        "🔹 **Infinity Grid:** Ha a Scanner 'LONG (Breakout)'-ot jelez. Ez követi az emelkedő trendet a végtelenségig.\n\n"
        "👇 **Indítsd el a saját botodat itt:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Pooolse Fiók Létrehozása / Belépés", url=POOOLSE_LINK)],
        [InlineKeyboardButton("🔙 Vissza a Menübe", callback_data='start_menu')]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Visszatérés a főmenübe (Gombnyomásra)"""
    await start(update, context)

# --- MAIN ---

def main():
    print("SkyAI Sniper Bot (Mentor Modul) Indítása...")
    application = Application.builder().token(TOKEN).build()

    # Handlerek
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", lambda u,c: u.message.reply_text("Itt vagyok! Kattints a /start -ra a menü megnyitásához.")))
    
    # Callback Handlerek
    application.add_handler(CallbackQueryHandler(education_handler, pattern='^edu_deepscan$'))
    application.add_handler(CallbackQueryHandler(strategy_handler, pattern='^strat_lowcap$'))
    application.add_handler(CallbackQueryHandler(pooolse_handler, pattern='^pooolse_info$'))
    application.add_handler(CallbackQueryHandler(start_menu_callback, pattern='^start_menu$'))

    application.run_polling()

if __name__ == '__main__':
    main()
