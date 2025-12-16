"""Configuration settings for the application"""

# Database settings
DATABASE_PATH = "market_data.db"

# WebSocket settings
BINANCE_WS_BASE = "wss://fstream.binance.com/ws"

# Default symbols
DEFAULT_SYMBOLS = ["btcusdt", "ethusdt"]

# Resampling timeframes (in seconds)
TIMEFRAMES = {
    "1s": 1,
    "1m": 60,
    "5m": 300
}

# Analytics settings
DEFAULT_ROLLING_WINDOW = 20
DEFAULT_Z_SCORE_THRESHOLD = 2.0

# Server settings
HOST = "127.0.0.1"
PORT = 8001
