import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# File path
data_path = 'c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv'

# Load dataset
print("Loading dataset...")
df = pd.read_csv(data_path)
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Check fraud distribution
fraud_count = df['is_fraud'].sum()
print(f"Fraud ratio: {fraud_count/len(df):.4f} ({fraud_count} out of {len(df)})")

# Preprocess data
print("Preprocessing data...")
# Drop non-numeric columns that can't be used directly in model training
# Keep important numerical features
numeric_cols = ['amount', 'account_age_days', 'num_prev_transactions']
X = df[numeric_cols]
y = df['is_fraud']

# Split data (70% train, 30% test)
print("Creating train/test split (70/30)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(f"Training set size: {X_train.shape}")
print(f"Test set size: {X_test.shape}")

# Standardize features
print("Standardizing features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate model
print("Evaluating model...")
train_accuracy = model.score(X_train_scaled, y_train)
test_accuracy = model.score(X_test_scaled, y_test)
print(f"Training accuracy: {train_accuracy:.4f}")
print(f"Test accuracy: {test_accuracy:.4f}")

# Save model and scaler
print("Saving model and scaler...")
output_dir = '.'
os.makedirs(output_dir, exist_ok=True)
joblib.dump(model, os.path.join(output_dir, 'financial_fraud_model.joblib'))
joblib.dump(scaler, os.path.join(output_dir, 'financial_fraud_scaler.joblib'))

print("Model training complete!")
print(f"Model and scaler saved to {output_dir}") 