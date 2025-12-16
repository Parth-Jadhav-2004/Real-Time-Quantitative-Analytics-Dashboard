"""Main FastAPI application with REST and WebSocket endpoints"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict
import io

from config import DEFAULT_SYMBOLS, TIMEFRAMES, DEFAULT_ROLLING_WINDOW
from data_ingestion import MarketDataIngestion
from data_storage import DataStorage
from analytics import QuantAnalytics, PairAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Real-Time Quantitative Analytics Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_storage = DataStorage("market_data.db")
analytics_engine = QuantAnalytics()
pair_analysis = PairAnalysis(analytics_engine)
market_ingestion = None
connected_clients = set()
alerts = []


async def on_tick_received(tick: Dict):
    """Callback when new tick is received"""
    await data_storage.add_tick(tick)
    
    # Broadcast to connected clients
    message = {
        'type': 'tick',
        'data': {
            'symbol': tick['symbol'],
            'price': tick['price'],
            'quantity': tick['quantity'],
            'timestamp': tick['timestamp'].isoformat()
        }
    }
    await broadcast_to_clients(message)


async def broadcast_to_clients(message: Dict):
    """Broadcast message to all connected WebSocket clients"""
    if connected_clients:
        await asyncio.gather(
            *[client.send_json(message) for client in connected_clients],
            return_exceptions=True
        )


@app.on_event("startup")
async def startup_event():
    """Start market data ingestion on startup"""
    global market_ingestion
    
    market_ingestion = MarketDataIngestion(DEFAULT_SYMBOLS, on_tick_received)
    
    # Start ingestion in background
    asyncio.create_task(market_ingestion.start())
    
    # Start resampling task
    asyncio.create_task(resampling_loop())
    
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if market_ingestion:
        await market_ingestion.stop()
    logger.info("Application shutdown")


async def resampling_loop():
    """Periodically resample tick data to OHLCV"""
    while True:
        try:
            await asyncio.sleep(1)  # Run every second
            
            symbols = data_storage.get_all_symbols()
            
            for symbol in symbols:
                for timeframe, seconds in TIMEFRAMES.items():
                    await data_storage.resample_to_ohlcv(symbol, timeframe, seconds)
                    
        except Exception as e:
            logger.error(f"Resampling error: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "message": "Real-Time Quantitative Analytics Dashboard"}


@app.get("/api/symbols")
async def get_symbols():
    """Get list of available symbols"""
    return {"symbols": data_storage.get_all_symbols()}


@app.get("/api/ohlcv/{symbol}/{timeframe}")
async def get_ohlcv(symbol: str, timeframe: str, limit: int = 1000):
    """Get OHLCV data for a symbol and timeframe"""
    if timeframe not in TIMEFRAMES:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
        
    df = data_storage.get_ohlcv(symbol, timeframe, limit)
    
    if df.empty:
        return {"data": []}
        
    # Convert to list of dicts, filtering out rows with NaN values
    data = []
    for timestamp, row in df.iterrows():
        # Skip rows with any NaN values
        if row.isna().any():
            continue
        data.append({
            'timestamp': timestamp.isoformat(),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row['volume'])
        })
    
    # HARD GUARD: Ensure at least 2 data points for valid time series
    if len(data) < 2:
        return {"data": []}
        
    return {"data": data}


@app.get("/api/analyze/{symbol1}/{symbol2}")
async def analyze_pair(
    symbol1: str, 
    symbol2: str, 
    timeframe: str = "1m", 
    window: int = DEFAULT_ROLLING_WINDOW
):
    """Analyze a pair of symbols"""
    if timeframe not in TIMEFRAMES:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
        
    # Get OHLCV data
    df1 = data_storage.get_ohlcv(symbol1, timeframe)
    df2 = data_storage.get_ohlcv(symbol2, timeframe)
    
    logger.info(f"Analyze: {symbol1} has {len(df1)} rows, {symbol2} has {len(df2)} rows")
    
    if df1.empty or df2.empty:
        raise HTTPException(status_code=404, detail="Insufficient data for analysis")
        
    # Extract close prices
    prices1 = df1['close']
    prices2 = df2['close']
    
    # Perform analysis
    result = pair_analysis.analyze_pair(symbol1, symbol2, prices1, prices2, window)
    
    logger.info(f"Analysis result keys: {result.keys()}")
    if 'error' in result:
        logger.warning(f"Analysis returned error: {result['error']}")
    else:
        logger.info(f"Analysis successful: hedge_ratio={result.get('hedge_ratio')}, zscore={result.get('current_zscore')}")
    
    return result


@app.get("/api/stats/{symbol}")
async def get_symbol_stats(symbol: str, timeframe: str = "1m"):
    """Get basic statistics for a symbol"""
    if timeframe not in TIMEFRAMES:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
        
    df = data_storage.get_ohlcv(symbol, timeframe)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available")
        
    stats = analytics_engine.compute_basic_stats(df['close'])
    return stats


@app.post("/api/alerts")
async def create_alert(alert_config: Dict):
    """Create a new alert"""
    alert = {
        'id': len(alerts) + 1,
        'config': alert_config,
        'created_at': datetime.now().isoformat(),
        'triggered': False
    }
    alerts.append(alert)
    return alert


@app.get("/api/alerts")
async def get_alerts():
    """Get all alerts"""
    return {"alerts": alerts}


@app.get("/api/export/{symbol}/{timeframe}")
async def export_data(symbol: str, timeframe: str):
    """Export OHLCV data as CSV"""
    if timeframe not in TIMEFRAMES:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
        
    df = data_storage.get_ohlcv(symbol, timeframe)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available")
        
    # Convert to CSV
    output = io.StringIO()
    df.to_csv(output)
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={symbol}_{timeframe}.csv"}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Echo or handle client requests if needed
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connected_clients.discard(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
