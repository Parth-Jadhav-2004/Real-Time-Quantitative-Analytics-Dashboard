import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PriceChart = ({ data, symbol }) => {
  // Safety check: ensure minimum data points
  if (!data || data.length < 2) {
    return (
      <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
        Waiting for sufficient data…
      </div>
    );
  }

  // Validate price values
  const prices = data
    .map(d => d.close)
    .filter(v => Number.isFinite(v));

  if (prices.length < 2) {
    return (
      <div style={{ padding: "1rem", color: "#888", textAlign: "center" }}>
        Insufficient variance for plotting
      </div>
    );
  }

  const chartData = data.map(d => ({
    timestamp: new Date(d.timestamp).toLocaleTimeString(),
    price: d.close,
    high: d.high,
    low: d.low
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
          domain={['auto', 'auto']}
        />
        <Tooltip 
          contentStyle={{ 
            background: '#0f172a', 
            border: '1px solid #334155',
            borderRadius: '8px'
          }}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="price" 
          stroke="#0ea5e9" 
          strokeWidth={2}
          dot={false}
          name="Close"
        />
        <Line 
          type="monotone" 
          dataKey="high" 
          stroke="#10b981" 
          strokeWidth={1}
          dot={false}
          name="High"
          strokeDasharray="5 5"
        />
        <Line 
          type="monotone" 
          dataKey="low" 
          stroke="#ef4444" 
          strokeWidth={1}
          dot={false}
          name="Low"
          strokeDasharray="5 5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;
