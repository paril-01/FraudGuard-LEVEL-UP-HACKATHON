import { useState, useEffect } from 'react';
import { 
  Code as CodeIcon,
  VerifiedUser as VerifiedUserIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

const SmartContractPanel = ({ transaction }) => {
  const [highlightedLine, setHighlightedLine] = useState(null);
  const [copied, setCopied] = useState(false);
  
  // Simulate highlighting different parts of the contract based on transaction stage
  useEffect(() => {
    if (!transaction) return;
    
    // Highlight different function based on transaction stage
    const lineMap = {
      1: 7, // detectAnomalies function
      2: 11, // calculateRiskScore function
      3: 15, // verifyTransaction function
      4: 19, // logToBlockchain function
    };
    
    setHighlightedLine(lineMap[transaction.stage] || null);
    
    // If stage changed, simulate contract function calls
    const timer = setTimeout(() => {
      // Move to next highlighted line within current function
      setHighlightedLine(prev => prev ? prev + 1 : null);
    }, 2000);
    
    return () => clearTimeout(timer);
  }, [transaction]);
  
  const handleCopyCode = () => {
    navigator.clipboard.writeText(contractCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  // Simulated smart contract code
  const contractCode = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FraudDetection {
    address public owner;
    mapping(bytes32 => bool) public verifiedTransactions;
    
    event AnomalyDetected(bytes32 txHash, uint256 riskScore, uint256 timestamp);
    event TransactionVerified(bytes32 txHash, bool isLegitimate, uint256 timestamp);
    
    constructor() {
        owner = msg.sender;
    }
    
    function detectAnomalies(bytes32 txHash, uint256 amount, address sender, address recipient) 
        public returns (uint256) 
    {
        // ML model integration happens off-chain
        // This function receives the risk assessment result
        uint256 riskScore = calculateRiskScore(txHash, amount);
        emit AnomalyDetected(txHash, riskScore, block.timestamp);
        return riskScore;
    }
    
    function calculateRiskScore(bytes32 txHash, uint256 amount) internal pure returns (uint256) {
        // Simplified risk calculation for demo
        // In production, this would use results from off-chain ML
        return (uint256(uint8(txHash[0])) * amount) % 100;
    }
    
    function verifyTransaction(bytes32 txHash, uint256 riskScore, bool manualApproval) 
        public returns (bool) 
    {
        require(msg.sender == owner, "Only owner can verify transactions");
        bool isLegitimate = riskScore < 70 || manualApproval;
        verifiedTransactions[txHash] = isLegitimate;
        emit TransactionVerified(txHash, isLegitimate, block.timestamp);
        return isLegitimate;
    }
    
    function logToBlockchain(bytes32 txHash, string memory ipfsHash) public {
        require(msg.sender == owner, "Only owner can log to blockchain");
        require(verifiedTransactions[txHash], "Transaction must be verified first");
        // Store IPFS hash containing full transaction details
        // This creates an immutable audit trail
        emit TransactionLogged(txHash, ipfsHash, block.timestamp);
    }
    
    event TransactionLogged(bytes32 txHash, string ipfsHash, uint256 timestamp);
}`;

  // Split code into lines for rendering with highlighting
  const codeLines = contractCode.split('\n');
  
  // Determine which function is currently active based on transaction stage
  const getActiveFunction = () => {
    if (!transaction) return null;
    
    const functionMap = {
      1: 'detectAnomalies',
      2: 'calculateRiskScore',
      3: 'verifyTransaction',
      4: 'logToBlockchain'
    };
    
    return functionMap[transaction.stage] || null;
  };
  
  const activeFunction = getActiveFunction();
  
  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <CodeIcon style={{ marginRight: '8px' }} />
          Smart Contract Interaction
        </h3>
        
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {activeFunction && (
            <div className="active-function">
              <VerifiedUserIcon fontSize="small" style={{ marginRight: '4px' }} />
              <span>Active: {activeFunction}()</span>
            </div>
          )}
          
          <button 
            className="copy-btn" 
            onClick={handleCopyCode} 
            title="Copy code"
          >
            <CopyIcon fontSize="small" />
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>
      
      <div className="contract-panel">
        <pre className="contract-code">
          {codeLines.map((line, index) => (
            <div 
              key={index} 
              className={`code-line ${highlightedLine === index + 1 ? 'highlight' : ''}`}
            >
              <span className="line-number">{index + 1}</span>
              <span className="line-content">{line}</span>
            </div>
          ))}
        </pre>
      </div>
      
      <div className="contract-info">
        <p>
          <strong>Network:</strong> Ethereum (Goerli Testnet)
        </p>
        <p>
          <strong>Contract Address:</strong> 0x9876...4321
        </p>
        <p>
          <strong>Last Interaction:</strong> {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default SmartContractPanel; 