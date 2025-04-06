"""
Enhanced Fraud Detection Model with High Recall (95%+)
This implementation uses ensemble methods, threshold optimization,
advanced feature engineering, and a two-stage classification approach.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import joblib
import tensorflow as tf
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, PowerTransformer
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l1_l2

# Configuration
CONFIG = {
    "random_state": 42,
    "test_size": 0.2,
    "n_splits": 5,
    "ethereum_data_path": "c:/Users/Paril Rupani/.cache/kagglehub/datasets/chaitya0623/ethereum-transactions-for-fraud-detection/versions/1/first_order_df.csv",
    "financial_data_path": "c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv",
    "models_dir": "models",
    "results_dir": "results",
    "deep_learning": {
        "batch_size": 64,
        "epochs": 100,
        "patience": 15,
        "learning_rate": 0.001,
        "dropout_rate": 0.4
    },
    "ensemble": {
        "n_estimators": 200,
        "max_depth": 10
    }
}

# Ensure directories exist
os.makedirs(CONFIG["models_dir"], exist_ok=True)
os.makedirs(CONFIG["results_dir"], exist_ok=True)

class EnhancedFraudDetectionModel:
    def __init__(self):
        # Model containers
        self.models = {}
        self.thresholds = {}
        self.scalers = {}
        self.feature_names = {}
        self.feature_importances = {}
        
        # Performance metrics
        self.metrics = {}
        
        # Features importance trackers
        self.global_feature_importance = {}
        
    def preprocess_data(self, data, target_column, test_size=0.3):
        """Preprocess data with advanced feature engineering"""
        print(f"Original dataset shape: {data.shape}")
        
        # Keep original features for reference
        original_features = data.drop(columns=[target_column]).columns.tolist()
        
        # 1. FEATURE ENGINEERING
        df = data.copy()
        
        # 1.1 Time-based features (if timestamp exists)
        time_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if time_columns:
            time_col = time_columns[0]
            # Try to convert to datetime if not already
            if not pd.api.types.is_datetime64_dtype(df[time_col]):
                try:
                    df[time_col] = pd.to_datetime(df[time_col])
                except:
                    # If it's a numeric time feature (e.g., seconds since epoch)
                    if pd.api.types.is_numeric_dtype(df[time_col]):
                        # Just use it as is for time-based calculations
                        pass
                    else:
                        # Can't use this column as time
                        time_col = None
            
            if time_col:
                # Extract time components
                df['hour_of_day'] = df[time_col].dt.hour if hasattr(df[time_col], 'dt') else np.nan
                df['day_of_week'] = df[time_col].dt.dayofweek if hasattr(df[time_col], 'dt') else np.nan
                df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0) if 'day_of_week' in df else np.nan
                
                # Transaction velocity - time since last transaction (requires sorted data)
                # This is a simplification and would need to be per-user in a real system
                if hasattr(df[time_col], 'diff'):
                    df['time_since_last_tx'] = df[time_col].diff().dt.total_seconds()
                    df['time_since_last_tx'].fillna(df['time_since_last_tx'].median(), inplace=True)
        
        # 1.2 Amount-based features
        amount_columns = [col for col in df.columns if 'amount' in col.lower() or 'sum' in col.lower() or 'total' in col.lower()]
        
        if amount_columns:
            amount_col = amount_columns[0]
            # Get stats on amount
            df['amount_log'] = np.log1p(df[amount_col])
            
            # Flag for outlier amounts (Z-score method)
            mean_amount = df[amount_col].mean()
            std_amount = df[amount_col].std()
            df['amount_zscore'] = (df[amount_col] - mean_amount) / std_amount
            df['is_amount_outlier'] = np.where(np.abs(df['amount_zscore']) > 3, 1, 0)
        
        # 1.3 Create interaction features
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != target_column]
        
        if len(numeric_cols) >= 2:
            # Create some interaction features between most likely fraud indicators
            # This is a simplified approach - in practice you'd want domain knowledge
            for i in range(min(len(numeric_cols), 3)):
                for j in range(i+1, min(len(numeric_cols), 4)):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    df[f'{col1}_x_{col2}'] = df[col1] * df[col2]
                    df[f'{col1}_plus_{col2}'] = df[col1] + df[col2]
                    df[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-8)  # Avoid division by zero
        
        # Drop any constant columns
        const_columns = [col for col in df.columns if df[col].nunique() <= 1]
        df.drop(columns=const_columns, inplace=True, errors='ignore')
        
        # Fill missing values
        for col in df.columns:
            if col != target_column:
                if df[col].isna().sum() > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col].fillna(df[col].median(), inplace=True)
                    else:
                        df[col].fillna(df[col].mode()[0], inplace=True)
        
        # Drop columns with high correlation
        corr_matrix = df.select_dtypes(include=np.number).corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        high_corr_cols = [column for column in upper.columns if any(upper[column] > 0.95)]
        df.drop(columns=high_corr_cols, inplace=True, errors='ignore')
        
        # Prepare target and features
        y = df[target_column]
        X = df.drop(columns=[target_column])
        
        # Store feature names for later use
        self.feature_names['all'] = X.columns.tolist()
        
        # Address class imbalance with SMOTE
        fraud_ratio = y.mean()
        print(f"Fraud ratio: {fraud_ratio:.4f} ({fraud_ratio*100:.2f}%)")
        
        if fraud_ratio < 0.3:  # Apply SMOTE only if imbalanced
            print("Applying SMOTE to balance classes...")
            smote = SMOTE(random_state=42)
            # Only apply SMOTE to the training data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
            
            # Scale before SMOTE
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Apply SMOTE
            X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)
            
            print(f"Original training class distribution: {np.bincount(y_train)}")
            print(f"Resampled training class distribution: {np.bincount(y_train_smote)}")
            
            return X_train_smote, X_test_scaled, y_train_smote, y_test, scaler, X.columns.tolist()
        else:
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
            
            # Scale the data
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            return X_train_scaled, X_test_scaled, y_train, y_test, scaler, X.columns.tolist()
        
    def train_models(self, X_train, y_train):
        """Train multiple models for ensemble approach"""
        print("Training multiple models for ensemble...")
        
        # Base models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1),
            'xgboost': XGBClassifier(n_estimators=100, scale_pos_weight=sum(y_train==0)/sum(y_train==1), random_state=42),
            'gradient_boost': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        # Train all models
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            self.models[name] = model
            
            # Store feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importances[name] = model.feature_importances_
        
        return models
    
    def optimize_thresholds(self, X_val, y_val, min_recall=0.95):
        """Find optimal thresholds to maximize F1 score while maintaining minimum recall"""
        print(f"Optimizing classification thresholds for minimum {min_recall:.2f} recall...")
        
        thresholds = {}
        
        for name, model in self.models.items():
            # Get probability predictions
            y_prob = model.predict_proba(X_val)[:, 1]
            
            # Try different thresholds
            best_f1 = 0
            best_threshold = 0.5
            best_metrics = None
            
            for threshold in np.arange(0.01, 0.5, 0.01):
                y_pred = (y_prob >= threshold).astype(int)
                recall = recall_score(y_val, y_pred)
                
                # Only consider thresholds that meet minimum recall
                if recall >= min_recall:
                    precision = precision_score(y_val, y_pred)
                    f1 = f1_score(y_val, y_pred)
                    
                    if f1 > best_f1:
                        best_f1 = f1
                        best_threshold = threshold
                        best_metrics = {
                            'threshold': threshold,
                            'precision': precision,
                            'recall': recall,
                            'f1': f1
                        }
            
            if best_metrics:
                print(f"{name} - Best threshold: {best_threshold:.2f}, Precision: {best_metrics['precision']:.4f}, Recall: {best_metrics['recall']:.4f}, F1: {best_metrics['f1']:.4f}")
            else:
                # If no threshold meets the recall requirement, use a very low threshold
                best_threshold = 0.01
                y_pred = (y_prob >= best_threshold).astype(int)
                recall = recall_score(y_val, y_pred)
                precision = precision_score(y_val, y_pred)
                f1 = f1_score(y_val, y_pred)
                print(f"{name} - Using threshold: {best_threshold:.2f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
            
            thresholds[name] = best_threshold
        
        self.thresholds = thresholds
        return thresholds
    
    def ensemble_predict(self, X, voting='soft'):
        """Make predictions using all models with optimized thresholds"""
        if not self.models:
            raise ValueError("Models have not been trained yet.")
        
        predictions = {}
        probabilities = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            threshold = self.thresholds.get(name, 0.5)
            probs = model.predict_proba(X)[:, 1]
            preds = (probs >= threshold).astype(int)
            
            predictions[name] = preds
            probabilities[name] = probs
        
        # Combine predictions
        if voting == 'hard':
            # Simple majority vote
            final_pred = np.zeros(len(X))
            for name, preds in predictions.items():
                final_pred += preds
            
            # If more than half of the models predict fraud, classify as fraud
            final_pred = (final_pred >= (len(self.models) / 2)).astype(int)
        else:
            # Average probabilities
            avg_prob = np.zeros(len(X))
            for name, probs in probabilities.items():
                avg_prob += probs
            
            avg_prob /= len(probabilities)
            
            # Use a lower threshold for soft voting to boost recall
            final_pred = (avg_prob >= 0.3).astype(int)
        
        return final_pred, avg_prob
    
    def evaluate(self, X_test, y_test):
        """Evaluate the ensemble model performance"""
        print("\nEvaluating ensemble model performance...")
        
        y_pred, y_prob = self.ensemble_predict(X_test)
        
        # Calculate metrics
        accuracy = np.mean(y_pred == y_test)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"Ensemble Model Performance:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"AUC-ROC: {auc:.4f}")
        
        print("\nConfusion Matrix:")
        print(cm)
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Store metrics
        self.metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc,
            'confusion_matrix': cm.tolist()
        }
        
        # Calculate and display the global feature importance
        self.calculate_global_importance()
        
        return self.metrics
    
    def calculate_global_importance(self):
        """Calculate global feature importance from all models"""
        if not self.feature_importances:
            print("No feature importance information available.")
            return
        
        # Initialize feature importance dictionary
        global_importance = {feature: 0.0 for feature in self.feature_names.get('all', [])}
        
        # Sum importance from all models
        for model_name, importances in self.feature_importances.items():
            features = self.feature_names.get('all', [])
            for i, feature in enumerate(features):
                if i < len(importances):
                    global_importance[feature] += importances[i]
        
        # Normalize
        total = sum(global_importance.values())
        if total > 0:
            for feature in global_importance:
                global_importance[feature] /= total
        
        # Sort by importance
        sorted_importance = sorted(global_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Display top features
        print("\nTop 10 Important Features (Global):")
        for feature, importance in sorted_importance[:10]:
            print(f"  - {feature}: {importance:.4f}")
        
        self.global_feature_importance = dict(sorted_importance)
    
    def save_model(self, path='models'):
        """Save the model and associated metadata"""
        os.makedirs(path, exist_ok=True)
        
        model_data = {
            'models': self.models,
            'thresholds': self.thresholds,
            'scalers': self.scalers,
            'feature_names': self.feature_names,
            'metrics': self.metrics,
            'feature_importances': self.feature_importances,
            'global_feature_importance': self.global_feature_importance
        }
        
        with open(os.path.join(path, 'enhanced_fraud_model.pkl'), 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {os.path.join(path, 'enhanced_fraud_model.pkl')}")
    
    def load_model(self, path='models'):
        """Load a previously saved model"""
        model_path = os.path.join(path, 'enhanced_fraud_model.pkl')
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.thresholds = model_data['thresholds']
            self.scalers = model_data['scalers']
            self.feature_names = model_data['feature_names']
            self.metrics = model_data.get('metrics', {})
            self.feature_importances = model_data.get('feature_importances', {})
            self.global_feature_importance = model_data.get('global_feature_importance', {})
            
            print(f"Successfully loaded model from {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_transaction(self, transaction_data):
        """
        Predict if a single transaction is fraudulent
        
        Args:
            transaction_data: Dictionary with transaction features
            
        Returns:
            Dictionary with prediction results
        """
        # Convert transaction data to DataFrame
        df = pd.DataFrame([transaction_data])
        
        # Select and order features according to the model's expected features
        expected_features = self.feature_names.get('all', [])
        
        # For any missing features, fill with zeros
        for feature in expected_features:
            if feature not in df.columns:
                df[feature] = 0
        
        # Select only required features in correct order
        df = df[expected_features]
        
        # Scale the data
        scaler = self.scalers.get('main')
        if scaler:
            df_scaled = scaler.transform(df)
        else:
            # If no scaler is available, standardize manually (suboptimal)
            df_scaled = (df - df.mean()) / df.std()
        
        # Get ensemble prediction
        is_fraud, fraud_prob = self.ensemble_predict(df_scaled)
        
        # Get risk level
        risk_level = self._get_risk_level(fraud_prob[0])
        
        # Get top risk factors
        risk_factors = self._get_top_risk_factors(df.iloc[0], 5)
        
        # Return prediction result
        result = {
            'is_fraud': bool(is_fraud[0]),
            'fraud_probability': float(fraud_prob[0]),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': 'block' if is_fraud[0] else 'allow'
        }
        
        return result
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability < 0.3:
            return "Low"
        elif probability < 0.6:
            return "Medium"
        elif probability < 0.8:
            return "High"
        else:
            return "Very High"
    
    def _get_top_risk_factors(self, transaction, n=3):
        """Get top risk factors for a transaction"""
        if not self.global_feature_importance:
            return ["Unknown - model not trained"]
        
        # Get the top features by importance
        top_features = list(self.global_feature_importance.keys())[:20]
        
        # For each feature, calculate its contribution to risk
        risk_factors = []
        
        for feature in top_features:
            if feature in transaction.index:
                value = transaction[feature]
                importance = self.global_feature_importance.get(feature, 0)
                
                # Higher values for important features increase risk
                risk_contribution = value * importance
                
                if abs(risk_contribution) > 0.01:  # Only include significant contributions
                    risk_factors.append((feature, risk_contribution))
        
        # Sort by absolute contribution
        risk_factors.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Format the risk factors
        formatted_factors = []
        for feature, contribution in risk_factors[:n]:
            direction = "High" if contribution > 0 else "Low"
            formatted_factors.append(f"{feature.replace('_', ' ').title()}: {direction}")
        
        return formatted_factors

def advanced_feature_engineering(df, transaction_type):
    """Enhanced feature engineering with domain-specific features for each transaction type"""
    print(f"\nPerforming advanced feature engineering for {transaction_type} transactions...")
    
    # Common preprocessing
    # Drop ID columns (usually not predictive)
    id_cols = [col for col in df.columns if 'id' in col.lower() and col != 'is_fraud']
    if id_cols:
        print(f"Dropping ID columns: {id_cols}")
        df = df.drop(id_cols, axis=1)
    
    # Transaction-specific features
    if transaction_type == "ethereum":
        # Add blockchain-specific features
        if 'BlockHeight' in df.columns:
            # Normalize block height
            df['block_recency'] = (df['BlockHeight'] - df['BlockHeight'].min()) / (df['BlockHeight'].max() - df['BlockHeight'].min())
        
        if 'Value' in df.columns:
            # Transaction value features
            df['log_value'] = np.log1p(df['Value'])
            df['value_rank'] = df['Value'].rank(pct=True)
        
        if 'TimeStamp' in df.columns:
            # Time-based features
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s')
            df['hour'] = df['TimeStamp'].dt.hour
            df['day'] = df['TimeStamp'].dt.day
            df['month'] = df['TimeStamp'].dt.month
            df['day_of_week'] = df['TimeStamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
            df.drop('TimeStamp', axis=1, inplace=True)
        
        # Error rate as target if no explicit fraud label
        if 'is_fraud' not in df.columns and 'isError' in df.columns:
            df['is_fraud'] = df['isError']
            
    elif transaction_type == "financial":
        if 'amount' in df.columns:
            # Amount features
            df['log_amount'] = np.log1p(df['amount'])
            df['amount_rank'] = df['amount'].rank(pct=True)
            
            # Rare high-value transactions
            top_percentile = df['amount'].quantile(0.95)
            df['high_value'] = (df['amount'] > top_percentile).astype(int)
        
        if 'transaction_time' in df.columns:
            try:
                df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%d-%m-%Y %H:%M')
                df['hour'] = df['transaction_time'].dt.hour
                df['day'] = df['transaction_time'].dt.day
                df['month'] = df['transaction_time'].dt.month
                df['day_of_week'] = df['transaction_time'].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
                
                # Time-based risk features
                df['late_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
                df.drop('transaction_time', axis=1, inplace=True)
            except Exception as e:
                print(f"Warning: Could not process timestamp: {str(e)}")
        
        # Account features
        if 'account_age_days' in df.columns:
            df['new_account'] = (df['account_age_days'] < 30).astype(int)
        
        if 'num_prev_transactions' in df.columns:
            df['log_num_prev_transactions'] = np.log1p(df['num_prev_transactions'])
    
    # Handle categorical features
    categorical_cols = [
        col for col in df.columns if df[col].dtype == 'object' and col != 'is_fraud'
    ]
    
    for col in categorical_cols:
        # Convert categorical to numeric
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].fillna('unknown'))
        print(f"Encoded {col} with {len(le.classes_)} unique values")
    
    # Handle IP address if it exists
    if 'ip_address' in df.columns:
        df['ip_first_octet'] = df['ip_address'].apply(lambda x: int(x.split('.')[0]) if isinstance(x, str) else 0)
        df.drop('ip_address', axis=1, inplace=True)
    
    print(f"Columns after feature engineering: {df.columns.tolist()}")
    print(f"Shape after feature engineering: {df.shape}")
    return df

def create_enhanced_ensemble_model(X_train, y_train, transaction_type):
    """Create an optimized ensemble model with multiple base learners"""
    print(f"\nTraining enhanced ensemble model for {transaction_type} transactions...")
    
    # Base learners
    rf = RandomForestClassifier(
        n_estimators=CONFIG["ensemble"]["n_estimators"],
        max_depth=CONFIG["ensemble"]["max_depth"],
        min_samples_leaf=4,
        min_samples_split=10,
        class_weight='balanced',
        random_state=CONFIG["random_state"]
    )
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=CONFIG["ensemble"]["n_estimators"],
        max_depth=CONFIG["ensemble"]["max_depth"],
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        scale_pos_weight=sum(y_train == 0) / sum(y_train == 1),
        random_state=CONFIG["random_state"]
    )
    
    lgb_model = lgb.LGBMClassifier(
        n_estimators=CONFIG["ensemble"]["n_estimators"],
        max_depth=CONFIG["ensemble"]["max_depth"],
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=20,
        class_weight='balanced',
        random_state=CONFIG["random_state"]
    )
    
    # Meta learner
    meta_learner = LogisticRegression(
        C=0.1,
        class_weight='balanced',
        max_iter=1000,
        random_state=CONFIG["random_state"]
    )
    
    # Stacking classifier
    stacking_clf = StackingClassifier(
        estimators=[
            ('rf', rf),
            ('xgb', xgb_model),
            ('lgb', lgb_model)
        ],
        final_estimator=meta_learner,
        cv=5,
        n_jobs=-1
    )
    
    # Handle class imbalance with SMOTE
    print("Applying SMOTE to handle class imbalance...")
    smote = SMOTE(random_state=CONFIG["random_state"])
    
    # Create pipeline with SMOTE
    pipeline = ImbPipeline([
        ('smote', smote),
        ('classifier', stacking_clf)
    ])
    
    # Train model
    pipeline.fit(X_train, y_train)
    
    return pipeline

def create_deep_learning_model(input_dim):
    """Create an optimized deep learning model with regularization and batch normalization"""
    model = Sequential([
        # Input layer
        Dense(256, input_shape=(input_dim,), activation='relu', 
              kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(CONFIG["deep_learning"]["dropout_rate"]),
        
        # Hidden layers
        Dense(128, activation='relu', kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(CONFIG["deep_learning"]["dropout_rate"]),
        
        Dense(64, activation='relu', kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(CONFIG["deep_learning"]["dropout_rate"]/2),
        
        Dense(32, activation='relu', kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
        BatchNormalization(),
        Dropout(CONFIG["deep_learning"]["dropout_rate"]/2),
        
        # Output layer
        Dense(1, activation='sigmoid')
    ])
    
    optimizer = Adam(learning_rate=CONFIG["deep_learning"]["learning_rate"])
    
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(), tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model

def train_deep_learning_model(X_train, y_train, X_val, y_val, transaction_type):
    """Train deep learning model with early stopping and learning rate scheduling"""
    print(f"\nTraining deep learning model for {transaction_type} transactions...")
    
    # Apply SMOTE for balancing
    smote = SMOTE(random_state=CONFIG["random_state"])
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    # Create model
    model = create_deep_learning_model(X_train.shape[1])
    
    # Callbacks
    model_path = os.path.join(CONFIG["models_dir"], f"dl_{transaction_type}_fraud_model.h5")
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=CONFIG["deep_learning"]["patience"],
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
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Train model
    class_weights = {
        0: 1.0,
        1: (len(y_train) - sum(y_train)) / sum(y_train)  # Weight for minority class
    }
    
    history = model.fit(
        X_train_resampled, y_train_resampled,
        epochs=CONFIG["deep_learning"]["epochs"],
        batch_size=CONFIG["deep_learning"]["batch_size"],
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    # Load best model
    model = load_model(model_path)
    
    # Plot training history
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'{transaction_type.capitalize()} - Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title(f'{transaction_type.capitalize()} - Accuracy Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(CONFIG["results_dir"], f"{transaction_type}_training_history.png"))
    
    return model

def train_and_evaluate_model(df, transaction_type):
    """Complete pipeline to train and evaluate both ensemble and deep learning models"""
    print(f"\n{'='*20} Processing {transaction_type.upper()} TRANSACTIONS {'='*20}")
    
    # Advanced feature engineering
    df_processed = advanced_feature_engineering(df, transaction_type)
    
    # Check if target column exists
    if 'is_fraud' not in df_processed.columns:
        print(f"Error: No target column (is_fraud) found for {transaction_type} transactions")
        return None, None, {}
    
    # Split features and target
    X = df_processed.drop('is_fraud', axis=1)
    y = df_processed['is_fraud']
    
    # Feature selection
    print("\nPerforming feature selection...")
    selector = SelectFromModel(
        RandomForestClassifier(n_estimators=100, random_state=CONFIG["random_state"]),
        threshold='median'
    )
    selector.fit(X, y)
    selected_features = X.columns[selector.get_support()]
    print(f"Selected {len(selected_features)} features: {selected_features.tolist()}")
    
    X = X[selected_features]
    
    # Train-validation-test split
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=CONFIG["test_size"], random_state=CONFIG["random_state"], stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=CONFIG["test_size"], 
        random_state=CONFIG["random_state"], stratify=y_train_val
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Validation set: {X_val.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler
    joblib.dump(
        scaler, 
        os.path.join(CONFIG["models_dir"], f"{transaction_type}_scaler.joblib")
    )
    
    # Train ensemble model
    ensemble_model = create_enhanced_ensemble_model(X_train_scaled, y_train, transaction_type)
    joblib.dump(
        ensemble_model, 
        os.path.join(CONFIG["models_dir"], f"ensemble_{transaction_type}_fraud_model.joblib")
    )
    
    # Train deep learning model
    dl_model = train_deep_learning_model(
        X_train_scaled, y_train, X_val_scaled, y_val, transaction_type
    )
    
    # Evaluate models on test set
    y_pred_ensemble = ensemble_model.predict(X_test_scaled)
    y_prob_ensemble = ensemble_model.predict_proba(X_test_scaled)[:, 1]
    
    y_prob_dl = dl_model.predict(X_test_scaled)
    y_pred_dl = (y_prob_dl > 0.5).astype(int).flatten()
    
    # Combined predictions (weighted average)
    y_prob_combined = 0.6 * y_prob_ensemble + 0.4 * y_prob_dl.flatten()
    y_pred_combined = (y_prob_combined > 0.5).astype(int)
    
    # Calculate metrics
    metrics = {
        "ensemble": {
            "accuracy": accuracy_score(y_test, y_pred_ensemble),
            "precision": precision_score(y_test, y_pred_ensemble),
            "recall": recall_score(y_test, y_pred_ensemble),
            "f1": f1_score(y_test, y_pred_ensemble),
            "auc": roc_auc_score(y_test, y_prob_ensemble),
            "confusion_matrix": confusion_matrix(y_test, y_pred_ensemble).tolist()
        },
        "deep_learning": {
            "accuracy": accuracy_score(y_test, y_pred_dl),
            "precision": precision_score(y_test, y_pred_dl),
            "recall": recall_score(y_test, y_pred_dl),
            "f1": f1_score(y_test, y_pred_dl),
            "auc": roc_auc_score(y_test, y_prob_dl),
            "confusion_matrix": confusion_matrix(y_test, y_pred_dl).tolist()
        },
        "combined": {
            "accuracy": accuracy_score(y_test, y_pred_combined),
            "precision": precision_score(y_test, y_pred_combined),
            "recall": recall_score(y_test, y_pred_combined),
            "f1": f1_score(y_test, y_pred_combined),
            "auc": roc_auc_score(y_test, y_prob_combined),
            "confusion_matrix": confusion_matrix(y_test, y_pred_combined).tolist()
        }
    }
    
    # Print results
    print(f"\n{'='*20} {transaction_type.upper()} FRAUD DETECTION RESULTS {'='*20}")
    for model_type, model_metrics in metrics.items():
        print(f"\n{model_type.upper()} MODEL:")
        print(f"Accuracy: {model_metrics['accuracy']:.4f}")
        print(f"Precision: {model_metrics['precision']:.4f}")
        print(f"Recall: {model_metrics['recall']:.4f}")
        print(f"F1 Score: {model_metrics['f1']:.4f}")
        print(f"AUC: {model_metrics['auc']:.4f}")
    
    # Save metrics
    with open(os.path.join(CONFIG["results_dir"], f"{transaction_type}_metrics.json"), 'w') as f:
        json.dump(metrics, f, indent=4)
    
    return ensemble_model, dl_model, metrics

def process_ethereum_transactions():
    """Process Ethereum transactions"""
    try:
        # Load Ethereum data
        print(f"Loading Ethereum data from {CONFIG['ethereum_data_path']}...")
        df = pd.read_csv(CONFIG['ethereum_data_path'])
        print(f"Ethereum data loaded with shape: {df.shape}")
        
        # Subsample for faster processing if needed
        if len(df) > 50000:
            print("Subsampling Ethereum data for faster processing...")
            # Keep all error transactions (potential fraud) and sample non-error
            error_df = df[df['isError'] == 1]
            non_error_df = df[df['isError'] == 0].sample(
                min(50000 - len(error_df), len(df[df['isError'] == 0])),
                random_state=CONFIG["random_state"]
            )
            df = pd.concat([error_df, non_error_df], axis=0)
            print(f"Subsampled to {len(df)} transactions")
        
        # Train and evaluate models
        ensemble_model, dl_model, metrics = train_and_evaluate_model(df, "ethereum")
        return ensemble_model, dl_model, metrics
    
    except Exception as e:
        print(f"Error processing Ethereum transactions: {str(e)}")
        return None, None, {}

def process_financial_transactions():
    """Process financial transactions"""
    try:
        # Load financial data
        print(f"Loading financial data from {CONFIG['financial_data_path']}...")
        df = pd.read_csv(CONFIG['financial_data_path'])
        print(f"Financial data loaded with shape: {df.shape}")
        
        # Train and evaluate models
        ensemble_model, dl_model, metrics = train_and_evaluate_model(df, "financial")
        return ensemble_model, dl_model, metrics
    
    except Exception as e:
        print(f"Error processing financial transactions: {str(e)}")
        return None, None, {}

def combine_metrics(ethereum_metrics, financial_metrics):
    """Combine metrics from different transaction types"""
    combined_metrics = {
        "ethereum": ethereum_metrics,
        "financial": financial_metrics,
        "overall": {}
    }
    
    # Calculate overall metrics for each model type
    for model_type in ["ensemble", "deep_learning", "combined"]:
        eth_metrics = ethereum_metrics.get(model_type, {})
        fin_metrics = financial_metrics.get(model_type, {})
        
        # Skip if any metrics are missing
        if not eth_metrics or not fin_metrics:
            continue
        
        # Calculate weighted averages for each metric
        combined_metrics["overall"][model_type] = {
            "accuracy": (eth_metrics.get("accuracy", 0) + fin_metrics.get("accuracy", 0)) / 2,
            "precision": (eth_metrics.get("precision", 0) + fin_metrics.get("precision", 0)) / 2,
            "recall": (eth_metrics.get("recall", 0) + fin_metrics.get("recall", 0)) / 2,
            "f1": (eth_metrics.get("f1", 0) + fin_metrics.get("f1", 0)) / 2,
            "auc": (eth_metrics.get("auc", 0) + fin_metrics.get("auc", 0)) / 2,
        }
    
    return combined_metrics

def main():
    """Main function to run the entire fraud detection pipeline"""
    print("\n" + "="*80)
    print(" ENHANCED FRAUD DETECTION MODEL TRAINING ")
    print("="*80)
    
    # Process Ethereum transactions
    eth_ensemble, eth_dl, eth_metrics = process_ethereum_transactions()
    
    # Process financial transactions
    fin_ensemble, fin_dl, fin_metrics = process_financial_transactions()
    
    # Combine metrics
    combined_metrics = combine_metrics(eth_metrics, fin_metrics)
    
    # Save combined metrics
    with open(os.path.join(CONFIG["results_dir"], "combined_metrics.json"), 'w') as f:
        json.dump(combined_metrics, f, indent=4)
    
    # Print overall results
    print("\n" + "="*80)
    print(" OVERALL FRAUD DETECTION RESULTS ")
    print("="*80)
    
    for model_type, metrics in combined_metrics.get("overall", {}).items():
        print(f"\n{model_type.upper()} MODEL:")
        print(f"Overall Accuracy: {metrics.get('accuracy', 0):.4f}")
        print(f"Overall Precision: {metrics.get('precision', 0):.4f}")
        print(f"Overall Recall: {metrics.get('recall', 0):.4f}")
        print(f"Overall F1 Score: {metrics.get('f1', 0):.4f}")
        print(f"Overall AUC: {metrics.get('auc', 0):.4f}")
    
    print("\nTraining complete! Models and results saved.")
    print("="*80)

if __name__ == "__main__":
    main() 