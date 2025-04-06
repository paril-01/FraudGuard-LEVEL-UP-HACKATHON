import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json
import sys

def download_dataset():
    """
    Download Ethereum transactions dataset using Kaggle API
    """
    try:
        import kagglehub
        # Download latest version
        path = kagglehub.dataset_download("chaitya0623/ethereum-transactions-for-fraud-detection")
        print("Path to dataset files:", path)
        return path
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("Please ensure you have kagglehub installed and configured.")
        print("Manual download: https://www.kaggle.com/datasets/chaitya0623/ethereum-transactions-for-fraud-detection")
        return None

def load_dataset(path=None):
    """
    Load the dataset from the given path or attempt to find it
    """
    if path and os.path.exists(path):
        if os.path.isdir(path):
            # Find CSV files in the directory
            files = [f for f in os.listdir(path) if f.endswith('.csv')]
            if files:
                data_path = os.path.join(path, files[0])
            else:
                print(f"No CSV files found in {path}")
                return None
        else:
            data_path = path
    else:
        # Try to find the dataset in common locations
        potential_paths = [
            "data/ethereum_transactions.csv",
            "../data/ethereum_transactions.csv",
            "ethereum_transactions.csv",
        ]
        
        for p in potential_paths:
            if os.path.exists(p):
                data_path = p
                break
        else:
            print("Dataset not found. Please provide a valid path.")
            return None
    
    print(f"Loading dataset from {data_path}")
    try:
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def analyze_dataset(df):
    """
    Perform basic analysis of the dataset
    """
    print("Dataset information:")
    print(f"Shape: {df.shape}")
    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nSummary statistics:")
    print(df.describe())
    
    print("\nNull values:")
    print(df.isnull().sum())
    
    # If there's a label column, check class distribution
    if 'flag' in df.columns or 'is_fraud' in df.columns or 'fraudulent' in df.columns:
        label_col = [col for col in ['flag', 'is_fraud', 'fraudulent'] if col in df.columns][0]
        print(f"\nClass distribution ({label_col}):")
        print(df[label_col].value_counts())
        print(df[label_col].value_counts(normalize=True).map(lambda x: f"{x:.2%}"))
    
    return df

def preprocess_dataset(df):
    """
    Preprocess the dataset for fraud detection
    """
    print("Preprocessing dataset...")
    
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Identify the target column
    target_columns = ['flag', 'is_fraud', 'fraudulent', 'label']
    target_col = None
    for col in target_columns:
        if col in processed_df.columns:
            target_col = col
            break
    
    if not target_col:
        print("Warning: No fraud label column found. Assuming this is unlabeled data.")
        # Create a placeholder target column
        processed_df['is_fraud'] = np.nan
        target_col = 'is_fraud'
    
    # Handle missing values
    for col in processed_df.columns:
        if processed_df[col].dtype == 'object':
            processed_df[col] = processed_df[col].fillna('')
        else:
            processed_df[col] = processed_df[col].fillna(0)
    
    # Feature Engineering
    
    # Convert timestamp if available
    time_cols = [col for col in processed_df.columns if 'time' in col.lower()]
    for col in time_cols:
        try:
            processed_df[col] = pd.to_datetime(processed_df[col])
            processed_df[f'{col}_hour'] = processed_df[col].dt.hour
            processed_df[f'{col}_day'] = processed_df[col].dt.day
            processed_df[f'{col}_month'] = processed_df[col].dt.month
            processed_df[f'{col}_year'] = processed_df[col].dt.year
            processed_df[f'{col}_dayofweek'] = processed_df[col].dt.dayofweek
        except:
            print(f"Could not convert {col} to datetime.")
    
    # Look for amount/value columns
    amount_cols = [col for col in processed_df.columns if any(term in col.lower() for term in ['amount', 'value', 'sum', 'total'])]
    
    # Create additional features for amounts
    for col in amount_cols:
        if processed_df[col].dtype in [np.float64, np.int64]:
            # Log transform for skewed financial data
            processed_df[f'{col}_log'] = np.log1p(processed_df[col].abs())
            
            # Flag for outlier amounts
            q1 = processed_df[col].quantile(0.25)
            q3 = processed_df[col].quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
            
            processed_df[f'{col}_is_outlier'] = (processed_df[col] > upper_bound).astype(int)
    
    # Address features
    address_cols = [col for col in processed_df.columns if 'address' in col.lower()]
    
    # Process categorical features
    cat_columns = [col for col in processed_df.columns if processed_df[col].dtype == 'object']
    for col in cat_columns:
        if col not in address_cols:  # Skip ETH addresses as they're too high cardinality
            # Convert to categorical codes
            processed_df[f'{col}_code'] = processed_df[col].astype('category').cat.codes
    
    # Prepare feature matrix
    # Remove original categorical columns and non-numeric columns
    X_columns = [col for col in processed_df.columns if col != target_col 
                and processed_df[col].dtype in [np.int64, np.float64]
                and not pd.api.types.is_datetime64_any_dtype(processed_df[col])]
    
    X = processed_df[X_columns]
    y = processed_df[target_col] if not processed_df[target_col].isnull().all() else None
    
    # Save the preprocessed data for the model
    processed_df.to_csv('frontend/fraud-detection/src/data/ethereum_processed.csv', index=False)
    
    # Save feature columns for later use
    with open('frontend/fraud-detection/src/data/ethereum_features.json', 'w') as f:
        json.dump({
            'feature_columns': X_columns,
            'target_column': target_col
        }, f)
    
    # Create a simple mapping schema to standardize fields for the frontend
    schema_mapping = {
        'timestamp_fields': time_cols,
        'amount_fields': amount_cols,
        'address_fields': address_cols,
        'target_field': target_col,
        'feature_fields': X_columns
    }
    
    with open('frontend/fraud-detection/src/data/ethereum_schema.json', 'w') as f:
        json.dump(schema_mapping, f)
    
    print(f"Preprocessing complete. Data saved to ethereum_processed.csv")
    print(f"Selected {len(X_columns)} features for modeling")
    
    return X, y, schema_mapping

def transform_for_frontend(df, schema):
    """
    Transform the Ethereum dataset into the format expected by the frontend
    """
    # Create a new dataframe with standardized columns
    transactions = []
    
    for _, row in df.iterrows():
        # Determine transaction status
        is_fraud = False
        if schema['target_field'] in row and not pd.isna(row[schema['target_field']]):
            is_fraud = bool(row[schema['target_field']])
        
        # Get timestamp
        timestamp = None
        for time_field in schema['timestamp_fields']:
            if time_field in row and not pd.isna(row[time_field]):
                timestamp = row[time_field]
                break
        
        if timestamp is None:
            timestamp = pd.Timestamp.now()
        
        # Get amount
        amount = 0
        for amount_field in schema['amount_fields']:
            if amount_field in row and not pd.isna(row[amount_field]):
                amount = float(row[amount_field])
                break
        
        # Get addresses
        from_address = to_address = "0x0000000000000000000000000000000000000000"
        for addr_field in schema['address_fields']:
            if 'from' in addr_field.lower() and addr_field in row:
                from_address = row[addr_field]
            elif 'to' in addr_field.lower() and addr_field in row:
                to_address = row[addr_field]
        
        # Calculate risk score (0-100)
        # Higher score means higher risk
        risk_features = []
        for feat in schema['feature_fields']:
            if feat in row and feat.endswith('_is_outlier') and row[feat] == 1:
                risk_features.append(50)  # Add 50 points for outlier features
            elif feat in row and feat.endswith('_log') and row[feat] > 15:  # log(3,269,017) ≈ 15
                risk_features.append(30)  # Add 30 points for high value logs
        
        base_risk = 10  # Base risk score
        fraud_risk = sum(risk_features) + base_risk
        fraud_risk = min(fraud_risk, 100)  # Cap at 100
        
        # Create transaction object
        transaction = {
            'id': str(row.name),
            'hash': f"0x{row.name:032x}" if isinstance(row.name, int) else f"0x{hash(str(row.name)) & 0xffffffffffffffff:016x}",
            'from': from_address,
            'to': to_address,
            'amount': str(amount),
            'timestamp': str(timestamp),
            'status': 'BLOCKED' if is_fraud else 'SUCCESS',
            'type': 'ETH',
            'blockNumber': int(row.name) + 10000000 if isinstance(row.name, int) else 10000000,
            'confirmations': 30,
            'fraudScore': fraud_risk if is_fraud else (100 - fraud_risk),
            'riskLevel': 'High' if fraud_risk > 70 else 'Medium' if fraud_risk > 40 else 'Low',
            'indicators': get_risk_indicators(row, schema, fraud_risk),
            'receiver': to_address
        }
        
        transactions.append(transaction)
    
    return transactions

def get_risk_indicators(row, schema, risk_score):
    """Generate risk indicators based on transaction features"""
    indicators = []
    
    # Check amount-related risks
    for field in schema['amount_fields']:
        if field in row and field + '_is_outlier' in row and row[field + '_is_outlier'] == 1:
            indicators.append('Unusual transaction amount')
            break
    
    # Check time-related risks
    for field in schema['timestamp_fields']:
        hour_field = f"{field}_hour"
        if hour_field in row and row[hour_field] is not None:
            hour = row[hour_field]
            if 0 <= hour < 5:  # Late night transactions
                indicators.append('Suspicious transaction time (late night)')
                break
    
    # Add general indicators based on risk score
    if risk_score > 70:
        indicators.append('Multiple risk factors detected')
    if risk_score > 50:
        indicators.append('Transaction pattern matches known fraud schemes')
    if risk_score > 30:
        indicators.append('Requires additional verification')
    
    return indicators

def save_frontend_data(transactions, output_file='frontend/fraud-detection/src/data/ethereum_frontend.json'):
    """Save the transformed data in a format ready for the frontend"""
    with open(output_file, 'w') as f:
        json.dump(transactions, f, indent=2)
    print(f"Frontend-ready data saved to {output_file}")
    return output_file

def main():
    # Download the dataset
    dataset_path = download_dataset()
    
    # Load the dataset
    df = load_dataset(dataset_path)
    if df is None:
        return
    
    # Analyze the dataset
    df = analyze_dataset(df)
    
    # Preprocess the dataset
    X, y, schema = preprocess_dataset(df)
    
    # Transform for frontend
    transactions = transform_for_frontend(df.head(100), schema)  # Using first 100 rows for example
    
    # Save for frontend use
    save_frontend_data(transactions)
    
    print("Processing complete!")

if __name__ == "__main__":
    main() 