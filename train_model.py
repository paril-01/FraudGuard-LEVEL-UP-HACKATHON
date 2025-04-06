import pandas as pd
import numpy as np
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt

# File path to the dataset
DATA_PATH = 'c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv'

print("========== FINANCIAL FRAUD DETECTION MODEL ==========")
print(f"Loading dataset from {DATA_PATH}")

# Load the dataset
df = pd.read_csv(DATA_PATH)
print(f"Dataset shape: {df.shape}")
print(f"Column names: {df.columns.tolist()}")

# Display sample data
print("\nSample data:")
print(df.head(2))

# Check fraud distribution
fraud_count = df['is_fraud'].sum()
print(f"\nFraud distribution: {fraud_count} fraudulent transactions out of {df.shape[0]} ({fraud_count/df.shape[0]*100:.2f}%)")

# Preprocess data
print("\nPreprocessing data...")

# Process timestamp if it exists
if 'transaction_time' in df.columns:
    try:
        df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%d-%m-%Y %H:%M')
        df['hour'] = df['transaction_time'].dt.hour
        df['day'] = df['transaction_time'].dt.day
        df['month'] = df['transaction_time'].dt.month
        df['day_of_week'] = df['transaction_time'].dt.dayofweek
    except Exception as e:
        print(f"Warning: Could not parse timestamp column: {str(e)}")

# Handle categorical features
categorical_cols = ['merchant', 'location', 'device', 'payment_method']
for col in categorical_cols:
    if col in df.columns:
        # Convert categorical to numeric
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        print(f"Encoded {col} with {len(le.classes_)} unique values")

# Process IP address if it exists
if 'ip_address' in df.columns:
    df['ip_first_octet'] = df['ip_address'].apply(lambda x: int(x.split('.')[0]) if isinstance(x, str) else 0)
    df.drop('ip_address', axis=1, inplace=True)

# Drop ID columns
id_cols = [col for col in df.columns if 'id' in col.lower()]
print(f"Dropping ID columns: {id_cols}")
df = df.drop(id_cols, axis=1)

# Drop timestamp after extracting features
if 'transaction_time' in df.columns:
    df.drop('transaction_time', axis=1, inplace=True)

# Keep track of remaining columns
print(f"Columns after preprocessing: {df.columns.tolist()}")

# Create features and target
X = df.drop('is_fraud', axis=1)
y = df['is_fraud']

# Split data (70% train, 30% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
print(f"\nTrain set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Build model
print("\nBuilding and training model...")
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train the model
history = model.fit(
    X_train_scaled, y_train,
    epochs=20,
    batch_size=32,
    validation_data=(X_test_scaled, y_test),
    verbose=1
)

# Evaluate the model
print("\nEvaluating model...")
loss, accuracy = model.evaluate(X_test_scaled, y_test)
print(f"Test loss: {loss:.4f}")
print(f"Test accuracy: {accuracy:.4f}")

# Create output directory if it doesn't exist
output_dir = 'models'
os.makedirs(output_dir, exist_ok=True)

# Save the model
model_path = os.path.join(output_dir, 'financial_fraud_model.h5')
model.save(model_path)
print(f"\nModel saved to {model_path}")

# Plot training history
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Loss Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Accuracy Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'training_history.png'))
print(f"Training history plot saved to {os.path.join(output_dir, 'training_history.png')}")

print("\nTraining complete!") 