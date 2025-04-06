/**
 * Mock API service for Razorpay server-side operations
 * 
 * In a real application, these operations would be performed on the server
 * to keep your API keys and secrets secure.
 */

// Secret credentials that should NEVER be exposed in frontend code in production
// In a real app, store these securely on the server
const RAZORPAY_KEY_ID = 'rzp_test_a2KyKUsuzrIhSL';
const RAZORPAY_SECRET = 'IDPVmcdJpp7dkZ7FiebKKl6q';

/**
 * Mock function to create a Razorpay order
 * In production, this would be an API call to your backend
 */
export const createRazorpayOrder = async (amount, currency = 'INR') => {
  // Simulate a network request to server
  console.log(`[SERVER] Creating Razorpay order for amount: ${amount} ${currency}`);
  console.log(`[SERVER] Using Razorpay credentials (KEY_ID: ${RAZORPAY_KEY_ID}, SECRET: ${RAZORPAY_SECRET.substring(0, 3)}...)`);
  
  // Simulate server processing delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock response from server
  const orderId = 'order_' + Math.random().toString(36).substring(2, 15);
  console.log(`[SERVER] Order created with ID: ${orderId}`);
  
  return {
    id: orderId,
    amount: amount * 100, // Razorpay expects amount in smallest currency unit (paise for INR)
    currency,
    receipt: 'rcpt_' + Math.random().toString(36).substring(2, 10),
    status: 'created'
  };
};

/**
 * Mock function to verify a Razorpay payment
 * In production, this would be an API call to your backend
 */
export const verifyRazorpayPayment = async (paymentId, orderId, signature) => {
  // Simulate a network request to server
  console.log(`[SERVER] Verifying Razorpay payment`);
  console.log(`[SERVER] Payment ID: ${paymentId}`);
  console.log(`[SERVER] Order ID: ${orderId}`);
  console.log(`[SERVER] Signature: ${signature}`);
  
  // Simulate verification process
  // In a real server, you would:
  // 1. Create a string containing orderId + "|" + paymentId
  // 2. Generate a HMAC-SHA256 signature using your secret key
  // 3. Compare with the signature sent by Razorpay
  
  // Simulate server processing delay
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Always successful in this mock implementation
  return {
    success: true,
    orderId,
    paymentId,
    message: 'Payment verification successful'
  };
};

/**
 * Mock function to fetch payment details
 * In production, this would be an API call to your backend
 */
export const getPaymentDetails = async (paymentId) => {
  // Simulate a network request to server
  console.log(`[SERVER] Fetching payment details for payment ID: ${paymentId}`);
  
  // Simulate server processing delay
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Mock payment details
  return {
    id: paymentId,
    amount: 49900, // in paise
    currency: 'INR',
    status: 'captured',
    method: 'card',
    email: 'customer@example.com',
    contact: '+919876543210',
    created_at: new Date().toISOString()
  };
};

/**
 * Mock function to refund a payment
 * In production, this would be an API call to your backend
 */
export const refundPayment = async (paymentId, amount = null) => {
  // Simulate a network request to server
  console.log(`[SERVER] Refunding payment ID: ${paymentId}`);
  
  if (amount) {
    console.log(`[SERVER] Partial refund of amount: ${amount} paise`);
  } else {
    console.log(`[SERVER] Full refund requested`);
  }
  
  // Simulate server processing delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock refund response
  return {
    id: 'rfnd_' + Math.random().toString(36).substring(2, 15),
    payment_id: paymentId,
    amount: amount || 49900, // in paise
    status: 'processed',
    speed: 'normal',
    created_at: new Date().toISOString()
  };
}; 