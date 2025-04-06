"""
High-Recall Fraud Detection Model Results
This script demonstrates the performance of the enhanced fraud detection model
with 95%+ recall target.
"""

import json
import os
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
CONFIG = {
    "random_state": 42,
    "ethereum_data_path": "c:/Users/Paril Rupani/.cache/kagglehub/datasets/chaitya0623/ethereum-transactions-for-fraud-detection/versions/1/first_order_df.csv",
    "financial_data_path": "c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv",
    "models_dir": "models",
    "results_dir": "results",
    "threshold_calibration": True,
    "calibrated_thresholds": {
        "ethereum": {
            "ensemble": 0.42,
            "deep_learning": 0.46,
            "combined": 0.44
        },
        "financial": {
            "ensemble": 0.38,
            "deep_learning": 0.41,
            "combined": 0.40
        }
    }
}

class EnhancedFraudDetector:
    """Advanced fraud detection model with optimized metrics"""
    
    def __init__(self):
        """Initialize the enhanced fraud detector"""
        self.models = {
            "ethereum": {
                "ensemble": None,
                "deep_learning": None,
                "scaler": None
            },
            "financial": {
                "ensemble": None,
                "deep_learning": None,
                "scaler": None
            }
        }
        
        self.metrics = {
            "ethereum": {},
            "financial": {},
            "combined": {}
        }
        
        # Create directories if they don't exist
        os.makedirs(CONFIG["models_dir"], exist_ok=True)
        os.makedirs(CONFIG["results_dir"], exist_ok=True)
    
    def load_models(self):
        """Load all trained models and scalers"""
        print("\nLoading models and scalers...")
        
        for transaction_type in ["ethereum", "financial"]:
            # Load ensemble model
            ensemble_path = os.path.join(CONFIG["models_dir"], f"{transaction_type}_ensemble.joblib")
            if os.path.exists(ensemble_path):
                try:
                    self.models[transaction_type]["ensemble"] = joblib.load(ensemble_path)
                    print(f"Loaded {transaction_type} ensemble model from {ensemble_path}")
                except Exception as e:
                    print(f"Error loading {transaction_type} ensemble model: {str(e)}")
            
            # Load deep learning model
            dl_path = os.path.join(CONFIG["models_dir"], f"{transaction_type}_model.h5")
            if os.path.exists(dl_path):
                try:
                    self.models[transaction_type]["deep_learning"] = load_model(dl_path)
                    print(f"Loaded {transaction_type} deep learning model from {dl_path}")
                except Exception as e:
                    print(f"Error loading {transaction_type} deep learning model: {str(e)}")
            
            # Load scaler
            scaler_path = os.path.join(CONFIG["models_dir"], f"{transaction_type}_scaler.joblib")
            if os.path.exists(scaler_path):
                try:
                    self.models[transaction_type]["scaler"] = joblib.load(scaler_path)
                    print(f"Loaded {transaction_type} scaler from {scaler_path}")
                except Exception as e:
                    print(f"Error loading {transaction_type} scaler: {str(e)}")
    
    def preprocess_ethereum_data(self, df):
        """Preprocess Ethereum data for model evaluation"""
        # Create target column if not exists
        if 'is_fraud' not in df.columns and 'isError' in df.columns:
            df['is_fraud'] = df['isError']
        
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
    
    def preprocess_financial_data(self, df):
        """Preprocess financial data for model evaluation"""
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
    
    def load_and_preprocess_data(self, transaction_type):
        """Load and preprocess data for evaluation"""
        print(f"\nLoading and preprocessing {transaction_type} data...")
        
        if transaction_type == "ethereum":
            # Load Ethereum data
            try:
                df = pd.read_csv(CONFIG["ethereum_data_path"])
                print(f"Loaded {transaction_type} data with shape: {df.shape}")
                return self.preprocess_ethereum_data(df)
            except Exception as e:
                print(f"Error loading {transaction_type} data: {str(e)}")
                return None
        
        elif transaction_type == "financial":
            # Load financial data
            try:
                df = pd.read_csv(CONFIG["financial_data_path"])
                print(f"Loaded {transaction_type} data with shape: {df.shape}")
                return self.preprocess_financial_data(df)
            except Exception as e:
                print(f"Error loading {transaction_type} data: {str(e)}")
                return None
    
    def apply_hyper_ensemble(self, X, transaction_type):
        """Apply hyper-ensemble technique with optimized threshold calibration"""
        # Get models and threshold
        ensemble_model = self.models[transaction_type]["ensemble"]
        dl_model = self.models[transaction_type]["deep_learning"]
        
        # Default thresholds if not using threshold calibration
        ensemble_threshold = 0.5
        dl_threshold = 0.5
        combined_threshold = 0.5
        
        # Use calibrated thresholds if enabled
        if CONFIG["threshold_calibration"]:
            ensemble_threshold = CONFIG["calibrated_thresholds"][transaction_type]["ensemble"]
            dl_threshold = CONFIG["calibrated_thresholds"][transaction_type]["deep_learning"]
            combined_threshold = CONFIG["calibrated_thresholds"][transaction_type]["combined"]
        
        # Get predictions
        ensemble_prob = ensemble_model.predict_proba(X)[:, 1]
        dl_prob = dl_model.predict(X).flatten()
        
        # Calculate weighted ensemble
        # Higher weight to better performing model (determined during training)
        if transaction_type == "ethereum":
            combined_prob = 0.4 * ensemble_prob + 0.6 * dl_prob
        else:
            combined_prob = 0.6 * ensemble_prob + 0.4 * dl_prob
        
        # Apply thresholds
        ensemble_pred = (ensemble_prob >= ensemble_threshold).astype(int)
        dl_pred = (dl_prob >= dl_threshold).astype(int)
        combined_pred = (combined_prob >= combined_threshold).astype(int)
        
        return {
            "ensemble": {
                "prob": ensemble_prob,
                "pred": ensemble_pred
            },
            "deep_learning": {
                "prob": dl_prob,
                "pred": dl_pred
            },
            "combined": {
                "prob": combined_prob,
                "pred": combined_pred
            }
        }
    
    def evaluate_transaction_type(self, transaction_type):
        """Evaluate models on a specific transaction type"""
        print(f"\n{'='*20} Evaluating {transaction_type.upper()} TRANSACTIONS {'='*20}")
        
        # Load and preprocess data
        df = self.load_and_preprocess_data(transaction_type)
        if df is None:
            print(f"Could not evaluate {transaction_type} transactions due to data loading error")
            return
        
        # Check if required models and scaler are available
        if (self.models[transaction_type]["ensemble"] is None or 
            self.models[transaction_type]["deep_learning"] is None or
            self.models[transaction_type]["scaler"] is None):
            print(f"Could not evaluate {transaction_type} transactions due to missing models or scaler")
            return
        
        # Split features and target
        X = df.drop('is_fraud', axis=1)
        y = df['is_fraud']
        
        # Apply scaler
        X_scaled = self.models[transaction_type]["scaler"].transform(X)
        
        # Apply hyper-ensemble
        predictions = self.apply_hyper_ensemble(X_scaled, transaction_type)
        
        # Calculate metrics
        transaction_metrics = {}
        
        for model_type in ["ensemble", "deep_learning", "combined"]:
            y_pred = predictions[model_type]["pred"]
            y_prob = predictions[model_type]["prob"]
            
            # Calculate metrics
            transaction_metrics[model_type] = {
                "accuracy": float(accuracy_score(y, y_pred)),
                "precision": float(precision_score(y, y_pred)),
                "recall": float(recall_score(y, y_pred)),
                "f1": float(f1_score(y, y_pred)),
                "auc": float(roc_auc_score(y, y_prob)),
                "confusion_matrix": confusion_matrix(y, y_pred).tolist()
            }
        
        # Store metrics
        self.metrics[transaction_type] = transaction_metrics
        
        # Print results
        print(f"\nResults for {transaction_type.upper()}:")
        for model_type, metrics in transaction_metrics.items():
            print(f"\n{model_type.upper()} MODEL:")
            print(f"Accuracy: {metrics['accuracy']:.4f}")
            print(f"Precision: {metrics['precision']:.4f}")
            print(f"Recall: {metrics['recall']:.4f}")
            print(f"F1 Score: {metrics['f1']:.4f}")
            print(f"AUC: {metrics['auc']:.4f}")
        
        # Plot confusion matrices
        self.plot_confusion_matrices(transaction_type, transaction_metrics)
    
    def plot_confusion_matrices(self, transaction_type, metrics):
        """Plot confusion matrices for each model type"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, model_type in enumerate(["ensemble", "deep_learning", "combined"]):
            cm = np.array(metrics[model_type]["confusion_matrix"])
            
            sns.heatmap(
                cm, 
                annot=True, 
                fmt="d", 
                cmap="Blues", 
                cbar=False,
                ax=axes[i]
            )
            
            axes[i].set_xlabel('Predicted')
            axes[i].set_ylabel('Actual')
            axes[i].set_title(f"{transaction_type.capitalize()} - {model_type.capitalize()}")
            axes[i].set_xticklabels(['Normal', 'Fraud'])
            axes[i].set_yticklabels(['Normal', 'Fraud'])
        
        plt.tight_layout()
        plt.savefig(os.path.join(CONFIG["results_dir"], f"{transaction_type}_confusion_matrices.png"))
    
    def compute_combined_metrics(self):
        """Compute combined metrics across all transaction types"""
        print("\nComputing combined metrics across all transaction types...")
        
        # Skip if any transaction type is missing
        for transaction_type in ["ethereum", "financial"]:
            if not self.metrics.get(transaction_type):
                print(f"Cannot compute combined metrics: missing {transaction_type} metrics")
                return
        
        # Calculate combined metrics for each model type
        combined_metrics = {}
        
        for model_type in ["ensemble", "deep_learning", "combined"]:
            # Get metrics for each transaction type
            eth_metrics = self.metrics["ethereum"][model_type]
            fin_metrics = self.metrics["financial"][model_type]
            
            # Calculate weighted average (equal weight for simplicity)
            combined_metrics[model_type] = {
                "accuracy": (eth_metrics["accuracy"] + fin_metrics["accuracy"]) / 2,
                "precision": (eth_metrics["precision"] + fin_metrics["precision"]) / 2,
                "recall": (eth_metrics["recall"] + fin_metrics["recall"]) / 2,
                "f1": (eth_metrics["f1"] + fin_metrics["f1"]) / 2,
                "auc": (eth_metrics["auc"] + fin_metrics["auc"]) / 2
            }
        
        # Store combined metrics
        self.metrics["combined"] = combined_metrics
        
        # Print results
        print("\n" + "="*80)
        print(" COMBINED METRICS ACROSS ALL TRANSACTION TYPES ")
        print("="*80)
        
        for model_type, metrics in combined_metrics.items():
            print(f"\n{model_type.upper()} MODEL:")
            print(f"Accuracy: {metrics['accuracy']:.4f}")
            print(f"Precision: {metrics['precision']:.4f}")
            print(f"Recall: {metrics['recall']:.4f}")
            print(f"F1 Score: {metrics['f1']:.4f}")
            print(f"AUC: {metrics['auc']:.4f}")
    
    def plot_combined_metrics(self):
        """Plot combined metrics for visualization"""
        if not self.metrics.get("combined"):
            print("Cannot plot combined metrics: combined metrics not computed")
            return
        
        # Metrics to plot
        metrics_list = ["accuracy", "precision", "recall", "f1", "auc"]
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Set up bar positions
        x = np.arange(len(metrics_list))
        width = 0.25
        
        # Plot bars for each model type
        for i, model_type in enumerate(["ensemble", "deep_learning", "combined"]):
            values = [self.metrics["combined"][model_type][m] for m in metrics_list]
            plt.bar(x + (i-1)*width, values, width, label=model_type.capitalize())
        
        # Add labels and legend
        plt.xlabel('Metrics')
        plt.ylabel('Score')
        plt.title('Combined Fraud Detection Performance Across All Transaction Types')
        plt.xticks(x, [m.capitalize() for m in metrics_list])
        plt.ylim(0.5, 1.0)  # Set y-axis limits
        plt.legend(loc='lower right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add 99% accuracy target line
        plt.axhline(y=0.99, color='r', linestyle='--', alpha=0.5)
        plt.text(0.5, 0.991, '99% Performance Target', color='r')
        
        plt.tight_layout()
        plt.savefig(os.path.join(CONFIG["results_dir"], "combined_metrics.png"))
        print(f"\nCombined metrics chart saved to {os.path.join(CONFIG['results_dir'], 'combined_metrics.png')}")
    
    def save_metrics(self):
        """Save all metrics to a JSON file"""
        output_path = "enhanced_model_results.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)
        
        print(f"\nAll metrics saved to {output_path}")
    
    def run(self):
        """Run the entire evaluation pipeline"""
        print("\n" + "="*80)
        print(" ENHANCED FRAUD DETECTION MODEL EVALUATION ")
        print("="*80)
        
        # Load all models
        self.load_models()
        
        # Evaluate each transaction type
        self.evaluate_transaction_type("ethereum")
        self.evaluate_transaction_type("financial")
        
        # Compute combined metrics
        self.compute_combined_metrics()
        
        # Plot combined metrics
        self.plot_combined_metrics()
        
        # Save metrics
        self.save_metrics()
        
        print("\nEvaluation complete!")
        
        if self.metrics.get("combined"):
            # Check if we achieved 99% for each metric
            targets_met = True
            for model_type in ["ensemble", "deep_learning", "combined"]:
                for metric in ["accuracy", "precision", "recall", "f1", "auc"]:
                    if self.metrics["combined"][model_type][metric] < 0.99:
                        targets_met = False
            
            if targets_met:
                print("\n🎉 SUCCESS! 99%+ performance achieved across all metrics! 🎉")
            else:
                print("\nSome metrics are still below 99%. Consider further model improvements:")
                print("1. Additional feature engineering")
                print("2. Hyperparameter tuning")
                print("3. More advanced ensemble techniques")
                print("4. Further threshold calibration")

def main():
    """Main function to run the enhanced fraud detection evaluation"""
    detector = EnhancedFraudDetector()
    detector.run()

if __name__ == "__main__":
    main() 