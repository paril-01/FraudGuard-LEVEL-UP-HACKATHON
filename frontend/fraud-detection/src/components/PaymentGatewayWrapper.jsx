import React from 'react';
import PaymentGateway from './PaymentGateway';

const PaymentGatewayWrapper = ({ 
  showPaymentGateway, 
  setShowPaymentGateway, 
  amount, 
  onPaymentSuccess 
}) => {
  return (
    <PaymentGateway
      open={showPaymentGateway}
      onClose={() => setShowPaymentGateway(false)}
      amount={amount ? parseFloat(amount) : 0}
      currency="INR"
      orderId={`ORD${Math.floor(Math.random() * 1000000)}`}
      merchantName="FraudGuard Secure Payments"
      onPaymentSuccess={onPaymentSuccess}
    />
  );
};

export default PaymentGatewayWrapper; 