import React from 'react';
import { ShieldAlert, X } from 'lucide-react';

const AlertsPanel = ({ alerts, removeAlert }) => {
  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
      <div className="panel-header" style={{ marginBottom: '16px' }}>
        <ShieldAlert size={18} color="var(--color-severe)" /> System Watchdog Alerts
        {alerts.length > 0 && (
           <div style={{ marginLeft: 'auto', background: 'var(--color-severe)', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>
             {alerts.length}
           </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {alerts.length === 0 ? (
           <div style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
             All systems clear. No critical alerts.
           </div>
        ) : (
           alerts.map(alert => (
             <div key={alert.id} style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px', borderRadius: '12px', position: 'relative' }}>
               <button 
                  onClick={() => removeAlert(alert.id)} 
                  style={{ position: 'absolute', top: '8px', right: '8px', background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', opacity: 0.6 }}
               >
                  <X size={14} />
               </button>
               <h4 style={{ fontSize: '14px', margin: '0 0 4px 0', color: 'var(--text-main)', paddingRight: '20px' }}>
                  {alert.name || 'Network Node'}
               </h4>
               <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                 <p style={{ fontSize: '12px', margin: 0, color: 'rgba(255,255,255,0.7)', lineHeight: 1.4 }}>{alert.reason}</p>
                 <span style={{ fontSize: '10px', color: 'var(--color-severe)', fontWeight: 600, whiteSpace: 'nowrap', marginLeft: '8px' }}>
                    {alert.timestamp}
                 </span>
               </div>
             </div>
           ))
        )}
      </div>
    </div>
  );
};

export default AlertsPanel;
