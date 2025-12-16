import React from 'react';

const StatsPanel = ({ analysis }) => {
  if (!analysis || analysis.error) {
    return (
      <div className="stats-panel">
        <h2>📈 Statistical Analysis</h2>
        <div style={{ padding: '20px', textAlign: 'center', color: '#94a3b8' }}>
          ⏳ Collecting data... Please wait for sufficient data to accumulate (minimum 5 data points required)
        </div>
      </div>
    );
  }

  const { stats, hedge_ratio, r_squared, current_spread, current_zscore, current_correlation, adf_test } = analysis;

  return (
    <div className="stats-panel">
      <h2>📈 Statistical Analysis</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h4>Hedge Ratio (β)</h4>
          <div className="stat-value">{hedge_ratio?.toFixed(4) || 'N/A'}</div>
          <div className="stat-label">OLS Regression Coefficient</div>
        </div>

        <div className="stat-card">
          <h4>R-Squared</h4>
          <div className="stat-value">{r_squared?.toFixed(4) || 'N/A'}</div>
          <div className="stat-label">Goodness of Fit</div>
        </div>

        <div className="stat-card">
          <h4>Current Spread</h4>
          <div className="stat-value">{current_spread?.toFixed(2) || 'N/A'}</div>
          <div className="stat-label">{analysis.symbol1} - β×{analysis.symbol2}</div>
        </div>

        <div className="stat-card">
          <h4>Z-Score</h4>
          <div className="stat-value" style={{ 
            color: Math.abs(current_zscore) > 2 ? '#ef4444' : '#10b981' 
          }}>
            {current_zscore?.toFixed(3) || 'N/A'}
          </div>
          <div className="stat-label">
            {Math.abs(current_zscore) > 2 ? '⚠️ Extreme Value' : '✅ Normal Range'}
          </div>
        </div>

        <div className="stat-card">
          <h4>Correlation</h4>
          <div className="stat-value">{current_correlation?.toFixed(4) || 'N/A'}</div>
          <div className="stat-label">Rolling Correlation</div>
        </div>

        <div className="stat-card">
          <h4>{analysis.symbol1} Price</h4>
          <div className="stat-value">${stats?.[analysis.symbol1]?.last?.toFixed(2) || 'N/A'}</div>
          <div className="stat-label">
            Vol: {(stats?.[analysis.symbol1]?.volatility * 100)?.toFixed(2)}%
          </div>
        </div>

        <div className="stat-card">
          <h4>{analysis.symbol2} Price</h4>
          <div className="stat-value">${stats?.[analysis.symbol2]?.last?.toFixed(2) || 'N/A'}</div>
          <div className="stat-label">
            Vol: {(stats?.[analysis.symbol2]?.volatility * 100)?.toFixed(2)}%
          </div>
        </div>

        <div className="stat-card">
          <h4>Spread Volatility</h4>
          <div className="stat-value">
            {(stats?.spread?.volatility * 100)?.toFixed(2) || 'N/A'}%
          </div>
          <div className="stat-label">Annualized Spread Vol</div>
        </div>
      </div>

      {adf_test && !adf_test.error && (
        <div className={`adf-result ${adf_test.is_stationary ? 'stationary' : 'non-stationary'}`}>
          <h3>🔬 Augmented Dickey-Fuller Test</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginTop: '10px' }}>
            <div>
              <strong>ADF Statistic:</strong> {adf_test.adf_statistic?.toFixed(4)}
            </div>
            <div>
              <strong>P-Value:</strong> {adf_test.p_value?.toFixed(4)}
            </div>
            <div>
              <strong>Result:</strong> {adf_test.is_stationary ? '✅ Stationary' : '❌ Non-Stationary'}
            </div>
          </div>
          <div style={{ marginTop: '10px', fontSize: '13px', color: '#94a3b8' }}>
            Critical Values: 1%={adf_test.critical_values?.['1%']?.toFixed(3)}, 
            5%={adf_test.critical_values?.['5%']?.toFixed(3)}, 
            10%={adf_test.critical_values?.['10%']?.toFixed(3)}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
