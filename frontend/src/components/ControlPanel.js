import React from 'react';

const ControlPanel = ({
  symbols,
  selectedSymbol1,
  selectedSymbol2,
  timeframe,
  window: rollingWindow,
  onSymbol1Change,
  onSymbol2Change,
  onTimeframeChange,
  onWindowChange,
  onExport
}) => {
  return (
    <div className="control-panel">
      <h2>⚙️ Controls</h2>
      
      <div className="controls-row">
        <div className="control-group">
          <label>Symbol 1</label>
          <select value={selectedSymbol1} onChange={(e) => onSymbol1Change(e.target.value)}>
            {symbols.map(symbol => (
              <option key={symbol} value={symbol}>{symbol}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Symbol 2</label>
          <select value={selectedSymbol2} onChange={(e) => onSymbol2Change(e.target.value)}>
            {symbols.map(symbol => (
              <option key={symbol} value={symbol}>{symbol}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Timeframe</label>
          <select value={timeframe} onChange={(e) => onTimeframeChange(e.target.value)}>
            <option value="1s">1 Second</option>
            <option value="1m">1 Minute</option>
            <option value="5m">5 Minutes</option>
          </select>
        </div>

        <div className="control-group">
          <label>Rolling Window</label>
          <input 
            type="number" 
            value={rollingWindow} 
            onChange={(e) => onWindowChange(parseInt(e.target.value))}
            min="5"
            max="100"
          />
        </div>
      </div>

      <div className="button-group">
        <button onClick={() => onExport(selectedSymbol1)}>
          📥 Export {selectedSymbol1}
        </button>
        <button onClick={() => onExport(selectedSymbol2)}>
          📥 Export {selectedSymbol2}
        </button>
        <button className="secondary" onClick={() => window.location.reload()}>
          🔄 Refresh
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
