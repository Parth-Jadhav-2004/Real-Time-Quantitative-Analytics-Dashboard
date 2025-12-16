"""WebSocket data ingestion service for Binance market data"""
import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, List, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataIngestion:
    """Handles real-time market data ingestion from Binance WebSocket"""
    
    def __init__(self, symbols: List[str], on_tick_callback: Callable):
        self.symbols = [s.lower() for s in symbols]
        self.on_tick_callback = on_tick_callback
        self.websockets = {}
        self.running = False
        
    async def connect_symbol(self, symbol: str):
        """Connect to WebSocket for a single symbol"""
        url = f"wss://fstream.binance.com/ws/{symbol}@trade"
        
        while self.running:
            try:
                async with websockets.connect(url) as ws:
                    logger.info(f"Connected to {symbol}")
                    self.websockets[symbol] = ws
                    
                    async for message in ws:
                        if not self.running:
                            break
                            
                        data = json.loads(message)
                        if data.get('e') == 'trade':
                            tick = self._normalize_tick(data)
                            await self.on_tick_callback(tick)
                            logger.debug(f"Received tick: {symbol} @ {tick['price']}")
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection closed for {symbol}, reconnecting...")
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in {symbol} stream: {e}")
                await asyncio.sleep(2)
                
    def _normalize_tick(self, data: Dict) -> Dict:
        """Normalize Binance tick data to standard format"""
        return {
            'symbol': data['s'],
            'timestamp': datetime.fromtimestamp(data['T'] / 1000),
            'price': float(data['p']),
            'quantity': float(data['q'])
        }
        
    async def start(self):
        """Start ingesting data for all symbols"""
        self.running = True
        logger.info(f"Starting ingestion for symbols: {self.symbols}")
        
        tasks = [self.connect_symbol(symbol) for symbol in self.symbols]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def stop(self):
        """Stop all WebSocket connections"""
        self.running = False
        for ws in self.websockets.values():
            await ws.close()
        logger.info("Stopped all WebSocket connections")
