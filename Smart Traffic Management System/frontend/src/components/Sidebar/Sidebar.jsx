import React from 'react';
import { Activity, Map as MapIcon, BarChart3, Settings, TrafficCone } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'overview', icon: MapIcon, label: 'Overview' },
    { id: 'analytics', icon: BarChart3, label: 'Analytics' },
    { id: 'signals', icon: TrafficCone, label: 'Signals Control' },
    { id: 'settings', icon: Settings, label: 'Settings', bottom: true }
  ];

  return (
    <div className="sidebar">
      <div className="logo-container">
        <Activity size={28} strokeWidth={2.5} />
      </div>
      
      <div className="nav-links">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <div 
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              style={tab.bottom ? { marginTop: 'auto' } : {}}
              onClick={() => setActiveTab(tab.id)}
              title={tab.label}
            >
              <Icon size={24} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Sidebar;
