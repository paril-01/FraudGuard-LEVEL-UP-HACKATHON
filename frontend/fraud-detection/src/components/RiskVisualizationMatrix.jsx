import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const RiskVisualizationMatrix = ({ transactions = [] }) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Initialize Three.js scene
    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    
    // Create scene, camera, and renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f7fb);
    
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 4;
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    containerRef.current.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Create cube frame
    const cubeSize = 2;
    const cubeGeometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
    const edgesGeometry = new THREE.EdgesGeometry(cubeGeometry);
    const cubeMaterial = new THREE.LineBasicMaterial({ color: 0x5c4ee5, linewidth: 2 });
    const cube = new THREE.LineSegments(edgesGeometry, cubeMaterial);
    scene.add(cube);
    
    // Add axes labels
    const createLabel = (text, position) => {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#333333';
      ctx.font = '24px Arial';
      ctx.fillText(text, 10, 30);
      
      const texture = new THREE.CanvasTexture(canvas);
      const material = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(material);
      sprite.position.copy(position);
      sprite.scale.set(0.5, 0.25, 1);
      scene.add(sprite);
    };
    
    createLabel('Amount Anomaly', new THREE.Vector3(1.5, 0, 0));
    createLabel('Location Anomaly', new THREE.Vector3(0, 1.5, 0));
    createLabel('Behavior Pattern', new THREE.Vector3(0, 0, 1.5));
    
    // Add orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Function to add transaction dots
    const addTransactionDot = (transaction, index) => {
      // Calculate risk factors (0-1 scale)
      const amountRisk = transaction.amountRisk || Math.random(); // X-axis
      const locationRisk = transaction.locationRisk || Math.random(); // Y-axis
      const behaviorRisk = transaction.behaviorRisk || Math.random(); // Z-axis
      
      // Calculate position (-1 to 1 within cube)
      const x = (amountRisk * 2 - 1);
      const y = (locationRisk * 2 - 1);
      const z = (behaviorRisk * 2 - 1);
      
      // Calculate total risk for color
      const totalRisk = (amountRisk + locationRisk + behaviorRisk) / 3;
      
      // Color based on risk (green to yellow to red)
      let color;
      if (totalRisk < 0.33) {
        color = new THREE.Color(0x4caf50); // Green - safe
      } else if (totalRisk < 0.66) {
        color = new THREE.Color(0xff9800); // Yellow - suspicious
      } else {
        color = new THREE.Color(0xf44336); // Red - high risk
      }
      
      // Create dot
      const geometry = new THREE.SphereGeometry(0.05, 16, 16);
      const material = new THREE.MeshBasicMaterial({ color });
      const dot = new THREE.Mesh(geometry, material);
      dot.position.set(x, y, z);
      
      // Store transaction data for hover info
      dot.userData = {
        transaction,
        index,
        totalRisk,
        position: { x, y, z }
      };
      
      scene.add(dot);
      return dot;
    };
    
    // Add transaction dots
    transactions.map((transaction, index) => 
      addTransactionDot(transaction, index)
    );
    
    // If no transactions are provided, add some demo dots
    if (transactions.length === 0) {
      for (let i = 0; i < 50; i++) {
        addTransactionDot({
          id: i,
          amount: Math.random() * 10000,
          amountRisk: Math.random(),
          locationRisk: Math.random(),
          behaviorRisk: Math.random()
        }, i);
      }
    }
    
    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      
      cube.rotation.x += 0.001;
      cube.rotation.y += 0.001;
      
      controls.update();
      renderer.render(scene, camera);
    };
    
    animate();
    
    // Store the scene for later use
    sceneRef.current = scene;
    
    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      
      const newWidth = containerRef.current.clientWidth;
      const newHeight = containerRef.current.clientHeight;
      
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
      
      window.removeEventListener('resize', handleResize);
      
      // Dispose geometries and materials
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          object.material.dispose();
        }
      });
    };
  }, [transactions]);
  
  return (
    <div className="card">
      <h3>Risk Visualization Matrix</h3>
      <p className="mb-4">3D visualization of transaction risk factors</p>
      <div 
        ref={containerRef} 
        className="risk-visualization-container"
        style={{ height: '400px' }}
      />
      <div className="risk-legend">
        <div className="risk-legend-item">
          <div className="risk-dot low-risk"></div>
          <span>Low Risk</span>
        </div>
        <div className="risk-legend-item">
          <div className="risk-dot medium-risk"></div>
          <span>Medium Risk</span>
        </div>
        <div className="risk-legend-item">
          <div className="risk-dot high-risk"></div>
          <span>High Risk</span>
        </div>
      </div>
    </div>
  );
};

export default RiskVisualizationMatrix; 