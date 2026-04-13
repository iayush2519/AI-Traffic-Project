import React from 'react';
import { Car, Clock, Zap, AlertTriangle } from 'lucide-react';

const StatsCards = ({ intersections }) => {
  // Compute aggregates
  const totalVehicles = intersections.reduce((sum, int) => sum + int.vehicle_count, 0);
  const avgWait = intersections.reduce((sum, int) => sum + int.waiting_time, 0) / (intersections.length || 1);
  
  const severeCount = intersections.filter(int => int.congestion_label === 'severe').length;

  return (
    <div className="stats-row">
      <div className="stat-card glass-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="stat-title">Active Vehicles</div>
            <div className="stat-value">{totalVehicles.toLocaleString()}</div>
          </div>
          <Car className="stat-icon" size={24} />
        </div>
      </div>

      <div className="stat-card glass-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="stat-title">Avg Wait Time</div>
            <div className="stat-value">{avgWait.toFixed(1)}s</div>
          </div>
          <Clock className="stat-icon" size={24} />
        </div>
      </div>

      <div className="stat-card glass-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="stat-title">Network Efficiency</div>
            <div className="stat-value">92%</div>
          </div>
          <Zap className="stat-icon" size={24} />
        </div>
      </div>

      <div className="stat-card glass-panel" style={{ borderLeft: severeCount > 0 ? '4px solid var(--color-severe)' : undefined }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="stat-title">Severe Alerts</div>
            <div className="stat-value" style={{ color: severeCount > 0 ? 'var(--color-severe)' : 'inherit' }}>
                {severeCount}
            </div>
          </div>
          <AlertTriangle className="stat-icon" size={24} color={severeCount > 0 ? "var(--color-severe)" : "var(--accent-cyan)"} />
        </div>
      </div>
    </div>
  );
};

export default StatsCards;
