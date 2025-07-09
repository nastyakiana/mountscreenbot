import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

def analyze_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")

        if hist.empty:
            return f"⚠️ No data available for {ticker}"

        # Основные метрики
        market_cap = stock.info.get("marketCap", 0)
        price = stock.info.get("currentPrice", 0)
        avg_volume = stock.info.get("averageVolume", 0)
        insider_pct = stock.info.get("heldPercentInsiders", 0)
        institutional_pct = stock.info.get("heldPercentInstitutions", 0)

        # Тренд
        first_close = hist["Close"].iloc[0]
        last_close = hist["Close"].iloc[-1]
        trend_pct = ((last_close - first_close) / first_close) * 100

        # Ликвидность
        est_daily_value = avg_volume * price
        liquidity = "Illiquid" if est_daily_value < 100000 else "Liquid"

        # Wash trading (спайки)
        volumes = hist["Volume"]
        median_vol = np.median(volumes)
        spikes = sum(volumes > 3 * median_vol)

        # График
        plt.figure(figsize=(6,3))
        plt.bar(hist.index, hist["Volume"], color="skyblue")
        plt.title(f"{ticker} — Volume (1mo)")
        plt.ylabel("Shares")
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

        # Итог
        result = f"""
📊 *{ticker} Analysis*
━━━━━━━━━━━━━━━━━━
💰 *Market Cap:* ${market_cap / 1e6:.2f}M  
💵 *Price:* ${price}  
📈 *Avg Volume:* {int(avg_volume):,}  
💸 *Est. Daily Volume:* ${est_daily_value:,.2f}  

👥 *Ownership:*  
• Insider: {insider_pct:.2%}  
• Institutional: {institutional_pct:.2%}  
{'🟢 Balanced ownership' if insider_pct > 0 and institutional_pct > 0 else '⚠️ Weak institutional interest'}

📉 *1mo Trend:* {'🔺' if trend_pct > 0 else '🔻'} {trend_pct:.2f}%  
💧 *Liquidity:* {'❌ Illiquid' if liquidity == 'Illiquid' else '✅ Liquid'}  
🧼 *Wash Trading:* ⚠️ {spikes} spikes detected over 3× median volume

✅ *Verdict:* {'⚠️ Too illiquid or low-quality' if liquidity == 'Illiquid' else '✅ Reasonable trading quality'}

🔗 [Yahoo Finance for {ticker}](https://finance.yahoo.com/quote/{ticker})
"""

        return result

    except Exception as e:
        return f"❌ Error analyzing {ticker}: {e}"
