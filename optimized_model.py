import os
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.combine import SMOTETomek
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

print("Optimized Fraud Detection Model (99%+ Performance)")
print("=" * 60)

# Configuration
CONFIG = {
    "financial_data_path": "c:/Users/Paril Rupani/OneDrive - Shri Vile Parle Kelavani Mandal/Desktop/synthetic_financial_fraud_data (2).csv",
    "ethereum_data_path": "c:/Users/Paril Rupani/.cache/kagglehub/datasets/chaitya0623/ethereum-transactions-for-fraud-detection/versions/1/first_order_df.csv",
    "models_dir": "models",
    "results_dir": "results",
    "random_state": 42,
    "cv_folds": 5
}

# Create directories if they don't exist
os.makedirs(CONFIG["models_dir"], exist_ok=True)
os.makedirs(CONFIG["results_dir"], exist_ok=True)

class OptimizedFraudDetector:
    """Optimized fraud detection model targeting 99%+ performance metrics"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.resampler = None
        self.metrics = {}
        self.feature_importances = {}
    
    def load_and_preprocess_data(self, dataset_path, dataset_type):
        """Load and preprocess data with advanced feature engineering"""
        print(f"\nLoading and preprocessing {dataset_type} dataset...")
        
        try:
            # Load dataset
            df = pd.read_csv(dataset_path)
            print(f"Dataset loaded with shape: {df.shape}")
            
            # Set target variable based on dataset type
            if dataset_type == "ethereum":
                # For Ethereum, use isError as fraud indicator
                if 'is_fraud' not in df.columns and 'isError' in df.columns:
                    df['is_fraud'] = df['isError']
                
                # Advanced feature engineering for Ethereum
                if 'BlockHeight' in df.columns:
                    # Block height features
                    df['block_height_norm'] = (df['BlockHeight'] - df['BlockHeight'].min()) / (df['BlockHeight'].max() - df['BlockHeight'].min())
                
                if 'Value' in df.columns:
                    # Transaction value features
                    df['log_value'] = np.log1p(df['Value'])
                    percentiles = [25, 50, 75, 90, 95, 99]
                    for p in percentiles:
                        threshold = df['Value'].quantile(p/100)
                        df[f'value_above_p{p}'] = (df['Value'] > threshold).astype(int)
                
                if 'Gas' in df.columns and 'GasPrice' in df.columns:
                    # Gas-related features
                    df['gas_price_ratio'] = df['GasPrice'] / (df['Gas'] + 1)
                    df['high_gas_price'] = (df['GasPrice'] > df['GasPrice'].quantile(0.9)).astype(int)
                
                if 'TimeStamp' in df.columns:
                    # Time-based features
                    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s')
                    df['hour'] = df['TimeStamp'].dt.hour
                    df['day'] = df['TimeStamp'].dt.day
                    df['month'] = df['TimeStamp'].dt.month
                    df['day_of_week'] = df['TimeStamp'].dt.dayofweek
                    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
                    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 4)).astype(int)
                    df.drop('TimeStamp', axis=1, inplace=True)
                
                # Drop identity columns
                for col in ['TxHash', 'From', 'To']:
                    if col in df.columns:
                        df.drop(col, axis=1, inplace=True)
                
            elif dataset_type == "financial":
                # Advanced feature engineering for financial data
                if 'transaction_time' in df.columns:
                    try:
                        df['transaction_time'] = pd.to_datetime(df['transaction_time'])
                        df['hour'] = df['transaction_time'].dt.hour
                        df['day'] = df['transaction_time'].dt.day
                        df['month'] = df['transaction_time'].dt.month
                        df['day_of_week'] = df['transaction_time'].dt.dayofweek
                        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
                        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
                        
                        # Create hour bins
                        df['hour_bin'] = pd.cut(df['hour'], bins=[0, 6, 12, 18, 24], 
                                               labels=['night', 'morning', 'afternoon', 'evening'])
                        hour_dummies = pd.get_dummies(df['hour_bin'], prefix='hour')
                        df = pd.concat([df, hour_dummies], axis=1)
                        df.drop(['hour_bin', 'transaction_time'], axis=1, inplace=True)
                    except Exception as e:
                        print(f"Error processing timestamp: {str(e)}")
                
                if 'amount' in df.columns:
                    # Amount features
                    df['log_amount'] = np.log1p(df['amount'])
                    
                    # Amount outlier flags
                    q1 = df['amount'].quantile(0.25)
                    q3 = df['amount'].quantile(0.75)
                    iqr = q3 - q1
                    upper_bound = q3 + 1.5 * iqr
                    df['amount_outlier'] = (df['amount'] > upper_bound).astype(int)
                    
                    # Create amount bins and categories
                    percentiles = [50, 75, 90, 95, 99]
                    for p in percentiles:
                        threshold = df['amount'].quantile(p/100)
                        df[f'amount_above_p{p}'] = (df['amount'] > threshold).astype(int)
                
                # Account features
                if 'account_age_days' in df.columns:
                    df['new_account'] = (df['account_age_days'] < 30).astype(int)
                    df['account_age_bins'] = pd.cut(df['account_age_days'], 
                                                  bins=[0, 30, 90, 180, 365, float('inf')],
                                                  labels=['new', 'recent', 'established', 'mature', 'old'])
                    age_dummies = pd.get_dummies(df['account_age_bins'], prefix='acc_age')
                    df = pd.concat([df, age_dummies], axis=1)
                    df.drop('account_age_bins', axis=1, inplace=True)
                
                # Transaction velocity
                if 'num_prev_transactions' in df.columns:
                    df['log_prev_txns'] = np.log1p(df['num_prev_transactions'])
                    df['high_velocity'] = (df['num_prev_transactions'] > df['num_prev_transactions'].quantile(0.9)).astype(int)
                
                # Handle categorical features
                categorical_cols = ['merchant', 'location', 'device', 'payment_method']
                for col in categorical_cols:
                    if col in df.columns:
                        # Create dummies
                        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                        df = pd.concat([df, dummies], axis=1)
                        df.drop(col, axis=1, inplace=True)
                
                # Handle IP address
                if 'ip_address' in df.columns:
                    df['ip_first_octet'] = df['ip_address'].apply(lambda x: int(x.split('.')[0]) if isinstance(x, str) else 0)
                    df.drop('ip_address', axis=1, inplace=True)
                
                # Drop identity columns
                for col in ['user_id', 'transaction_id']:
                    if col in df.columns:
                        df.drop(col, axis=1, inplace=True)
            
            # Check if target column exists
            if 'is_fraud' not in df.columns:
                print(f"Error: No target column found for {dataset_type} dataset")
                return None
                
            # Feature interactions
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col != 'is_fraud' and not col.startswith('is_')]
            
            if len(numeric_cols) >= 2:
                print("Creating feature interactions...")
                # Limit the number of interactions to avoid explosion
                for i in range(min(3, len(numeric_cols))):
                    for j in range(i+1, min(4, len(numeric_cols))):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        # Multiplication interaction
                        df[f'{col1}_x_{col2}'] = df[col1] * df[col2]
                        # Division interaction (safe)
                        df[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-8)
            
            # Handle missing values
            for col in df.columns:
                if df[col].isnull().sum() > 0:
                    if df[col].dtype != 'object':
                        # Use median for numeric columns
                        df[col] = df[col].fillna(df[col].median())
                    else:
                        # Use most frequent for categorical
                        df[col] = df[col].fillna(df[col].mode()[0])
            
            print(f"Preprocessed data shape: {df.shape}")
            return df
        
        except Exception as e:
            print(f"Error in data preprocessing: {str(e)}")
            return None
    
    def _normalize_and_balance_data(self, X, y, dataset_type):
        """Apply normalization and class balancing techniques"""
        print("Normalizing and balancing data...")
        
        # Choose scaler based on dataset
        if dataset_type == "ethereum":
            scaler = StandardScaler()  # Standard scaler works well for Ethereum data
        else:
            scaler = RobustScaler()    # Robust scaler for financial data with outliers
        
        # Fit and transform
        X_scaled = scaler.fit_transform(X)
        
        # Save scaler
        self.scalers[dataset_type] = scaler
        
        # Create synthetic samples for minority class if needed
        class_distribution = np.bincount(y)
        fraud_ratio = class_distribution[1] / len(y) if len(class_distribution) > 1 else 0
        
        print(f"Class distribution - Non-fraud: {class_distribution[0]}, Fraud: {class_distribution[1] if len(class_distribution) > 1 else 0}")
        print(f"Fraud ratio: {fraud_ratio:.4f}")
        
        # Apply resampling only if there's significant imbalance
        if 0.1 < fraud_ratio < 0.4:
            # Moderate imbalance: use SMOTE
            print("Applying SMOTE for moderate class imbalance...")
            resampler = SMOTE(random_state=CONFIG["random_state"])
            X_resampled, y_resampled = resampler.fit_resample(X_scaled, y)
            
        elif fraud_ratio <= 0.1:
            # Severe imbalance: use SMOTETomek
            print("Applying SMOTETomek for severe class imbalance...")
            resampler = SMOTETomek(random_state=CONFIG["random_state"])
            X_resampled, y_resampled = resampler.fit_resample(X_scaled, y)
            
        else:
            # No significant imbalance
            print("No resampling applied - class distribution is balanced enough")
            X_resampled, y_resampled = X_scaled, y
        
        # Save resampler
        self.resampler = resampler if fraud_ratio < 0.4 else None
        
        # Report new distribution if resampling was applied
        if fraud_ratio < 0.4:
            new_class_distribution = np.bincount(y_resampled)
            print(f"After resampling - Non-fraud: {new_class_distribution[0]}, Fraud: {new_class_distribution[1]}")
        
        return X_resampled, y_resampled
    
    def _select_best_features(self, X, y, dataset_type, X_test=None, threshold=0.9):
        """Select the most discriminative features"""
        print("Selecting most informative features...")
        
        # Use random forest to assess feature importance
        base_model = RandomForestClassifier(n_estimators=100, random_state=CONFIG["random_state"])
        base_model.fit(X, y)
        
        # Get feature importance
        importance = base_model.feature_importances_
        
        # Calculate cumulative importance and select top features
        sorted_idx = np.argsort(importance)[::-1]
        cumulative_importance = np.cumsum(importance[sorted_idx])
        
        # Select features needed to reach the threshold
        last_idx = np.searchsorted(cumulative_importance, threshold) + 1
        selected_idx = sorted_idx[:last_idx]
        
        # Create feature selector
        selector = SelectFromModel(base_model, threshold=importance[sorted_idx[last_idx-1]] - 1e-7, prefit=True)
        
        # Transform data
        X_reduced = selector.transform(X)
        X_test_reduced = selector.transform(X_test) if X_test is not None else None
        
        # Save feature selector and importance
        self.feature_selectors[dataset_type] = selector
        
        # Get original feature names if X is a DataFrame
        if hasattr(X, 'columns'):
            selected_features = X.columns[selected_idx].tolist()
            remaining_features = len(selected_features)
            total_features = X.shape[1]
            
            # Store feature importance info
            feature_importance_dict = {feature: importance for feature, importance 
                                     in zip(X.columns[selected_idx], importance[selected_idx])}
            self.feature_importances[dataset_type] = feature_importance_dict
            
            print(f"Selected {remaining_features} out of {total_features} features ({(remaining_features/total_features)*100:.1f}%)")
            
            # Print top 10 features
            print("Top 10 features:")
            for i, feature in enumerate(X.columns[sorted_idx[:10]]):
                print(f"  {i+1}. {feature}: {importance[sorted_idx[i]]:.4f}")
        else:
            print(f"Selected {X_reduced.shape[1]} out of {X.shape[1]} features")
        
        return X_reduced, X_test_reduced
    
    def build_optimized_model(self, X_train, y_train, dataset_type):
        """Build a highly-optimized ensemble model"""
        print(f"\nBuilding optimized model for {dataset_type} dataset...")
        
        # Base models with optimized hyperparameters
        # 1. Random Forest - great for structured tabular data
        rf = RandomForestClassifier(
            n_estimators=500,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=4,
            max_features='sqrt',
            class_weight='balanced',
            bootstrap=True,
            random_state=CONFIG["random_state"],
            n_jobs=-1
        )
        
        # 2. Gradient Boosting - excellent for catching subtle patterns
        gb = GradientBoostingClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.03,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features=0.7,
            random_state=CONFIG["random_state"]
        )
        
        # 3. Logistic Regression - linear model that works well with normalized features
        lr = LogisticRegression(
            C=0.1,
            penalty='l2',
            solver='liblinear',
            class_weight='balanced',
            random_state=CONFIG["random_state"],
            max_iter=1000
        )
        
        # 4. SVM - effective for medium-sized datasets with clear margins
        svm = SVC(
            C=1.0,
            kernel='rbf',
            gamma='scale',
            probability=True,
            class_weight='balanced',
            random_state=CONFIG["random_state"]
        )
        
        # Create voting ensemble with optimized weights
        if dataset_type == "ethereum":
            # Ethereum often has clearer patterns, give more weight to RF and GB
            weights = [0.4, 0.4, 0.1, 0.1]
        else:
            # Financial data can be noisier, balance the weights more
            weights = [0.3, 0.3, 0.2, 0.2]
        
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf),
                ('gb', gb),
                ('lr', lr),
                ('svm', svm)
            ],
            voting='soft',
            weights=weights
        )
        
        # Train the ensemble model
        ensemble.fit(X_train, y_train)
        
        # Store the model
        self.models[dataset_type] = ensemble
        
        return ensemble
    
    def find_optimal_threshold(self, model, X, y, class_ratio=None):
        """Find the optimal decision threshold to maximize performance metrics"""
        # Get predicted probabilities
        y_prob = model.predict_proba(X)[:, 1]
        
        # Try different thresholds
        thresholds = np.arange(0.1, 0.91, 0.01)
        best_results = {
            'threshold': 0.5,
            'f1': 0.0,
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'balanced_score': 0.0
        }
        
        print("Finding optimal threshold...")
        
        # Try each threshold and calculate metrics
        for threshold in thresholds:
            y_pred = (y_prob >= threshold).astype(int)
            
            # Calculate metrics
            acc = accuracy_score(y, y_pred)
            prec = precision_score(y, y_pred, zero_division=0)
            rec = recall_score(y, y_pred, zero_division=0)
            f1 = f1_score(y, y_pred, zero_division=0)
            
            # Balanced score - equally weight all metrics
            balanced_score = (acc + prec + rec + f1) / 4
            
            # Update best results if this threshold is better
            if balanced_score > best_results['balanced_score']:
                best_results = {
                    'threshold': threshold,
                    'f1': f1,
                    'accuracy': acc,
                    'precision': prec,
                    'recall': rec,
                    'balanced_score': balanced_score
                }
        
        print(f"Optimal threshold: {best_results['threshold']:.2f}")
        print(f"At this threshold - Accuracy: {best_results['accuracy']:.4f}, "
              f"Precision: {best_results['precision']:.4f}, "
              f"Recall: {best_results['recall']:.4f}, "
              f"F1: {best_results['f1']:.4f}")
        
        return best_results['threshold']
    
    def evaluate_model(self, model, X_test, y_test, threshold=0.5, dataset_type=None):
        """Evaluate model performance with optimal threshold"""
        # Get predictions using the optimal threshold
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= threshold).astype(int)
        
        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "auc": roc_auc_score(y_test, y_prob),
            "threshold": threshold,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Store metrics if dataset_type is provided
        if dataset_type:
            self.metrics[dataset_type] = metrics
        
        # Print evaluation results
        print(f"\nModel Evaluation Results:")
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1']:.4f}")
        print(f"AUC-ROC:   {metrics['auc']:.4f}")
        
        # Plot confusion matrix if dataset_type is provided
        if dataset_type:
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'Confusion Matrix - {dataset_type.capitalize()} Fraud Detection')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.savefig(os.path.join(CONFIG["results_dir"], f"{dataset_type}_confusion_matrix.png"))
            plt.close()
        
        return metrics
    
    def process_dataset(self, dataset_path, dataset_type):
        """Complete pipeline for processing a dataset"""
        # 1. Load and preprocess data
        df = self.load_and_preprocess_data(dataset_path, dataset_type)
        if df is None:
            return False
        
        # 2. Split features and target
        X = df.drop('is_fraud', axis=1)
        y = df['is_fraud']
        
        # 3. Split into train, validation and test sets
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=0.2, random_state=CONFIG["random_state"], stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=0.25, 
            random_state=CONFIG["random_state"], stratify=y_train_val
        )
        
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # 4. Feature selection
        X_train_reduced, X_test_reduced = self._select_best_features(X_train, y_train, dataset_type, X_test)
        X_val_reduced = self.feature_selectors[dataset_type].transform(X_val)
        
        # 5. Normalize and balance data
        X_train_prep, y_train_prep = self._normalize_and_balance_data(X_train_reduced, y_train, dataset_type)
        
        # 6. Build optimized model
        model = self.build_optimized_model(X_train_prep, y_train_prep, dataset_type)
        
        # 7. Normalize validation and test data with the same scaler
        X_val_scaled = self.scalers[dataset_type].transform(X_val_reduced)
        X_test_scaled = self.scalers[dataset_type].transform(X_test_reduced)
        
        # 8. Find optimal threshold using validation set
        optimal_threshold = self.find_optimal_threshold(model, X_val_scaled, y_val)
        
        # 9. Evaluate on test set with optimal threshold
        test_metrics = self.evaluate_model(model, X_test_scaled, y_test, 
                                          threshold=optimal_threshold, 
                                          dataset_type=dataset_type)
        
        # 10. Save model and artifacts
        model_artifacts = {
            "model": model,
            "scaler": self.scalers[dataset_type],
            "feature_selector": self.feature_selectors[dataset_type],
            "resampler": self.resampler,
            "threshold": optimal_threshold,
            "metrics": test_metrics,
            "feature_importances": self.feature_importances.get(dataset_type, {})
        }
        
        model_path = os.path.join(CONFIG["models_dir"], f"{dataset_type}_optimized_model.joblib")
        joblib.dump(model_artifacts, model_path)
        print(f"Model artifacts saved to {model_path}")
        
        # Check if we achieved 99% across all metrics
        achieved_target = all(value >= 0.99 for key, value in test_metrics.items() 
                             if key in ['accuracy', 'precision', 'recall', 'f1', 'auc'])
        
        if achieved_target:
            print(f"\n✓ 99%+ TARGET ACHIEVED FOR {dataset_type.upper()} DATASET!")
        else:
            print(f"\n× 99%+ target not yet achieved for all metrics in {dataset_type} dataset")
        
        return achieved_target
    
    def compute_combined_metrics(self):
        """Compute combined metrics across all datasets"""
        print("\nComputing combined metrics across all datasets...")
        
        # Check if we have metrics for all datasets
        if not all(dataset_type in self.metrics for dataset_type in ["ethereum", "financial"]):
            print("Cannot compute combined metrics: missing metrics for one or more datasets")
            return
        
        # Combine metrics with equal weight to each dataset
        combined_metrics = {}
        for metric in ["accuracy", "precision", "recall", "f1", "auc"]:
            combined_metrics[metric] = (
                self.metrics["ethereum"][metric] + 
                self.metrics["financial"][metric]
            ) / 2
        
        # Store combined metrics
        self.metrics["combined"] = combined_metrics
        
        # Print combined results
        print("\nCOMBINED RESULTS ACROSS ALL DATASETS:")
        for metric, value in combined_metrics.items():
            print(f"{metric.capitalize()}: {value:.4f}")
            
            # Check if we achieved 99% target
            if value >= 0.99:
                print(f"✓ {metric.upper()} TARGET ACHIEVED!")
            else:
                target_gap = 0.99 - value
                print(f"× {metric.upper()} TARGET NOT YET ACHIEVED (gap: {target_gap:.4f})")
        
        # Save combined metrics
        with open(os.path.join(CONFIG["results_dir"], "optimized_model_metrics.json"), 'w') as f:
            json.dump(self.metrics, f, indent=4)
        
        print(f"\nAll metrics saved to {os.path.join(CONFIG['results_dir'], 'optimized_model_metrics.json')}")
        
        # Check if we achieved 99% across all metrics
        achieved_target = all(value >= 0.99 for key, value in combined_metrics.items() 
                             if key in ['accuracy', 'precision', 'recall', 'f1', 'auc'])
        
        if achieved_target:
            print("\n✓ 99%+ TARGET ACHIEVED ACROSS ALL METRICS AND DATASETS!")
        else:
            print("\n× 99%+ target not yet achieved for all combined metrics")
        
        return achieved_target
    
    def run(self):
        """Run the complete optimization process"""
        print("\n" + "="*60)
        print(" OPTIMIZED FRAUD DETECTION MODEL PIPELINE ")
        print("="*60)
        
        ethereum_success = False
        financial_success = False
        
        # Process Ethereum dataset if available
        if os.path.exists(CONFIG["ethereum_data_path"]):
            print("\nProcessing Ethereum dataset...")
            ethereum_success = self.process_dataset(CONFIG["ethereum_data_path"], "ethereum")
        else:
            print(f"\nEthereum dataset not found at {CONFIG['ethereum_data_path']}")
        
        # Process Financial dataset if available
        if os.path.exists(CONFIG["financial_data_path"]):
            print("\nProcessing Financial dataset...")
            financial_success = self.process_dataset(CONFIG["financial_data_path"], "financial")
        else:
            print(f"\nFinancial dataset not found at {CONFIG['financial_data_path']}")
        
        # Compute combined metrics
        if ethereum_success or financial_success:
            combined_success = self.compute_combined_metrics()
            
            if combined_success:
                print("\n🎉 OPTIMIZATION SUCCESSFUL! 99%+ PERFORMANCE ACHIEVED! 🎉")
            else:
                print("\nOptimization process completed, but 99%+ target not achieved for all metrics.")
                print("Consider further tuning or additional feature engineering.")
        else:
            print("\nNo datasets were successfully processed.")
        
        return ethereum_success or financial_success

if __name__ == "__main__":
    detector = OptimizedFraudDetector()
    detector.run() 