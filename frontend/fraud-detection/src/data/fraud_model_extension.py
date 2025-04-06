import os
import numpy as np
import pandas as pd
import json
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input, concatenate
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, f1_score

# This file is designed to extend the existing fraud detection model
# to handle Ethereum transactions in addition to regular banking transactions.

def load_ethereum_data(data_path='frontend/fraud-detection/src/data/ethereum_processed.csv',
                      feature_path='frontend/fraud-detection/src/data/ethereum_features.json'):
    """
    Load preprocessed Ethereum transaction data
    """
    try:
        df = pd.read_csv(data_path)
        
        with open(feature_path, 'r') as f:
            feature_info = json.load(f)
        
        X_columns = feature_info['feature_columns']
        target_column = feature_info['target_column']
        
        X = df[X_columns]
        y = df[target_column] if target_column in df.columns and not df[target_column].isnull().all() else None
        
        return X, y, X_columns
    except Exception as e:
        print(f"Error loading Ethereum data: {e}")
        return None, None, None

def load_existing_model(model_path='frontend/fraud-detection/src/models/fraud_detection_model.h5'):
    """
    Load the existing fraud detection model
    """
    try:
        # Check for TensorFlow model
        if os.path.exists(model_path):
            print(f"Loading TensorFlow model from {model_path}")
            model = load_model(model_path)
            model_type = 'tensorflow'
        # Check for scikit-learn model
        elif os.path.exists(model_path.replace('.h5', '.joblib')):
            print(f"Loading scikit-learn model from {model_path.replace('.h5', '.joblib')}")
            model = joblib.load(model_path.replace('.h5', '.joblib'))
            model_type = 'sklearn'
        else:
            print("No existing model found, will train from scratch")
            model = None
            model_type = None
        
        return model, model_type
    except Exception as e:
        print(f"Error loading existing model: {e}")
        return None, None

def create_extended_model(base_model=None, model_type=None, input_dim=None):
    """
    Create or extend the model to handle Ethereum transactions
    """
    if model_type == 'tensorflow' and base_model is not None:
        # Extract the last few layers of the base model
        base_layers = base_model.layers[:-2]  # Remove the last two layers
        
        # Create a new input for Ethereum features
        eth_input = Input(shape=(input_dim,), name="ethereum_input")
        
        # Create the Ethereum processing branch
        eth_branch = Dense(64, activation='relu')(eth_input)
        eth_branch = BatchNormalization()(eth_branch)
        eth_branch = Dropout(0.3)(eth_branch)
        eth_branch = Dense(32, activation='relu')(eth_branch)
        
        # Get the output from the base model's intermediate layer
        base_output = base_layers[-1].output
        
        # Combine the outputs
        combined = concatenate([base_output, eth_branch])
        
        # Add final layers
        x = Dense(32, activation='relu')(combined)
        x = Dropout(0.2)(x)
        output = Dense(1, activation='sigmoid')(x)
        
        # Create the new model
        extended_model = Model(inputs=[base_model.input, eth_input], outputs=output)
        
        # Compile the model
        extended_model.compile(
            loss='binary_crossentropy',
            optimizer=Adam(learning_rate=0.001),
            metrics=['accuracy']
        )
        
        return extended_model, 'tensorflow_extended'
    
    elif model_type == 'sklearn' and base_model is not None:
        # For sklearn, we'll create a new ensemble model that includes both models
        extended_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        return extended_model, 'sklearn'
    
    else:
        # Create a new model from scratch
        model = Sequential([
            Dense(64, activation='relu', input_dim=input_dim),
            BatchNormalization(),
            Dropout(0.3),
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            loss='binary_crossentropy',
            optimizer=Adam(learning_rate=0.001),
            metrics=['accuracy']
        )
        
        return model, 'tensorflow'

def train_model(model, model_type, X, y, validation_split=0.2, epochs=50, batch_size=32):
    """
    Train the model on Ethereum transaction data
    """
    if y is None:
        print("No labels available for training. Skipping training phase.")
        return model, {}
    
    # Split data into train and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Save the scaler for future use
    joblib.dump(scaler, 'frontend/fraud-detection/src/models/ethereum_scaler.joblib')
    
    # Train the model
    if 'tensorflow' in model_type:
        history = model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        # Evaluate the model
        metrics = {
            'train_loss': history.history['loss'][-1],
            'val_loss': history.history['val_loss'][-1],
            'train_accuracy': history.history['accuracy'][-1],
            'val_accuracy': history.history['val_accuracy'][-1]
        }
        
        # Save the training history
        with open('frontend/fraud-detection/src/models/ethereum_training_history.json', 'w') as f:
            json.dump(history.history, f)
    
    else:  # sklearn model
        model.fit(X_train_scaled, y_train)
        
        # Evaluate the model
        train_preds = model.predict(X_train_scaled)
        val_preds = model.predict(X_val_scaled)
        
        metrics = {
            'train_accuracy': accuracy_score(y_train, train_preds),
            'val_accuracy': accuracy_score(y_val, val_preds),
            'train_f1': f1_score(y_train, train_preds, average='weighted'),
            'val_f1': f1_score(y_val, val_preds, average='weighted')
        }
    
    return model, metrics

def save_model(model, model_type, output_dir='frontend/fraud-detection/src/models'):
    """
    Save the extended or new model
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if 'tensorflow' in model_type:
        model_path = os.path.join(output_dir, 'ethereum_fraud_model.h5')
        model.save(model_path)
    else:
        model_path = os.path.join(output_dir, 'ethereum_fraud_model.joblib')
        joblib.dump(model, model_path)
    
    print(f"Model saved to {model_path}")
    return model_path

def create_prediction_function(model, model_type, scaler_path='frontend/fraud-detection/src/models/ethereum_scaler.joblib'):
    """
    Create a prediction function that can be used by the frontend
    """
    scaler = joblib.load(scaler_path)
    
    def predict_fraud_probability(transaction_features):
        """
        Predict the probability of fraud for a given transaction
        
        Args:
            transaction_features: A dictionary of features for the transaction
            
        Returns:
            fraud_probability: Probability that the transaction is fraudulent (0-1)
            risk_score: Risk score (0-100)
            is_fraud: Boolean indicating if the transaction is likely fraudulent
        """
        # Convert features to a format the model can use
        features = []
        for feature in model.feature_names_in_:
            features.append(transaction_features.get(feature, 0))
        
        features = np.array(features).reshape(1, -1)
        features_scaled = scaler.transform(features)
        
        # Make prediction
        if 'tensorflow' in model_type:
            fraud_probability = model.predict(features_scaled)[0][0]
        else:
            fraud_probability = model.predict_proba(features_scaled)[0][1]
        
        # Convert to risk score (0-100)
        risk_score = int(fraud_probability * 100)
        
        # Determine if transaction is likely fraudulent
        # Can adjust threshold based on desired sensitivity
        is_fraud = fraud_probability > 0.7  
        
        return {
            'fraud_probability': float(fraud_probability),
            'risk_score': risk_score,
            'is_fraud': bool(is_fraud)
        }
    
    # Save the prediction function to be imported by the frontend
    with open('frontend/fraud-detection/src/models/ethereum_prediction_info.json', 'w') as f:
        json.dump({
            'model_type': model_type,
            'scaler_path': scaler_path,
            'feature_names': list(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else []
        }, f)
    
    return predict_fraud_probability

def main():
    # Load the Ethereum dataset
    X_eth, y_eth, feature_columns = load_ethereum_data()
    if X_eth is None:
        print("Failed to load Ethereum data. Exiting.")
        return
    
    print(f"Loaded Ethereum data with {X_eth.shape[1]} features and {X_eth.shape[0]} samples")
    
    # Load the existing model if available
    base_model, model_type = load_existing_model()
    
    # Create or extend the model
    model, model_type = create_extended_model(base_model, model_type, input_dim=X_eth.shape[1])
    
    # Train the model on Ethereum data
    model, metrics = train_model(model, model_type, X_eth, y_eth)
    
    # Save the extended model
    model_path = save_model(model, model_type)
    
    # Create prediction function
    if model_type == 'sklearn':
        try:
            predict_func = create_prediction_function(model, model_type)
            print("Prediction function created successfully")
        except Exception as e:
            print(f"Error creating prediction function: {e}")
    
    print("Model extension complete!")
    print(f"Model metrics: {metrics}")

if __name__ == "__main__":
    main() 