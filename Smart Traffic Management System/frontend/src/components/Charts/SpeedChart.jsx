import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ 
        background: 'rgba(15, 17, 26, 0.95)', 
        border: '1px solid rgba(255,255,255,0.1)',
        padding: '8px 12px',
        borderRadius: '8px',
        fontSize: '12px'
      }}>
        <p style={{ margin: 0, color: '#8b9bb4' }}>Average Network Speed</p>
        <p style={{ margin: '4px 0 0 0', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>
          {payload[0].value.toFixed(1)} mph
        </p>
      </div>
    );
  }
  return null;
};

// Represents a mock historical trend of average speed
const generateMockSpeedData = () => {
    const data = [];
    const now = new Date();
    for (let i = 24; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 5 * 60000);
        data.push({
            time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            speed: 35 + Math.random() * 15 - 5 // Random baseline around 40
        });
    }
    return data;
};

const mockData = generateMockSpeedData();

const SpeedChart = ({ intersections }) => {
  // In a real app we'd compute average speed over time.
  // Here we use mock data but update the last element with current average.
  
  const currentAvgSpeed = intersections.length > 0 
    ? intersections.reduce((acc, curr) => acc + curr.average_speed, 0) / intersections.length
    : 0;

  const data = mockData.map(item => ({...item}));
  if (data.length > 0 && currentAvgSpeed > 0) {
      data[data.length - 1].speed = currentAvgSpeed;
  }

  return (
    <div className="chart-panel glass-panel">
      <div className="panel-header">
        <TrendingUp size={18} color="var(--accent-cyan)" />
        Network Average Speed
      </div>
      <div style={{ flex: 1, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorSpeed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="time" hide />
            <YAxis domain={['auto', 'auto']} axisLine={false} tickLine={false} tick={{ fill: '#8b9bb4', fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="speed" stroke="var(--accent-cyan)" strokeWidth={2} fillOpacity={1} fill="url(#colorSpeed)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SpeedChart;
