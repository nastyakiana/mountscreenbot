import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yfinance as yf
import matplotlib.pyplot as plt
import io

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker = update.message.text.strip().upper()
    await update.message.reply_text("🔍 Analyzing...")

    summary, buf = analyze_ticker(ticker)

    await update.message.reply_text(summary, parse_mode="HTML")
    if buf:
        await update.message.reply_photo(buf)

def analyze_ticker(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period='1mo')

        market_cap = info.get("marketCap", 0)
        prev_close = info.get("previousClose", 0)
        avg_volume = info.get("averageVolume", 0)
        insider_own = info.get("heldPercentInsiders", 0) * 100
        inst_own = info.get("heldPercentInstitutions", 0) * 100
        est_daily_vol = avg_volume * prev_close

        if len(hist) >= 2:
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            trend_pct = ((end_price - start_price) / start_price) * 100
        else:
            trend_pct = 0

        volume_median = hist['Volume'].median()
        suspicious_spikes = (hist['Volume'] > volume_median * 3).sum()
        if suspicious_spikes >= 2:
            wash_trading_comment = f"⚠️ {suspicious_spikes} spikes detected over 3× median volume"
        elif suspicious_spikes == 1:
            wash_trading_comment = f"⚠️ 1 spike detected over 3× median volume"
        else:
            wash_trading_comment = "✅ No significant anomalies"

        if est_daily_vol >= 5_000_000:
            liquidity = "✅ Strong liquidity"
        elif est_daily_vol >= 1_000_000:
            liquidity = "🟡 Sufficient liquidity"
        else:
            liquidity = "❌ Illiquid"

        inst_comment = "🟢 Strong institutional support" if inst_own >= 30 else "⚠️ Weak institutional interest"
        insider_comment = "🟢 Balanced ownership" if insider_own < 25 else "🔴 High insider concentration"
        verdict = "✅ Stock looks viable for financing" if est_daily_vol >= 1_000_000 and inst_own > 20 else "⚠️ Too illiquid or low-quality"

        def fmt(n, is_money=True):
            if n is None: return "—"
            if abs(n) >= 1e9:
                return f"${n/1e9:.2f}B" if is_money else f"{n/1e9:.2f}B"
            elif abs(n) >= 1e6:
                return f"${n/1e6:.2f}M" if is_money else f"{n/1e6:.2f}M"
            else:
                return f"${n:.2f}" if is_money else f"{n:.2f}"

        summary = f"""
<b>📊 {ticker_symbol.upper()} Analysis</b>
━━━━━━━━━━━━━━━━━━━━━
💰 <b>Market Cap:</b> {fmt(market_cap)}
📉 <b>Price:</b> {fmt(prev_close)}
📊 <b>Avg Volume:</b> {fmt(avg_volume, False)}
💵 <b>Est. Daily Volume:</b> {fmt(est_daily_vol)}

👥 <b>Ownership:</b>
• Insider: {insider_own:.2f}%
• Institutional: {inst_own:.2f}%
{insider_comment}
{inst_comment}

📈 <b>1mo Trend:</b> {'🔺' if trend_pct > 1 else '🔻' if trend_pct < -1 else '➖'} {trend_pct:.2f}%
💧 <b>Liquidity:</b> {liquidity}
🧼 <b>Wash Trading:</b> {wash_trading_comment}

<b>✅ Verdict:</b> {verdict}
""".strip()

        fig, ax = plt.subplots(figsize=(10, 3))
        hist['Volume'].plot(kind='bar', color='skyblue', ax=ax)
        plt.title(f"{ticker_symbol.upper()} — Volume (1mo)")
        plt.ylabel("Shares")
        plt.xticks([])
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return summary, buf

    except Exception as e:
        return f"⚠️ Error analyzing {ticker_symbol.upper()}: {e}", None

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
