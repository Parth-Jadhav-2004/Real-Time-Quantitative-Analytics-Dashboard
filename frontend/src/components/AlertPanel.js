import React, { useState } from 'react';

const AlertPanel = ({ currentZScore, onCreateAlert, alerts }) => {
  const [threshold, setThreshold] = useState(2.0);
  const [condition, setCondition] = useState('above');

  const handleCreateAlert = () => {
    const alertConfig = {
      type: 'zscore',
      condition,
      threshold,
      timestamp: new Date().toISOString()
    };
    onCreateAlert(alertConfig);
  };

  const checkAlert = (alert) => {
    if (!currentZScore) return false;
    
    if (alert.config.condition === 'above') {
      return currentZScore > alert.config.threshold;
    } else if (alert.config.condition === 'below') {
      return currentZScore < -alert.config.threshold;
    }
    return false;
  };

  return (
    <div className="alert-panel">
      <h2>🔔 Alerts</h2>
      
      <div className="alert-form">
        <div className="control-group">
          <label>Condition</label>
          <select value={condition} onChange={(e) => setCondition(e.target.value)}>
            <option value="above">Z-Score Above</option>
            <option value="below">Z-Score Below</option>
          </select>
        </div>

        <div className="control-group">
          <label>Threshold</label>
          <input 
            type="number" 
            step="0.1"
            value={threshold} 
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
          />
        </div>

        <button onClick={handleCreateAlert}>
          ➕ Create Alert
        </button>
      </div>

      <div>
        <h3>Active Alerts ({alerts.length})</h3>
        {alerts.length === 0 ? (
          <div style={{ color: '#64748b', padding: '20px', textAlign: 'center' }}>
            No alerts configured
          </div>
        ) : (
          alerts.map(alert => {
            const isTriggered = checkAlert(alert);
            return (
              <div 
                key={alert.id} 
                className={`alert-item ${isTriggered ? 'alert-triggered' : ''}`}
              >
                <div>
                  <strong>
                    Z-Score {alert.config.condition === 'above' ? '>' : '<'} {alert.config.threshold}
                  </strong>
                  {isTriggered && <span style={{ marginLeft: '10px', color: '#ef4444' }}>🔴 TRIGGERED</span>}
                </div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Created: {new Date(alert.created_at).toLocaleString()}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default AlertPanel;
