import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(
    page_title="VECTIS Market Watch",
    page_icon="📈",
    layout="wide"
)

# --- STYLES ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #00FFCC;
    }
    .metric-delta-up {
        color: #00FF00;
    }
    .metric-delta-down {
        color: #FF0000;
    }
</style>
""", unsafe_allow_html=True)

# --- TARGETS ---
TICKERS = {
    "🇺🇸 S&P 500": "^GSPC",
    "🇯🇵 Nikkei 225": "^N225",
    "💵 USD/JPY": "JPY=X",
    "🔶 Bitcoin": "BTC-USD",
    "💎 Ethereum": "ETH-USD",
    "🏢 TSMC": "TSM",
    "🤖 NVIDIA": "NVDA"
}

def get_data(ticker_symbol, period="1mo", interval="1d"):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period, interval=interval)
    return hist

def plot_sparkline(data, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines',
        line=dict(color='#00FFCC', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.1)'
    ))
    fig.update_layout(
        title=title,
        xaxis_visible=False,
        yaxis_visible=False,
        margin=dict(l=0, r=0, t=30, b=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

# --- MAIN ---
st.title("📈 VECTIS Market Watch")
st.write(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

# Layout
cols = st.columns(len(TICKERS))
# Wrap columns if too many
col_idx = 0
row_cols = st.columns(4)

for name, symbol in TICKERS.items():
    with row_cols[col_idx % 4]:
        try:
            data = get_data(symbol, period="5d") # Short period for quick load
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                prev_price = data['Close'].iloc[-2]
                delta = current_price - prev_price
                delta_pct = (delta / prev_price) * 100
                
                # Display metric
                st.metric(
                    label=name,
                    value=f"{current_price:,.2f}",
                    delta=f"{delta:,.2f} ({delta_pct:+.2f}%)"
                )
                
                # Sparkline (Mini chart)
                # chart_data = get_data(symbol, period="3mo")
                # st.plotly_chart(plot_sparkline(chart_data, ""), use_container_width=True)
                
            else:
                st.error(f"No data: {name}")
        except Exception as e:
            st.error(f"Error: {e}")
            
    col_idx += 1
    if col_idx % 4 == 0 and col_idx < len(TICKERS):
        row_cols = st.columns(4) # New row

st.divider()

# --- DETAILED CHART ---
st.sidebar.header("📊 Detail View")
selected_ticker = st.sidebar.selectbox("Select Asset", list(TICKERS.keys()))
period = st.sidebar.select_slider("Period", options=["1mo", "3mo", "6mo", "1y", "5y", "max"], value="6mo")

st.subheader(f"History: {selected_ticker}")
symbol = TICKERS[selected_ticker]
long_data = get_data(symbol, period=period)

if not long_data.empty:
    # Candle chart
    fig = go.Figure(data=[go.Candlestick(
        x=long_data.index,
        open=long_data['Open'],
        high=long_data['High'],
        low=long_data['Low'],
        close=long_data['Close']
    )])
    fig.update_layout(
        height=500,
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Loading chart data...")
