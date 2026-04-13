import React, { useState } from 'react';
import Sidebar from '../Sidebar/Sidebar';
import StatsCards from './StatsCards';
import TrafficMap from '../Map/TrafficMap';
import CongestionChart from '../Charts/CongestionChart';
import SpeedChart from '../Charts/SpeedChart';
import SignalPanel from '../Signals/SignalPanel';
import AlertsPanel from '../Alerts/AlertsPanel';
import { useTrafficData } from '../../hooks/useTrafficData';

// Sub-components for different views
import AnalyticsView from './views/AnalyticsView';
import SignalsFullView from './views/SignalsFullView';
import SettingsView from './views/SettingsView';

const Dashboard = () => {
  const { intersections, isConnected, alerts, removeAlert } = useTrafficData();
  const [activeTab, setActiveTab] = useState('overview');

  const renderContent = () => {
    switch (activeTab) {
      case 'analytics':
        return <AnalyticsView intersections={intersections} />;
      case 'signals':
        return <SignalsFullView intersections={intersections} />;
      case 'settings':
        return <SettingsView />;
      case 'overview':
      default:
        return (
          <>
            <StatsCards intersections={intersections} />
            <div className="dashboard-grid">
              <div className="left-column">
                 <TrafficMap intersections={intersections} />
                 <div className="charts-row">
                    <CongestionChart intersections={intersections} />
                    <SpeedChart intersections={intersections} />
                 </div>
              </div>
              <div className="right-column">
                 <AlertsPanel alerts={alerts} removeAlert={removeAlert} />
                 <SignalPanel intersections={intersections} />
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content fade-in">
        <header className="dashboard-header">
          <div>
            <h1>{activeTab === 'overview' ? 'Nexus Traffic AI' : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '15px', marginTop: '6px' }}>
              Real-time congestion prediction & adaptive signal control
            </p>
          </div>
          <div className="status-badge">
             <div style={{ 
                 width: '10px', 
                 height: '10px', 
                 borderRadius: '50%', 
                 backgroundColor: isConnected ? 'var(--color-low)' : 'var(--color-severe)',
                 boxShadow: isConnected ? '0 0 12px var(--color-low)' : '0 0 12px var(--color-severe)',
                 animation: isConnected ? 'pulse 2s infinite' : 'none'
              }}></div>
             <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>
                 {isConnected ? 'System Online (Live)' : 'Reconnecting...'}
             </span>
          </div>
        </header>

        {renderContent()}
      </main>
    </div>
  );
};

export default Dashboard;
