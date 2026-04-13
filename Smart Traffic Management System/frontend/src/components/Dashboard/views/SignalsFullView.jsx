import React from 'react';
import { TrafficCone, Navigation } from 'lucide-react';
import { getCongestionColor } from '../../../utils/congestionColors';

const SignalsFullView = ({ intersections }) => {
  const sorted = [...intersections].sort((a, b) => {
     // Sort correctly by breaking out Int number
     const aNum = parseInt(a.intersection_id.split('_')[1]) || 0;
     const bNum = parseInt(b.intersection_id.split('_')[1]) || 0;
     return aNum - bNum;
  });

  return (
    <div className="full-page fade-in">
      <div className="panel-header"><TrafficCone size={20} color="var(--accent-primary)" /> Complete Intersection Network Control</div>
      
      <div className="glass-panel" style={{ padding: '0', overflowX: 'auto', borderRadius: '16px' }}>
        <table className="table-glass">
          <thead style={{ background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(10px)' }}>
            <tr>
              <th>ID</th>
              <th>Road Class</th>
              <th>Volume (Veh)</th>
              <th>Queue Length</th>
              <th>Avg Delay</th>
              <th>Congestion Level</th>
              <th>Pred (15m)</th>
              <th>NS Green</th>
              <th>EW Green</th>
              <th>Cycle</th>
              <th>Mode</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(int => (
              <tr key={int.intersection_id} style={{ transition: 'background 0.2s', cursor: 'pointer' }} onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'} onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}>
                <td style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                   <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: getCongestionColor(int.congestion_label) }}></div>
                   Int {parseInt(int.intersection_id.split('_')[1]) || int.intersection_id}
                </td>
                <td style={{ textTransform: 'capitalize', color: 'var(--text-muted)' }}>{int.road_class}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '14px' }}>{int.vehicle_count}</td>
                <td>{int.queue_length.toFixed(1)}</td>
                <td>{int.waiting_time.toFixed(1)}s</td>
                <td>
                   <span style={{ 
                     color: getCongestionColor(int.congestion_label), 
                     background: `${getCongestionColor(int.congestion_label)}22`, 
                     padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase' 
                   }}>
                     {int.congestion_label}
                   </span>
                </td>
                <td>
                   <span style={{ color: getCongestionColor(int.predicted_label_15min), fontWeight: 700, textTransform: 'uppercase', fontSize: '12px' }}>
                     {int.predicted_label_15min}
                   </span>
                </td>
                <td style={{ fontWeight: 700, color: 'var(--color-low)' }}>{int.phase_ns_green || 45}s</td>
                <td style={{ fontWeight: 700, color: 'var(--color-severe)' }}>{int.phase_ew_green || 35}s</td>
                <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{int.cycle_time || 90}s</td>
                <td>
                  <span className={`signal-mode ${int.signal_mode === 'emergency' ? 'emergency' : ''}`}>
                    {int.signal_mode || 'adaptive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SignalsFullView;
