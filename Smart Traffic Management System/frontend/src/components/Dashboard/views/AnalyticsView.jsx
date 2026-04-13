import React from 'react';
import { Database, TrendingUp, Cpu, Server } from 'lucide-react';
import CongestionChart from '../../Charts/CongestionChart';
import SpeedChart from '../../Charts/SpeedChart';
import { useSettings } from '../../../contexts/SettingsContext';

const AnalyticsView = ({ intersections }) => {
  const { activeEngine, horizon } = useSettings();
  
  const getEngineName = () => {
    switch (activeEngine) {
      case 'xgboost': return 'XGBoost Ensemble (V1)';
      case 'rule': return 'Rule-Based Fallback';
      case 'lstm': default: return 'LSTM Deep Learning (V2)';
    }
  };
  return (
    <div className="full-page fade-in">
      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        
        {/* ML Model Performance Card */}
        <div className="glass-panel" style={{ flex: '1 1 300px', padding: '24px' }}>
          <div className="panel-header"><Cpu size={18} color="var(--accent-primary)" /> Model Performance ({getEngineName()})</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Horizon ({horizon}m) Accuracy</span>
                <span style={{ fontWeight: 700, color: 'var(--color-low)' }}>94.2%</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Horizon (30m) Accuracy</span>
                <span style={{ fontWeight: 700, color: 'var(--color-medium)' }}>88.7%</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>ROC-AUC Macro</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-secondary)' }}>0.915</span>
             </div>
          </div>
        </div>

        {/* Pipeline Stats */}
        <div className="glass-panel" style={{ flex: '1 1 300px', padding: '24px' }}>
          <div className="panel-header"><Database size={18} color="var(--accent-primary)" /> Data Pipeline</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Ingestion Rate</span>
                <span style={{ fontWeight: 700 }}>240 records/min</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Total Training Rows</span>
                <span style={{ fontWeight: 700 }}>1.04 Million</span>
             </div>
             <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Processing Latency</span>
                <span style={{ fontWeight: 700, color: 'var(--color-low)' }}>42ms</span>
             </div>
          </div>
        </div>

        {/* Distributed Load */}
        <div className="glass-panel" style={{ flex: '1 1 300px', padding: '24px' }}>
          <div className="panel-header"><Server size={18} color="var(--accent-primary)" /> Node Status</div>
          <div style={{ display: 'flex', alignItems: 'center', height: '100px', justifyContent: 'center', gap: '20px' }}>
             <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--color-low)' }}>3</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Active API Workers</div>
             </div>
             <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-secondary)' }}>99.9%</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Uptime</div>
             </div>
          </div>
        </div>
      </div>

      <div className="charts-row" style={{ height: '400px', marginTop: '12px' }}>
          <CongestionChart intersections={intersections} />
          <SpeedChart intersections={intersections} />
      </div>

    </div>
  );
};

export default AnalyticsView;
