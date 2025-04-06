import { useEffect, useRef } from 'react';
import Globe from 'react-globe.gl';
import { useTheme } from '../context/ThemeContext';

const GeographicRiskHeatmap = ({ data = [] }) => {
  const globeRef = useRef();
  const { theme } = useTheme() || { theme: 'light' };
  
  // Default sample data if none provided
  const defaultData = [
    { lat: 40.7128, lng: -74.0060, risk: 0.8, size: 0.3, city: 'New York', transactions: 156, country: 'USA' },
    { lat: 34.0522, lng: -118.2437, risk: 0.6, size: 0.2, city: 'Los Angeles', transactions: 98, country: 'USA' },
    { lat: 51.5074, lng: -0.1278, risk: 0.7, size: 0.25, city: 'London', transactions: 134, country: 'UK' },
    { lat: 19.4326, lng: -99.1332, risk: 0.9, size: 0.35, city: 'Mexico City', transactions: 212, country: 'Mexico' },
    { lat: 48.8566, lng: 2.3522, risk: 0.5, size: 0.15, city: 'Paris', transactions: 67, country: 'France' },
    { lat: 55.7558, lng: 37.6173, risk: 0.85, size: 0.3, city: 'Moscow', transactions: 178, country: 'Russia' },
    { lat: 35.6762, lng: 139.6503, risk: 0.4, size: 0.2, city: 'Tokyo', transactions: 86, country: 'Japan' },
    { lat: 22.3193, lng: 114.1694, risk: 0.75, size: 0.25, city: 'Hong Kong', transactions: 142, country: 'China' },
    { lat: -33.8688, lng: 151.2093, risk: 0.3, size: 0.15, city: 'Sydney', transactions: 54, country: 'Australia' },
    { lat: -22.9068, lng: -43.1729, risk: 0.65, size: 0.2, city: 'Rio de Janeiro', transactions: 112, country: 'Brazil' },
    { lat: 28.6139, lng: 77.2090, risk: 0.7, size: 0.25, city: 'New Delhi', transactions: 133, country: 'India' },
    { lat: 1.3521, lng: 103.8198, risk: 0.45, size: 0.15, city: 'Singapore', transactions: 78, country: 'Singapore' },
  ];
  
  const pointData = data.length > 0 ? data : defaultData;
  
  // Process data for visualization
  const points = pointData.map(point => ({
    ...point,
    color: getPointColor(point.risk),
    altitude: 0.02 + (point.risk * 0.05) // Height based on risk
  }));
  
  // Get color based on risk level
  function getPointColor(risk) {
    if (risk < 0.3) return '#4caf50'; // Low risk - green
    if (risk < 0.6) return '#ff9800'; // Medium risk - orange
    return '#f44336'; // High risk - red
  }
  
  // Set up globe on initial render
  useEffect(() => {
    if (globeRef.current) {
      // Auto-rotate
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 0.5;
      
      // Set initial position to show more data points
      globeRef.current.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 1000);
    }
  }, []);
  
  // Update globe theme when app theme changes
  useEffect(() => {
    if (globeRef.current) {
      globeRef.current.backgroundColor(theme === 'dark' ? '#1a1a1a' : '#f5f7fb');
    }
  }, [theme]);
  
  return (
    <div className="card">
      <h3>Geographic Risk Heatmap</h3>
      <p className="mb-4">Global view of transaction risk by location</p>
      
      <div className="globe-container">
        <Globe
          ref={globeRef}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
          bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
          backgroundColor={theme === 'dark' ? '#1a1a1a' : '#f5f7fb'}
          
          // Points configuration
          pointsData={points}
          pointAltitude="altitude"
          pointColor="color"
          pointRadius="size"
          pointLabel={point => `
            <div class="globe-tooltip">
              <div class="tooltip-header">${point.city}, ${point.country}</div>
              <div class="tooltip-content">
                <div>Risk Level: ${Math.round(point.risk * 100)}%</div>
                <div>Transactions: ${point.transactions}</div>
              </div>
            </div>
          `}
          
          // Arc configuration
          arcsData={[]}
          arcColor={() => ['rgba(92, 78, 229, 0.8)', 'rgba(92, 78, 229, 0.2)']}
          arcDashLength={0.4}
          arcDashGap={0.2}
          arcDashAnimateTime={1500}
          
          // Atmosphere configuration
          atmosphereColor={theme === 'dark' ? 'rgba(92, 78, 229, 0.5)' : 'rgba(92, 78, 229, 0.3)'}
          atmosphereAltitude={0.15}
          
          // Performance settings
          rendererConfig={{ antialias: true, alpha: true }}
        />
      </div>
      
      <div className="risk-legend">
        <div className="risk-legend-item">
          <div className="risk-dot low-risk"></div>
          <span>Low Risk Regions</span>
        </div>
        <div className="risk-legend-item">
          <div className="risk-dot medium-risk"></div>
          <span>Medium Risk Regions</span>
        </div>
        <div className="risk-legend-item">
          <div className="risk-dot high-risk"></div>
          <span>High Risk Regions</span>
        </div>
      </div>
    </div>
  );
};

export default GeographicRiskHeatmap; 