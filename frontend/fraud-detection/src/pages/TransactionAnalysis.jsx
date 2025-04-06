import { useState, useEffect, useCallback } from 'react';
import { 
  Tabs, 
  Tab, 
  Card, 
  CardContent, 
  TextField, 
  Button, 
  Grid, 
  CircularProgress, 
  Alert,
  Divider,
  Tooltip,
  IconButton,
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  InputAdornment
} from '@mui/material';
import {
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer
} from 'recharts';
import {
  Payment as PaymentIcon,
  LockOutlined as LockIcon,
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { getTransactionHistory } from '../utils/metamask';
import { useNotifications } from '../context/NotificationContext';
import { useTransactions } from '../context/TransactionContext';

const TransactionAnalysis = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeframe, setTimeframe] = useState('week');
  const [formData, setFormData] = useState({
    transactionId: '',
    amount: '',
    sender: '',
    recipient: '',
  });
  const [prediction, setPrediction] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [advancedAnalysis, setAdvancedAnalysis] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [fraudMetrics, setFraudMetrics] = useState({
    totalScanned: 0,
    fraudDetected: 0,
    amountSaved: 0,
    fraudRate: 0
  });
  
  const notificationContext = useNotifications();
  const addNotification = notificationContext ? notificationContext.addNotification : () => {};
  
  const { transactions, loading: txLoading, error: txError, forceRefresh } = useTransactions();
  
  // Update loading and error states from transaction context
  useEffect(() => {
    setLoading(txLoading);
    if (txError) {
      setError(txError);
    }
  }, [txLoading, txError]);
  
  // Listen for transaction update events
  useEffect(() => {
    const handleTransactionUpdate = (event) => {
      console.log('TransactionAnalysis received transaction update:', event.detail);
      forceRefresh();
      
      // Update the UI immediately with the new transaction
      if (event.detail && event.detail.transaction) {
        const tx = event.detail.transaction;
        
        // Update fraud metrics immediately
        setFraudMetrics(prev => {
          const newMetrics = { ...prev };
          newMetrics.totalScanned += 1;
          
          if (tx.status === 'BLOCKED') {
            newMetrics.fraudDetected += 1;
            newMetrics.amountSaved += tx.value || 0;
          }
          
          newMetrics.fraudRate = (newMetrics.fraudDetected / newMetrics.totalScanned) * 100;
          
          return newMetrics;
        });
      }
    };
    
    // Listen for custom transaction update events
    window.addEventListener('transaction-update', handleTransactionUpdate);
    
    return () => {
      window.removeEventListener('transaction-update', handleTransactionUpdate);
    };
  }, [forceRefresh]);
  
  // Calculate fraud metrics whenever transactions change
  useEffect(() => {
    calculateFraudMetrics(transactions);
  }, [transactions]);
  
  // Daily data
  const [dailyVolumeData, setDailyVolumeData] = useState([
    { name: '00:00', amount: 3200 },
    { name: '04:00', amount: 1800 },
    { name: '08:00', amount: 4500 },
    { name: '12:00', amount: 7800 },
    { name: '16:00', amount: 6200 },
    { name: '20:00', amount: 4100 }
  ]);

  const [dailySuccessRateData, setDailySuccessRateData] = useState([
    { name: '00:00', rate: 95 },
    { name: '04:00', rate: 97 },
    { name: '08:00', rate: 96 },
    { name: '12:00', rate: 98 },
    { name: '16:00', rate: 99 },
    { name: '20:00', rate: 97 }
  ]);

  const [dailyFraudCategoryData, setDailyFraudCategoryData] = useState([
    { name: 'Identity Theft', value: 22 },
    { name: 'Account Takeover', value: 18 },
    { name: 'Transaction Fraud', value: 30 },
    { name: 'Card Testing', value: 20 },
    { name: 'Others', value: 10 }
  ]);

  const [dailyRiskFactorData, setDailyRiskFactorData] = useState([
    { name: 'IP Location', score: 2.8 },
    { name: 'Transaction Pattern', score: 5.2 },
    { name: 'Amount', score: 3.1 },
    { name: 'Time of Day', score: 2.5 },
    { name: 'Device Trust', score: 4.1 }
  ]);

  // Weekly data
  const [weeklyVolumeData, setWeeklyVolumeData] = useState([
    { name: 'Monday', amount: 12400 },
    { name: 'Tuesday', amount: 14800 },
    { name: 'Wednesday', amount: 17800 },
    { name: 'Thursday', amount: 15200 },
    { name: 'Friday', amount: 21000 },
    { name: 'Saturday', amount: 8500 },
    { name: 'Sunday', amount: 9300 }
  ]);

  const [weeklySuccessRateData, setWeeklySuccessRateData] = useState([
    { name: 'Monday', rate: 97 },
    { name: 'Tuesday', rate: 98 },
    { name: 'Wednesday', rate: 95 },
    { name: 'Thursday', rate: 99 },
    { name: 'Friday', rate: 96 },
    { name: 'Saturday', rate: 98 },
    { name: 'Sunday', rate: 97 }
  ]);

  const [weeklyFraudCategoryData, setWeeklyFraudCategoryData] = useState([
    { name: 'Identity Theft', value: 35 },
    { name: 'Account Takeover', value: 25 },
    { name: 'Transaction Fraud', value: 20 },
    { name: 'Card Testing', value: 15 },
    { name: 'Others', value: 5 }
  ]);

  const [weeklyRiskFactorData, setWeeklyRiskFactorData] = useState([
    { name: 'IP Location', score: 3.2 },
    { name: 'Transaction Pattern', score: 4.5 },
    { name: 'Amount', score: 2.8 },
    { name: 'Time of Day', score: 1.5 },
    { name: 'Device Trust', score: 3.9 }
  ]);

  // Monthly data
  const [monthlyVolumeData, setMonthlyVolumeData] = useState([
    { name: 'Week 1', amount: 68000 },
    { name: 'Week 2', amount: 72400 },
    { name: 'Week 3', amount: 81200 },
    { name: 'Week 4', amount: 75300 }
  ]);

  const [monthlySuccessRateData, setMonthlySuccessRateData] = useState([
    { name: 'Week 1', rate: 96 },
    { name: 'Week 2', rate: 97 },
    { name: 'Week 3', rate: 98 },
    { name: 'Week 4', rate: 95 }
  ]);

  const [monthlyFraudCategoryData, setMonthlyFraudCategoryData] = useState([
    { name: 'Identity Theft', value: 30 },
    { name: 'Account Takeover', value: 28 },
    { name: 'Transaction Fraud', value: 22 },
    { name: 'Card Testing', value: 12 },
    { name: 'Others', value: 8 }
  ]);

  const [monthlyRiskFactorData, setMonthlyRiskFactorData] = useState([
    { name: 'IP Location', score: 3.4 },
    { name: 'Transaction Pattern', score: 4.0 },
    { name: 'Amount', score: 3.2 },
    { name: 'Time of Day', score: 1.8 },
    { name: 'Device Trust', score: 3.6 }
  ]);
  
  const COLORS = ['#5c4ee5', '#5e74e5', '#e55e4e', '#e5b64e', '#4ee58e'];

  // Get current data based on selected timeframe
  const getVolumeData = () => {
    switch(timeframe) {
      case 'day': return dailyVolumeData;
      case 'month': return monthlyVolumeData;
      default: return weeklyVolumeData;
    }
  };

  const getSuccessRateData = () => {
    switch(timeframe) {
      case 'day': return dailySuccessRateData;
      case 'month': return monthlySuccessRateData;
      default: return weeklySuccessRateData;
    }
  };

  const getFraudCategoryData = () => {
    switch(timeframe) {
      case 'day': return dailyFraudCategoryData;
      case 'month': return monthlyFraudCategoryData;
      default: return weeklyFraudCategoryData;
    }
  };

  const getRiskFactorData = () => {
    switch(timeframe) {
      case 'day': return dailyRiskFactorData;
      case 'month': return monthlyRiskFactorData;
      default: return weeklyRiskFactorData;
    }
  };

  // Simulate real-time data updates from ML model
  const updateData = useCallback(() => {
    // Update volume data
    const updateVolumeData = (prevData) => {
      return prevData.map(item => ({
        ...item,
        amount: Math.max(1000, item.amount + (Math.random() * 2000 - 1000))
      }));
    };

    // Update success rate data
    const updateSuccessRateData = (prevData) => {
      return prevData.map(item => ({
        ...item,
        rate: Math.min(100, Math.max(90, item.rate + (Math.random() * 4 - 2)))
      }));
    };

    // Update fraud category data
    const updateFraudCategoryData = (prevData) => {
      // Ensure sum remains 100
      let newData = prevData.map(item => ({
        ...item,
        value: Math.max(5, item.value + (Math.random() * 6 - 3))
      }));
      
      const total = newData.reduce((sum, item) => sum + item.value, 0);
      return newData.map(item => ({
        ...item,
        value: Math.round((item.value / total) * 100)
      }));
    };

    // Update risk factor data
    const updateRiskFactorData = (prevData) => {
      return prevData.map(item => ({
        ...item,
        score: Math.max(0.5, Math.min(5, item.score + (Math.random() - 0.5)))
      }));
    };

    // Update data based on timeframe
    if (timeframe === 'day') {
      setDailyVolumeData(updateVolumeData);
      setDailySuccessRateData(updateSuccessRateData);
      setDailyFraudCategoryData(updateFraudCategoryData);
      setDailyRiskFactorData(updateRiskFactorData);
    } else if (timeframe === 'week') {
      setWeeklyVolumeData(updateVolumeData);
      setWeeklySuccessRateData(updateSuccessRateData);
      setWeeklyFraudCategoryData(updateFraudCategoryData);
      setWeeklyRiskFactorData(updateRiskFactorData);
    } else if (timeframe === 'month') {
      setMonthlyVolumeData(updateVolumeData);
      setMonthlySuccessRateData(updateSuccessRateData);
      setMonthlyFraudCategoryData(updateFraudCategoryData);
      setMonthlyRiskFactorData(updateRiskFactorData);
    }
  }, [timeframe]);

  useEffect(() => {
    // Update data initially and set up interval
    updateData();
    
    // Set up interval for real-time updates
    const interval = setInterval(() => {
      updateData();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [timeframe, updateData]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleTimeframeChange = (newTimeframe) => {
    setTimeframe(newTimeframe);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    updateData();
    setTimeout(() => setRefreshing(false), 800);
  };

  const handleAdvancedAnalysisPayment = () => {
    // Directly enable advanced analysis without payment
    setAdvancedAnalysis(true);
    // Proceed with analysis
    handleAnalyzeTransaction(true);
  };

  const handleAnalyzeTransaction = (isAdvanced = false) => {
    setAnalyzing(true);
    // Simulate API call to fraud detection model
    setTimeout(() => {
      // Generate more detailed results for advanced analysis
      const mockResult = {
        riskScore: Math.floor(Math.random() * 100),
        factors: isAdvanced ? [
          { name: 'Transaction Amount', impact: 'high', description: 'Unusually large amount for this account', score: 0.85, confidence: '92%' },
          { name: 'Location Anomaly', impact: 'medium', description: 'Transaction from uncommon location', score: 0.65, confidence: '78%' },
          { name: 'Time Pattern', impact: 'low', description: 'Transaction time is within normal patterns', score: 0.25, confidence: '95%' },
          { name: 'Device Trust', impact: 'medium', description: 'Device fingerprint has some suspicious characteristics', score: 0.55, confidence: '82%' },
          { name: 'Behavioral Biometrics', impact: 'high', description: 'Typing patterns differ from account holder', score: 0.78, confidence: '88%' }
        ] : [
          { name: 'Transaction Amount', impact: 'high', description: 'Unusually large amount for this account' },
          { name: 'Location', impact: 'medium', description: 'Transaction from uncommon location' },
          { name: 'Time Pattern', impact: 'low', description: 'Transaction time is within normal patterns' }
        ],
        advancedAnalysis: isAdvanced,
        networkInsights: isAdvanced ? {
          similarTransactions: 7,
          knownFraudPatterns: 3,
          accountRiskLevel: 'Medium',
          recommendedAction: 'Additional verification required'
        } : null
      };
      setPrediction(mockResult);
      setAnalyzing(false);
    }, 2000);
  };

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const history = await getTransactionHistory();
      if (!history) {
        console.warn('No transaction history returned');
        setTransactions([]);
        calculateFraudMetrics([]);
        return;
      }
      setTransactions(history);
      calculateFraudMetrics(history);
    } catch (err) {
      console.error('Failed to load transaction history:', err);
      setError('Failed to load transaction data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadTransactions();
    
    // Set up interval to refresh data
    const intervalId = setInterval(() => {
      loadTransactions();
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(intervalId);
  }, []);
  
  // Listen for new transaction events
  useEffect(() => {
    const handleNewTransaction = event => {
      if (event.detail && event.detail.type === 'transaction') {
        // Refresh transaction data when a new transaction occurs
        loadTransactions();
        
        // If it was a blocked fraud transaction, show a notification
        if (event.detail.status === 'BLOCKED') {
          addNotification({
            type: 'warning',
            title: 'Fraud Analysis Update',
            message: 'New fraud pattern detected and blocked. View details in Transaction Analysis.',
            timestamp: new Date().toISOString(),
            link: '/transaction-analysis'
          });
        }
      }
    };
    
    window.addEventListener('new-transaction', handleNewTransaction);
    
    return () => {
      window.removeEventListener('new-transaction', handleNewTransaction);
    };
  }, [addNotification]);
  
  const calculateFraudMetrics = (txHistory) => {
    if (!txHistory || txHistory.length === 0) {
      setFraudMetrics({
        totalScanned: 0,
        fraudDetected: 0,
        amountSaved: 0,
        fraudRate: 0
      });
      return;
    }
    
    const totalScanned = txHistory.length;
    const fraudulent = txHistory.filter(tx => tx.status === 'BLOCKED');
    const fraudCount = fraudulent.length;
    const amountSaved = fraudulent.reduce((sum, tx) => sum + (tx.value || 0), 0);
    const fraudRate = totalScanned > 0 ? (fraudCount / totalScanned) * 100 : 0;
    
    setFraudMetrics({
      totalScanned,
      fraudDetected: fraudCount,
      amountSaved,
      fraudRate
    });
  };

  const filteredTransactions = searchTerm 
    ? transactions.filter(tx => 
        tx.hash?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tx.to?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (tx.status && tx.status.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : transactions;
    
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  const handleRowClick = (tx) => {
    setSelectedTransaction(tx);
  };
  
  const getTypologyData = () => {
    const typologies = {
      'Large Amount': 0,
      'Suspicious Address': 0,
      'Unusual Pattern': 0,
      'New Recipient': 0
    };
    
    transactions.forEach(tx => {
      if (tx.indicators) {
        tx.indicators.forEach(indicator => {
          if (indicator.includes('Large transaction')) typologies['Large Amount']++;
          if (indicator.includes('Suspicious wallet')) typologies['Suspicious Address']++;
          if (indicator.includes('Unusual transaction')) typologies['Unusual Pattern']++;
          if (indicator.includes('New recipient')) typologies['New Recipient']++;
        });
      }
    });
    
    return Object.keys(typologies).map(key => ({
      name: key,
      value: typologies[key]
    })).filter(item => item.value > 0);
  };
  
  const getRiskDistribution = () => {
    const distribution = {
      'High': 0,
      'Medium': 0,
      'Low': 0
    };
    
    transactions.forEach(tx => {
      if (tx.riskLevel) {
        distribution[tx.riskLevel]++;
      } else if (tx.securityScore) {
        if (tx.securityScore > 80) distribution['Low']++;
        else if (tx.securityScore > 60) distribution['Medium']++;
        else distribution['High']++;
      }
    });
    
    return Object.keys(distribution).map(key => ({
      name: key,
      value: distribution[key]
    }));
  };
  
  const getTimelineData = () => {
    const timeline = {};
    const now = new Date();
    
    // Create hourly buckets for the last 24 hours
    for (let i = 23; i >= 0; i--) {
      const date = new Date(now);
      date.setHours(date.getHours() - i);
      const hour = date.getHours();
      timeline[hour] = { hour: `${hour}:00`, successful: 0, blocked: 0 };
    }
    
    // Fill with transaction data
    transactions.forEach(tx => {
      const txDate = new Date(tx.timestamp);
      // Only include transactions from the last 24 hours
      if (now - txDate <= 24 * 60 * 60 * 1000) {
        const hour = txDate.getHours();
        if (timeline[hour]) {
          if (tx.status === 'BLOCKED') {
            timeline[hour].blocked++;
          } else {
            timeline[hour].successful++;
          }
        }
      }
    });
    
    return Object.values(timeline);
  };
  
  const downloadCSV = () => {
    if (transactions.length === 0) return;
    
    // Create CSV content
    const headers = ['Transaction Hash', 'From', 'To', 'Amount (INR)', 'Status', 'Timestamp', 'Risk Level', 'Security Score'];
    const csvRows = [headers.join(',')];
    
    transactions.forEach(tx => {
      const row = [
        tx.hash || 'N/A',
        tx.from,
        tx.to,
        tx.value,
        tx.status,
        new Date(tx.timestamp).toLocaleString(),
        tx.riskLevel || 'N/A',
        tx.securityScore || tx.fraudScore || 'N/A'
      ];
      
      csvRows.push(row.join(','));
    });
    
    const csvContent = csvRows.join('\n');
    
    // Create and download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `transaction_analysis_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show notification
    addNotification({
      type: 'success',
      title: 'Export Successful',
      message: 'Transaction analysis data has been exported to CSV.',
      timestamp: new Date().toISOString()
    });
  };

  // Format currency in INR
  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '₹0.00';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(amount);
  };

  // Generate daily transaction data
  const getDailyData = () => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const data = days.map(day => ({ day, successful: 0, blocked: 0 }));
    
    if (!transactions.length) return data;
    
    // Group transactions by day
    transactions.forEach(tx => {
      const date = new Date(tx.timestamp);
      const dayIndex = date.getDay(); // 0 = Sun, 1 = Mon, ...
      const adjustedIndex = dayIndex === 0 ? 6 : dayIndex - 1; // Convert to 0 = Mon, ... 6 = Sun
      
      if (tx.status === 'BLOCKED') {
        data[adjustedIndex].blocked += 1;
      } else {
        data[adjustedIndex].successful += 1;
      }
    });
    
    return data;
  };

  return (
    <Layout title="Transaction Analysis">
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          <Grid container alignItems="center" spacing={1}>
            <Grid item>
              <TimelineIcon color="primary" />
            </Grid>
            <Grid item>
              Transaction Analysis
            </Grid>
          </Grid>
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Analyze transaction patterns and fraud detection results
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {loading && transactions.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Fraud Detection Metrics */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={3} sx={{ p: 2 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Transactions Scanned
                  </Typography>
                  <Typography variant="h5">
                    {fraudMetrics.totalScanned}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                    All transactions are ML scanned
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={3} sx={{ p: 2 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Fraud Transactions Blocked
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {fraudMetrics.fraudDetected}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                    {fraudMetrics.fraudRate.toFixed(1)}% fraud rate
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={3} sx={{ p: 2 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Amount Saved
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {formatCurrency(fraudMetrics.amountSaved)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                    Protected from fraud transactions
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper elevation={3} sx={{ 
                  p: 2, 
                  bgcolor: 'primary.dark',
                  color: 'white',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <SecurityIcon sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      ML Analysis Active
                    </Typography>
                  </Box>
                  <Typography variant="body1">
                    Real-time fraud detection
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
            
            {/* Charts and Tables */}
            <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
              <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
                <Tab label="Transaction Summary" />
                <Tab label="Fraud Analysis" />
              </Tabs>
              
              {activeTab === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Transaction Volume by Day
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getDailyData()} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <RechartsTooltip />
                        <Bar dataKey="successful" name="Successful" fill="#4caf50" />
                        <Bar dataKey="blocked" name="Blocked Fraud" fill="#f44336" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>
              )}
              
              {activeTab === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Fraud Detection Analysis
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Our ML model analyzes each transaction in real-time to detect potential fraud.
                    The model uses pattern recognition to identify suspicious activities and prevent fraudulent transactions.
                  </Typography>
                  
                  <Box sx={{ mb: 2, mt: 3 }}>
                    <TextField
                      placeholder="Search transactions..."
                      size="small"
                      value={searchTerm}
                      onChange={handleSearchChange}
                      fullWidth
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Box>
                  
                  <TableContainer sx={{ maxHeight: 400 }}>
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontSize: '0.8rem' }}>Status</TableCell>
                          <TableCell sx={{ fontSize: '0.8rem' }}>Transaction ID</TableCell>
                          <TableCell sx={{ fontSize: '0.8rem' }}>To</TableCell>
                          <TableCell sx={{ fontSize: '0.8rem' }}>Amount</TableCell>
                          <TableCell sx={{ fontSize: '0.8rem' }}>Time</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filteredTransactions.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={5} align="center">
                              {searchTerm ? 'No matching transactions found' : 'No transactions available'}
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredTransactions.map((tx) => (
                            <TableRow 
                              key={tx.hash || Math.random().toString(16).slice(2)}
                              hover
                            >
                              <TableCell>
                                {tx.status === 'BLOCKED' ? (
                                  <Chip size="small" icon={<ErrorIcon />} label="Blocked" color="error" sx={{ fontSize: '0.7rem' }} />
                                ) : (
                                  <Chip 
                                    size="small" 
                                    icon={<CheckCircleIcon />}
                                    label="Success" 
                                    color="success"
                                    sx={{ fontSize: '0.7rem' }}
                                  />
                                )}
                              </TableCell>
                              <TableCell sx={{ fontSize: '0.8rem' }}>{tx.hash ? `${tx.hash.substring(0, 10)}...` : 'N/A'}</TableCell>
                              <TableCell sx={{ fontSize: '0.8rem' }}>{tx.to ? `${tx.to.substring(0, 10)}...` : 'N/A'}</TableCell>
                              <TableCell sx={{ fontSize: '0.8rem' }}>{formatCurrency(tx.value)}</TableCell>
                              <TableCell sx={{ fontSize: '0.8rem' }}>{new Date(tx.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </Paper>
          </>
        )}
      </Box>
    </Layout>
  );
};

export default TransactionAnalysis; 