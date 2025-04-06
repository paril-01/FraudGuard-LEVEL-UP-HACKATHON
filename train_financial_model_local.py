#!/usr/bin/env python
"""
Train a fraud detection model on the financial fraud dataset using a 70:30 train-test split ratio.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
import joblib
import json

def load_financial_dataset(filepath):
    """Load the financial fraud dataset."""
    print(f"Loading financial dataset from {filepath}")
    try:
        # Try to infer header names if not in file
        column_names = [
            'transaction_id', 'user_id', 'timestamp', 'amount', 'merchant', 
            'location', 'device', 'ip_address', 'payment_method', 
            'numeric_1', 'numeric_2', 'is_fraud'
        ]
        
        df = pd.read_csv(filepath)
        
        # If no header in file, set column names
        if len(df.columns) == len(column_names):
            df.columns = column_names
        
        print(f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns")
        
        # Basic data exploration
        print("\nDataset overview:")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sample data:\n{df.head(3)}")
        
        # Check fraud distribution
        if 'is_fraud' in df.columns:
            fraud_count = df['is_fraud'].sum()
            print(f"\nFraud distribution: {fraud_count} fraudulent transactions out of {df.shape[0]} ({fraud_count/df.shape[0]*100:.2f}%)")
        
        return df
    except Exception as e:
        print(f"Error loading dataset: {str(e)}")
        sys.exit(1)

def preprocess_financial_data(df):
    """Preprocess the financial dataset for model training."""
    print("\nPreprocessing financial dataset...")
    
    # Convert date string to datetime
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M')
            
            # Extract useful time features
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            df['day_of_week'] = df['timestamp'].dt.dayofweek
        except Exception as e:
            print(f"Warning: Could not parse timestamp column: {str(e)}")
    
    # Handle categorical features
    categorical_cols = ['merchant', 'location', 'device', 'payment_method']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category').cat.codes
    
    # IP address processing - extract first octet as a proxy for country/region
    if 'ip_address' in df.columns:
        df['ip_first_octet'] = df['ip_address'].apply(lambda x: int(x.split('.')[0]) if isinstance(x, str) else 0)
        df.drop('ip_address', axis=1, inplace=True)
    
    # Drop ID columns as they shouldn't influence fraud
    id_cols = [col for col in df.columns if 'id' in col.lower()]
    df.drop(id_cols, axis=1, inplace=True)
    
    # Drop timestamp column after extracting features
    if 'timestamp' in df.columns:
        df.drop('timestamp', axis=1, inplace=True)
    
    # Get features and target
    X = df.drop('is_fraud', axis=1) if 'is_fraud' in df.columns else df
    y = df['is_fraud'] if 'is_fraud' in df.columns else None
    
    # Save feature columns for future reference
    feature_cols = X.columns.tolist()
    try:
        with open('financial_features.json', 'w') as f:
            json.dump(feature_cols, f)
    except Exception as e:
        print(f"Warning: Could not save feature list: {str(e)}")
    
    print(f"Preprocessing complete. Features: {feature_cols}")
    return X, y

def create_model(input_dim):
    """Create a model for financial fraud detection."""
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"Created model with input dimension {input_dim}")
    model.summary()
    
    return model

def train_model(X, y):
    """Train the model on financial data with 70:30 train-test split."""
    print("\nPreparing to train model on financial data...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Split data into train and test sets (70:30)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler for future use
    try:
        joblib.dump(scaler, 'models/financial_scaler.joblib')
    except Exception as e:
        print(f"Warning: Could not save feature scaler: {str(e)}")
    
    # Create a new model
    model = create_model(X_train_scaled.shape[1])
    
    # Train the model
    print("\nTraining model on financial data...")
    history = model.fit(
        X_train_scaled, y_train,
        epochs=20,  # Reduced epochs for testing
        batch_size=64,
        validation_data=(X_test_scaled, y_test),
        verbose=1
    )
    
    # Evaluate the model
    print("\nEvaluating model on test data...")
    loss, accuracy = model.evaluate(X_test_scaled, y_test)
    print(f"Test loss: {loss:.4f}")
    print(f"Test accuracy: {accuracy:.4f}")
    
    # Save the trained model
    try:
        model_save_path = 'models/financial_fraud_model.h5'
        model.save(model_save_path)
        print(f"Model saved to {model_save_path}")
    except Exception as e:
        print(f"Warning: Could not save model: {str(e)}")
    
    # Save model metrics for reference
    metrics = {
        'train_loss': float(history.history['loss'][-1]),
        'val_loss': float(history.history['val_loss'][-1]),
        'train_accuracy': float(history.history['accuracy'][-1]),
        'val_accuracy': float(history.history['val_accuracy'][-1]),
        'test_accuracy': float(accuracy),
        'test_loss': float(loss)
    }
    
    try:
        with open('models/financial_model_metrics.json', 'w') as f:
            json.dump(metrics, f)
    except Exception as e:
        print(f"Warning: Could not save model metrics: {str(e)}")
    
    return model, metrics

def main():
    """Main function to train the financial fraud model."""
    # Define the dataset file path
    dataset_file = 'c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv'
    
    if not os.path.exists(dataset_file):
        print(f"Could not find dataset at {dataset_file}")
        print("Please provide the full path to the financial dataset:")
        dataset_file = input("Path to financial dataset: ")
    
    # Load and preprocess the dataset
    df = load_financial_dataset(dataset_file)
    X, y = preprocess_financial_data(df)
    
    # Train the model
    model, metrics = train_model(X, y)
    
    print("\nFinancial fraud model training completed successfully!")
    print(f"Final accuracy: {metrics['test_accuracy']:.4f}")

if __name__ == "__main__":
    main() 