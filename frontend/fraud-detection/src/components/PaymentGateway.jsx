import React, { useState } from 'react';
import {
  Box,
  Card,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
  IconButton,
  Dialog,
  DialogContent,
  CircularProgress,
  Tabs,
  Tab,
  InputAdornment,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Paper,
  Checkbox
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import LockIcon from '@mui/icons-material/Lock';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PhoneAndroidIcon from '@mui/icons-material/PhoneAndroid';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { styled } from '@mui/material/styles';

// Styled components
const GatewayHeader = styled(Box)(({ theme }) => ({
  backgroundColor: '#3395ff',
  color: '#fff',
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const SecureText = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.text.secondary,
  fontSize: '0.75rem',
  marginTop: theme.spacing(1),
}));

const PaymentOption = styled(Paper)(({ theme, selected }) => ({
  padding: theme.spacing(2),
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  border: selected ? `1px solid ${theme.palette.primary.main}` : '1px solid #e0e0e0',
  backgroundColor: selected ? 'rgba(51, 149, 255, 0.04)' : theme.palette.background.paper,
  '&:hover': {
    backgroundColor: 'rgba(51, 149, 255, 0.04)',
  },
}));

const PayButtonContainer = styled(Box)(({ theme }) => ({
  backgroundColor: '#f5f5f5',
  padding: theme.spacing(2),
  position: 'sticky',
  bottom: 0,
}));

const PayButton = styled(Button)(() => ({
  backgroundColor: '#3395ff',
  color: '#fff',
  fontWeight: 'bold',
  '&:hover': {
    backgroundColor: '#2d85e4',
  },
  '&.Mui-disabled': {
    backgroundColor: '#cccccc',
    color: '#666666',
  },
}));

// Payment Gateway Component
const PaymentGateway = ({ 
  open, 
  onClose, 
  amount, 
  currency = 'INR', 
  orderId = 'ORDER123', 
  merchantName = 'FraudGuard',
  onPaymentSuccess 
}) => {
  // States
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [loading, setLoading] = useState(false);
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [cardName, setCardName] = useState('');
  const [paymentComplete, setPaymentComplete] = useState(false);
  const [saveCard, setSaveCard] = useState(false);
  
  // Format amount
  const formattedAmount = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 2
  }).format(amount);
  
  // Handle payment method change
  const handleMethodChange = (method) => {
    setPaymentMethod(method);
  };
  
  // Handle card number input with formatting
  const handleCardNumberChange = (e) => {
    let value = e.target.value.replace(/\s/g, '');
    if (value.length > 16) return;
    if (/^\d*$/.test(value)) {
      // Format with spaces every 4 digits
      value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
      setCardNumber(value);
    }
  };
  
  // Handle card expiry input with formatting
  const handleExpiryChange = (e) => {
    let value = e.target.value.replace(/\s/g, '');
    if (value.length > 5) return;
    
    // Only allow digits and forward slash
    value = value.replace(/[^\d/]/g, '');
    
    // Add slash after 2 digits if not already there
    if (value.length === 2 && !value.includes('/')) {
      value += '/';
    }
    
    setCardExpiry(value);
  };
  
  // Handle payment submission
  const handleSubmitPayment = () => {
    // Validate card details for card payment
    if (paymentMethod === 'card') {
      if (!cardNumber || cardNumber.replace(/\s/g, '').length < 16) {
        alert('Please enter a valid card number');
        return;
      }
      
      if (!cardExpiry || !/^\d{2}\/\d{2}$/.test(cardExpiry)) {
        alert('Please enter a valid expiry date (MM/YY)');
        return;
      }
      
      if (!cardCvv || !/^\d{3}$/.test(cardCvv)) {
        alert('Please enter a valid CVV');
        return;
      }
      
      if (!cardName) {
        alert('Please enter the name on card');
        return;
      }
    }
    
    // Process payment
    setLoading(true);
    
    // Simulate payment processing
    setTimeout(() => {
      setLoading(false);
      setPaymentComplete(true);
      
      // Call success callback after showing success screen
      setTimeout(() => {
        if (onPaymentSuccess) {
          onPaymentSuccess({
            paymentId: 'pay_' + Math.random().toString(36).substring(2, 15),
            orderId: orderId,
            signature: 'sig_' + Math.random().toString(36).substring(2, 15)
          });
        }
        onClose();
      }, 2000);
    }, 2000);
  };
  
  return (
    <Dialog 
      open={open} 
      onClose={loading || paymentComplete ? null : onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogContent sx={{ p: 0, position: 'relative' }}>
        {/* Gateway Header */}
        <GatewayHeader>
          <Typography variant="h6">Secure Checkout</Typography>
          {!loading && !paymentComplete && (
            <IconButton onClick={onClose} color="inherit">
              <CloseIcon />
            </IconButton>
          )}
        </GatewayHeader>
        
        {/* Order Details */}
        <Box p={2} bgcolor="#f9f9f9">
          <Grid container justifyContent="space-between" alignItems="center">
            <Grid item>
              <Typography variant="subtitle1">{merchantName}</Typography>
              <Typography variant="caption" color="textSecondary">Order #{orderId}</Typography>
            </Grid>
            <Grid item>
              <Typography variant="h6">{formattedAmount}</Typography>
            </Grid>
          </Grid>
        </Box>
        
        <Divider />
        
        {/* Payment Success Screen */}
        {paymentComplete && (
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            p={4} 
            textAlign="center"
            minHeight="400px"
          >
            <CheckCircleIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>Payment Successful</Typography>
            <Typography variant="body1" color="textSecondary">
              Your payment of {formattedAmount} has been processed successfully.
            </Typography>
            <Typography variant="caption" color="textSecondary" mt={2}>
              Transaction ID: pay_{Math.random().toString(36).substring(2, 15)}
            </Typography>
          </Box>
        )}
        
        {/* Payment Processing Screen */}
        {loading && (
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            p={4} 
            textAlign="center"
            minHeight="400px"
          >
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h5" gutterBottom>Processing Payment</Typography>
            <Typography variant="body1" color="textSecondary">
              Please wait while we process your payment...
            </Typography>
          </Box>
        )}
        
        {/* Payment Options and Form */}
        {!loading && !paymentComplete && (
          <Box>
            {/* Payment Methods */}
            <Box p={2}>
              <Typography variant="subtitle1" gutterBottom>Payment Methods</Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <PaymentOption 
                    selected={paymentMethod === 'card'} 
                    onClick={() => handleMethodChange('card')}
                  >
                    <CreditCardIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">Credit / Debit Card</Typography>
                      <Typography variant="caption" color="textSecondary">Visa, Mastercard, RuPay & more</Typography>
                    </Box>
                  </PaymentOption>
                </Grid>
                
                <Grid item xs={12}>
                  <PaymentOption 
                    selected={paymentMethod === 'upi'} 
                    onClick={() => handleMethodChange('upi')}
                  >
                    <PhoneAndroidIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">UPI</Typography>
                      <Typography variant="caption" color="textSecondary">Google Pay, PhonePe, BHIM UPI</Typography>
                    </Box>
                  </PaymentOption>
                </Grid>
                
                <Grid item xs={12}>
                  <PaymentOption 
                    selected={paymentMethod === 'netbanking'} 
                    onClick={() => handleMethodChange('netbanking')}
                  >
                    <AccountBalanceIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">Netbanking</Typography>
                      <Typography variant="caption" color="textSecondary">All Indian banks</Typography>
                    </Box>
                  </PaymentOption>
                </Grid>
              </Grid>
            </Box>
            
            <Divider />
            
            {/* Card Payment Form */}
            {paymentMethod === 'card' && (
              <Box p={2}>
                <Typography variant="subtitle1" gutterBottom>Card Details</Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Card Number"
                      variant="outlined"
                      value={cardNumber}
                      onChange={handleCardNumberChange}
                      placeholder="4111 1111 1111 1111"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <CreditCardIcon color="action" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Expiry (MM/YY)"
                      variant="outlined"
                      value={cardExpiry}
                      onChange={handleExpiryChange}
                      placeholder="MM/YY"
                    />
                  </Grid>
                  
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="CVV"
                      variant="outlined"
                      value={cardCvv}
                      onChange={(e) => {
                        const val = e.target.value.replace(/[^\d]/g, '');
                        if (val.length <= 3) setCardCvv(val);
                      }}
                      type="password"
                      placeholder="***"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockIcon color="action" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Name on Card"
                      variant="outlined"
                      value={cardName}
                      onChange={(e) => setCardName(e.target.value)}
                      placeholder="John Doe"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={saveCard} 
                          onChange={(e) => setSaveCard(e.target.checked)} 
                        />
                      }
                      label="Save card for future payments"
                    />
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {/* UPI Payment Form */}
            {paymentMethod === 'upi' && (
              <Box p={2}>
                <Typography variant="subtitle1" gutterBottom>UPI Payment</Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="UPI ID"
                      variant="outlined"
                      placeholder="name@upi"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PhoneAndroidIcon color="action" />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      You will receive a payment request on your UPI app
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {/* Netbanking Payment Form */}
            {paymentMethod === 'netbanking' && (
              <Box p={2}>
                <Typography variant="subtitle1" gutterBottom>Select Bank</Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl component="fieldset">
                      <RadioGroup>
                        <FormControlLabel value="sbi" control={<Radio />} label="State Bank of India" />
                        <FormControlLabel value="hdfc" control={<Radio />} label="HDFC Bank" />
                        <FormControlLabel value="icici" control={<Radio />} label="ICICI Bank" />
                        <FormControlLabel value="axis" control={<Radio />} label="Axis Bank" />
                      </RadioGroup>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {/* Secure Payment Button */}
            <PayButtonContainer>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <PayButton
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleSubmitPayment}
                    startIcon={<LockIcon />}
                  >
                    Pay {formattedAmount}
                  </PayButton>
                  
                  <SecureText>
                    <SecurityIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="caption">100% Secure Payments Powered by Razorpay</Typography>
                  </SecureText>
                </Grid>
              </Grid>
            </PayButtonContainer>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default PaymentGateway; 