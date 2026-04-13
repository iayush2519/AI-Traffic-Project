import React from 'react';
import Dashboard from './components/Dashboard/Dashboard';
import { SettingsProvider } from './contexts/SettingsContext';

function App() {
  return (
    <SettingsProvider>
      <Dashboard />
    </SettingsProvider>
  );
}

export default App;
