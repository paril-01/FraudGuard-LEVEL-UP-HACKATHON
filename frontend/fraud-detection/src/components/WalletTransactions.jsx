import { useState, useEffect } from 'react';
import { 
  Search as SearchIcon, 
  Refresh as RefreshIcon, 
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Help as HelpIcon,
  LocalPolice as ProtectIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { 
  getTransactionHistory,
  getWalletAddress
} from '../utils/metamask';

const WalletTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analyzeLoading, setAnalyzeLoading] = useState({});
  const [analyzedResults, setAnalyzedResults] = useState({});
  const [walletAddress, setWalletAddress] = useState('');
  
  useEffect(() => {
    fetchTransactions();
    setWalletAddress(getWalletAddress() || '');
  }, []);
  
  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const txs = await getTransactionHistory();
      setTransactions(txs);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setError(error.message || 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAnalyzeTransaction = async (txHash) => {
    setAnalyzeLoading(prev => ({ ...prev, [txHash]: true }));
    
    try {
      // Simulate analysis with mock data
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const result = {
        riskScore: Math.floor(Math.random() * 100),
        recommendation: "This transaction appears to be legitimate based on our analysis.",
        riskFactors: [
          {
            name: "Destination Address",
            description: "The destination address has a good reputation.",
            impact: "low"
          },
          {
            name: "Transaction Amount",
            description: "The transaction amount is within normal range for this account.",
            impact: "low"
          },
          {
            name: "Transaction Frequency",
            description: "The transaction timing matches historical patterns.",
            impact: "low"
          }
        ]
      };
      
      // Customize based on random risk score
      if (result.riskScore > 80) {
        result.recommendation = "This transaction shows high-risk patterns. We recommend additional verification.";
        result.riskFactors = [
          {
            name: "Destination Address",
            description: "The destination address is associated with known scams.",
            impact: "high"
          },
          {
            name: "Transaction Amount",
            description: "The transaction amount is unusually high for this account.",
            impact: "high"
          },
          {
            name: "Transaction Frequency",
            description: "Multiple transactions in a short time period.",
            impact: "medium"
          }
        ];
      } else if (result.riskScore > 50) {
        result.recommendation = "This transaction shows some unusual patterns. Consider verifying before proceeding.";
        result.riskFactors = [
          {
            name: "Destination Address",
            description: "The destination address is new with limited history.",
            impact: "medium"
          },
          {
            name: "Transaction Pattern",
            description: "This transaction differs from your usual activity.",
            impact: "medium"
          },
          {
            name: "Network Activity",
            description: "Normal network behavior observed.",
            impact: "low"
          }
        ];
      }
      
      setAnalyzedResults(prev => ({ ...prev, [txHash]: result }));
    } catch (error) {
      console.error('Error analyzing transaction:', error);
      // Set an error result
      setAnalyzedResults(prev => ({ 
        ...prev, 
        [txHash]: { error: error.message || 'Analysis failed' } 
      }));
    } finally {
      setAnalyzeLoading(prev => ({ ...prev, [txHash]: false }));
    }
  };
  
  const formatAddress = (address, length = 6) => {
    if (!address) return '';
    return `${address.substring(0, length)}...${address.substring(address.length - 4)}`;
  };
  
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  const formatAmount = (amountWei) => {
    if (!amountWei) return '0 ETH';
    // Convert Wei to ETH
    const amountEth = parseFloat(amountWei) / 1e18;
    return `${amountEth.toFixed(6)} ETH`;
  };
  
  const getRiskClass = (riskScore) => {
    if (riskScore === undefined || riskScore === null) return '';
    if (riskScore > 80) return 'high-risk';
    if (riskScore > 50) return 'medium-risk';
    return 'low-risk';
  };
  
  return (
    <div className="wallet-transactions-container">
      <div className="wallet-header">
        <div className="wallet-info">
          <h2>Blockchain Transactions</h2>
          <p className="wallet-address">
            <ProtectIcon /> Connected Wallet: {formatAddress(walletAddress, 10)}
          </p>
        </div>
        <button className="refresh-btn" onClick={fetchTransactions} disabled={loading}>
          <RefreshIcon /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      
      {error && (
        <div className="error-alert">
          <ErrorIcon /> {error}
        </div>
      )}
      
      <div className="transaction-filter">
        <div className="search-box">
          <SearchIcon />
          <input type="text" placeholder="Search transactions" />
        </div>
        <div className="filter-info">
          <TimelineIcon />
          <span>Showing the last {transactions.length} transactions</span>
        </div>
      </div>
      
      <div className="transactions-table-container">
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Transaction Hash</th>
              <th>From</th>
              <th>To</th>
              <th>Amount</th>
              <th>Timestamp</th>
              <th>Risk Analysis</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 && !loading ? (
              <tr>
                <td colSpan="7" className="no-transactions">
                  No transactions found. Try refreshing or connecting a different wallet.
                </td>
              </tr>
            ) : (
              transactions.map(tx => (
                <tr key={tx.hash}>
                  <td className="hash-cell">
                    <span className="tx-hash" title={tx.hash}>{formatAddress(tx.hash, 8)}</span>
                  </td>
                  <td>
                    <span className="address" title={tx.from}>{formatAddress(tx.from)}</span>
                  </td>
                  <td>
                    <span className="address" title={tx.to}>{formatAddress(tx.to)}</span>
                  </td>
                  <td className={tx.isOutgoing ? 'amount-out' : 'amount-in'}>
                    {tx.isOutgoing ? '- ' : '+ '}{formatAmount(tx.value)}
                  </td>
                  <td>{formatTimestamp(tx.timestamp)}</td>
                  <td>
                    {analyzedResults[tx.hash] ? (
                      <div className={`risk-badge ${getRiskClass(analyzedResults[tx.hash].riskScore)}`}>
                        {analyzedResults[tx.hash].error ? (
                          <span className="analysis-error" title={analyzedResults[tx.hash].error}>
                            <ErrorIcon /> Error
                          </span>
                        ) : (
                          <>
                            {analyzedResults[tx.hash].riskScore > 80 ? (
                              <ErrorIcon />
                            ) : analyzedResults[tx.hash].riskScore > 50 ? (
                              <HelpIcon />
                            ) : (
                              <CheckCircleIcon />
                            )}
                            <span>{analyzedResults[tx.hash].riskScore}/100</span>
                          </>
                        )}
                      </div>
                    ) : (
                      <span className="not-analyzed">Not analyzed</span>
                    )}
                  </td>
                  <td>
                    <button 
                      className="analyze-btn"
                      onClick={() => handleAnalyzeTransaction(tx.hash)}
                      disabled={analyzeLoading[tx.hash]}
                    >
                      {analyzeLoading[tx.hash] ? 'Analyzing...' : 'Analyze'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {analyzedResults && Object.keys(analyzedResults).length > 0 && (
        <div className="analysis-details">
          <h3>Analysis Details</h3>
          {Object.entries(analyzedResults).map(([hash, result]) => (
            !result.error && (
              <div key={hash} className={`analysis-card ${getRiskClass(result.riskScore)}`}>
                <div className="analysis-header">
                  <div className="analysis-tx-hash" title={hash}>{formatAddress(hash, 10)}</div>
                  <div className={`analysis-score ${getRiskClass(result.riskScore)}`}>
                    Risk Score: {result.riskScore}/100
                  </div>
                </div>
                <div className="analysis-recommendation">
                  {result.recommendation}
                </div>
                <div className="risk-factors">
                  <h4>Risk Factors:</h4>
                  <ul>
                    {result.riskFactors.map((factor, index) => (
                      <li key={index} className={`risk-factor ${factor.impact}`}>
                        <span className="risk-factor-name">{factor.name}</span>
                        <span className="risk-factor-description">{factor.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )
          ))}
        </div>
      )}
    </div>
  );
};

export default WalletTransactions; 