import { useState, useEffect } from 'react';
import { 
  FindInPage as ScanIcon, 
  Calculate as CalculateIcon, 
  Security as SecurityIcon, 
  Gavel as GavelIcon 
} from '@mui/icons-material';

const BlockchainVerificationJourney = ({ transaction }) => {
  const [progress, setProgress] = useState(0);
  
  const stages = [
    { 
      id: 1, 
      title: 'Anomaly Detection', 
      description: 'Transaction analyzed for unusual patterns', 
      icon: <ScanIcon fontSize="medium" /> 
    },
    { 
      id: 2, 
      title: 'Risk Score Calculation', 
      description: 'AI models evaluate transaction risk', 
      icon: <CalculateIcon fontSize="medium" /> 
    },
    { 
      id: 3, 
      title: 'Verification', 
      description: 'Transaction validated by network nodes', 
      icon: <SecurityIcon fontSize="medium" /> 
    },
    { 
      id: 4, 
      title: 'Blockchain Commit', 
      description: 'Transaction confirmed and logged', 
      icon: <GavelIcon fontSize="medium" /> 
    }
  ];
  
  useEffect(() => {
    // Simulate progress animation when transaction stage changes
    if (transaction) {
      setProgress(0);
      const targetProgress = (transaction.stage / stages.length) * 100;
      
      let currentProgress = 0;
      const interval = setInterval(() => {
        currentProgress += 2;
        setProgress(Math.min(currentProgress, targetProgress));
        
        if (currentProgress >= targetProgress) {
          clearInterval(interval);
        }
      }, 50);
      
      return () => clearInterval(interval);
    }
  }, [transaction, stages.length]);
  
  if (!transaction) return null;
  
  return (
    <div className="card">
      <h3>Blockchain Verification Journey</h3>
      
      <div className="progress-container">
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="progress-percentage">
          {Math.round(progress)}% Complete
        </div>
      </div>
      
      <div className="journey-stages">
        {stages.map((stage) => {
          const isCompleted = transaction.stage >= stage.id;
          const isActive = transaction.stage === stage.id;
          
          return (
            <div 
              key={stage.id} 
              className={`journey-stage ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
            >
              <div className="stage-indicator">
                <div className="stage-icon">
                  {stage.icon}
                </div>
                <div className="stage-connector" />
              </div>
              
              <div className="stage-content">
                <h4>{stage.title}</h4>
                <p>{stage.description}</p>
                
                {isCompleted && (
                  <div className="stage-timing">
                    <span className="checkmark">✓</span>
                    {stage.id < transaction.stage ? 'Completed' : 'In Progress'}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BlockchainVerificationJourney; 