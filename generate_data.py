import os
import pandas as pd
import numpy as np

def generate_synthetic_fraud_data():
    """Generate synthetic fraud detection dataset"""
    print("Generating synthetic fraud dataset...")
    
    # Create synthetic data
    np.random.seed(42)
    
    # Number of records
    n_records = 10000
    
    # Create transaction amounts with most being smaller and some larger
    amounts = np.exp(np.random.normal(4, 1, n_records))
    
    # Create transaction types
    types = np.random.choice(['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT'], n_records, 
                          p=[0.5, 0.3, 0.1, 0.1])
    
    # Create hour of day (0-23)
    hours = np.random.randint(0, 24, n_records)
    
    # Create day of week (0-6, where 0 is Monday)
    days = np.random.randint(0, 7, n_records)
    
    # Create merchant category
    categories = np.random.choice(['retail', 'entertainment', 'food', 'travel', 'other'], 
                               n_records, p=[0.4, 0.2, 0.2, 0.1, 0.1])
    
    # Create account age in days (older accounts are less likely to be fraudulent)
    account_age = np.random.gamma(5, 100, n_records)
    
    # Create number of previous transactions (higher number is less likely to be fraudulent)
    prev_transactions = np.random.gamma(2, 10, n_records)
    
    # Calculate fraud probability based on features
    fraud_prob = (
        0.9 * (1 - np.tanh(account_age / 500)) +  # newer accounts
        0.7 * (1 - np.tanh(prev_transactions / 20)) +  # fewer previous transactions
        0.5 * np.tanh(amounts / 1000) +  # higher amounts
        0.3 * np.sin(np.pi * hours / 12)  # late night hours
    ) / 2.4  # normalize
    
    # Add random noise
    fraud_prob = fraud_prob + np.random.normal(0, 0.1, n_records)
    
    # Clip to [0, 1] range
    fraud_prob = np.clip(fraud_prob, 0, 1)
    
    # Convert to binary labels with around 10% fraud rate
    fraud_threshold = np.percentile(fraud_prob, 90)
    is_fraud = (fraud_prob > fraud_threshold).astype(int)
    
    # Create dataframe
    df = pd.DataFrame({
        'transactionAmount': amounts,
        'transactionType': types,
        'hourOfDay': hours,
        'dayOfWeek': days,
        'merchantCategory': categories,
        'accountAgeDays': account_age,
        'numPrevTransactions': prev_transactions,
        'isFraud': is_fraud
    })
    
    # Ensure directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_path = os.path.join('data', 'online_fraud.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Synthetic dataset created with {n_records} records")
    print(f"Fraud rate: {df['isFraud'].mean():.1%}")
    print(f"Dataset saved to: {output_path}")
    
    return output_path

if __name__ == '__main__':
    generate_synthetic_fraud_data() 