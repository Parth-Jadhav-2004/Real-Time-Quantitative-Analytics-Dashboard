import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import PriceChart from './components/PriceChart';
import SpreadChart from './components/SpreadChart';
import StatsPanel from './components/StatsPanel';
import ControlPanel from './components/ControlPanel';
import AlertPanel from './components/AlertPanel';

const API_BASE = 'http://127.0.0.1:8001';

function App() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol1, setSelectedSymbol1] = useState('BTCUSDT');
  const [selectedSymbol2, setSelectedSymbol2] = useState('ETHUSDT');
  const [timeframe, setTimeframe] = useState('1m');
  const [window, setWindow] = useState(20);
  const [pairAnalysis, setPairAnalysis] = useState(null);
  const [priceData1, setPriceData1] = useState([]);
  const [priceData2, setPriceData2] = useState([]);
  const [ws, setWs] = useState(null);
  const [livePrices, setLivePrices] = useState({});
  const [alerts, setAlerts] = useState([]);

  // Fetch available symbols
  useEffect(() => {
    fetchSymbols();
  }, []);

  // Connect to WebSocket
  useEffect(() => {
    const websocket = new WebSocket('ws://127.0.0.1:8001/ws');
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'tick') {
        console.log('Tick received:', message.data);
        const symbol = message.data.symbol.toLowerCase();
        setLivePrices(prev => ({
          ...prev,
          [symbol]: message.data.price
        }));
      }
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, []);

  // Fetch data periodically
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [selectedSymbol1, selectedSymbol2, timeframe, window]);

  const fetchSymbols = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/symbols`);
      setSymbols(response.data.symbols);
    } catch (error) {
      console.error('Error fetching symbols:', error);
    }
  };

  const fetchData = useCallback(async () => {
    try {
      // Fetch OHLCV data for both symbols
      const [data1Response, data2Response, analysisResponse] = await Promise.all([
        axios.get(`${API_BASE}/api/ohlcv/${selectedSymbol1}/${timeframe}`),
        axios.get(`${API_BASE}/api/ohlcv/${selectedSymbol2}/${timeframe}`),
        axios.get(`${API_BASE}/api/analyze/${selectedSymbol1}/${selectedSymbol2}`, {
          params: { timeframe, window }
        })
      ]);

      setPriceData1(data1Response.data.data);
      setPriceData2(data2Response.data.data);
      
      // Only set analysis if it doesn't have an error
      if (analysisResponse.data && !analysisResponse.data.error) {
        setPairAnalysis(analysisResponse.data);
      } else {
        console.log('Waiting for sufficient data...', analysisResponse.data);
        setPairAnalysis(null);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, [selectedSymbol1, selectedSymbol2, timeframe, window]);

  const handleExport = async (symbol) => {
    try {
      const response = await axios.get(
        `${API_BASE}/api/export/${symbol}/${timeframe}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${symbol}_${timeframe}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  const handleCreateAlert = async (alertConfig) => {
    try {
      const response = await axios.post(`${API_BASE}/api/alerts`, alertConfig);
      setAlerts([...alerts, response.data]);
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  // Get latest price from live prices or from OHLCV data
  const getDisplayPrice = (symbol, priceData) => {
    const symbolLower = symbol.toLowerCase();
    if (livePrices[symbolLower]) {
      return livePrices[symbolLower];
    }
    if (priceData && priceData.length > 0) {
      return priceData[priceData.length - 1].close;
    }
    return null;
  };

  const price1 = getDisplayPrice(selectedSymbol1, priceData1);
  const price2 = getDisplayPrice(selectedSymbol2, priceData2);

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Real-Time Quantitative Analytics Dashboard</h1>
        <div className="live-indicators">
          {price1 && (
            <div className="live-indicator">
              🟢 {selectedSymbol1}: ${Number(price1).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          )}
          {price2 && (
            <div className="live-indicator">
              🟢 {selectedSymbol2}: ${Number(price2).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          )}
        </div>
      </header>

      <div className="dashboard-container">
        <ControlPanel
          symbols={symbols}
          selectedSymbol1={selectedSymbol1}
          selectedSymbol2={selectedSymbol2}
          timeframe={timeframe}
          window={window}
          onSymbol1Change={setSelectedSymbol1}
          onSymbol2Change={setSelectedSymbol2}
          onTimeframeChange={setTimeframe}
          onWindowChange={setWindow}
          onExport={handleExport}
        />

        <div className="charts-grid">
          <div className="chart-container">
            <h3>{selectedSymbol1} Price Chart</h3>
            <PriceChart data={priceData1} symbol={selectedSymbol1} />
          </div>

          <div className="chart-container">
            <h3>{selectedSymbol2} Price Chart</h3>
            <PriceChart data={priceData2} symbol={selectedSymbol2} />
          </div>

          {pairAnalysis && pairAnalysis.series && (
            <>
              <div className="chart-container full-width">
                <h3>Spread & Z-Score</h3>
                <SpreadChart 
                  spreadData={pairAnalysis.series.spread}
                  zscoreData={pairAnalysis.series.zscore}
                />
              </div>

              <div className="chart-container full-width">
                <h3>Rolling Correlation</h3>
                <SpreadChart 
                  correlationData={pairAnalysis.series.correlation}
                  isCorrelation={true}
                />
              </div>
            </>
          )}
        </div>

        <StatsPanel analysis={pairAnalysis} />

        <AlertPanel
          currentZScore={pairAnalysis?.current_zscore}
          onCreateAlert={handleCreateAlert}
          alerts={alerts}
        />
      </div>
    </div>
  );
}

export default App;
