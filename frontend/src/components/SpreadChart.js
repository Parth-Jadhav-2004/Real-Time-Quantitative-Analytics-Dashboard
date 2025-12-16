import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const SpreadChart = ({ spreadData, zscoreData, correlationData, isCorrelation }) => {
  if (isCorrelation && correlationData) {
    // Safety check: ensure minimum data points
    if (!correlationData || correlationData.length < 2) {
      return (
        <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
          Waiting for sufficient data…
        </div>
      );
    }

    // Validate data values
    const values = correlationData
      .map(d => d[1])
      .filter(v => Number.isFinite(v));

    if (values.length < 2) {
      return (
        <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
          Insufficient variance for plotting
        </div>
      );
    }

    const chartData = correlationData.map(([timestamp, value]) => ({
      timestamp: new Date(timestamp).toLocaleTimeString(),
      correlation: value
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="timestamp" 
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
            domain={[-1, 1]}
          />
          <Tooltip 
            contentStyle={{ 
              background: '#0f172a', 
              border: '1px solid #334155',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
          <Line 
            type="monotone" 
            dataKey="correlation" 
            stroke="#a855f7" 
            strokeWidth={2}
            dot={false}
            name="Correlation"
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  // Safety check: ensure minimum data points for spread
  if (!spreadData || spreadData.length < 2) {
    return (
      <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
        Waiting for sufficient data…
      </div>
    );
  }

  // Validate spread data values
  const spreadValues = spreadData
    .map(d => d[1])
    .filter(v => Number.isFinite(v));

  if (spreadValues.length < 2) {
    return (
      <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
        Insufficient variance for plotting
      </div>
    );
  }

  const chartData = spreadData.map(([timestamp, spreadValue]) => {
    // Find matching zscore by timestamp if available
    const zScore = zscoreData?.find(([ts]) => ts === timestamp)?.[1] || null;
    return {
      timestamp: new Date(timestamp).toLocaleTimeString(),
      spread: spreadValue,
      zscore: zScore
    };
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="timestamp" 
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          yAxisId="left"
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          yAxisId="right"
          orientation="right"
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{ 
            background: '#0f172a', 
            border: '1px solid #334155',
            borderRadius: '8px'
          }}
        />
        <Legend />
        <ReferenceLine yAxisId="right" y={0} stroke="#64748b" strokeDasharray="3 3" />
        <ReferenceLine yAxisId="right" y={2} stroke="#ef4444" strokeDasharray="3 3" />
        <ReferenceLine yAxisId="right" y={-2} stroke="#ef4444" strokeDasharray="3 3" />
        <Line 
          yAxisId="left"
          type="monotone" 
          dataKey="spread" 
          stroke="#0ea5e9" 
          strokeWidth={2}
          dot={false}
          name="Spread"
        />
        <Line 
          yAxisId="right"
          type="monotone" 
          dataKey="zscore" 
          stroke="#f59e0b" 
          strokeWidth={2}
          dot={false}
          name="Z-Score"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default SpreadChart;
