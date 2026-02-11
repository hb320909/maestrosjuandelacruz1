import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time
import numpy as np

st.set_page_config(page_title="Stock Financial Dashboard", page_icon="📈", layout="wide")

# Title and description
st.title("📈 Stock Financial Data Dashboard")
st.markdown("Track stock prices and key financial information from Binance")

# Sidebar for input
st.sidebar.header("Settings")

# Stock symbol input
symbol = st.sidebar.text_input(
    "Enter Stock Symbol", 
    value="BTCUSDT",
    help="Enter a trading pair symbol (e.g., BTCUSDT, ETHUSDT, BNBUSDT)"
).upper()

# Multiple stock comparison
st.sidebar.subheader("Stock Comparison")
enable_comparison = st.sidebar.checkbox("Enable Multiple Stock Comparison", value=False)
comparison_symbols = []
if enable_comparison:
    comparison_input = st.sidebar.text_input(
        "Compare With (comma-separated)",
        value="ETHUSDT,BNBUSDT",
        help="Enter additional symbols separated by commas"
    )
    comparison_symbols = [s.strip().upper() for s in comparison_input.split(',') if s.strip()]

# Time interval selection
interval_options = {
    "1 minute": "1m",
    "5 minutes": "5m",
    "15 minutes": "15m",
    "1 hour": "1h",
    "4 hours": "4h",
    "1 day": "1d",
    "1 week": "1w"
}
interval_label = st.sidebar.selectbox("Time Interval", list(interval_options.keys()), index=5)
interval = interval_options[interval_label]

# Time range selection
st.sidebar.subheader("Time Range")
time_range_mode = st.sidebar.radio(
    "Select Mode",
    ["Preset Range", "Custom Points"],
    index=0
)

if time_range_mode == "Preset Range":
    # Calculate data points based on time range and interval
    def calculate_limit(range_option, interval_str):
        """Calculate number of data points needed for a time range"""
        interval_minutes = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
            "1w": 10080
        }
        
        range_minutes = {
            "1D": 1440,
            "1W": 10080,
            "1M": 43200,
            "3M": 129600,
            "1Y": 525600,
            "All": 1000000
        }
        
        minutes = range_minutes.get(range_option, 1440)
        interval_min = interval_minutes.get(interval_str, 60)
        points = int(minutes / interval_min)
        points = min(points, 1000)
        return max(points, 1)
    
    range_option = st.sidebar.selectbox(
        "Select Time Range",
        ["1D", "1W", "1M", "3M", "1Y", "All"],
        index=2
    )
    limit = calculate_limit(range_option, interval)
    st.sidebar.info(f"📊 Fetching {limit} data points")
else:
    # Number of data points
    limit = st.sidebar.slider("Number of Data Points", min_value=10, max_value=1000, value=100, step=10)

# Function to fetch data from Binance
@st.cache_data(ttl=60)
def fetch_binance_data(symbol, interval, limit):
    """Fetch kline/candlestick data from Binance API"""
    base_url = "https://api.binance.com/api/v3/klines"
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        # Convert string values to float
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
        for col in numeric_columns:
            df[col] = df[col].astype(float)
        
        df['trades'] = df['trades'].astype(int)
        
        return df, None
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {str(e)}"
    except Exception as e:
        return None, f"Error processing data: {str(e)}"

# Function to fetch current price
@st.cache_data(ttl=5)
def fetch_current_price(symbol):
    """Fetch current price from Binance API"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data, None
    except Exception as e:
        return None, f"Error fetching current price: {str(e)}"

# Technical indicator calculation functions
def calculate_sma(data, period):
    """Calculate Simple Moving Average"""
    return data.rolling(window=period).mean()

def calculate_ema(data, period):
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()

def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Handle edge cases to avoid division by zero and NaN values
    # When both gain and loss are zero (sideways market), RSI should be 50
    both_zero = (gain == 0) & (loss == 0)
    
    # Calculate RS and RSI with proper edge case handling
    rs = np.where(loss == 0, np.inf, gain / loss)
    rsi = 100 - (100 / (1 + rs))
    
    # Apply edge case corrections
    rsi = np.where(both_zero, 50, rsi)  # Sideways market
    rsi = np.where((loss == 0) & ~both_zero, 100, rsi)  # Only gains
    rsi = np.where((gain == 0) & ~both_zero, 0, rsi)  # Only losses
    
    return pd.Series(rsi, index=data.index)

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# Chart Type Selection
st.sidebar.subheader("Chart Settings")
chart_type = st.sidebar.radio("Chart Type", ["Candlestick", "Line"], index=0)

# Technical Indicators
st.sidebar.subheader("Technical Indicators")
show_sma = st.sidebar.checkbox("Show SMA (Simple Moving Average)", value=False)
if show_sma:
    sma_period = st.sidebar.slider("SMA Period", min_value=5, max_value=200, value=20, step=5)

show_ema = st.sidebar.checkbox("Show EMA (Exponential Moving Average)", value=False)
if show_ema:
    ema_period = st.sidebar.slider("EMA Period", min_value=5, max_value=200, value=20, step=5)

show_rsi = st.sidebar.checkbox("Show RSI (Relative Strength Index)", value=False)
if show_rsi:
    rsi_period = st.sidebar.slider("RSI Period", min_value=5, max_value=30, value=14, step=1)

show_macd = st.sidebar.checkbox("Show MACD", value=False)

# Fetch button
if st.sidebar.button("🔄 Refresh Data", type="primary"):
    st.cache_data.clear()

# Main content
all_symbols = [symbol] + comparison_symbols if enable_comparison else [symbol]

# Fetch data for all symbols
symbol_data = {}
symbol_errors = {}

with st.spinner(f"Fetching data for {', '.join(all_symbols)}..."):
    for sym in all_symbols:
        df, error = fetch_binance_data(sym, interval, limit)
        ticker_data, ticker_error = fetch_current_price(sym)
        
        if error or ticker_error:
            symbol_errors[sym] = error or ticker_error
        else:
            symbol_data[sym] = {'df': df, 'ticker': ticker_data}

# Check if primary symbol loaded successfully
if symbol not in symbol_data:
    st.error(symbol_errors.get(symbol, "Error loading primary symbol"))
    st.info("💡 Make sure you're using a valid trading pair symbol from Binance (e.g., BTCUSDT, ETHUSDT, BNBUSDT)")
else:
    # Display errors for comparison symbols if any
    if symbol_errors:
        for sym, err in symbol_errors.items():
            if sym != symbol:
                st.warning(f"Could not load {sym}: {err}")
    
    # Get primary symbol data
    df = symbol_data[symbol]['df']
    ticker_data = symbol_data[symbol]['ticker']
    # Display current price information
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_price = float(ticker_data['lastPrice'])
        st.metric("Current Price", f"${current_price:,.2f}")
    
    with col2:
        price_change = float(ticker_data['priceChange'])
        price_change_pct = float(ticker_data['priceChangePercent'])
        st.metric("24h Change", f"${price_change:,.2f}", f"{price_change_pct:.2f}%")
    
    with col3:
        high_24h = float(ticker_data['highPrice'])
        st.metric("24h High", f"${high_24h:,.2f}")
    
    with col4:
        low_24h = float(ticker_data['lowPrice'])
        st.metric("24h Low", f"${low_24h:,.2f}")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📊 Price Chart", "📋 Data Table"])
    
    with tab1:
        if enable_comparison and len(symbol_data) > 1:
            st.subheader("Stock Price Comparison (Normalized)")
            st.info("📊 Prices are normalized to 100% at the start for easy comparison")
            
            # Create comparison chart with normalized prices
            fig = go.Figure()
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            for idx, (sym, data) in enumerate(symbol_data.items()):
                sym_df = data['df']
                # Normalize to percentage change from first close price
                first_close = sym_df['close'].iloc[0]
                normalized_close = (sym_df['close'] / first_close) * 100
                
                fig.add_trace(go.Scatter(
                    x=sym_df['timestamp'],
                    y=normalized_close,
                    name=sym,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    mode='lines'
                ))
            
            fig.update_layout(
                title="Normalized Price Comparison",
                xaxis_title="Date/Time",
                yaxis_title="Normalized Price (Base = 100)",
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                height=600,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f"{symbol} Price Chart")
            
            # Create interactive Plotly chart
            fig = go.Figure()
            
            # Add price trace based on chart type selection
            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ))
            else:  # Line chart
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['close'],
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2),
                    mode='lines'
                ))
            
            # Add technical indicators to the chart
            if show_sma:
                sma_values = calculate_sma(df['close'], sma_period)
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=sma_values,
                    name=f'SMA({sma_period})',
                    line=dict(color='blue', width=2)
                ))
            
            if show_ema:
                ema_values = calculate_ema(df['close'], ema_period)
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=ema_values,
                    name=f'EMA({ema_period})',
                    line=dict(color='orange', width=2)
                ))
            
            # Update layout
            fig.update_layout(
                title=f"{symbol} Price Movement ({interval_label})",
                xaxis_title="Date/Time",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                height=600,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # RSI Chart (separate subplot)
        if show_rsi:
            st.subheader("Relative Strength Index (RSI)")
            rsi_values = calculate_rsi(df['close'], rsi_period)
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df['timestamp'],
                y=rsi_values,
                name='RSI',
                line=dict(color='purple', width=2)
            ))
            
            # Add overbought/oversold lines
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
            
            fig_rsi.update_layout(
                title=f"RSI({rsi_period})",
                xaxis_title="Date/Time",
                yaxis_title="RSI Value",
                height=300,
                template="plotly_white",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        # MACD Chart (separate subplot)
        if show_macd:
            st.subheader("MACD (Moving Average Convergence Divergence)")
            macd_line, signal_line, histogram = calculate_macd(df['close'])
            
            fig_macd = go.Figure()
            
            # MACD Line
            fig_macd.add_trace(go.Scatter(
                x=df['timestamp'],
                y=macd_line,
                name='MACD',
                line=dict(color='blue', width=2)
            ))
            
            # Signal Line
            fig_macd.add_trace(go.Scatter(
                x=df['timestamp'],
                y=signal_line,
                name='Signal',
                line=dict(color='red', width=2)
            ))
            
            # Histogram
            colors = ['green' if val >= 0 else 'red' for val in histogram]
            fig_macd.add_trace(go.Bar(
                x=df['timestamp'],
                y=histogram,
                name='Histogram',
                marker_color=colors,
                opacity=0.5
            ))
            
            fig_macd.update_layout(
                title="MACD",
                xaxis_title="Date/Time",
                yaxis_title="MACD Value",
                height=300,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_macd, use_container_width=True)
        
        # Volume chart
        st.subheader("Trading Volume")
        fig_volume = go.Figure()
        
        fig_volume.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        fig_volume.update_layout(
            title=f"{symbol} Trading Volume",
            xaxis_title="Date/Time",
            yaxis_title="Volume",
            height=300,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with tab2:
        st.subheader(f"{symbol} Financial Data")
        
        # Prepare display dataframe
        display_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']].copy()
        display_df.columns = ['Date/Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades']
        
        # Calculate additional metrics
        display_df['Change'] = display_df['Close'] - display_df['Open']
        display_df['Change %'] = ((display_df['Close'] - display_df['Open']) / display_df['Open'] * 100).round(2)
        
        # Format numeric columns
        display_df['Open'] = display_df['Open'].apply(lambda x: f"${x:,.4f}")
        display_df['High'] = display_df['High'].apply(lambda x: f"${x:,.4f}")
        display_df['Low'] = display_df['Low'].apply(lambda x: f"${x:,.4f}")
        display_df['Close'] = display_df['Close'].apply(lambda x: f"${x:,.4f}")
        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.2f}")
        display_df['Change'] = display_df['Change'].apply(lambda x: f"${x:,.4f}")
        
        # Display table
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_price = df['close'].mean()
            st.metric("Average Price", f"${avg_price:,.2f}")
            
        with col2:
            total_volume = df['volume'].sum()
            st.metric("Total Volume", f"{total_volume:,.2f}")
            
        with col3:
            total_trades = df['trades'].sum()
            st.metric("Total Trades", f"{total_trades:,}")
        
        # CSV Download
        st.subheader("Download Data")
        
        # Prepare CSV data (with raw numeric values)
        csv_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']].copy()
        csv_df['change'] = csv_df['close'] - csv_df['open']
        csv_df['change_percent'] = ((csv_df['close'] - csv_df['open']) / csv_df['open'] * 100)
        
        csv_data = csv_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
        
        st.info(f"💾 Downloaded data includes {len(csv_df)} rows with columns: timestamp, open, high, low, close, volume, trades, change, and change_percent")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.info(
    "This dashboard fetches real-time financial data from Binance API. "
    "Enter a valid trading pair symbol (e.g., BTCUSDT for Bitcoin/USD, ETHUSDT for Ethereum/USD) to view price charts and download data."
)

# Additional market info
st.sidebar.markdown("**Popular Symbols**")
st.sidebar.markdown("""
- BTCUSDT (Bitcoin)
- ETHUSDT (Ethereum)
- BNBUSDT (Binance Coin)
- SOLUSDT (Solana)
- ADAUSDT (Cardano)
- XRPUSDT (Ripple)
""")

