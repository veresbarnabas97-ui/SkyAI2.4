import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- KONFIGURÁCIÓ ---
# FIGYELEM: Ez a SkyAI Whale Értesítő Bot tokenje, amelyet élesíteni kell
TELEGRAM_BOT_TOKEN = '8414813040:AAGNNWePEdixbhBC2-JEd-riObEcjGX6iIs' 

# Admin ID (a teszteléshez, ide fog menni a szignál, ha a /signal parancsot használja)
# Cserélje ki 1979330363-at a saját ADMIN_USER_ID-jére
ADMIN_USER_ID = 1979330363 

# Ide tárolhatja majd a fizetős felhasználók listáját egy adatbázisból/fájlból
WHALE_SUBSCRIBERS = [ADMIN_USER_ID] 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- HANDLEREK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A /start parancs kezelése, ami alapvető üdvözletet küld (fontos a működéshez)."""
    user_id = update.effective_user.id
    if user_id in WHALE_SUBSCRIBERS:
        text = (
            "🐋 **Üdvözöllek a SkyAI Whale (VIP) Értesítő Botban!**\n\n"
            "Ez a privát csatorna biztosítja az azonnali AI szignálokat és fontos frissítéseket.\n"
            "Készülj a következő szignálra!"
        )
    else:
        text = (
            "⚠️ **Hozzáférés Megtagadva!**\n\n"
            "Ez a bot a **SkyAI Whale (VIP)** csomag előfizetői számára készült, és privát. "
            "A hozzáférés megszerzéséhez látogasson el a fő központunkba!"
        )
    await update.message.reply_text(text, parse_mode='Markdown')

async def send_test_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ADMIN parancs: Teszt szignál küldése a WHALE_SUBSCRIBERS listában szereplő ID-kre."""
    # Csak az admin küldhet teszt szignált
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Nincs jogosultságod ehhez a parancshoz.")
        return

    # Az AI által generált szignál üzenete
    signal_message = (
        "📈 **SKYAI WHALE VIP SZIGNÁL** 🐋\n\n"
        "**COIN:** **ETH/USDT**\n"
        "**Típus:** **LONG (Vétel)**\n"
        "**Belépési Zóna:** $3100 - $3150\n"
        "**Célár (TP1):** $3250 (3.2x tőkeáttétel)\n"
        "**Stop Loss (SL):** $3080\n\n"
        "▶️ **Futtatás:** Szigorúan 5x-ös tőkeáttétel ajánlott.\n"
        "Ne feledje: Ne fektessen be annál többet, mint amennyit hajlandó elveszíteni!"
    )

    sent_count = 0
    for user_id in WHALE_SUBSCRIBERS:
        try:
            await context.bot.send_message(
                chat_id=user_id, 
                text=signal_message, 
                parse_mode='Markdown'
            )
            sent_count += 1
        except Exception as e:
            logger.warning(f"Sikertelen szignálküldés az ID {user_id} részére: {e}")

    await update.message.reply_text(f"✅ Teszt szignál elküldve {sent_count} felhasználónak (beleértve Önt is, ha szerepel a listában).")

def main():
    """A bot elindítása (polling módban)."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Parancsok hozzáadása
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", send_test_signal)) # Admin tesztelésre

    logger.info("SkyAI Whale Signal Bot indítása...")
    application.run_polling()

if __name__ == '__main__':
    main()
