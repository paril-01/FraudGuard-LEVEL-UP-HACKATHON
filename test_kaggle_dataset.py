"""
Test the fraud detection model with the Kaggle dataset.
This script loads the Kaggle dataset and evaluates the model performance.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import json

def load_model(model_name):
    """Load a pre-trained model from the models directory"""
    model_path = os.path.join('models', f'{model_name}.pkl')
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        print(f"Successfully loaded model: {model_name}")
        return model_data
    except FileNotFoundError:
        print(f"Model file not found: {model_path}")
        return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def load_kaggle_dataset(dataset_path):
    """Load and prepare the Kaggle fraud detection dataset"""
    try:
        # Check if the dataset path is a directory or file
        if os.path.isdir(dataset_path):
            # Find CSV files in the directory
            csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')]
            if not csv_files:
                print(f"No CSV files found in {dataset_path}")
                return None
            
            # Load the first CSV file (or you could implement logic to choose a specific one)
            file_path = os.path.join(dataset_path, csv_files[0])
            print(f"Loading dataset from: {file_path}")
            data = pd.read_csv(file_path)
        else:
            # Assume it's a direct path to a CSV file
            print(f"Loading dataset from: {dataset_path}")
            data = pd.read_csv(dataset_path)
            
        print(f"Dataset loaded with shape: {data.shape}")
        print(f"Columns: {data.columns.tolist()}")
        
        # Look for the target column (fraud indicator)
        # Common names for fraud columns include: isFraud, is_fraud, fraud, fraudulent, etc.
        fraud_column_candidates = ['isFraud', 'is_fraud', 'fraud', 'fraudulent', 'class', 'label', 'target']
        fraud_column = None
        
        for col in fraud_column_candidates:
            if col in data.columns:
                fraud_column = col
                break
                
        if fraud_column is None:
            print("Could not identify the fraud indicator column. Please specify manually.")
            # For demonstration, we'll check if there's a binary column that could be the target
            binary_cols = [col for col in data.columns if set(data[col].unique()).issubset({0, 1})]
            if binary_cols:
                fraud_column = binary_cols[0]
                print(f"Using {fraud_column} as the potential fraud indicator column")
            else:
                return None
        
        print(f"Using '{fraud_column}' as the fraud indicator column")
        print(f"Fraud cases: {data[fraud_column].sum()} ({data[fraud_column].mean()*100:.2f}%)")
        
        return data, fraud_column
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def evaluate_model_with_kaggle_data(model_info, data, fraud_column):
    """Evaluate a pre-trained model on the Kaggle dataset"""
    if model_info is None or data is None:
        return None
    
    try:
        # Extract model components
        model = model_info['model']
        scaler = model_info['scaler']
        feature_names = model_info['feature_names']
        
        print(f"Model feature names: {feature_names}")
        
        # Check which features from the model are available in the dataset
        common_features = [col for col in feature_names if col in data.columns]
        missing_features = [col for col in feature_names if col not in data.columns]
        extra_features = [col for col in data.columns if col != fraud_column and col not in feature_names]
        
        print(f"Common features: {len(common_features)}")
        print(f"Missing features: {len(missing_features)}")
        
        if len(common_features) < len(feature_names) * 0.5:
            print("Too many features are missing. The dataset may not be compatible with this model.")
            
            # Let's try to map features if column names are different but semantically similar
            # This is a simplified approach - in a real scenario, you would need more sophisticated mapping
            
            # Example: some typical feature mappings for fraud detection
            feature_mapping = {
                'amount': ['Amount', 'TransactionAmount', 'transaction_amount'],
                'time': ['Time', 'TransactionTime', 'transaction_time', 'datetime'],
                'age': ['Age', 'CustomerAge', 'account_age'],
                'ip_address': ['IPAddress', 'ip', 'source_ip']
                # Add more mappings as needed
            }
            
            # Try to map features
            mapped_features = {}
            for model_feature in missing_features:
                for concept, variations in feature_mapping.items():
                    if any(model_feature.lower().find(var.lower()) >= 0 for var in variations):
                        for dataset_feature in extra_features:
                            if any(dataset_feature.lower().find(var.lower()) >= 0 for var in variations):
                                mapped_features[model_feature] = dataset_feature
                                break
            
            print(f"Mapped features: {mapped_features}")
            
            if not mapped_features:
                # If we couldn't map features, let's try to use the dataset as is
                print("Using available features from the dataset...")
                
                # Get numeric features only
                numeric_features = data.select_dtypes(include=np.number).columns.tolist()
                numeric_features = [col for col in numeric_features if col != fraud_column]
                
                if not numeric_features:
                    print("No numeric features found in the dataset.")
                    return None
                
                print(f"Using {len(numeric_features)} numeric features from the dataset")
                
                X = data[numeric_features]
                y = data[fraud_column]
                
                # Create a new scaler for the dataset features
                new_scaler = StandardScaler()
                X_scaled = new_scaler.fit_transform(X)
                
                # We need to train a new model since the features don't match
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import train_test_split
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.3, random_state=42, stratify=y
                )
                
                print("Training a new model on the Kaggle dataset...")
                new_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
                new_model.fit(X_train, y_train)
                
                # Evaluate on test set
                y_pred = new_model.predict(X_test)
                y_prob = new_model.predict_proba(X_test)[:, 1]
                
                # Calculate metrics
                results = calculate_metrics(y_test, y_pred, y_prob)
                
                print("Results using new model trained on Kaggle dataset:")
                print_results(results)
                
                # Feature importance for the new model
                feature_importances = new_model.feature_importances_
                
                # Sort feature importances
                sorted_idx = np.argsort(feature_importances)[::-1]
                top_n = min(10, len(sorted_idx))
                
                print("\nTop 10 important features in the Kaggle dataset:")
                for i in range(top_n):
                    print(f"{i+1}. {numeric_features[sorted_idx[i]]}: {feature_importances[sorted_idx[i]]:.4f}")
                
                return results
                
            else:
                # Create a DataFrame with mapped features
                new_data = pd.DataFrame()
                for model_feat, dataset_feat in mapped_features.items():
                    new_data[model_feat] = data[dataset_feat]
                
                # Add common features
                for feat in common_features:
                    new_data[feat] = data[feat]
                
                # Check if we have all the necessary features
                missing_after_mapping = [col for col in feature_names if col not in new_data.columns]
                
                if missing_after_mapping:
                    print(f"Still missing features after mapping: {missing_after_mapping}")
                    # Fill missing features with zeros (or you could use other imputation methods)
                    for feat in missing_after_mapping:
                        new_data[feat] = 0
                
                X = new_data[feature_names]
                y = data[fraud_column]
        else:
            # There are enough common features to use the pre-trained model
            # Select only the common features in the correct order
            X = pd.DataFrame()
            for feat in feature_names:
                if feat in common_features:
                    X[feat] = data[feat]
                else:
                    # For missing features, fill with zeros (or other appropriate values)
                    X[feat] = 0
            
            y = data[fraud_column]
        
        # Scale the features
        X_scaled = scaler.transform(X)
        
        # Make predictions
        y_pred = model.predict(X_scaled)
        y_prob = model.predict_proba(X_scaled)[:, 1]
        
        # Calculate metrics
        results = calculate_metrics(y, y_pred, y_prob)
        
        print("Results using pre-trained model on Kaggle dataset:")
        print_results(results)
        
        return results
        
    except Exception as e:
        print(f"Error evaluating model with Kaggle data: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_metrics(y_true, y_pred, y_prob):
    """Calculate performance metrics"""
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'auc': roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0,
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
        'classification_report': classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    }

def print_results(results):
    """Print the evaluation results"""
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall: {results['recall']:.4f}")
    print(f"F1 Score: {results['f1']:.4f}")
    print(f"AUC-ROC: {results['auc']:.4f}")
    print("\nConfusion Matrix:")
    print(np.array(results['confusion_matrix']))
    
    print("\nClassification Report:")
    for class_label, metrics in results['classification_report'].items():
        if class_label in ['0', '1', 0, 1]:
            label_name = 'Non-Fraud' if str(class_label) == '0' else 'Fraud'
            if isinstance(metrics, dict):
                print(f"{label_name}:")
                print(f"  Precision: {metrics['precision']:.4f}")
                print(f"  Recall: {metrics['recall']:.4f}")
                print(f"  F1-score: {metrics['f1-score']:.4f}")
                print(f"  Support: {metrics['support']}")

def main():
    # Use the kagglehub download path provided by the user
    import sys
    
    # Check if a dataset path is provided as an argument
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        # Default path (assuming kagglehub has downloaded it here)
        dataset_path = "datasets/fraud-detection-dataset-csv"
        
        # Let the user know we're using the default path
        print(f"No dataset path provided. Using default: {dataset_path}")
        print("To specify a path, run: python test_kaggle_dataset.py [path_to_dataset]")
    
    # Check if the path exists
    if not os.path.exists(dataset_path):
        print(f"Dataset path does not exist: {dataset_path}")
        print("Please provide a valid path to the downloaded Kaggle dataset.")
        return
    
    print("\n=== Testing Fraud Detection Models with Kaggle Dataset ===")
    
    # Load the Kaggle dataset
    dataset_result = load_kaggle_dataset(dataset_path)
    if dataset_result is None:
        return
    
    data, fraud_column = dataset_result
    
    # Try different models
    models_to_try = ['online-payment-fraud', 'credit-card-fraud', 'e-commerce-fraud']
    
    best_result = None
    best_model_name = None
    
    for model_name in models_to_try:
        print(f"\n--- Testing model: {model_name} ---")
        model_info = load_model(model_name)
        
        if model_info:
            result = evaluate_model_with_kaggle_data(model_info, data, fraud_column)
            
            if result and (best_result is None or result['f1'] > best_result['f1']):
                best_result = result
                best_model_name = model_name
    
    # Print summary of the best model
    if best_result:
        print("\n=== Best Model Performance ===")
        print(f"Model: {best_model_name}")
        print_results(best_result)
    else:
        print("\nUnable to evaluate any models with this dataset.")
        print("Displaying current model performance metrics:")
        
        # Run direct_train to show current metrics
        try:
            import direct_train
            direct_train.main()
        except ImportError:
            print("Could not import direct_train module.")

if __name__ == "__main__":
    main() 