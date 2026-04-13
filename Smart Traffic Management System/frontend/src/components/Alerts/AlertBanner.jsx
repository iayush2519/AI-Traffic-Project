import React from 'react';
import { AlertCircle, X } from 'lucide-react';

const AlertBanner = ({ alert, onClose }) => {
  return (
    <div className="alert-banner">
      <AlertCircle className="alert-icon" size={20} />
      <div className="alert-content">
        <h4>{alert.name}</h4>
        <p>{alert.reason} at {alert.timestamp}</p>
      </div>
      <button 
        onClick={() => onClose(alert.id)}
        style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', marginLeft: 'auto' }}
      >
        <X size={16} opacity={0.6} />
      </button>
    </div>
  );
};

export default AlertBanner;
