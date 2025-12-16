# Real-Time Quantitative Analytics Dashboard

A local, real-time analytical application for quantitative traders that ingests live market tick data from Binance, processes and resamples it into configurable timeframes, computes key quantitative trading analytics, and presents insights through an interactive dashboard.

## Architecture Diagram 
<img width="2816" height="1536" alt="Image" src="https://github.com/user-attachments/assets/b9b2fc9e-0c48-43ad-aece-6885391573a4" />

## 🎯 Features

### Data Ingestion
- ✅ Live WebSocket connection to Binance Futures market data
- ✅ Support for multiple symbols simultaneously (BTC/USDT, ETH/USDT)
- ✅ High-frequency tick-level data capture

### Data Processing
- ✅ In-memory tick data buffering for low-latency processing
- ✅ SQLite persistence for resampled data
- ✅ OHLCV resampling at multiple timeframes:
  - 1 second
  - 1 minute  
  - 5 minutes

### Quantitative Analytics
- ✅ **Basic Statistics**: Mean, standard deviation, volatility
- ✅ **OLS Hedge Ratio**: Ordinary Least Squares regression between pairs
- ✅ **Spread Calculation**: Price spread using hedge ratio
- ✅ **Rolling Z-Score**: Statistical deviation detection
- ✅ **Rolling Correlation**: Time-series correlation analysis
- ✅ **ADF Test**: Augmented Dickey-Fuller test for stationarity

### Interactive Dashboard
- ✅ Real-time price charts with Recharts
- ✅ Spread and Z-score visualization
- ✅ Correlation plots
- ✅ Configurable controls:
  - Symbol selection
  - Timeframe selection
  - Rolling window adjustment
- ✅ Live data updates via WebSocket

### Additional Features
- ✅ Threshold-based alerts
- ✅ CSV data export
- ✅ Comprehensive statistics panel
- ✅ Responsive modern UI

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Data Processing**: pandas, numpy
- **Statistics**: scipy, statsmodels
- **Database**: SQLite with aiosqlite
- **WebSockets**: websockets library

### Frontend
- **Framework**: React 18
- **Charts**: Recharts (responsive charts)
- **HTTP Client**: axios
- **Build Tool**: Create React App

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Internet connection (for live market data)

## 🚀 Quick Start

### Windows

1. **Navigate to the project directory:**
   ```bash
   cd "e:\GemScamp Assignment\realtime-quant-dashboard"
   ```

2. **Run the startup script:**
   ```bash
   start.bat
   ```

The script will automatically:
- Create Python virtual environment
- Install all dependencies
- Start the backend server
- Start the frontend development server
- Open the dashboard in your browser

### Linux/Mac

1. **Navigate to the project directory:**
   ```bash
   cd "e:/GemScamp Assignment/realtime-quant-dashboard"
   ```

2. **Make the script executable and run:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Manual Setup (Alternative)

#### Backend Setup:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

#### Frontend Setup (in a new terminal):
```bash
cd frontend
npm install
npm start
```

## 📱 Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## 🎮 How to Use

### 1. Dashboard Controls

- **Symbol Selection**: Choose two symbols to analyze (e.g., BTCUSDT, ETHUSDT)
- **Timeframe**: Select data resampling interval (1s, 1m, 5m)
- **Rolling Window**: Adjust the window size for rolling calculations (5-100)

### 2. Viewing Analytics

The dashboard displays:
- **Price Charts**: Real-time OHLC data for both symbols
- **Spread Chart**: Calculated spread with Z-score overlay
- **Correlation Chart**: Rolling correlation between instruments
- **Statistics Panel**: Key metrics including:
  - Hedge ratio (β)
  - R-squared
  - Current spread and Z-score
  - Volatility metrics
  - ADF test results

### 3. Setting Alerts

1. Navigate to the Alerts section
2. Choose condition (Z-Score Above/Below)
3. Set threshold value
4. Click "Create Alert"
5. Alerts will trigger visually when conditions are met

### 4. Exporting Data

- Click "Export [Symbol]" buttons to download OHLCV data as CSV
- Data includes timestamp, open, high, low, close, and volume

## 📊 Understanding the Analytics

### Hedge Ratio (β)
The OLS regression coefficient that minimizes the spread variance. Formula: `Symbol1 = β × Symbol2 + α`

### Spread
The price difference adjusted by hedge ratio: `Spread = Price1 - β × Price2`

### Z-Score
Standardized measure of how far the spread is from its mean:
```
Z-Score = (Spread - Mean) / StdDev
```
- Z-Score > 2: Spread is extremely high (potential short opportunity)
- Z-Score < -2: Spread is extremely low (potential long opportunity)

### ADF Test
Tests if the spread is stationary (mean-reverting):
- **p-value < 0.05**: Spread is stationary (good for pairs trading)
- **p-value > 0.05**: Spread is non-stationary (not suitable for mean reversion)

## 🏗️ Project Structure

```
realtime-quant-dashboard/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── data_ingestion.py    # WebSocket market data ingestion
│   ├── data_storage.py      # SQLite storage and resampling
│   ├── analytics.py         # Quantitative analytics engine
│   ├── requirements.txt     # Python dependencies
│   └── market_data.db       # SQLite database (created at runtime)
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── PriceChart.js
│   │   │   ├── SpreadChart.js
│   │   │   ├── StatsPanel.js
│   │   │   ├── ControlPanel.js
│   │   │   └── AlertPanel.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
├── start.bat                # Windows startup script
├── start.sh                 # Linux/Mac startup script
└── README.md
```

## 🔧 API Endpoints

### REST API

- `GET /` - Health check
- `GET /api/symbols` - Get available symbols
- `GET /api/ohlcv/{symbol}/{timeframe}` - Get OHLCV data
- `GET /api/analyze/{symbol1}/{symbol2}` - Pair analysis
- `GET /api/stats/{symbol}` - Symbol statistics
- `POST /api/alerts` - Create alert
- `GET /api/alerts` - Get all alerts
- `GET /api/export/{symbol}/{timeframe}` - Export data as CSV

### WebSocket

- `WS /ws` - Real-time tick data stream

## ⚙️ Configuration

Edit [backend/config.py](backend/config.py) to customize:

```python
# Default symbols to track
DEFAULT_SYMBOLS = ["btcusdt", "ethusdt"]

# Resampling timeframes
TIMEFRAMES = {
    "1s": 1,
    "1m": 60,
    "5m": 300
}

# Analytics settings
DEFAULT_ROLLING_WINDOW = 20
DEFAULT_Z_SCORE_THRESHOLD = 2.0
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python --version`
- Check all dependencies are installed: `pip list`
- Look for error messages in the backend terminal

### Frontend won't start
- Ensure Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check for port conflicts (default: 3000)

### No data appearing
- Check internet connection
- Verify Binance WebSocket is accessible
- Wait 10-30 seconds for initial data accumulation
- Check browser console for errors

### WebSocket connection fails
- Ensure backend is running on port 8000
- Check firewall settings
- Try refreshing the browser

## 📈 Performance Considerations

- **Memory Usage**: Tick buffer stores up to 10,000 ticks per symbol in memory
- **Database Size**: SQLite stores last 100 OHLCV bars per symbol/timeframe
- **Update Frequency**: 
  - Tick data: Real-time (~milliseconds)
  - Frontend refresh: 2 seconds
  - Resampling: Every 1 second

## ⚠️ Limitations & Disclaimers

- **Educational Purpose Only**: This is a research tool, not a production trading system
- **No Trade Execution**: Does not connect to trading accounts
- **Local Only**: Not designed for cloud deployment
- **Limited History**: Only maintains recent data in memory
- **No Authentication**: Designed for local use only


## 📝 License

This project is for educational purposes. Use at your own risk.

## 🙏 Acknowledgments

- Market data provided by Binance Futures API
- Built with FastAPI, React, and Recharts

---

**Note**: This application connects to live market data. Always verify calculations independently before making any trading decisions.
