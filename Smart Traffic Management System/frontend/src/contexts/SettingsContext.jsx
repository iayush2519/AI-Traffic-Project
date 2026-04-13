import React, { createContext, useState, useContext } from 'react';

export const SettingsContext = createContext();

export const SettingsProvider = ({ children }) => {
   const [saved, setSaved] = useState(false);
   const [activeEngine, setActiveEngine] = useState("lstm");
   const [horizon, setHorizon] = useState("15");
   const [autoApply, setAutoApply] = useState(true);
   const [emergencyOverride, setEmergencyOverride] = useState(false);
   const [minGreen, setMinGreen] = useState(10);

   const handleSave = () => {
       setSaved(true);
       setTimeout(() => setSaved(false), 2000);
   };

   return (
       <SettingsContext.Provider value={{
           saved, activeEngine, setActiveEngine,
           horizon, setHorizon,
           autoApply, setAutoApply,
           emergencyOverride, setEmergencyOverride,
           minGreen, setMinGreen,
           handleSave
       }}>
           {children}
       </SettingsContext.Provider>
   );
};

export const useSettings = () => useContext(SettingsContext);
