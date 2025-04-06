import { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Button,
  IconButton,
  Card,
  CardContent,
  Stack
} from '@mui/material';
import {
  Security as SecurityIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Timeline as TimelineIcon,
  Visibility as VisibilityIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import React from 'react';

// Format currency in INR
const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '₹0.00';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(amount);
};

const COLORS = ['#4caf50', '#f44336', '#FFBB28', '#FF8042', '#8884d8'];

// Generate risk score for visualization
const getRiskScore = (transactions) => {
  if (!transactions || transactions.length === 0) return 85;
  
  const blockedCount = transactions.filter(tx => tx.status === 'BLOCKED').length;
  const totalCount = transactions.length;
  
  // Higher score is better (less fraud)
  const baseScore = 85;
  
  if (totalCount === 0) return baseScore;
  
  // Reduce score based on percentage of blocked transactions
  const fraudPercentage = (blockedCount / totalCount) * 100;
  return Math.max(60, Math.min(98, baseScore - (fraudPercentage * 2)));
};

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [stats, setStats] = useState({
    totalTransactions: 0,
    successfulTransactions: 0,
    blockedTransactions: 0,
    totalAmount: 0,
    averageAmount: 0,
    riskScore: 85
  });
  const [chartData, setChartData] = useState([]);
  const [pieData, setPieData] = useState([]);
  const [activeTimeFilter, setActiveTimeFilter] = useState("24h");
  const [transactions, setTransactions] = useState([]);
  
  const navigate = useNavigate();
  
  // Load transaction data directly
  useEffect(() => {
    const loadData = async () => {
      try {
        console.log("Loading transaction data...");
        setLoading(true);
        const { getTransactionHistory } = await import('../utils/metamask');
        const txData = await getTransactionHistory();
        console.log("Loaded transaction data:", txData?.length || 0);
        setTransactions(txData || []);
        
        // Initially filter data based on default time filter
        const filtered = filterTransactionsByTime(txData || [], activeTimeFilter);
        processTransactionData(filtered);
      } catch (err) {
        console.error("Error loading transaction data:", err);
        setError("Failed to load transaction data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
    
    // Set a safety timer to make sure loading stops
    const safetyTimer = setTimeout(() => {
      setLoading(false);
    }, 3000);
    
    return () => clearTimeout(safetyTimer);
  }, []);
  
  // Add time filter effect
  useEffect(() => {
    // When time filter changes, filter transactions and update data
    console.log(`Filtering transactions for time period: ${activeTimeFilter}`);
    const filtered = filterTransactionsByTime(transactions, activeTimeFilter);
    processTransactionData(filtered);
  }, [activeTimeFilter, transactions]);
  
  // Function to filter transactions by time
  const filterTransactionsByTime = (txList, timeFilter) => {
    if (!txList || txList.length === 0) return [];
    
    const now = new Date();
    let cutoffDate = new Date();
    
    switch (timeFilter) {
      case '24h':
        cutoffDate.setDate(now.getDate() - 1);
        break;
      case '7d':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        cutoffDate.setDate(now.getDate() - 30);
        break;
      case '1y':
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        cutoffDate.setDate(now.getDate() - 1); // Default to 24h
    }
    
    return txList.filter(tx => {
      try {
        const txDate = new Date(tx.timestamp);
        return txDate >= cutoffDate;
      } catch (e) {
        console.error("Error filtering transaction date:", e);
        return false;
      }
    });
  };
  
  // Process transaction data into stats, charts, and activity
  const processTransactionData = (txData) => {
    if (!txData || txData.length === 0) {
      setDefaultEmptyState();
      return;
    }
    
    try {
      // Calculate basic stats
      const totalTx = txData.length;
      const successfulTx = txData.filter(tx => tx.status === 'SUCCESS').length;
      const blockedTx = txData.filter(tx => tx.status === 'BLOCKED').length;
      
      // Calculate amounts
      const validAmounts = txData
        .map(tx => parseFloat(tx.amount || tx.value || 0))
        .filter(amount => !isNaN(amount));
      
      const totalAmount = validAmounts.reduce((sum, amount) => sum + amount, 0);
      const avgAmount = validAmounts.length > 0 ? totalAmount / validAmounts.length : 0;
      
      // Set stats
      const updatedStats = {
        totalTransactions: totalTx,
        successfulTransactions: successfulTx,
        blockedTransactions: blockedTx,
        totalAmount,
        averageAmount: avgAmount,
        riskScore: getRiskScore(txData)
      };
      
      setStats(updatedStats);
      
      // Generate pie chart data
      const newPieData = [
        { name: 'Successful', value: successfulTx || 0 },
        { name: 'Blocked', value: blockedTx || 0 }
      ];
      
      setPieData(newPieData);
      
      // Generate chart data for the past week
      const newChartData = generateChartData(txData);
      setChartData(newChartData);
      
      // Process recent activity
      const recentActivity = generateRecentActivity(txData);
      setRecentActivity(recentActivity);
      
    } catch (err) {
      console.error("Error processing transaction data:", err);
      setDefaultEmptyState();
    }
  };
  
  // Set default empty state for all data
  const setDefaultEmptyState = () => {
    setStats({
      totalTransactions: 0,
      successfulTransactions: 0,
      blockedTransactions: 0,
      totalAmount: 0,
      averageAmount: 0,
      riskScore: 85
    });
    
    setRecentActivity([]);
    setPieData([{ name: 'No Data', value: 1 }]);
    
    // Empty chart data for the past week
    const emptyChartData = Array(7).fill().map((_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return {
        date: date.toLocaleDateString('en-US', { weekday: 'short' }),
        value: 0,
        blocked: 0
      };
    });
    
    setChartData(emptyChartData);
  };
  
  // Generate chart data from transactions
  const generateChartData = (transactions) => {
    // Different time scales based on the filter
    const timeScale = activeTimeFilter;
    
    if (timeScale === '24h' || timeScale === '7d') {
      // Daily view for 24h and 7d
      return generateDailyChartData(transactions, timeScale === '24h' ? 1 : 7);
    } else if (timeScale === '30d') {
      // Weekly view for 30d
      return generateWeeklyChartData(transactions);
    } else {
      // Monthly view for 1y
      return generateMonthlyChartData(transactions);
    }
  };
  
  // Daily chart data (for 24h and 7d)
  const generateDailyChartData = (transactions, days = 7) => {
    const dataPoints = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      dataPoints.push({
        date: date.toLocaleDateString('en-US', { weekday: 'short' }),
        value: 0,
        blocked: 0,
        rawDate: new Date(date)
      });
    }
    
    // Populate with actual transaction data
    transactions.forEach(tx => {
      try {
        const txDate = new Date(tx.timestamp);
        
        // Skip if date is invalid
        if (isNaN(txDate.getTime())) return;
        
        // Find the right day
        const matchingDay = dataPoints.find(point => {
          return point.rawDate.getDate() === txDate.getDate() && 
                 point.rawDate.getMonth() === txDate.getMonth() &&
                 point.rawDate.getFullYear() === txDate.getFullYear();
        });
        
        if (matchingDay) {
          const amountValue = parseFloat(tx.amount || tx.value || 0);
          
          if (tx.status === 'BLOCKED') {
            matchingDay.blocked += amountValue;
          } else {
            matchingDay.value += amountValue;
          }
        }
      } catch (err) {
        console.error("Error processing transaction for chart:", err);
      }
    });
    
    return dataPoints.map(point => ({
      date: point.date,
      value: point.value,
      blocked: point.blocked
    }));
  };
  
  // Weekly chart data (for 30d)
  const generateWeeklyChartData = (transactions) => {
    const weeks = [];
    const today = new Date();
    
    // Create 4 weekly data points
    for (let i = 4; i >= 0; i--) {
      const weekStart = new Date(today);
      weekStart.setDate(today.getDate() - (i * 7));
      
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      
      weeks.push({
        date: `W${5-i}`,
        label: `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { day: 'numeric' })}`,
        startDate: new Date(weekStart),
        endDate: new Date(weekEnd),
        value: 0,
        blocked: 0
      });
    }
    
    // Populate with actual transaction data
    transactions.forEach(tx => {
      try {
        const txDate = new Date(tx.timestamp);
        
        // Skip if date is invalid
        if (isNaN(txDate.getTime())) return;
        
        // Find the right week
        const matchingWeek = weeks.find(week => 
          txDate >= week.startDate && txDate <= week.endDate
        );
        
        if (matchingWeek) {
          const amountValue = parseFloat(tx.amount || tx.value || 0);
          
          if (tx.status === 'BLOCKED') {
            matchingWeek.blocked += amountValue;
          } else {
            matchingWeek.value += amountValue;
          }
        }
      } catch (err) {
        console.error("Error processing transaction for weekly chart:", err);
      }
    });
    
    return weeks.map(week => ({
      date: week.label,
      value: week.value,
      blocked: week.blocked
    }));
  };
  
  // Monthly chart data (for 1y)
  const generateMonthlyChartData = (transactions) => {
    const months = [];
    const today = new Date();
    
    // Create 12 monthly data points
    for (let i = 11; i >= 0; i--) {
      const monthDate = new Date(today.getFullYear(), today.getMonth() - i, 1);
      
      const monthEnd = new Date(monthDate);
      monthEnd.setMonth(monthEnd.getMonth() + 1);
      monthEnd.setDate(0); // Last day of the month
      
      months.push({
        date: monthDate.toLocaleDateString('en-US', { month: 'short' }),
        startDate: new Date(monthDate),
        endDate: new Date(monthEnd),
        value: 0,
        blocked: 0
      });
    }
    
    // Populate with actual transaction data
    transactions.forEach(tx => {
      try {
        const txDate = new Date(tx.timestamp);
        
        // Skip if date is invalid
        if (isNaN(txDate.getTime())) return;
        
        // Find the right month
        const matchingMonth = months.find(month => 
          txDate >= month.startDate && txDate <= month.endDate
        );
        
        if (matchingMonth) {
          const amountValue = parseFloat(tx.amount || tx.value || 0);
          
          if (tx.status === 'BLOCKED') {
            matchingMonth.blocked += amountValue;
          } else {
            matchingMonth.value += amountValue;
          }
        }
      } catch (err) {
        console.error("Error processing transaction for monthly chart:", err);
      }
    });
    
    return months.map(month => ({
      date: month.date,
      value: month.value,
      blocked: month.blocked
    }));
  };
  
  // Generate recent activity from transactions
  const generateRecentActivity = (transactions) => {
    // Sort transactions by timestamp
    const sortedTx = [...transactions].sort((a, b) => {
      try {
        return new Date(b.timestamp) - new Date(a.timestamp);
      } catch (error) {
        console.error("Error sorting transactions:", error);
        return 0;
      }
    });
    
    // Take the 5 most recent
    return sortedTx.slice(0, 5).map(tx => {
      try {
        return {
          id: tx.id || tx.hash || `tx-${Math.random().toString(16).slice(2)}`,
          type: tx.status === 'BLOCKED' ? 'blocked' : 'success',
          title: tx.status === 'BLOCKED' ? 'Fraud Prevented' : 'Transaction Completed',
          message: `${tx.status === 'BLOCKED' ? 'Blocked' : 'Sent'} ${formatCurrency(tx.amount || tx.value || 0)} to ${(tx.receiver || tx.to || "").substring(0, 8) || 'unknown'}...`,
          timestamp: tx.timestamp
        };
      } catch (error) {
        console.error("Error processing transaction for activity:", error);
        return {
          id: `error-${Math.random().toString(16).slice(2)}`,
          type: 'success', 
          title: 'Transaction',
          message: 'Transaction details unavailable',
          timestamp: new Date().toISOString()
        };
      }
    });
  };
  
  const goToTransactionAnalysis = () => {
    navigate('/analysis');
  };
  
  const handleTimeFilterClick = (filter) => {
    setActiveTimeFilter(filter);
  };

  return (
    <Layout title="Dashboard">
      <Box sx={{ p: { xs: 1, md: 3 }, backgroundColor: '#f7f9fc', width: '100%', maxWidth: '100%' }}>
        {/* Page Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, px: 2 }}>
          <Typography variant="h5" component="h1">
            Fraud Detection Dashboard
          </Typography>
          
          {/* Time filter options like in Transaction Analysis page */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton sx={{ mr: 1 }}>
              <FilterListIcon />
            </IconButton>
            <Stack direction="row" spacing={1}>
              {["24h", "7d", "30d", "1y"].map((filter) => (
                <Button 
                  key={filter}
                  variant={activeTimeFilter === filter ? "contained" : "outlined"}
                  size="small"
                  onClick={() => handleTimeFilterClick(filter)}
                  sx={{
                    borderRadius: '20px',
                    backgroundColor: activeTimeFilter === filter ? '#5e72e4' : 'transparent',
                    borderColor: activeTimeFilter === filter ? '#5e72e4' : '#ddd',
                    color: activeTimeFilter === filter ? 'white' : '#777',
                    '&:hover': {
                      backgroundColor: activeTimeFilter === filter ? '#4c5fd5' : '#f1f3fa'
                    }
                  }}
                >
                  {filter}
                </Button>
              ))}
            </Stack>
          </Box>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3, mt: 2, mx: 2 }}>
            {error}
          </Alert>
        )}
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Stats Cards */}
            <Grid container spacing={2} sx={{ mb: 3, px: 1 }}>
              {/* 1. Total Transactions */}
              <Grid item xs={12} sm={6} lg={3}>
                <Card elevation={1} sx={{ borderRadius: '10px', height: '100%' }}>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Total Transactions
                    </Typography>
                    <Typography variant="h4" sx={{ mb: 1, fontWeight: 'medium' }}>
                      {stats.totalTransactions}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        size="small" 
                        label={`${stats.successfulTransactions} Successful`} 
                        color="success"
                        sx={{ fontSize: '0.75rem' }}
                      />
                      <Chip 
                        size="small" 
                        label={`${stats.blockedTransactions} Blocked`} 
                        color="error" 
                        sx={{ fontSize: '0.75rem' }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* 2. Average Transaction Value */}
              <Grid item xs={12} sm={6} lg={3}>
                <Card elevation={1} sx={{ borderRadius: '10px', height: '100%' }}>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Average Transaction Value
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 'medium' }}>
                      {formatCurrency(stats.averageAmount)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* 3. Transaction Volume */}
              <Grid item xs={12} sm={6} lg={3}>
                <Card elevation={1} sx={{ borderRadius: '10px', height: '100%' }}>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Transaction Volume
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 'medium' }}>
                      {formatCurrency(stats.totalAmount)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* 4. ML Protection Status */}
              <Grid item xs={12} sm={6} lg={3}>
                <Card elevation={1} sx={{ 
                  borderRadius: '10px',
                  height: '100%',
                  backgroundColor: '#5e72e4',
                  color: 'white'
                }}>
                  <CardContent sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <SecurityIcon fontSize="small" />
                      <Typography variant="body2">
                        ML Protection
                      </Typography>
                    </Box>
                    <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
                      Active
                    </Typography>
                    <Button 
                      variant="contained" 
                      size="small"
                      startIcon={<VisibilityIcon />}
                      onClick={goToTransactionAnalysis}
                      sx={{ 
                        mt: 'auto',
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        '&:hover': {
                          backgroundColor: 'rgba(255,255,255,0.3)'
                        }
                      }}
                    >
                      View Analysis
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            {/* Charts */}
            <Grid container spacing={2} sx={{ mb: 3, mx: 0, width: '100%' }}>
              <Grid item xs={12} lg={8} sx={{ width: '100%' }}>
                <Card elevation={1} sx={{ borderRadius: '10px', width: '100%' }}>
                  <CardContent sx={{ p: { xs: 1, md: 2 }, width: '100%' }}>
                    <Typography variant="h6" gutterBottom sx={{ px: 1 }}>
                      Transaction Volume
                    </Typography>
                    <Box sx={{ 
                      width: '100%', 
                      height: { xs: 300, md: 350 },
                      position: 'relative',
                      overflowX: 'visible',
                      overflowY: 'visible',
                      '& .recharts-wrapper': {
                        width: '100% !important'
                      }
                    }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={chartData}
                          margin={{
                            top: 5,
                            right: 10,
                            left: 10,
                            bottom: 5,
                          }}
                        >
                          <defs>
                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#5e72e4" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#5e72e4" stopOpacity={0.1}/>
                            </linearGradient>
                            <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#f5365c" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#f5365c" stopOpacity={0.1}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis dataKey="date" stroke="#999" />
                          <YAxis 
                            tickFormatter={(value) => 
                              new Intl.NumberFormat('en-IN', { 
                                style: 'currency', 
                                currency: 'INR',
                                notation: 'compact',
                                maximumFractionDigits: 1
                              }).format(value)
                            } 
                            stroke="#999"
                          />
                          <Tooltip 
                            formatter={(value) => [
                              formatCurrency(value), 
                              "Volume"
                            ]}
                            contentStyle={{
                              backgroundColor: '#fff',
                              border: '1px solid #f0f0f0',
                              borderRadius: '4px',
                              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                            }}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="value" 
                            stackId="1" 
                            stroke="#5e72e4" 
                            fillOpacity={1}
                            fill="url(#colorValue)" 
                            name="Successful" 
                          />
                          <Area 
                            type="monotone" 
                            dataKey="blocked" 
                            stackId="1" 
                            stroke="#f5365c" 
                            fillOpacity={1}
                            fill="url(#colorBlocked)" 
                            name="Blocked" 
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} lg={4} sx={{ width: '100%' }}>
                <Card elevation={1} sx={{ borderRadius: '10px', width: '100%' }}>
                  <CardContent sx={{ p: { xs: 1, md: 2 }, width: '100%' }}>
                    <Typography variant="h6" gutterBottom sx={{ px: 1 }}>
                      Success Rate
                    </Typography>
                    <Box sx={{ 
                      height: { xs: 300, md: 350 },
                      width: '100%',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      position: 'relative',
                      '& .recharts-wrapper': {
                        width: '100% !important'
                      }
                    }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius={70}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {pieData.map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={index === 0 ? '#2dce89' : '#f5365c'} 
                              />
                            ))}
                          </Pie>
                          <Tooltip 
                            formatter={(value) => [`${value} transactions`, '']}
                            contentStyle={{
                              backgroundColor: '#fff',
                              border: '1px solid #f0f0f0',
                              borderRadius: '4px',
                              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            {/* Recent Activity */}
            <Card elevation={1} sx={{ borderRadius: '10px', mx: 2 }}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, px: 1 }}>
                  Transaction History
                </Typography>
                
                {recentActivity.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                    No transactions found
                  </Typography>
                ) : (
                  <List>
                    {recentActivity.map((activity, index) => (
                      <Box key={activity.id}>
                        {index > 0 && <Divider component="li" />}
                        <ListItem sx={{ py: 2 }}>
                          <ListItemIcon sx={{ minWidth: 40 }}>
                            {activity.type === 'blocked' ? (
                              <ErrorIcon color="error" fontSize="small" />
                            ) : (
                              <CheckCircleIcon color="success" fontSize="small" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={activity.message}
                            secondary={new Date(activity.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                            primaryTypographyProps={{ 
                              variant: 'body2', 
                              style: { fontWeight: 500 }
                            }}
                            secondaryTypographyProps={{ 
                              variant: 'caption', 
                              style: { color: '#999' } 
                            }}
                          />
                          <Chip 
                            label={activity.type === 'blocked' ? 'Blocked' : 'Success'} 
                            size="small"
                            sx={{ 
                              borderRadius: '12px',
                              backgroundColor: activity.type === 'blocked' ? '#fff5f7' : '#f6fff9',
                              color: activity.type === 'blocked' ? '#f5365c' : '#2dce89',
                              border: activity.type === 'blocked' ? '1px solid #f5365c' : '1px solid #2dce89',
                              fontWeight: 500,
                              fontSize: '0.7rem'
                            }}
                          />
                        </ListItem>
                      </Box>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </Box>
    </Layout>
  );
};

export default Dashboard;