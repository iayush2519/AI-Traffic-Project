import { useState, useEffect, useCallback } from 'react';
import { trafficApi } from '../api/trafficApi';

export function useTrafficData() {
  const [intersections, setIntersections] = useState([]);

  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState([]);

  // Fetch initial state via REST
  const fetchInitialData = useCallback(async () => {
    try {
      const data = await trafficApi.getStatus();
      setIntersections(data);
    } catch (error) {
      console.error("Failed to fetch initial traffic data:", error);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchInitialData();

    // Setup WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/traffic');

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket Connected');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'initial_state' || message.type === 'traffic_update') {
          setIntersections(message.data);
          
          // Check for severe congestion and generate alerts
          const newAlerts = message.data
            .filter(int => int.congestion_label === 'severe' || int.predicted_label_15min === 'severe')
            .map(int => ({
              id: `${int.intersection_id}-${Date.now()}`,
              intersectionId: int.intersection_id,
              name: int.intersection_name,
              reason: int.congestion_label === 'severe' ? 'Current severe traffic' : 'Predicted severe traffic in 15m',
              timestamp: new Date().toLocaleTimeString()
            }));

          // Very simple alert logic: keep last 3, unique by intersection ID
          if (newAlerts.length > 0) {
             setAlerts(prev => {
                const combined = [...newAlerts, ...prev];
                const unique = Array.from(new Map(combined.map(item => [item.intersectionId, item])).values());
                return unique.slice(0, 3);
             });
          }
        }
      } catch (err) {
        console.error("Error parsing WS message:", err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket Disconnected');
    };

    return () => {
      ws.close();
    };
  }, [fetchInitialData]);

  const removeAlert = (alertId) => {
    setAlerts(prev => prev.filter(a => a.id !== alertId));
  };

  return { intersections, isConnected, alerts, removeAlert };
}
