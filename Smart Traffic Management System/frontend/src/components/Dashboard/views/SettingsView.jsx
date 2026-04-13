import React from 'react';
import { Settings, Save, Database, Shield, Zap } from 'lucide-react';
import { useSettings } from '../../../contexts/SettingsContext';

const SettingsView = () => {
   const {
       saved, activeEngine, setActiveEngine,
       horizon, setHorizon,
       autoApply, setAutoApply,
       emergencyOverride, setEmergencyOverride,
       minGreen, setMinGreen,
       handleSave
   } = useSettings();

  return (
    <div className="full-page fade-in">
      <div className="panel-header"><Settings size={20} color="var(--accent-primary)" /> System Configuration</div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(300px, 1fr)', gap: '32px' }}>
          
         {/* ML Config */}
         <div className="glass-panel" style={{ padding: '32px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', fontSize: '18px' }}>
                <Database size={20} color="var(--accent-secondary)" /> Model Strategy
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ color: 'var(--text-muted)', fontSize: '13px', fontWeight: 600 }}>Active Prediction Engine</label>
                    <select 
                        value={activeEngine}
                        onChange={(e) => setActiveEngine(e.target.value)}
                        style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: 'white', padding: '12px', borderRadius: '8px', outline: 'none' }}
                    >
                        <option value="lstm">LSTM Deep Learning (V2)</option>
                        <option value="xgboost">XGBoost Ensemble (V1)</option>
                        <option value="rule">Rule-Based Fallback</option>
                    </select>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ color: 'var(--text-muted)', fontSize: '13px', fontWeight: 600 }}>Forecasting Horizon</label>
                    <select 
                        value={horizon}
                        onChange={(e) => setHorizon(e.target.value)}
                        style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', color: 'white', padding: '12px', borderRadius: '8px', outline: 'none' }}
                    >
                        <option value="5">5 Minutes</option>
                        <option value="15">15 Minutes</option>
                        <option value="30">30 Minutes</option>
                    </select>
                </div>
            </div>
         </div>

         {/* Controller Config */}
         <div className="glass-panel" style={{ padding: '32px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', fontSize: '18px' }}>
                <Zap size={20} color="var(--color-medium)" /> Signal Controller Safety Bounds
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>Auto-Apply Adaptive Timings</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Automatically push timings to field hardware</div>
                    </div>
                    {/* Interactive Toggle Switch */}
                    <div 
                        onClick={() => setAutoApply(!autoApply)}
                        style={{ width: '48px', height: '24px', background: autoApply ? 'var(--accent-primary)' : 'rgba(255,255,255,0.2)', borderRadius: '12px', padding: '2px', cursor: 'pointer', transition: 'background 0.3s' }}
                    >
                        <div style={{ width: '20px', height: '20px', background: 'white', borderRadius: '50%', transform: autoApply ? 'translateX(24px)' : 'translateX(0px)', transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}></div>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>Emergency Corridor Override</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Allow 85% phase lock for first responders</div>
                    </div>
                    {/* Interactive Toggle Switch */}
                    <div 
                        onClick={() => setEmergencyOverride(!emergencyOverride)}
                        style={{ width: '48px', height: '24px', background: emergencyOverride ? 'var(--accent-primary)' : 'rgba(255,255,255,0.2)', borderRadius: '12px', padding: '2px', cursor: 'pointer', transition: 'background 0.3s' }}
                    >
                        <div style={{ width: '20px', height: '20px', background: 'white', borderRadius: '50%', transform: emergencyOverride ? 'translateX(24px)' : 'translateX(0px)', transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}></div>
                    </div>
                </div>
                
                <div style={{ marginTop: '16px' }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                       <span style={{ fontSize: '14px', fontWeight: 600 }}>Minimum Green Allowed</span>
                       <span style={{ fontWeight: 700, color: 'var(--accent-secondary)' }}>{minGreen}s</span>
                   </div>
                   <input 
                      type="range" 
                      min="5" 
                      max="25" 
                      value={minGreen} 
                      onChange={(e) => setMinGreen(e.target.value)}
                      style={{ width: '100%', accentColor: 'var(--accent-secondary)' }} 
                   />
                </div>
            </div>
         </div>

      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto', paddingTop: '24px' }}>
            <button 
                onClick={handleSave}
                style={{ 
                    display: 'flex', alignItems: 'center', gap: '8px', 
                    padding: '12px 24px', borderRadius: '8px', border: 'none', 
                    background: saved ? 'var(--color-low)' : 'var(--accent-gradient)', 
                    color: 'white', fontWeight: 700, fontSize: '15px', cursor: 'pointer', transition: 'all 0.3s'
                }}>
                <Save size={18} />
                {saved ? 'Configurations Saved' : 'Save Configurations'}
            </button>
      </div>

    </div>
  );
};

export default SettingsView;
