import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  Stepper, 
  Step, 
  StepLabel,
  Divider,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';
import PaymentIcon from '@mui/icons-material/Payment';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import SearchIcon from '@mui/icons-material/Search';
import ErrorIcon from '@mui/icons-material/Error';

import Layout from '../components/Layout';
import { getWalletAddress } from '../utils/metamask';
import { 
  initializeSyntheticData,
  getAllSyntheticTransactions,
  processTransaction,
  checkAddressFraudHistory
} from '../utils/synthetic-transactions';
import { useTransactions } from '../context/TransactionContext';

// Transaction workflow steps
const steps = [
  { label: 'Initiate Transaction', icon: <PaymentIcon /> },
  { label: 'ML Fraud Check', icon: <SecurityIcon /> },
  { label: 'Process Payment', icon: <AccountBalanceIcon /> },
  { label: 'Complete Transaction', icon: <CheckCircleIcon /> }
];

// Format currency in INR
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(amount);
};

// Convert number to words (for INR amount)
const numberToWords = (amount) => {
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  });
  
  return `${formatter.format(amount)} (${amount} Rupees only)`;
};

// Styled components
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  fontWeight: 'bold',
  backgroundColor: theme.palette.primary.light,
  color: theme.palette.common.white,
}));

const StatusChip = styled(Chip)(({ theme, status }) => ({
  fontWeight: 'bold',
  backgroundColor: status === 'SUCCESS' ? theme.palette.success.main : 
                   status === 'BLOCKED' ? theme.palette.error.main :
                   theme.palette.warning.main,
  color: theme.palette.common.white,
}));

const RiskChip = styled(Chip)(({ theme, risk }) => ({
  fontWeight: 'bold',
  backgroundColor: 
    risk === 'Low' ? theme.palette.success.main :
    risk === 'Medium' ? theme.palette.warning.main :
    risk === 'High' ? theme.palette.error.main :
    theme.palette.error.dark,
  color: theme.palette.common.white,
}));

const TransactionsPage = () => {
  const { addTransaction, forceRefresh } = useTransactions();
  // State for transaction form
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [transactions, setTransactions] = useState([]);
  const [fraudResult, setFraudResult] = useState(null);
  const [blockReason, setBlockReason] = useState([]);
  const [addressStatus, setAddressStatus] = useState(null);
  const [addressDialogOpen, setAddressDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [transactionCounter, setTransactionCounter] = useState(0);
  
  // --- Log 1: Log state at render time ---
  console.log('[TransactionsPage Render] transactions state:', transactions);
  
  // Load transactions on component mount
  useEffect(() => {
    const loadTransactions = async () => {
      try {
        setLoading(true);
        // Initialize synthetic data if needed
        await initializeSyntheticData();
        
        // Get all transactions
        const txs = await getAllSyntheticTransactions();
        console.log("[Initial Load] Fetched transactions:", txs);
        setTransactions(txs.slice().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
      } catch (error) {
        console.error('Error loading transactions:', error);
        setError('Failed to load transaction history');
      } finally {
        setLoading(false);
      }
    };
    
    loadTransactions();
  }, []);
  
  // Reload transactions whenever a new transaction is processed
  useEffect(() => {
    if (transactionCounter > 0) { // Skip on initial render
      const reloadTransactions = async () => {
        try {
          console.log(`[Transaction Counter Effect] Reloading transactions after counter update: ${transactionCounter}`);
          const txs = await getAllSyntheticTransactions();
          console.log("[Reload] Fetched transactions:", txs);
          setTransactions(txs.slice().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
        } catch (error) {
          console.error('Error reloading transactions:', error);
        }
      };
      
      reloadTransactions();
    }
  }, [transactionCounter]); // Only reload when transactionCounter changes
  
  // Reset workflow
  const resetWorkflow = () => {
    setActiveStep(0);
    setFraudResult(null);
    setBlockReason([]);
    setError('');
    setSuccess('');
  };
  
  // Check recipient address
  const checkRecipient = async () => {
    if (!recipient) {
      setError('Please enter a recipient address');
      return false;
    }
    
    try {
      setLoading(true);
      const addressCheck = await checkAddressFraudHistory(recipient);
      setAddressStatus(addressCheck);
      
      if (addressCheck.hasFraudHistory) {
        setLoading(false);
        setAddressDialogOpen(true);
        return false;
      }
      
      setLoading(false);
      return true;
    } catch (error) {
      console.error('Error checking address:', error);
      setError('Error checking recipient address');
      setLoading(false);
      return false;
    }
  };
  
  // Handle initiate transaction
  const handleInitiateTransaction = async () => {
    resetWorkflow();
    
    // Validate form
    if (!recipient) {
      setError('Please enter a recipient address');
      return;
    }
    
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }
    
    // Get sender address (current user)
    const senderAddress = getWalletAddress() || '0x1111111111111111111111111111111111111111';
    
    // Check recipient address
    const recipientOk = await checkRecipient();
    if (!recipientOk) return;
    
    // Update active step
    setActiveStep(1);
    
    try {
      setLoading(true);
      
      // Create transaction object
      const transaction = {
        sender: senderAddress,
        receiver: recipient,
        amount: parseFloat(amount),
        currency: 'INR',
        timestamp: new Date().toISOString(),
        merchant: 'Manual Transfer',
        merchant_category: 'transfer',
        merchant_risk: 'low'
      };
      
      // Process transaction through ML fraud detection
      setTimeout(async () => {
        try { // Added inner try block
          const result = await processTransaction(transaction);
          // --- Log 2: Log processTransaction result --- 
          console.log('[handleInitiateTransaction] processTransaction result:', result);
          setFraudResult(result);
          
          if (result.success) {
            // Transaction passed ML checks
            setActiveStep(2);
            
            // Simulate payment processing delay
            setTimeout(() => {
              setActiveStep(3);
              setSuccess(`Transaction of ${formatCurrency(parseFloat(amount))} completed successfully`);
              
              // Add transaction to context and force a refresh
              if (result.transaction) {
                console.log('Adding successful transaction to context:', result.transaction);
                addTransaction(result.transaction); 
                forceRefresh(); // Force dashboard to update
              }
              
              // Update transaction counter to trigger reloading transactions
              setTransactionCounter(prev => prev + 1);
              setLoading(false);
            }, 1500);
  
          } else {
            // Transaction blocked due to fraud detection
            setError(`Transaction blocked: Risk level ${result.fraudDetection?.riskLevel || 'Unknown'}`);
            setBlockReason(result.fraudDetection?.indicators || ['Reason unknown']);
            setActiveStep(1); // Stay at ML check step
            
            // Add blocked transaction to context and force a refresh
            if (result.transaction) {
              console.log('Adding blocked transaction to context:', result.transaction);
              addTransaction(result.transaction);
              forceRefresh(); // Force dashboard to update
            }
            
            // Update transaction counter to trigger reloading transactions
            setTransactionCounter(prev => prev + 1);
          }
        } catch (innerError) { // Added inner catch block
          console.error('Error during transaction processing timeout:', innerError);
          setError('Failed to process transaction after check.');
          setActiveStep(0); // Reset step on error
        } finally { // Added inner finally block
           // Ensure loading is always set to false unless we are in the final success step timeout
           if (activeStep !== 2) { // Don't set loading false if we are waiting for the final step 3 timeout
              setLoading(false); 
           } else {
             // Need to ensure loading becomes false after the final step 3 timeout
             // The second setTimeout handles this for the success case.
           }
        }
      }, 2000); 

    } catch (error) { // Outer catch for initial errors
      console.error('Transaction initiation error:', error);
      setError('Error initiating transaction check');
      setLoading(false); 
      setActiveStep(0);
    }
  };
  
  // Handle transaction details dialog
  const openTransactionDetails = (transaction) => {
    setSelectedTransaction(transaction);
    setDetailsDialogOpen(true);
  };
  
  return (
    <Layout title="Transactions">
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          <Grid container alignItems="center" spacing={1}>
            <Grid item>
              <PaymentIcon color="primary" /> 
            </Grid>
            <Grid item>
              Transactions
            </Grid>
          </Grid>
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Send payments securely with our advanced ML fraud detection system.
          Every transaction is analyzed in real-time to protect you from fraud.
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 2, mb: 4 }}>
          {/* Transaction Form */}
          <Grid item xs={12} md={6}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  New Transaction
                </Typography>
                
                <TextField
                  fullWidth
                  label="Recipient Address"
                  margin="normal"
                  variant="outlined"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  placeholder="0x..."
                  disabled={loading || activeStep > 0}
                />
                
                <TextField
                  fullWidth
                  label="Amount (INR)"
                  margin="normal"
                  variant="outlined"
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={loading || activeStep > 0}
                  InputProps={{
                    startAdornment: <Typography variant="body2" color="textSecondary" sx={{ mr: 1 }}>₹</Typography>,
                  }}
                  helperText={amount ? `Amount in words: ${numberToWords(parseFloat(amount))}` : ''}
                />
                
                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                    {blockReason.length > 0 && (
                      <Box mt={1}>
                        <Typography variant="subtitle2">Fraud indicators:</Typography>
                        <ul>
                          {blockReason.map((reason, index) => (
                            <li key={index}>{reason}</li>
                          ))}
                        </ul>
                      </Box>
                    )}
                  </Alert>
                )}
                
                {success && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {success}
                  </Alert>
                )}
                
                <Box mt={2} display="flex" justifyContent="space-between">
                  {activeStep === 0 ? (
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleInitiateTransaction}
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} /> : <PaymentIcon />}
                      fullWidth
                    >
                      {loading ? 'Processing...' : 'Send Payment'}
                    </Button>
                  ) : (
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={resetWorkflow}
                      disabled={loading}
                      fullWidth
                    >
                      New Transaction
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Transaction Workflow */}
          <Grid item xs={12} md={6}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Transaction Security Process
                </Typography>
                
                <Stepper activeStep={activeStep} alternativeLabel>
                  {steps.map((step, index) => (
                    <Step key={index}>
                      <StepLabel
                        StepIconComponent={() => (
                          <Box
                            sx={{
                              backgroundColor: activeStep >= index ? 'primary.main' : 'grey.400',
                              color: 'white',
                              borderRadius: '50%',
                              width: 32,
                              height: 32,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            {/* Show error icon if transaction is blocked at this step */}
                            {activeStep === index && error && index === 1 ? (
                              <BlockIcon />
                            ) : (
                              step.icon
                            )}
                          </Box>
                        )}
                      >
                        {step.label}
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
                
                <Box mt={4} textAlign="center">
                  {activeStep === 0 && (
                    <Typography>
                      Enter the recipient's address and amount to start a new transaction.
                    </Typography>
                  )}
                  
                  {activeStep === 1 && loading && (
                    <Box display="flex" flexDirection="column" alignItems="center">
                      <CircularProgress size={40} />
                      <Typography mt={2}>
                        Running fraud detection checks...
                      </Typography>
                    </Box>
                  )}
                  
                  {activeStep === 1 && !loading && error && (
                    <Box display="flex" flexDirection="column" alignItems="center">
                      <ErrorIcon color="error" sx={{ fontSize: 40 }} />
                      <Typography variant="h6" color="error" mt={1}>
                        Transaction Blocked
                      </Typography>
                      <Typography color="textSecondary">
                        Our ML security system has detected high-risk patterns.
                      </Typography>
                    </Box>
                  )}
                  
                  {activeStep === 2 && (
                    <Box display="flex" flexDirection="column" alignItems="center">
                      <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
                      <Typography mt={2}>
                        Redirecting to payment gateway...
                      </Typography>
                    </Box>
                  )}
                  
                  {activeStep === 3 && (
                    <Box display="flex" flexDirection="column" alignItems="center">
                      <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
                      <Typography variant="h6" color="success.main" mt={1}>
                        Transaction Complete
                      </Typography>
                      <Typography>
                        Your payment of {formatCurrency(parseFloat(amount))} has been processed securely.
                      </Typography>
                    </Box>
                  )}
                </Box>
                
                {fraudResult && !loading && (
                  <Box mt={3} p={2} bgcolor="background.paper" borderRadius={1}>
                    <Typography variant="subtitle2" gutterBottom>
                      Fraud Detection Result:
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Risk Score:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" fontWeight="bold">
                          {(fraudResult.fraudDetection.fraudScore * 100).toFixed(0)}%
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Risk Level:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <RiskChip 
                          label={fraudResult.fraudDetection.riskLevel}
                          risk={fraudResult.fraudDetection.riskLevel}
                          size="small"
                        />
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Decision:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" fontWeight="bold" color={fraudResult.success ? "success.main" : "error.main"}>
                          {fraudResult.success ? "APPROVED" : "BLOCKED"}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          {/* Transaction History */}
          <Grid item xs={12}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Transaction History
                </Typography>
                
                {loading && transactions.length === 0 ? (
                  <Box display="flex" justifyContent="center" my={3}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <TableContainer component={Paper} sx={{ mt: 2 }}>
                    <Table sx={{ minWidth: 650 }} size="small">
                      <TableHead>
                        <TableRow>
                          <StyledTableCell>Transaction ID</StyledTableCell>
                          <StyledTableCell>Date & Time</StyledTableCell>
                          <StyledTableCell>From</StyledTableCell>
                          <StyledTableCell>To</StyledTableCell>
                          <StyledTableCell align="right">Amount</StyledTableCell>
                          <StyledTableCell>Risk Level</StyledTableCell>
                          <StyledTableCell>Status</StyledTableCell>
                          <StyledTableCell>Action</StyledTableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {transactions.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={8} align="center">
                              No transactions found
                            </TableCell>
                          </TableRow>
                        ) : (
                          transactions.map((tx) => (
                            <TableRow key={tx.id} hover>
                              <TableCell>{tx.id}</TableCell>
                              <TableCell>{new Date(tx.timestamp).toLocaleString()}</TableCell>
                              <TableCell>{`${tx.sender.substring(0, 6)}...${tx.sender.substring(tx.sender.length - 4)}`}</TableCell>
                              <TableCell>{`${tx.receiver.substring(0, 6)}...${tx.receiver.substring(tx.receiver.length - 4)}`}</TableCell>
                              <TableCell align="right">{formatCurrency(tx.amount)}</TableCell>
                              <TableCell>
                                <RiskChip 
                                  label={tx.risk_level}
                                  risk={tx.risk_level}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <StatusChip 
                                  label={tx.status}
                                  status={tx.status}
                                  size="small"
                                  icon={tx.status === 'BLOCKED' ? <BlockIcon /> : <CheckCircleIcon />}
                                />
                              </TableCell>
                              <TableCell>
                                <Button
                                  size="small"
                                  startIcon={<SearchIcon />}
                                  onClick={() => openTransactionDetails(tx)}
                                >
                                  Details
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* High Risk Address Dialog */}
        <Dialog open={addressDialogOpen} onClose={() => setAddressDialogOpen(false)}>
          <DialogTitle>
            <Box display="flex" alignItems="center">
              <WarningIcon color="error" sx={{ mr: 1 }} />
              High Risk Address Detected
            </Box>
          </DialogTitle>
          <DialogContent>
            <Typography variant="body1" gutterBottom>
              The recipient address has a history of fraudulent transactions.
            </Typography>
            
            {addressStatus && addressStatus.details && (
              <Box mt={2}>
                <Typography variant="subtitle2">Fraud Risk Information:</Typography>
                <Grid container spacing={1} mt={1}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Risk Score:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" fontWeight="bold">
                      {(addressStatus.riskScore * 100).toFixed(0)}%
                    </Typography>
                  </Grid>
                  
                  {addressStatus.details.fraud_transactions && (
                    <>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Fraudulent Transactions:</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" fontWeight="bold">
                          {addressStatus.details.fraud_transactions}
                        </Typography>
                      </Grid>
                    </>
                  )}
                  
                  {addressStatus.details.last_fraud && (
                    <>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Last Fraud Activity:</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" fontWeight="bold">
                          {new Date(addressStatus.details.last_fraud).toLocaleString()}
                        </Typography>
                      </Grid>
                    </>
                  )}
                </Grid>
                
                {addressStatus.details.indicators && addressStatus.details.indicators.length > 0 && (
                  <Box mt={2}>
                    <Typography variant="subtitle2">Common Fraud Indicators:</Typography>
                    <ul>
                      {[...new Set(addressStatus.details.indicators)].map((indicator, idx) => (
                        <li key={idx}>
                          <Typography variant="body2">{indicator}</Typography>
                        </li>
                      ))}
                    </ul>
                  </Box>
                )}
              </Box>
            )}
            
            <Alert severity="warning" sx={{ mt: 2 }}>
              It is not recommended to proceed with this transaction. The funds may be at risk.
            </Alert>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddressDialogOpen(false)} color="primary">
              Cancel Transaction
            </Button>
            <Button 
              onClick={() => {
                setAddressDialogOpen(false);
                handleInitiateTransaction();
              }} 
              color="error"
            >
              Proceed Anyway (Risky)
            </Button>
          </DialogActions>
        </Dialog>
        
        {/* Transaction Details Dialog */}
        <Dialog 
          open={detailsDialogOpen} 
          onClose={() => setDetailsDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Transaction Details
          </DialogTitle>
          <DialogContent>
            {selectedTransaction && (
              <>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Transaction Information</Typography>
                    <Box mt={1}>
                      <Grid container spacing={1}>
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Transaction ID:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2" fontWeight="bold">{selectedTransaction.id}</Typography>
                        </Grid>
                        
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Date & Time:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2">{new Date(selectedTransaction.timestamp).toLocaleString()}</Typography>
                        </Grid>
                        
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Amount:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2" fontWeight="bold">
                            {formatCurrency(selectedTransaction.amount)}
                          </Typography>
                        </Grid>
                        
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Status:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <StatusChip 
                            label={selectedTransaction.status}
                            status={selectedTransaction.status}
                            size="small"
                          />
                        </Grid>
                        
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Merchant:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2">{selectedTransaction.merchant}</Typography>
                        </Grid>
                        
                        {selectedTransaction.merchant_category && (
                          <>
                            <Grid item xs={5}>
                              <Typography variant="body2" color="textSecondary">Category:</Typography>
                            </Grid>
                            <Grid item xs={7}>
                              <Typography variant="body2">{selectedTransaction.merchant_category}</Typography>
                            </Grid>
                          </>
                        )}
                      </Grid>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Security Information</Typography>
                    <Box mt={1}>
                      <Grid container spacing={1}>
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Risk Level:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <RiskChip 
                            label={selectedTransaction.risk_level}
                            risk={selectedTransaction.risk_level}
                            size="small"
                          />
                        </Grid>
                        
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Fraud Score:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2">
                            {(selectedTransaction.fraud_score * 100).toFixed(0)}%
                          </Typography>
                        </Grid>
                        
                        {selectedTransaction.device_info && (
                          <>
                            <Grid item xs={5}>
                              <Typography variant="body2" color="textSecondary">Device:</Typography>
                            </Grid>
                            <Grid item xs={7}>
                              <Typography variant="body2">
                                {selectedTransaction.device_info.type}
                                {selectedTransaction.device_info.is_new && ' (New)'}
                              </Typography>
                            </Grid>
                          </>
                        )}
                        
                        {selectedTransaction.velocity && (
                          <>
                            <Grid item xs={5}>
                              <Typography variant="body2" color="textSecondary">Tx Velocity:</Typography>
                            </Grid>
                            <Grid item xs={7}>
                              <Typography variant="body2">
                                {selectedTransaction.velocity} transactions in 24h
                              </Typography>
                            </Grid>
                          </>
                        )}
                      </Grid>
                    </Box>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Sender Information</Typography>
                    <Box mt={1}>
                      <Grid container spacing={1}>
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Address:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                            {selectedTransaction.sender}
                          </Typography>
                        </Grid>
                        
                        {selectedTransaction.sender_info && (
                          <>
                            {selectedTransaction.sender_info.name && (
                              <>
                                <Grid item xs={5}>
                                  <Typography variant="body2" color="textSecondary">Name:</Typography>
                                </Grid>
                                <Grid item xs={7}>
                                  <Typography variant="body2">{selectedTransaction.sender_info.name}</Typography>
                                </Grid>
                              </>
                            )}
                            
                            {selectedTransaction.sender_info.fraud_history !== undefined && (
                              <>
                                <Grid item xs={5}>
                                  <Typography variant="body2" color="textSecondary">Fraud History:</Typography>
                                </Grid>
                                <Grid item xs={7}>
                                  <Typography variant="body2" color={selectedTransaction.sender_info.fraud_history ? "error.main" : "success.main"}>
                                    {selectedTransaction.sender_info.fraud_history ? "Yes" : "No"}
                                  </Typography>
                                </Grid>
                              </>
                            )}
                          </>
                        )}
                      </Grid>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Recipient Information</Typography>
                    <Box mt={1}>
                      <Grid container spacing={1}>
                        <Grid item xs={5}>
                          <Typography variant="body2" color="textSecondary">Address:</Typography>
                        </Grid>
                        <Grid item xs={7}>
                          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                            {selectedTransaction.receiver}
                          </Typography>
                        </Grid>
                        
                        {selectedTransaction.receiver_info && (
                          <>
                            {selectedTransaction.receiver_info.name && (
                              <>
                                <Grid item xs={5}>
                                  <Typography variant="body2" color="textSecondary">Name:</Typography>
                                </Grid>
                                <Grid item xs={7}>
                                  <Typography variant="body2">{selectedTransaction.receiver_info.name}</Typography>
                                </Grid>
                              </>
                            )}
                            
                            {selectedTransaction.receiver_info.fraud_history !== undefined && (
                              <>
                                <Grid item xs={5}>
                                  <Typography variant="body2" color="textSecondary">Fraud History:</Typography>
                                </Grid>
                                <Grid item xs={7}>
                                  <Typography variant="body2" color={selectedTransaction.receiver_info.fraud_history ? "error.main" : "success.main"}>
                                    {selectedTransaction.receiver_info.fraud_history ? "Yes" : "No"}
                                  </Typography>
                                </Grid>
                              </>
                            )}
                          </>
                        )}
                      </Grid>
                    </Box>
                  </Grid>
                </Grid>
                
                {selectedTransaction.fraud_indicators && selectedTransaction.fraud_indicators.length > 0 && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" color={selectedTransaction.is_fraudulent ? "error.main" : "warning.main"}>
                      {selectedTransaction.is_fraudulent ? "Fraud Indicators" : "Risk Indicators"}
                    </Typography>
                    <Box mt={1}>
                      <ul style={{ paddingLeft: '20px', margin: 0 }}>
                        {selectedTransaction.fraud_indicators.map((indicator, idx) => (
                          <li key={idx}>
                            <Typography variant="body2">{indicator}</Typography>
                          </li>
                        ))}
                      </ul>
                    </Box>
                  </>
                )}
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsDialogOpen(false)} color="primary">
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default TransactionsPage; 