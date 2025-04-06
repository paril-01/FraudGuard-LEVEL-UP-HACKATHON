import { useState } from 'react';
import {
  Help as HelpIcon,
  BarChart as BarChartIcon,
  ArrowDownward as ArrowDownIcon,
  ArrowUpward as ArrowUpIcon
} from '@mui/icons-material';

const RiskScoreExplainer = ({ prediction }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  // Default risk factors if none are provided
  const defaultFactors = [
    { name: 'Transaction Amount', value: 0.85, impact: 35, description: 'Unusually high amount for this account type' },
    { name: 'Time of Transaction', value: 0.45, impact: 15, description: 'Outside typical user activity hours' },
    { name: 'Location Anomaly', value: 0.65, impact: 20, description: 'Transaction originated from unusual location' },
    { name: 'Account History', value: 0.25, impact: 10, description: 'Account has established history of normal activity' },
    { name: 'Frequency Pattern', value: 0.55, impact: 20, description: 'Multiple transactions in short time period' }
  ];
  
  // Use provided factors or fall back to defaults
  const riskFactors = prediction?.factors || defaultFactors;
  
  // Calculate total risk score (weighted average)
  const totalRiskScore = riskFactors.reduce((sum, factor) => sum + (factor.value * factor.impact), 0) / 
    riskFactors.reduce((sum, factor) => sum + factor.impact, 0);
  
  // Determine risk level
  const getRiskLevel = (score) => {
    if (score < 0.4) return { level: 'Low', class: 'low-risk' };
    if (score < 0.7) return { level: 'Medium', class: 'medium-risk' };
    return { level: 'High', class: 'high-risk' };
  };
  
  const riskLevel = getRiskLevel(totalRiskScore);
  
  // Sort factors by impact
  const sortedFactors = [...riskFactors].sort((a, b) => b.impact - a.impact);
  
  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };
  
  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <BarChartIcon style={{ marginRight: '8px' }} />
          Risk Score Explainability
        </h3>
        <button className="explain-btn" onClick={toggleDetails}>
          {showDetails ? 'Hide Details' : 'Explain This Score'}
        </button>
      </div>
      
      <div className="risk-score-summary">
        <div className="score-display">
          <div className={`score-circle ${riskLevel.class}`}>
            {Math.round(totalRiskScore * 100)}
          </div>
          <div className="score-label">
            <h4>{riskLevel.level} Risk</h4>
            <p>Transaction Risk Score</p>
          </div>
        </div>
        
        <div className="score-recommendation">
          {riskLevel.level === 'High' ? (
            <p>
              <ArrowUpIcon className="high-risk" />
              This transaction has been flagged for review due to multiple risk factors.
            </p>
          ) : riskLevel.level === 'Medium' ? (
            <p>
              <HelpIcon className="medium-risk" />
              This transaction shows some unusual patterns and requires additional verification.
            </p>
          ) : (
            <p>
              <ArrowDownIcon className="low-risk" />
              This transaction appears to be legitimate based on our analysis.
            </p>
          )}
        </div>
      </div>
      
      {showDetails && (
        <div className="risk-score-explainer">
          <h4>Risk Factor Breakdown</h4>
          <p className="factor-description">
            Below is a breakdown of what factors contributed to this risk score and their relative impact.
          </p>
          
          <div className="factor-tree">
            {sortedFactors.map((factor, index) => (
              <div key={index} className="risk-factor">
                <div className="factor-name">
                  {factor.name}
                  <span className="factor-impact">({factor.impact}%)</span>
                </div>
                
                <div className="factor-bar">
                  <div 
                    className={`factor-value ${getRiskLevel(factor.value).class}`}
                    style={{ width: `${factor.value * 100}%` }}
                  ></div>
                </div>
                
                <div className="factor-score">
                  {Math.round(factor.value * 100)}
                </div>
              </div>
            ))}
          </div>
          
          <div className="factor-details">
            <h4>Factor Details</h4>
            <ul className="factor-details-list">
              {sortedFactors.map((factor, index) => (
                <li key={index}>
                  <strong>{factor.name}:</strong> {factor.description}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="recommendation-box">
            <h4>Risk Mitigation</h4>
            {riskLevel.level === 'High' ? (
              <ul>
                <li>Implement additional identity verification</li>
                <li>Contact the customer through verified channels</li>
                <li>Apply temporary transaction limits</li>
                <li>Consider blocking transaction until verified</li>
              </ul>
            ) : riskLevel.level === 'Medium' ? (
              <ul>
                <li>Request additional authorization</li>
                <li>Flag account for monitoring</li>
                <li>Consider step-up authentication</li>
              </ul>
            ) : (
              <ul>
                <li>Transaction can proceed normally</li>
                <li>Continue routine monitoring</li>
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskScoreExplainer; 