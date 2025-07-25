import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import ta  # For technical indicators

def main():
    st.sidebar.title("Stock Market Dashboard")
    
    # User inputs for stock and data options
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
    period = st.sidebar.selectbox("Period", options=["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=3)
    interval = st.sidebar.selectbox("Interval", options=["1m", "5m", "15m", "1h", "1d"], index=4)
    
    st.title(f"Real-Time Stock Dashboard: {symbol.upper()}")
    
    try:
        # Download historical market data
        data = yf.download(tickers=symbol, period=period, interval=interval)
        
        if data.empty:
            st.error("No data found for symbol. Please check the input and try again.")
            return
        
        data.reset_index(inplace=True)
        
        # Calculate technical indicators
        data["SMA20"] = data["Close"].rolling(window=20).mean()
        data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()
        data["RSI14"] = ta.momentum.rsi(data["Close"], window=14)
        
        # Option to show raw data
        if st.checkbox("Show Raw Data"):
            st.write(data.tail(20))
        
        # Candlestick chart with SMA and EMA overlays
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data['Datetime'], open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="Candlestick"
        ))
        
        fig.add_trace(go.Scatter(
            x=data['Datetime'], y=data["SMA20"], mode="lines",
            name="SMA 20", line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=data['Datetime'], y=data["EMA20"], mode="lines",
            name="EMA 20", line=dict(color='orange')
        ))
        
        fig.update_layout(
            title=f"{symbol.upper()} Price Chart with SMA and EMA",
            xaxis_title="Date",
            yaxis_title="Price USD",
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # RSI Plot
        st.subheader("RSI (14)")
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=data['Datetime'], y=data['RSI14'], mode='lines', name='RSI14'))
        rsi_fig.update_layout(yaxis=dict(range=[0,100]))
        st.plotly_chart(rsi_fig, use_container_width=True)
        
        # Display latest metrics
        last_close = data['Close'].iloc[-1]
        change = last_close - data['Close'].iloc[-2] if len(data) > 1 else 0
        pct_change = (change / data['Close'].iloc[-2] * 100) if len(data) > 1 else 0
        
        st.metric(label="Last Close Price (USD)", value=f"${last_close:.2f}",
                  delta=f"{pct_change:.2f}%")
    
    except Exception as e:
        st.error(f"Error fetching or processing data: {e}")

if __name__ == "__main__":
    main()
