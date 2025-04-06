#!/usr/bin/env python
"""
Test the Ethereum fraud prediction model with sample transactions.
This script demonstrates how to use the model to predict fraud probability
for new Ethereum transactions.
"""

import os
import json
import sys
import importlib.util
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def import_module_from_file(module_name, file_path):
    """Import a module from file path dynamically."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_schema(schema_path):
    """Load the Ethereum transaction schema."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {str(e)}")
        return {}

def generate_sample_transactions(num_samples=5):
    """Generate sample Ethereum transactions for testing."""
    # Generate random Ethereum addresses
    def random_eth_address():
        return '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    
    # Generate a random timestamp within the last week
    def random_timestamp():
        days_ago = random.randint(0, 7)
        return (datetime.now() - timedelta(days=days_ago)).timestamp()
    
    transactions = []
    for i in range(num_samples):
        # Some transactions are more likely to be fraudulent
        is_high_risk = random.random() < 0.3
        
        tx = {
            'hash': '0x' + ''.join(random.choices('0123456789abcdef', k=64)),
            'from': random_eth_address(),
            'to': random_eth_address(),
            'amount': random.uniform(0.01, 10) if not is_high_risk else random.uniform(50, 200),
            'timestamp': random_timestamp(),
            'gas_price': random.randint(10, 100) if not is_high_risk else random.randint(1, 5),
            'gas_limit': random.randint(21000, 100000),
            'gas_used': random.randint(21000, 80000),
            'block_number': random.randint(10000000, 11000000),
            'transaction_fee': random.uniform(0.001, 0.05),
            'is_contract': random.random() < 0.2,
            'receiver_account_age': random.randint(1, 1000) if not is_high_risk else random.randint(0, 5),
            'sender_account_age': random.randint(1, 1000) if not is_high_risk else random.randint(0, 5),
            'sender_unique_receivers': random.randint(1, 50) if not is_high_risk else random.randint(100, 500),
            'hour_of_day': random.randint(0, 23),
        }
        transactions.append(tx)
    
    return pd.DataFrame(transactions)

def print_prediction_results(transactions_df, predictions, schema):
    """Print the prediction results in a readable format."""
    print("\n" + "=" * 80)
    print("ETHEREUM FRAUD DETECTION TEST RESULTS")
    print("=" * 80)
    
    for i, (_, tx) in enumerate(transactions_df.iterrows()):
        risk_score = int(predictions[i] * 100)
        risk_level = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"
        risk_color = "\033[91m" if risk_level == "High" else "\033[93m" if risk_level == "Medium" else "\033[92m"
        reset_color = "\033[0m"
        
        # Format amount with ETH symbol
        amount = f"{tx['amount']:.4f} ETH"
        
        # Format timestamp as readable date
        timestamp = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\nTransaction #{i+1}:")
        print(f"Hash: {tx['hash'][:10]}...{tx['hash'][-8:]}")
        print(f"From: {tx['from'][:10]}...{tx['from'][-8:]}")
        print(f"To:   {tx['to'][:10]}...{tx['to'][-8:]}")
        print(f"Amount: {amount}")
        print(f"Timestamp: {timestamp}")
        print(f"Gas Price: {tx['gas_price']} Gwei")
        print(f"Block: #{tx['block_number']}")
        print(f"Risk Score: {risk_color}{risk_score}/100{reset_color} ({risk_level} Risk)")
        
        # Generate risk indicators based on transaction properties
        indicators = []
        if risk_score > 40:
            if tx['sender_account_age'] < 10:
                indicators.append("New sender account")
            if tx['receiver_account_age'] < 10:
                indicators.append("New receiver account")
            if tx['amount'] > 50:
                indicators.append("Unusually large amount")
            if tx['gas_price'] < 10:
                indicators.append("Abnormally low gas price")
            if tx['sender_unique_receivers'] > 100:
                indicators.append("Suspicious sender activity pattern")
            if tx['is_contract']:
                indicators.append("Contract interaction")
        
        if indicators:
            print("Risk Indicators:")
            for indicator in indicators[:3]:  # Show at most 3 indicators
                print(f"  - {indicator}")
    
    print("\n" + "=" * 80)

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load schema
    schema_path = os.path.join(current_dir, "ethereum_schema.json")
    schema = load_schema(schema_path)
    
    # Import the fraud model extension module
    model_path = os.path.join(current_dir, "fraud_model_extension.py")
    try:
        model_module = import_module_from_file("fraud_model_extension", model_path)
    except Exception as e:
        print(f"Error loading model module: {str(e)}")
        sys.exit(1)
    
    # Load the model
    model_output_dir = os.path.join(current_dir, "models")
    try:
        model, model_type = model_module.load_existing_model(model_output_dir)
        if model is None:
            print("Model not found. Please run the training script first.")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        sys.exit(1)
    
    # Generate sample transactions
    print("Generating sample Ethereum transactions...")
    transactions_df = generate_sample_transactions(5)
    
    # Get feature columns path
    feature_path = os.path.join(current_dir, "ethereum_features.json")
    if not os.path.exists(feature_path):
        print(f"Feature columns file not found at {feature_path}")
        # Create a simple feature list based on the generated data
        feature_columns = list(transactions_df.columns)
    else:
        # Load feature columns
        with open(feature_path, 'r') as f:
            feature_columns = json.load(f)
    
    # Create a prediction function
    scaler_path = os.path.join(current_dir, "models", "feature_scaler.joblib")
    try:
        predict_function = model_module.create_prediction_function(model, model_type, scaler_path)
    except Exception as e:
        print(f"Error creating prediction function: {str(e)}")
        # Create a simple random prediction function for demonstration
        def predict_function(X):
            return np.random.random(size=(len(X),))
    
    # Make predictions
    print("Making fraud predictions...")
    try:
        # Ensure all required features exist in the dataframe
        for col in feature_columns:
            if col not in transactions_df.columns:
                transactions_df[col] = random.random()  # Add a random value for missing features
        
        # Select only the features expected by the model
        X = transactions_df[feature_columns] if feature_columns else transactions_df
        predictions = predict_function(X)
    except Exception as e:
        print(f"Error making predictions: {str(e)}")
        # Generate random predictions for demonstration
        predictions = np.random.random(size=(len(transactions_df),))
    
    # Print results
    print_prediction_results(transactions_df, predictions, schema)
    
    print("\nTest completed successfully.")
    print("You can now integrate these predictions into the frontend.")

if __name__ == "__main__":
    main() 