"""Data storage and resampling using SQLite and in-memory buffers"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import asyncio
import logging

logger = logging.getLogger(__name__)


class DataStorage:
    """Manages tick data storage and OHLCV resampling"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.tick_buffer = defaultdict(lambda: deque(maxlen=10000))  # In-memory tick buffer
        self.resampled_data = defaultdict(dict)  # {symbol: {timeframe: DataFrame}}
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create resampled OHLCV table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ohlcv (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf_ts 
            ON ohlcv(symbol, timeframe, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
        
    async def add_tick(self, tick: Dict):
        """Add a tick to the in-memory buffer"""
        symbol = tick['symbol']
        self.tick_buffer[symbol].append(tick)
        if len(self.tick_buffer[symbol]) % 100 == 0:
            logger.info(f"Buffer size for {symbol}: {len(self.tick_buffer[symbol])} ticks")
        
    def get_recent_ticks(self, symbol: str, limit: int = 1000) -> List[Dict]:
        """Get recent ticks from buffer"""
        ticks = list(self.tick_buffer[symbol])
        return ticks[-limit:] if len(ticks) > limit else ticks
        
    async def resample_to_ohlcv(self, symbol: str, timeframe: str, seconds: int):
        """Resample tick data to OHLCV for a given timeframe"""
        ticks = self.get_recent_ticks(symbol)
        
        logger.debug(f"Resampling {symbol}: {len(ticks)} ticks available")
        
        if len(ticks) < 2:
            logger.warning(f"Not enough ticks for {symbol}: {len(ticks)}")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(ticks)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Resample to OHLCV - resample the FULL DataFrame, not a Series
        ohlcv = (
            df
            .resample(f'{seconds}s')
            .agg({
                'price': ['first', 'max', 'min', 'last'],
                'quantity': 'sum'
            })
        )
        
        ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Drop rows ONLY if close is missing (not all NaN)
        ohlcv = ohlcv.dropna(subset=['close'])
        
        logger.info(
            f"OHLC {symbol} {timeframe}: "
            f"rows={len(ohlcv)}, "
            f"nulls={ohlcv.isna().sum().to_dict()}"
        )
        
        # Store in memory
        self.resampled_data[symbol][timeframe] = ohlcv
        
        # Persist to database (last N rows)
        await self._persist_ohlcv(symbol, timeframe, ohlcv.tail(100))
        
        return ohlcv
        
    async def _persist_ohlcv(self, symbol: str, timeframe: str, df: pd.DataFrame):
        """Persist OHLCV data to SQLite"""
        if df.empty:
            return
            
        conn = sqlite3.connect(self.db_path)
        
        for timestamp, row in df.iterrows():
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO ohlcv 
                    (symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, timeframe, timestamp.isoformat(),
                    row['open'], row['high'], row['low'], row['close'], row['volume']
                ))
            except Exception as e:
                logger.error(f"Error persisting OHLCV: {e}")
                
        conn.commit()
        conn.close()
        
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
        """Get OHLCV data from memory"""
        if symbol in self.resampled_data and timeframe in self.resampled_data[symbol]:
            df = self.resampled_data[symbol][timeframe]
            return df.tail(limit)
        return pd.DataFrame()
        
    def get_all_symbols(self) -> List[str]:
        """Get list of all symbols with data"""
        return list(self.tick_buffer.keys())
