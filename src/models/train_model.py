import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import GridSearchCV

from src.preprocessing.preprocess import load_data, preprocess_data

def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Evaluate model performance and print results"""
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    # Print results
    print(f"\n{model_name} Performance:")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"AUC-ROC:   {auc:.4f}")
    
    # Print confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"TN: {cm[0][0]}, FP: {cm[0][1]}")
    print(f"FN: {cm[1][0]}, TP: {cm[1][1]}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc,
        'confusion_matrix': cm
    }

def train_xgboost(X_train, y_train, feature_names=None):
    """Train an XGBoost model"""
    print("Training XGBoost model...")

    # Calculate scale_pos_weight for handling class imbalance
    # Ensure y_train is not empty and contains positive examples before division
    if len(y_train) > 0 and sum(y_train) > 0:
        scale_pos_weight = len(y_train[y_train == 0]) / sum(y_train)
    else:
        scale_pos_weight = 1 # Default if no positive samples or empty

    # Initialize XGBoost model with parameters suitable for fraud detection
    # Using parameters similar to those in download_and_train.py, adjusted slightly
    model = xgb.XGBClassifier(
        objective='binary:logistic', # Explicitly set objective
        scale_pos_weight=scale_pos_weight,
        learning_rate=0.1,
        n_estimators=100,
        max_depth=5, # Slightly deeper than some examples
        min_child_weight=1,
        gamma=0,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.005,
        use_label_encoder=False, # Recommended setting
        eval_metric='auc', # Use AUC for evaluation during potential training rounds
        random_state=42
    )

    # Train the model
    # For simplicity, not including GridSearchCV here, but it could be added later
    # Also not using early stopping here, but could be added with an eval_set
    model.fit(X_train, y_train)

    print("XGBoost model training complete.")

    # If feature names are provided, display feature importance
    if feature_names is not None and hasattr(model, 'feature_importances_'):
        try:
            feature_importances = model.feature_importances_
            # Ensure feature_names matches the number of features used by the model
            # The preprocessor might generate more features than initially passed
            # Let's try to get names from preprocessor if possible, otherwise slice
            # Note: Getting correct feature names after one-hot encoding can be complex
            # and might require changes in preprocess.py or how names are passed.
            # For now, assume feature_names roughly aligns or use available importance count.
            num_features_in_model = len(feature_importances)
            if len(feature_names) > num_features_in_model:
                 print(f"Warning: Number of feature names ({len(feature_names)}) exceeds model features ({num_features_in_model}). Truncating names list.")
                 feature_names = feature_names[:num_features_in_model]
            elif len(feature_names) < num_features_in_model:
                 print(f"Warning: Number of feature names ({len(feature_names)}) is less than model features ({num_features_in_model}). Padding names.")
                 feature_names.extend([f'feature_{i}' for i in range(len(feature_names), num_features_in_model)])


            importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': feature_importances
            }).sort_values('Importance', ascending=False)

            print("\nTop 10 Most Important Features (XGBoost):")
            print(importance_df.head(10))
        except Exception as e:
            print(f"Could not display feature importances: {e}")
            # Fallback if feature_names doesn't match feature_importances_ length
            # This might happen if the preprocessor changes the number of features
            print("\nFeature Importances (Indices):")
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            for i in range(min(10, len(importances))): # Print top 10 or fewer
                 print(f"{i+1}. Feature {indices[i]}: {importances[indices[i]]:.4f}")


    return model

def save_model(model, preprocessor, model_name="model"):
    """Save the model and preprocessor to disk"""
    # Create models directory if it doesn't exist
    save_dir = os.path.join('src', 'models', 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(save_dir, f"{model_name}_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save preprocessor
    preprocessor_path = os.path.join(save_dir, f"{model_name}_preprocessor.pkl")
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    print(f"Model saved to {model_path}")
    print(f"Preprocessor saved to {preprocessor_path}")
    
    return model_path, preprocessor_path

def main():
    """Main function to train and evaluate models"""
    # Load and preprocess data
    print("Loading and preprocessing data...")
    
    try:
        # Check if data exists
        data_path = os.path.join('data', 'online_fraud.csv')
        if not os.path.exists(data_path):
            print(f"Data not found at {data_path}. Please run the download step first.")
            return
            
        # Load and preprocess
        df = load_data(data_path)
        X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_data(df)
        
        # Train XGBoost model
        xgb_model = train_xgboost(X_train, y_train, feature_names)
        
        # Evaluate model
        results = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        
        # Save model
        save_model(xgb_model, preprocessor, "xgboost")
        
        print("\nModel training and evaluation complete!")
        
    except Exception as e:
        print(f"Error in model training: {e}")
        raise

if __name__ == "__main__":
    main() 