import React from 'react';
import { TrafficCone } from 'lucide-react';

const SignalPanel = ({ intersections }) => {
  // Get top 5 most critical intersections for the side panel
  const criticalSignals = [...intersections]
    .sort((a, b) => b.traffic_density - a.traffic_density)
    .slice(0, 5);

  return (
    <div className="signal-panel glass-panel">
      <div className="panel-header" style={{ marginBottom: '24px' }}>
        <TrafficCone size={18} color="var(--color-medium)" />
        Adaptive Signal Controller
      </div>
      
      <div className="signal-list">
        {criticalSignals.map((int) => (
          <div key={int.intersection_id} className="signal-item">
            <div className="signal-header">
              <span className="signal-title">{(int.intersection_name || `Int ${int.intersection_id}`).replace('Intersection ', 'Int ')}</span>
              <span className={`signal-mode ${int.signal_mode === 'emergency' ? 'emergency' : ''}`}>
                {int.signal_mode || 'adaptive'}
              </span>
            </div>
            
            <div className="signal-timers">
              <div className="timer-box green">
                <span className="timer-val">{int.phase_ns_green || 45}s</span>
                <span className="timer-lbl">NS Green</span>
              </div>
              <div className="timer-box red">
                <span className="timer-val">{int.phase_ew_green || 35}s</span>
                <span className="timer-lbl">EW Green</span>
              </div>
            </div>
            
            {/* Tiny progress bar representing cycle */}
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px', display: 'flex', overflow: 'hidden' }}>
              <div style={{ width: `${((int.phase_ns_green || 45) / (int.cycle_time || 90)) * 100}%`, background: 'var(--color-low)' }}></div>
              <div style={{ width: `${(3 / (int.cycle_time || 90)) * 100}%`, background: '#ffeb3b' }}></div>
              <div style={{ width: `${((int.phase_ew_green || 35) / (int.cycle_time || 90)) * 100}%`, background: 'var(--color-severe)' }}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SignalPanel;
