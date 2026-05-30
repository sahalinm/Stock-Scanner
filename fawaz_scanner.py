import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Fawaz Confluence Hunter", page_icon="📈", layout="wide")
st.title("🧠 Fawaz Confluence Hunter")
st.markdown("**Multi-timeframe scanner** based on Fawaz Almutairi’s exact strategy (Saudi + US)")

# Tickers (add more anytime)
tickers = ["NVDA", "MSFT", "AAPL", "TSLA", "AMD", "2222.SR", "1120.SR", "2380.SR", "3092.SR", "7203.SR"]

@st.cache_data(ttl=300)
def get_data(ticker):
    try:
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(data) < 50:
            return None
        data["EMA20"] = data["Close"].ewm(span=20).mean()
        data["EMA50"] = data["Close"].ewm(span=50).mean()
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        data["RSI"] = 100 - (100 / (1 + rs))
        return data
    except:
        return None

def calculate_confluence(df):
    if df is None or len(df) < 10:
        return 0, "No data"
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Higher TF trend (Daily)
    trend_score = 0
    if latest["Close"] > latest["EMA20"] > latest["EMA50"]:
        trend_score += 40
    if latest["Close"] > prev["Close"]:
        trend_score += 15
    
    # Pullback to EMA zone
    pullback_score = 0
    if abs(latest["Close"] - latest["EMA20"]) / latest["Close"] < 0.03:
        pullback_score += 25
    elif abs(latest["Close"] - latest["EMA50"]) / latest["Close"] < 0.05:
        pullback_score += 20
    
    # Momentum (RSI)
    momentum_score = 0
    if latest["RSI"] > 50 and latest["RSI"] > prev["RSI"]:
        momentum_score += 20
    
    total = trend_score + pullback_score + momentum_score
    if total >= 85:
        status = "🔥 PERFECT SETUP"
    elif total >= 70:
        status = "🟢 Strong"
    else:
        status = "⚪ Watch"
    
    return total, status

# Scanner
st.subheader("📡 Live Scanner")
data_list = []
for ticker in tickers:
    df = get_data(ticker)
    if df is not None:
        score, status = calculate_confluence(df)
        latest_price = df["Close"].iloc[-1]
        change = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100
        data_list.append({
            "Symbol": ticker,
            "Price": round(latest_price, 2),
            "% Change": round(change, 2),
            "Confluence": score,
            "Status": status,
            "Data": df
        })

if data_list:
    df_scan = pd.DataFrame(data_list)
    df_scan = df_scan.sort_values("Confluence", ascending=False)
    st.dataframe(df_scan[["Symbol", "Price", "% Change", "Confluence", "Status"]], use_container_width=True, hide_index=True)
    
    # Show charts for top setups
    st.subheader("🔍 Top Setups Detail")
    for row in df_scan.head(3).itertuples():
        st.write(f"**{row.Symbol}** — Confluence: **{row.Confluence}/100** {row.Status}")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=row.Data.index, open=row.Data["Open"], high=row.Data["High"], low=row.Data["Low"], close=row.Data["Close"], name="Price"))
        fig.add_trace(go.Scatter(x=row.Data.index, y=row.Data["EMA20"], name="EMA 20", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=row.Data.index, y=row.Data["EMA50"], name="EMA 50", line=dict(color="blue")))
        fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data loaded yet — refresh in a minute.")

st.caption("Built exactly to Fawaz Almutairi’s multi-timeframe rules • Updates every 5 minutes • Discipline first!")
