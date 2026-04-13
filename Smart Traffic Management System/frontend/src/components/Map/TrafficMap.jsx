import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { getCongestionColor } from '../../utils/congestionColors';

// Fix Leaflet default icon issues
delete L.Icon.Default.prototype._getIconUrl;

const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div class="custom-marker" style="background-color: ${color};"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

// Component to handle map bounds
const MapBounds = ({ intersections }) => {
  const map = useMap();
  
  useEffect(() => {
    if (intersections && intersections.length > 0) {
      const bounds = L.latLngBounds(intersections.map(int => [int.lat, int.lon]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [intersections, map]);
  
  return null;
};

const TrafficMap = ({ intersections, onSelectIntersection }) => {
  // Default LA center
  const center = [34.0522, -118.2437];

  return (
    <div className="map-container glass-panel">
      <MapContainer 
        center={center} 
        zoom={11} 
        style={{ height: '100%', width: '100%', background: '#0f111a' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        {intersections.length > 0 && <MapBounds intersections={intersections} />}
        
        {intersections.map((intersection) => (
          <Marker 
            key={intersection.intersection_id}
            position={[intersection.lat, intersection.lon]}
            icon={createCustomIcon(getCongestionColor(intersection.congestion_label))}
            eventHandlers={{
              click: () => {
                if (onSelectIntersection) onSelectIntersection(intersection);
              },
            }}
          >
            <Popup className="custom-popup">
              <div style={{ padding: '4px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px' }}>
                   {intersection.intersection_name || `Intersection ${intersection.intersection_id}`}
                </h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: '#8b9bb4' }}>Speed:</span>
                  <span>{intersection.average_speed} mph</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                   <span style={{ color: '#8b9bb4' }}>Density:</span>
                   <span>{(intersection.traffic_density * 100).toFixed(0)}%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: '8px' }}>
                   <span style={{ color: '#8b9bb4' }}>Prediction (15m):</span>
                   <span style={{ color: getCongestionColor(intersection.predicted_label_15min), fontWeight: 'bold', textTransform: 'uppercase' }}>
                     {intersection.predicted_label_15min}
                   </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;
