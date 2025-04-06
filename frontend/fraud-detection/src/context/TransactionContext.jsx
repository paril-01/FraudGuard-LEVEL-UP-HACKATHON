import { createContext, useContext, useState, useEffect } from 'react';
import { getTransactionHistory } from '../utils/metamask';

// Create transaction context
const TransactionContext = createContext();

// Custom hook to use the transaction context
export const useTransactions = () => {
  return useContext(TransactionContext);
};

// Provider component to wrap around the app
export const TransactionProvider = ({ children }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  // Load transaction data function
  const loadTransactions = async () => {
    try {
      setLoading(true);
      const history = await getTransactionHistory();
      if (!history) {
        console.warn('No transaction history returned');
        setTransactions([]);
        return;
      }
      setTransactions(history);
    } catch (err) {
      console.error('Failed to load transaction history:', err);
      setError('Failed to load transaction data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load and refresh on lastUpdate change
  useEffect(() => {
    loadTransactions();
    
    // Set up interval to refresh data
    const intervalId = setInterval(() => {
      loadTransactions();
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [lastUpdate]);

  // Listen for transaction update events
  useEffect(() => {
    const handleTransactionUpdate = () => {
      // Force refresh the transaction list
      setLastUpdate(Date.now());
    };

    // Listen for custom transaction update events
    window.addEventListener('transaction-update', handleTransactionUpdate);

    return () => {
      window.removeEventListener('transaction-update', handleTransactionUpdate);
    };
  }, []);
  
  // Add a new transaction to the state
  const addTransaction = (transaction) => {
    console.log('Adding transaction to context:', transaction);
    
    // Add the transaction to the state immediately
    setTransactions((prev) => {
      const newTransactions = [transaction, ...prev];
      console.log('Updated transactions:', newTransactions);
      return newTransactions;
    });
    
    // Trigger update across components
    setLastUpdate(Date.now());
  };

  // Force a refresh of transactions
  const forceRefresh = () => {
    console.log('Force refreshing transactions');
    setLastUpdate(Date.now());
  };
  
  // Value object to be provided to context consumers
  const value = {
    transactions,
    loading,
    error,
    addTransaction,
    refreshTransactions: forceRefresh,
    forceRefresh
  };
  
  return (
    <TransactionContext.Provider value={value}>
      {children}
    </TransactionContext.Provider>
  );
};

export default TransactionContext; 