import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { getCongestionColor } from '../../utils/congestionColors';
import { Activity } from 'lucide-react';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{ 
        background: 'rgba(15, 17, 26, 0.95)', 
        border: '1px solid rgba(255,255,255,0.1)',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
      }}>
        <p style={{ margin: '0 0 8px 0', fontSize: '13px', fontWeight: 'bold' }}>{data.name}</p>
        <p style={{ margin: '0', fontSize: '12px', color: '#8b9bb4' }}>
          Density: <span style={{ color: '#fff' }}>{(data.density * 100).toFixed(1)}%</span>
        </p>
        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#8b9bb4' }}>
          Speed: <span style={{ color: '#fff' }}>{data.speed} mph</span>
        </p>
      </div>
    );
  }
  return null;
};

const CongestionChart = ({ intersections }) => {
  // Take top 10 most congested intersections
  const data = useMemo(() => {
    return [...intersections]
      .sort((a, b) => b.traffic_density - a.traffic_density)
      .slice(0, 10)
      .map(int => ({
        id: int.intersection_id,
        name: (int.intersection_name || `Int ${int.intersection_id}`).replace('Intersection ', 'Int '),
        density: int.traffic_density,
        label: int.congestion_label,
        speed: int.average_speed
      }));
  }, [intersections]);

  return (
    <div className="chart-panel glass-panel">
      <div className="panel-header">
        <Activity size={18} color="var(--accent-orange)" />
        Top Congested Intersections
      </div>
      <div style={{ flex: 1, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <XAxis type="number" domain={[0, 1]} hide />
            <YAxis 
              dataKey="name" 
              type="category" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#8b9bb4', fontSize: 11 }}
              width={60}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
            <Bar dataKey="density" radius={[0, 4, 4, 0]} barSize={12}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getCongestionColor(entry.label)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CongestionChart;
