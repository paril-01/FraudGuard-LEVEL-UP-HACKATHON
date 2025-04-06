import { createRazorpayOrder, verifyRazorpayPayment } from '../api/razorpayService';

// Razorpay configuration - only the public key should be here
const RAZORPAY_KEY_ID = 'rzp_test_a2KyKUsuzrIhSL';

/**
 * Initialize a Razorpay payment
 * @param {number} amount - Amount in currency unit (rupees for INR)
 * @param {Function} onSuccess - Callback when payment is successful
 * @param {Object} options - Additional options for payment
 */
export const initializeRazorpayPayment = async (amount, onSuccess, options = {}) => {
  try {
    // Load Razorpay script dynamically
    const scriptLoaded = await loadRazorpayScript();
    if (!scriptLoaded) {
      alert('Failed to load Razorpay SDK. Please try again later.');
      return;
    }

    // Create order using our mock server API
    const orderData = await createRazorpayOrder(amount);
    
    // Configure Razorpay options
    const paymentOptions = {
      key: RAZORPAY_KEY_ID,
      amount: orderData.amount.toString(),
      currency: orderData.currency,
      name: 'FraudGuard Advanced Analysis',
      description: 'Payment for advanced fraud detection services',
      order_id: orderData.id,
      handler: function (response) {
        // Verify payment on our mock server
        verifyRazorpayPayment(
          response.razorpay_payment_id,
          response.razorpay_order_id,
          response.razorpay_signature
        ).then(verificationResult => {
          if (verificationResult.success) {
            console.log('Payment verified successfully:', verificationResult);
            if (onSuccess && typeof onSuccess === 'function') {
              onSuccess(response.razorpay_payment_id);
            }
          } else {
            console.error('Payment verification failed');
            alert('Payment verification failed. Please contact support.');
          }
        });
      },
      prefill: {
        name: 'User',
        email: 'user@example.com',
        contact: '9999999999'
      },
      notes: {
        address: 'FraudGuard Corporate Office'
      },
      theme: {
        color: '#5c4ee5'
      },
      ...options
    };

    // Open Razorpay checkout
    const razorpay = new window.Razorpay(paymentOptions);
    razorpay.open();
  } catch (error) {
    console.error('Error initializing payment:', error);
    alert('Could not initiate payment. Please try again.');
  }
};

/**
 * Load the Razorpay script dynamically
 * @returns {Promise<boolean>} - Whether the script loaded successfully
 */
const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    // Check if Razorpay is already loaded
    if (window.Razorpay) {
      resolve(true);
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => {
      console.error('Failed to load Razorpay SDK');
      resolve(false);
    };
    document.body.appendChild(script);
  });
};

// Note: In a production environment, always use a backend API for:
// 1. Creating orders (to keep your secret key secure)
// 2. Verifying payments (using Razorpay webhooks or API)
// The secret key should never be exposed in frontend code 