import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Fawaz Confluence Hunter", layout="wide", page_icon="📈")

st.title("🧠 Fawaz Almutairi Confluence Scanner")
st.markdown("**Multi-Timeframe Technical Scanner** - Pullback Setups (Saudi + US)")

# Sidebar
st.sidebar.header("Settings")
markets = st.sidebar.selectbox("Market", ["US Tech/Growth", "Saudi TASI (Limited)", "Both"])
min_score = st.sidebar.slider("Minimum Confluence Score", 70, 100, 85)

# Tickers
us_tickers = ['NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'META', 'TSLA', 'AMD']
sa_tickers = ['2222.SR', '2380.SR', '2082.SR', '1120.SR']

if markets == "US Tech/Growth":
    tickers = us_tickers
elif markets == "Saudi TASI (Limited)":
    tickers = sa_tickers
else:
    tickers = us_tickers + sa_tickers

def get_data(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if data.empty or len(data) < 60:
            return None
        return data
    except:
        return None

def analyze_setup(df, ticker):
    if df is None or len(df) < 60:
        return None
    try:
        df = df.copy()
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        close_latest = float(df['Close'].iloc[-1])
        ema20_latest = float(df['EMA20'].iloc[-1])
        ema50_latest = float(df['EMA50'].iloc[-1])
        rsi_latest = float(df['RSI'].iloc[-1])
        rsi_5ago = float(df['RSI'].iloc[-6]) if len(df) > 6 else rsi_latest
        
        # Fawaz Higher TF Trend
        higher_trend_bull = (close_latest > ema20_latest > ema50_latest) and (ema20_latest > ema50_latest)
        
        # Pullback to EMA zone
        recent_low = float(df['Close'].rolling(20).min().iloc[-1])
        pullback = (close_latest > recent_low * 0.97) and (close_latest < ema20_latest * 1.03)
        
        # Momentum
        rsi_rising = rsi_latest > rsi_5ago
        
        # Confluence Score
        score = 0
        if higher_trend_bull:
            score += 40
        if pullback:
            score += 30
        if rsi_rising and rsi_latest > 52:
            score += 20
        if close_latest > ema20_latest:
            score += 10
        
        score = min(100, score)
        
        if score >= min_score:
            return {
                'ticker': ticker,
                'price': round(close_latest, 2),
                'change': round((close_latest / float(df['Close'].iloc[-2]) - 1) * 100, 2),
                'score': score,
                'trend': 'Strong Bullish 🔥' if higher_trend_bull else 'Neutral',
                'setup': 'EMA Pullback + RSI' if pullback else 'Monitor',
                'target': round(close_latest * 1.18, 2)
            }
    except:
        return None
    return None

# Scanner Button
if st.button("🔄 Run Fawaz Scanner Now"):
    with st.spinner("Scanning for perfect high-confluence setups..."):
        results = []
        for ticker in tickers:
            df = get_data(ticker)
            setup = analyze_setup(df, ticker)
            if setup:
                results.append(setup)
            time.sleep(0.3)
        
        if results:
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values('score', ascending=False)
            
            st.success(f"Found {len(results)} Perfect Fawaz Setups!")
