import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Configure axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const getModels = async () => {
  try {
    const response = await api.get('/models');
    return response.data;
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
};

export const getModelAccuracies = async () => {
  try {
    const response = await api.get('/model_accuracies');
    return response.data;
  } catch (error) {
    console.error('Error fetching model accuracies:', error);
    throw error;
  }
};

export const getExampleInput = async (modelName) => {
  try {
    const response = await api.get(`/example_input?model_name=${modelName}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching example input:', error);
    throw error;
  }
};

export const predictFraud = async (modelName, inputData) => {
  try {
    const response = await api.post('/predict', {
      model_name: modelName,
      input_data: inputData,
    });
    return response.data;
  } catch (error) {
    console.error('Error making prediction:', error);
    throw error;
  }
};

// Mock functions for demo purposes (when backend is not available)
const mockTransactionData = [
  {
    id: 'tx123456',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    amount: 1234.56,
    type: 'Transfer',
    status: 'Success',
    is_fraud: false,
    fraud_probability: 0.05,
    risk_level: 'Low'
  },
  {
    id: 'tx123457',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    amount: 2000.00,
    type: 'Cash Out',
    status: 'Success',
    is_fraud: false,
    fraud_probability: 0.15,
    risk_level: 'Low'
  },
  {
    id: 'tx123458',
    timestamp: new Date(Date.now() - 10 * 60000).toISOString(),
    amount: 50000.00,
    type: 'Transfer',
    status: 'Pending',
    is_fraud: true,
    fraud_probability: 0.89,
    risk_level: 'Very High'
  },
  {
    id: 'tx123459',
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    amount: 7500.00,
    type: 'Payment',
    status: 'Failed',
    is_fraud: true,
    fraud_probability: 0.95,
    risk_level: 'Very High'
  },
  {
    id: 'tx123460',
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
    amount: 100.00,
    type: 'Payment',
    status: 'Success',
    is_fraud: false,
    fraud_probability: 0.02,
    risk_level: 'Low'
  },
];

const mockBlocks = [
  {
    id: '0x1234...5678',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    transactions: 150,
    size: '1.5 MB',
    validator: '0xabc...def',
    status: 'Confirmed'
  },
  {
    id: '0x8765...4321',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    transactions: 120,
    size: '1.2 MB',
    validator: '0xdef...abc',
    status: 'Confirmed'
  },
  {
    id: '0x9876...5432',
    timestamp: new Date(Date.now() - 8 * 60000).toISOString(),
    transactions: 180,
    size: '1.8 MB',
    validator: '0x123...456',
    status: 'Pending'
  },
  {
    id: '0x5432...7890',
    timestamp: new Date(Date.now() - 12 * 60000).toISOString(),
    transactions: 90,
    size: '0.9 MB',
    validator: '0x789...012',
    status: 'Failed'
  }
];

export const mockUsers = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    status: 'Active'
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'User',
    status: 'Active'
  },
  {
    id: 3,
    name: 'Bob Johnson',
    email: 'bob@example.com',
    role: 'User',
    status: 'Inactive'
  }
];

// Mock API functions
export const getMockTransactions = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        transactions: mockTransactionData
      });
    }, 500);
  });
};

export const getMockBlocks = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        blocks: mockBlocks
      });
    }, 500);
  });
};

export const getMockUsers = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        users: mockUsers
      });
    }, 500);
  });
};

export const mockPredictFraud = (transactionData) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate a prediction based on the amount
      const fraudProbability = transactionData.amount > 10000 ? 0.85 : 
                              transactionData.type === 'Transfer' ? 0.65 : 0.15;
      
      const riskLevel = fraudProbability < 0.2 ? 'Low' : 
                        fraudProbability < 0.5 ? 'Medium' : 
                        fraudProbability < 0.8 ? 'High' : 'Very High';
      
      resolve({
        success: true,
        prediction: {
          model_name: 'online-payment-fraud',
          fraud_probability: fraudProbability,
          is_fraud: fraudProbability > 0.5,
          risk_level: riskLevel,
          risk_factors: transactionData.amount > 10000 ? 
            ['Large transaction amount', 'Pattern matches known fraud cases'] : 
            ['No significant risk factors detected']
        }
      });
    }, 1000);
  });
};

export default {
  getModels,
  getModelAccuracies,
  getExampleInput,
  predictFraud,
  getMockTransactions,
  getMockBlocks,
  getMockUsers,
  mockPredictFraud
}; 