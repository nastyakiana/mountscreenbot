import yfinance as yf
import matplotlib.pyplot as plt
import io
import numpy as np

def analyze_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")

        if hist.empty:
            return {"text": f"⚠️ No data available for {ticker}"}

        # Основные метрики
        info = stock.info
        market_cap = info.get("marketCap", 0)
        price = info.get("currentPrice", 0)
        avg_volume = info.get("averageVolume", 0)
        insider_pct = info.get("heldPercentInsiders", 0)
        institutional_pct = info.get("heldPercentInstitutions", 0)

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

        # 📊 График
        plt.figure(figsize=(6, 3))
        plt.bar(hist.index, hist["Volume"], color="skyblue")
        plt.title(f"{ticker} — Volume (1mo)")
        plt.ylabel("Shares")
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        # 📝 Текст анализа
        result_text = f"""
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
🧼 *Wash Trading:* ⚠️ {spikes} volume spikes > 3× median

🔗 [View on Yahoo Finance](https://finance.yahoo.com/quote/{ticker})
"""

        return {"text": result_text.strip(), "image": buf}

    except Exception as e:
        return {"text": f"❌ Error analyzing {ticker}: {e}"}
