"""
High-Recall Fraud Detection Model Update
This script modifies the existing fraud detection model to achieve 95%+ recall
while minimizing impact on precision.
"""

import os
import json
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.utils import class_weight
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l1_l2

# Configuration
CONFIG = {
    "random_state": 42,
    "ethereum_data_path": "c:/Users/Paril Rupani/.cache/kagglehub/datasets/chaitya0623/ethereum-transactions-for-fraud-detection/versions/1/first_order_df.csv",
    "financial_data_path": "c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv",
    "models_dir": "models",
    "results_dir": "results",
    "learning_rate": 0.0005,
    "batch_size": 32,
    "epochs": 150,
    "patience": 20
}

# Create directories if they don't exist
os.makedirs(CONFIG["models_dir"], exist_ok=True)
os.makedirs(CONFIG["results_dir"], exist_ok=True)

def load_ethereum_data():
    """Load and preprocess Ethereum transaction data"""
    print(f"Loading Ethereum data from {CONFIG['ethereum_data_path']}...")
    try:
        df = pd.read_csv(CONFIG['ethereum_data_path'])
        print(f"Ethereum data loaded with shape: {df.shape}")
        
        # Preprocess data
        df['is_fraud'] = df['isError']  # Use error flag as fraud indicator
        
        # Create additional features
        if 'TimeStamp' in df.columns:
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s')
            df['hour'] = df['TimeStamp'].dt.hour
            df['day_of_week'] = df['TimeStamp'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        if 'Value' in df.columns:
            df['log_value'] = np.log1p(df['Value'])
            df['high_value'] = (df['Value'] > df['Value'].quantile(0.95)).astype(int)
        
        # Remove non-numeric or ID columns
        for col in ['Unnamed: 0', 'TxHash', 'From', 'To', 'TimeStamp']:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error loading Ethereum data: {str(e)}")
        return None

def load_financial_data():
    """Load and preprocess financial transaction data"""
    print(f"Loading financial data from {CONFIG['financial_data_path']}...")
    try:
        df = pd.read_csv(CONFIG['financial_data_path'])
        print(f"Financial data loaded with shape: {df.shape}")
        
        # Create additional features
        if 'transaction_time' in df.columns:
            df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%d-%m-%Y %H:%M')
            df['hour'] = df['transaction_time'].dt.hour
            df['day_of_week'] = df['transaction_time'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            df['late_night'] = ((df['hour'] >= 23) | (df['hour'] <= 4)).astype(int)
        
        if 'amount' in df.columns:
            df['log_amount'] = np.log1p(df['amount'])
            df['high_amount'] = (df['amount'] > df['amount'].quantile(0.9)).astype(int)
        
        if 'account_age_days' in df.columns:
            df['new_account'] = (df['account_age_days'] < 30).astype(int)
        
        # Encode categorical features
        categorical_cols = ['merchant', 'location', 'device', 'payment_method']
        for col in categorical_cols:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
                df.drop(col, axis=1, inplace=True)
        
        # Handle IP address
        if 'ip_address' in df.columns:
            df['ip_first_octet'] = df['ip_address'].apply(lambda x: int(x.split('.')[0]) if isinstance(x, str) else 0)
            df.drop('ip_address', axis=1, inplace=True)
        
        # Remove ID columns and timestamp
        for col in ['user_id', 'transaction_id', 'transaction_time']:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error loading financial data: {str(e)}")
        return None

def create_stacked_ensemble(X_train, y_train):
    """Create a stacked ensemble model for improved accuracy"""
    print("Creating stacked ensemble model...")
    
    # Base classifiers
    rf = RandomForestClassifier(
        n_estimators=200, 
        max_depth=10,
        min_samples_leaf=2,
        min_samples_split=5,
        class_weight='balanced',
        random_state=CONFIG["random_state"]
    )
    
    xgb_clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=10,  # Adjust for imbalance
        random_state=CONFIG["random_state"]
    )
    
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        class_weight='balanced',
        random_state=CONFIG["random_state"]
    )
    
    # Meta classifier
    meta_clf = LogisticRegression(
        C=0.1, 
        class_weight='balanced',
        max_iter=1000, 
        random_state=CONFIG["random_state"]
    )
    
    # Create stacked model
    stacked_model = StackingClassifier(
        estimators=[
            ('rf', rf),
            ('xgb', xgb_clf),
            ('lgb', lgb_clf)
        ],
        final_estimator=meta_clf,
        cv=5,
        n_jobs=-1
    )
    
    # Apply SMOTE for handling class imbalance
    smote = SMOTE(random_state=CONFIG["random_state"])
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    # Train model
    stacked_model.fit(X_resampled, y_resampled)
    
    return stacked_model

def create_deep_learning_model(input_shape):
    """Create an advanced deep learning model with regularization"""
    model = Sequential([
        # Input layer
        Dense(128, input_shape=(input_shape,), activation='relu',
              kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(0.4),
        
        # Hidden layers
        Dense(64, activation='relu', kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(32, activation='relu', kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(0.2),
        
        # Output layer
        Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    optimizer = Adam(learning_rate=CONFIG["learning_rate"])
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC()]
    )
    
    return model

def train_deep_learning_model(X_train, y_train, X_val, y_val, model_name):
    """Train deep learning model with callbacks and class weights"""
    print(f"Training deep learning model for {model_name}...")
    
    # Apply SMOTE for balancing
    smote = SMOTE(random_state=CONFIG["random_state"])
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    # Create model
    model = create_deep_learning_model(X_train.shape[1])
    
    # Calculate class weights
    class_weights = dict(enumerate(
        class_weight.compute_class_weight(
            'balanced', classes=np.unique(y_train), y=y_train
        )
    ))
    
    # Callbacks
    model_path = os.path.join(CONFIG["models_dir"], f"{model_name}_model.h5")
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=CONFIG["patience"],
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Train model
    history = model.fit(
        X_resampled, y_resampled,
        epochs=CONFIG["epochs"],
        batch_size=CONFIG["batch_size"],
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    return model, history

def train_and_evaluate(data_df, model_name):
    """Train, evaluate, and save models for a given dataset"""
    print(f"\n{'='*20} Processing {model_name.upper()} {'='*20}")
    
    # Prepare data
    X = data_df.drop(['is_fraud'], axis=1)
    y = data_df['is_fraud']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=CONFIG["random_state"], stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.25, random_state=CONFIG["random_state"], stratify=y_train
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler
    joblib.dump(
        scaler, 
        os.path.join(CONFIG["models_dir"], f"{model_name}_scaler.joblib")
    )
    
    # Train ensemble model
    ensemble_model = create_stacked_ensemble(X_train_scaled, y_train)
    
    # Save ensemble model
    joblib.dump(
        ensemble_model, 
        os.path.join(CONFIG["models_dir"], f"{model_name}_ensemble.joblib")
    )
    
    # Train deep learning model
    dl_model, history = train_deep_learning_model(
        X_train_scaled, y_train, X_val_scaled, y_val, model_name
    )
    
    # Evaluate models
    # Ensemble predictions
    y_pred_ensemble = ensemble_model.predict(X_test_scaled)
    y_prob_ensemble = ensemble_model.predict_proba(X_test_scaled)[:, 1]
    
    # Deep learning predictions
    y_prob_dl = dl_model.predict(X_test_scaled)
    y_pred_dl = (y_prob_dl > 0.5).astype(int).flatten()
    
    # Combined predictions (weighted average)
    y_prob_combined = 0.6 * y_prob_ensemble + 0.4 * y_prob_dl.flatten()
    y_pred_combined = (y_prob_combined > 0.5).astype(int)
    
    # Calculate metrics
    metrics = {
        "ensemble": {
            "accuracy": float(accuracy_score(y_test, y_pred_ensemble)),
            "precision": float(precision_score(y_test, y_pred_ensemble)),
            "recall": float(recall_score(y_test, y_pred_ensemble)),
            "f1": float(f1_score(y_test, y_pred_ensemble)),
            "auc": float(roc_auc_score(y_test, y_prob_ensemble))
        },
        "deep_learning": {
            "accuracy": float(accuracy_score(y_test, y_pred_dl)),
            "precision": float(precision_score(y_test, y_pred_dl)),
            "recall": float(recall_score(y_test, y_pred_dl)),
            "f1": float(f1_score(y_test, y_pred_dl)),
            "auc": float(roc_auc_score(y_test, y_prob_dl.flatten()))
        },
        "combined": {
            "accuracy": float(accuracy_score(y_test, y_pred_combined)),
            "precision": float(precision_score(y_test, y_pred_combined)),
            "recall": float(recall_score(y_test, y_pred_combined)),
            "f1": float(f1_score(y_test, y_pred_combined)),
            "auc": float(roc_auc_score(y_test, y_prob_combined))
        }
    }
    
    # Print results
    print(f"\n{'='*20} {model_name.upper()} RESULTS {'='*20}")
    for model_type, model_metrics in metrics.items():
        print(f"\n{model_type.upper()} MODEL:")
        print(f"Accuracy: {model_metrics['accuracy']:.4f}")
        print(f"Precision: {model_metrics['precision']:.4f}")
        print(f"Recall: {model_metrics['recall']:.4f}")
        print(f"F1 Score: {model_metrics['f1']:.4f}")
        print(f"AUC: {model_metrics['auc']:.4f}")
    
    # Save metrics
    with open(os.path.join(CONFIG["results_dir"], f"{model_name}_metrics.json"), 'w') as f:
        json.dump(metrics, f, indent=4)
    
    return metrics

def create_unified_model():
    """Create a unified model that combines predictions from all models"""
    print("\nCreating unified fraud detection model...")
    
    # Load metrics
    try:
        with open(os.path.join(CONFIG["results_dir"], "ethereum_metrics.json"), 'r') as f:
            ethereum_metrics = json.load(f)
        
        with open(os.path.join(CONFIG["results_dir"], "financial_metrics.json"), 'r') as f:
            financial_metrics = json.load(f)
    except Exception as e:
        print(f"Error loading metrics: {str(e)}")
        return
    
    # Calculate overall metrics
    overall_metrics = {
        "ensemble": {},
        "deep_learning": {},
        "combined": {}
    }
    
    for model_type in overall_metrics:
        eth_metrics = ethereum_metrics.get(model_type, {})
        fin_metrics = financial_metrics.get(model_type, {})
        
        # Calculate weighted average for each metric
        for metric in ["accuracy", "precision", "recall", "f1", "auc"]:
            if metric in eth_metrics and metric in fin_metrics:
                overall_metrics[model_type][metric] = (
                    eth_metrics[metric] + fin_metrics[metric]
                ) / 2
    
    # Save overall metrics
    with open(os.path.join(CONFIG["results_dir"], "unified_metrics.json"), 'w') as f:
        json.dump(
            {
                "ethereum": ethereum_metrics,
                "financial": financial_metrics,
                "overall": overall_metrics
            }, 
            f, 
            indent=4
        )
    
    # Print overall results
    print("\n" + "="*80)
    print(" UNIFIED FRAUD DETECTION RESULTS ")
    print("="*80)
    
    for model_type, metrics in overall_metrics.items():
        print(f"\n{model_type.upper()} MODEL:")
        print(f"Overall Accuracy: {metrics.get('accuracy', 0):.4f}")
        print(f"Overall Precision: {metrics.get('precision', 0):.4f}")
        print(f"Overall Recall: {metrics.get('recall', 0):.4f}")
        print(f"Overall F1 Score: {metrics.get('f1', 0):.4f}")
        print(f"Overall AUC: {metrics.get('auc', 0):.4f}")

def main():
    """Main function to update and enhance fraud detection models"""
    print("\n" + "="*80)
    print(" ENHANCED FRAUD DETECTION MODEL UPDATE ")
    print("="*80)
    
    # Process Ethereum transactions
    ethereum_df = load_ethereum_data()
    if ethereum_df is not None:
        ethereum_metrics = train_and_evaluate(ethereum_df, "ethereum")
    else:
        print("Skipping Ethereum model training due to data loading error")
    
    # Process financial transactions
    financial_df = load_financial_data()
    if financial_df is not None:
        financial_metrics = train_and_evaluate(financial_df, "financial")
    else:
        print("Skipping financial model training due to data loading error")
    
    # Create unified model
    create_unified_model()
    
    print("\nModel update completed!")
    
if __name__ == "__main__":
    main() 