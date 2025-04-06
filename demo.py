import os
import sys
import pickle
import pandas as pd
import numpy as np
import json
from pprint import pprint
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Add the source directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_synthetic_model():
    """Create a synthetic model for demo purposes"""
    print("Creating synthetic model for demonstration...")
    
    # Create directory if needed
    models_dir = os.path.join('src', 'models', 'saved_models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Create a simple model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Create a simple preprocessor
    preprocessor = StandardScaler()
    
    # Create some synthetic training data that follows fraud patterns
    n_samples = 1000
    np.random.seed(42)
    
    # Features that simulate normal transactions
    X_normal = np.random.rand(n_samples, 5)
    y_normal = np.zeros(n_samples)
    
    # Features that simulate fraudulent transactions (including account drain pattern)
    X_fraud = np.random.rand(n_samples // 10, 5)
    X_fraud[:, 0] = 0  # Simulate drained accounts
    y_fraud = np.ones(n_samples // 10)
    
    # Combine datasets
    X = np.vstack([X_normal, X_fraud])
    y = np.hstack([y_normal, y_fraud])
    
    # Fit the preprocessor and transform the data
    X_scaled = preprocessor.fit_transform(X)
    
    # Train the model
    model.fit(X_scaled, y)
    
    # Save the model
    model_path = os.path.join(models_dir, "synthetic_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save the preprocessor
    preprocessor_path = os.path.join(models_dir, "synthetic_model_preprocessor.pkl")
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    # Save feature names
    feature_names = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
    feature_names_path = os.path.join(models_dir, "synthetic_model_feature_names.pkl")
    with open(feature_names_path, 'wb') as f:
        pickle.dump(feature_names, f)
    
    print(f"Synthetic model created at {model_path}")
    return model, preprocessor, feature_names

def load_model(model_name='synthetic_model'):
    """Load a trained model and its preprocessor"""
    try:
        # Define paths
        models_dir = os.path.join('src', 'models', 'saved_models')
        model_path = os.path.join(models_dir, f"{model_name}.pkl")
        preprocessor_path = os.path.join(models_dir, f"{model_name}_preprocessor.pkl")
        feature_names_path = os.path.join(models_dir, f"{model_name}_feature_names.pkl")
        
        # Check if files exist
        if not os.path.exists(model_path):
            return create_synthetic_model()
        
        # Load model and preprocessor
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(preprocessor_path, 'rb') as f:
            preprocessor = pickle.load(f)
        
        with open(feature_names_path, 'rb') as f:
            feature_names = pickle.load(f)
        
        return model, preprocessor, feature_names
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("Creating synthetic model for demonstration...")
        return create_synthetic_model()

def preprocess_transaction(transaction_data, preprocessor):
    """Preprocess a transaction for synthetic prediction"""
    # For demo purposes, convert transaction data to a feature vector
    features = np.zeros(5)
    
    # Feature 1: Account drain indicator (1 if account drained, 0 otherwise)
    if transaction_data['oldbalanceOrg'] > 0 and transaction_data['newbalanceOrig'] == 0:
        features[0] = 0  # This pattern correlates with fraud in our synthetic model
    else:
        features[0] = np.random.rand()
    
    # Feature 2: Large amount indicator
    if transaction_data['amount'] > 200000:
        features[1] = 0.9
    else:
        features[1] = transaction_data['amount'] / 100000
    
    # Feature 3: New destination account
    if transaction_data['oldbalanceDest'] == 0 and transaction_data['newbalanceDest'] > 0:
        features[2] = 0.1
    else:
        features[2] = 0.7
    
    # Feature 4: Transaction type
    if transaction_data['type'] == 'TRANSFER':
        features[3] = 0.2
    elif transaction_data['type'] == 'CASH_OUT':
        features[3] = 0.3
    else:
        features[3] = 0.8
    
    # Feature 5: Random noise
    features[4] = np.random.rand()
    
    # Scale features
    X = preprocessor.transform(features.reshape(1, -1))
    
    return X

def get_risk_factors(transaction_data):
    """Get risk factors for a transaction"""
    risk_factors = {}
    
    # Identify common fraud patterns
    if transaction_data['oldbalanceOrg'] > 0 and transaction_data['newbalanceOrig'] == 0:
        risk_factors["account_drained"] = "Originator account was completely drained"
    
    if transaction_data['amount'] > 200000:
        risk_factors["large_amount"] = "Unusually large transaction amount"
    
    if transaction_data['oldbalanceDest'] == 0 and transaction_data['newbalanceDest'] > 0:
        risk_factors["new_destination_account"] = "Previously empty destination account"
    
    # Transaction type risk
    if transaction_data['type'] == 'TRANSFER':
        risk_factors["transfer_risk"] = "Transfer transactions have higher fraud risk"
    
    # If no risk factors identified, provide a default message
    if not risk_factors:
        risk_factors["general"] = "No specific risk factors identified"
    
    return risk_factors

def predict_transaction(transaction_data, model_name='synthetic_model'):
    """Make a prediction for a single transaction"""
    # Load model and preprocessor
    model, preprocessor, _ = load_model(model_name)
    
    if model is None or preprocessor is None:
        print("Error: Could not load or create model.")
        return None
    
    # Preprocess the transaction
    X = preprocess_transaction(transaction_data, preprocessor)
    
    # Make prediction
    prediction = int(model.predict(X)[0])
    fraud_probability = float(model.predict_proba(X)[0, 1])
    
    # Determine risk level
    if fraud_probability < 0.3:
        risk_level = "Low"
    elif fraud_probability < 0.7:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    # Get risk factors
    risk_factors = get_risk_factors(transaction_data)
    
    # Return result
    result = {
        'prediction': prediction,
        'fraud_probability': round(fraud_probability, 4),
        'risk_level': risk_level,
        'risk_factors': risk_factors
    }
    
    return result

def main():
    """Run demo predictions on sample transactions"""
    print("\n=== Fraud Detection Demo ===\n")
    
    # Example 1: A normal payment
    print("Transaction 1: Normal Payment")
    transaction1 = {
        'type': 'PAYMENT',
        'amount': 9839.64,
        'oldbalanceOrg': 9839.64,
        'newbalanceOrig': 9839.64,  # No drain - balance stays the same
        'oldbalanceDest': 1000.0,
        'newbalanceDest': 10839.64,
        'step': 1,
    }
    pprint(transaction1)
    result1 = predict_transaction(transaction1)
    print("\nPrediction:")
    pprint(result1)
    
    print("\n" + "-"*50 + "\n")
    
    # Example 2: A fraudulent transfer (typical pattern)
    print("Transaction 2: Suspicious Transfer")
    transaction2 = {
        'type': 'TRANSFER',
        'amount': 181.0,
        'oldbalanceOrg': 181.0,
        'newbalanceOrig': 0.0,  # Account drain - balance goes to zero
        'oldbalanceDest': 0.0,
        'newbalanceDest': 181.0,
        'step': 1,
    }
    pprint(transaction2)
    result2 = predict_transaction(transaction2)
    print("\nPrediction:")
    pprint(result2)
    
    print("\n" + "-"*50 + "\n")
    
    # Example 3: Large transaction 
    print("Transaction 3: Large Amount Transaction")
    transaction3 = {
        'type': 'TRANSFER',
        'amount': 250000.0,
        'oldbalanceOrg': 300000.0,
        'newbalanceOrig': 50000.0,
        'oldbalanceDest': 0.0,
        'newbalanceDest': 250000.0,
        'step': 1,
    }
    pprint(transaction3)
    result3 = predict_transaction(transaction3)
    print("\nPrediction:")
    pprint(result3)
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main() 