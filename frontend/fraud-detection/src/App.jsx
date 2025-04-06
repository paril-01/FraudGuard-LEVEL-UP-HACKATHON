import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { NotificationProvider } from './context/NotificationContext'
import { TransactionProvider } from './context/TransactionContext'
import { initializeSyntheticData } from './utils/synthetic-transactions'

// Page imports
import Dashboard from './pages/Dashboard'
import BlockchainHub from './pages/BlockchainHub'
import TransactionAnalysis from './pages/TransactionAnalysis'
import TransactionsPage from './pages/Transactions'
import UserManagement from './pages/UserManagement'
import Settings from './pages/Settings'
import Login from './pages/Login'

// Simplified ProtectedRoute component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  // Initialize synthetic transaction data when app starts
  useEffect(() => {
    const initData = async () => {
      try {
        console.log('Initializing synthetic transaction data...');
        await initializeSyntheticData();
        console.log('Synthetic data initialized successfully');
      } catch (error) {
        console.error('Error initializing synthetic data:', error);
      }
    };
    
    initData();
  }, []);

  return (
    <NotificationProvider>
      <TransactionProvider>
        <div className="app-container">
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/blockchain" element={
              <ProtectedRoute>
                <BlockchainHub />
              </ProtectedRoute>
            } />
            
            <Route path="/analysis" element={
              <ProtectedRoute>
                <TransactionAnalysis />
              </ProtectedRoute>
            } />

            <Route path="/transactions" element={
              <ProtectedRoute>
                <TransactionsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/users" element={
              <ProtectedRoute>
                <UserManagement />
              </ProtectedRoute>
            } />
            
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />

            {/* Redirect all other routes to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </TransactionProvider>
    </NotificationProvider>
  )
}

export default App
