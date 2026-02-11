# Overview

This is a Stock Financial Data Dashboard built with Streamlit that provides real-time tracking and visualization of cryptocurrency trading pairs from the Binance exchange. The application fetches candlestick data (OHLC - Open, High, Low, Close) and displays financial metrics through an interactive web interface. 

## Key Features (Updated: October 2025)
- **Flexible Time Ranges**: Preset time ranges (1D, 1W, 1M, 3M, 1Y, All) or custom data point selection
- **Technical Indicators**: SMA, EMA, RSI, and MACD with configurable periods and visual overlays
- **Multiple Chart Types**: Toggle between candlestick and line chart views
- **Stock Comparison**: Compare multiple trading pairs with normalized price overlay
- **Data Export**: Download financial data as CSV with comprehensive metrics
- **Real-time Updates**: Manual refresh with 60-second cache TTL for performance

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Technology Stack**: Streamlit web framework
- **Rationale**: Streamlit was chosen for rapid prototyping of data-driven dashboards with minimal frontend code. It provides native Python integration and automatic UI generation from Python code.
- **Pros**: Fast development, Python-native, built-in widgets and charts
- **Cons**: Limited customization compared to traditional web frameworks, may not scale well for complex UI interactions

**Visualization Library**: Plotly
- **Rationale**: Plotly Graph Objects are used for interactive financial charts (candlestick charts, line charts)
- **Pros**: Interactive charts out-of-the-box, excellent for financial data visualization
- **Cons**: Heavier than static plotting libraries

**Layout Design**: Wide layout configuration with sidebar controls
- Settings and user inputs are placed in a sidebar
- Main content area displays charts and financial metrics
- Page configuration includes custom title and icon for branding

## Backend Architecture

**Data Processing**: Pandas DataFrame
- **Rationale**: Financial time-series data is processed using pandas for easy manipulation and analysis
- **Pros**: Industry standard for data analysis, rich functionality for time-series operations
- **Cons**: Memory-intensive for very large datasets

**API Integration Pattern**: Direct REST API calls
- Uses Python `requests` library for HTTP communication
- **Rationale**: Simple synchronous API calls sufficient for real-time data fetching without complex orchestration
- **Alternative Considered**: WebSocket connections for streaming data were not implemented, likely to keep the architecture simple
- **Pros**: Simple implementation, reliable
- **Cons**: Requires periodic polling rather than push-based updates

**Caching Strategy**: Streamlit's @st.cache_data decorator with 60-second TTL
- **Rationale**: Reduces redundant API calls to Binance and improves application performance
- **Requirement Addressed**: Prevent rate limiting from Binance API and improve user experience
- **Pros**: Automatic cache invalidation, reduces API load
- **Cons**: Data may be stale for up to 60 seconds

## Data Storage

**Storage Approach**: In-memory only (no persistent database)
- **Rationale**: Application fetches fresh data on-demand from Binance API
- **Requirement Addressed**: Real-time dashboard doesn't require historical data persistence
- **Pros**: Simpler architecture, no database maintenance
- **Cons**: No historical data analysis beyond API limits, no offline access

## Configuration Management

**User Inputs**:
- Trading pair symbol (default: BTCUSDT) with multi-symbol comparison support
- Time interval selection (1m, 5m, 15m, 1h, 4h, 1d, 1w)
- Time range mode: Preset ranges (1D-All) or custom data points (10-1000)
- Chart type selection: Candlestick or Line
- Technical indicators: SMA (5-200), EMA (5-200), RSI (5-30), MACD (enabled/disabled)

**Input Validation**: String normalization using `.upper()` for symbol consistency

# External Dependencies

## Third-Party APIs

**Binance Public API**
- Endpoint: `https://api.binance.com/api/v3/klines`
- Purpose: Fetch candlestick/kline data for cryptocurrency trading pairs
- Authentication: None (public endpoint)
- Rate Limits: Mitigated through caching strategy
- Data Format: JSON array of candlestick data [timestamp, open, high, low, close, volume, ...]

## Python Libraries

**Core Dependencies**:
- `streamlit` - Web application framework
- `pandas` - Data manipulation and analysis
- `plotly` - Interactive data visualization
- `requests` - HTTP library for API calls
- `datetime` - Time-based data handling

**Standard Library**:
- `time` - Used for time-based operations
- `numpy` - Used for technical indicator calculations (RSI edge case handling)

## External Services

**Binance Exchange**
- Public market data provider
- No authentication required for public endpoints
- Provides real-time and historical cryptocurrency market data
- Service availability directly impacts application functionality
- **Known Limitation**: Binance API returns 451 errors in some regions due to regulatory restrictions. Users in affected regions may need to use a VPN or alternative data source.

# Recent Changes

## October 2025 - Advanced Features Update

### Time Range Filters
- Added preset time range options (1D, 1W, 1M, 3M, 1Y, All)
- Implemented dynamic calculation of data points based on interval and range
- Fixed issue where minimum data points were artificially enforced

### Technical Indicators
- **SMA/EMA**: Configurable moving averages with period selection (5-200)
- **RSI**: Relative Strength Index with proper edge case handling:
  - Sideways market (no gains/losses) returns RSI = 50
  - Pure upward movement returns RSI = 100
  - Pure downward movement returns RSI = 0
- **MACD**: Moving Average Convergence Divergence with line, signal, and histogram visualization

### Chart Enhancements
- Added chart type toggle between Candlestick and Line views
- Implemented multiple stock comparison with normalized price overlay (base = 100)
- Technical indicators overlay on main chart (SMA/EMA)
- Separate chart panels for RSI and MACD below main chart

### Auto-Refresh Feature
- **Note**: Auto-refresh feature was explored but removed due to Streamlit architecture limitations
- Streamlit's execution model doesn't support background timers without continuous rerun loops
- Manual refresh button provides equivalent functionality
- 60-second cache TTL provides automatic data freshness on user interaction