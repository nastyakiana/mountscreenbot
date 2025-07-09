import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from utils import analyze_ticker  # ваш анализатор

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a ticker (e.g., TSLA), and I'll analyze it for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker = update.message.text.strip().upper()
    logger.info(f"Received ticker: {ticker}")

    try:
        result = analyze_ticker(ticker)

        if "error" in result or "text" not in result:
            await update.message.reply_text(result.get("text", "Something went wrong."))
        else:
            if "image" in result:
                await update.message.reply_photo(photo=result["image"], caption=result["text"], parse_mode="Markdown")
            else:
                await update.message.reply_text(result["text"], parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error analyzing ticker: {e}")
        await update.message.reply_text("Sorry, something went wrong. Please try again later.")

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
