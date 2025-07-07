
import logging
import os
import yfinance as yf
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Send me a stock ticker (e.g., AAPL) and I'll give you a quick summary.")

async def analyze_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a ticker symbol (e.g., /analyze AAPL).")
        return

    ticker = context.args[0].upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="5d")

        if hist.empty:
            await update.message.reply_text(f"Could not retrieve data for {ticker}.")
            return

        current_price = info.get("currentPrice", "N/A")
        fifty_day_avg = info.get("fiftyDayAverage", "N/A")
        two_hundred_day_avg = info.get("twoHundredDayAverage", "N/A")
        volume = info.get("volume", "N/A")
        average_volume = info.get("averageVolume", "N/A")
        sector = info.get("sector", "N/A")
        market_cap = info.get("marketCap", "N/A")

        reply = (
            f"📈 *{ticker}* Quick Summary:\n"
            f"• Current Price: ${current_price}\n"
            f"• 50D Avg: ${fifty_day_avg}\n"
            f"• 200D Avg: ${two_hundred_day_avg}\n"
            f"• Volume: {volume}\n"
            f"• Avg Volume: {average_volume}\n"
            f"• Sector: {sector}\n"
            f"• Market Cap: ${market_cap}"
        )
        await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        await update.message.reply_text(f"An error occurred while analyzing {ticker}.")

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze_ticker))

    # Webhook instead of polling
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"https://mountscreenbot.onrender.com"
    )

if __name__ == "__main__":
    main()
