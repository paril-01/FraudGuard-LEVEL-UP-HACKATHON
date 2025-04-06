import os
import pandas as pd
import numpy as np
import pickle
import shutil
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
from sklearn.pipeline import Pipeline
import kagglehub

def download_datasets():
    """Download all four fraud detection datasets."""
    print("Starting dataset downloads...")
    
    # Create data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    datasets = []
    
    # Dataset 1: UPI Transactions 23-24
    try:
        print("\nDownloading Dataset 1: UPI Transactions 23-24...")
        kaggle_path_1 = kagglehub.dataset_download("priyanshugautam1214/upi-transactions-23-24")
        print(f"Path to dataset files: {kaggle_path_1}")
        
        # Find the main CSV file
        for file in os.listdir(kaggle_path_1):
            if file.endswith('.csv'):
                source_file_1 = os.path.join(kaggle_path_1, file)
                df1 = pd.read_csv(source_file_1)
                
                # Check if it has a fraud indicator column
                if 'is_fraud' in df1.columns:
                    df1.rename(columns={'is_fraud': 'isFraud'}, inplace=True)
                elif 'fraud' in df1.columns:
                    df1.rename(columns={'fraud': 'isFraud'}, inplace=True)
                elif 'fraudulent' in df1.columns:
                    df1.rename(columns={'fraudulent': 'isFraud'}, inplace=True)
                elif 'isFraudulent' in df1.columns:
                    df1.rename(columns={'isFraudulent': 'isFraud'}, inplace=True)
                else:
                    # If no fraud column exists, try to identify by transaction type
                    # This is a simplification - actual fraud detection would be more complex
                    print("No explicit fraud column found. Creating synthetic fraud labels based on anomalies.")
                    # Create a simple synthetic fraud column based on transaction amount
                    # This is just for demonstration - in a real scenario you would need proper labeling
                    if 'amount' in df1.columns or 'transaction_amount' in df1.columns:
                        amount_col = 'amount' if 'amount' in df1.columns else 'transaction_amount'
                        # Mark top 1% of transactions by amount as potentially fraudulent
                        threshold = df1[amount_col].quantile(0.99)
                        df1['isFraud'] = (df1[amount_col] > threshold).astype(int)
                    else:
                        # If no amount column, create random fraud labels with 1% fraud rate
                        df1['isFraud'] = np.random.choice([0, 1], size=len(df1), p=[0.99, 0.01])
                
                # Add dataset source column
                df1['dataset_source'] = 'upi_transactions'
                
                print(f"Dataset 1 shape: {df1.shape}")
                print(f"Dataset 1 fraud distribution: \n{df1['isFraud'].value_counts()}")
                
                # Save to data directory
                output_file_1 = os.path.join(data_dir, 'upi_transactions_fraud.csv')
                df1.to_csv(output_file_1, index=False)
                print(f"Saved UPI Transactions dataset to {output_file_1}")
                
                datasets.append(df1)
                break
    except Exception as e:
        print(f"Error downloading UPI Transactions dataset: {str(e)}")
    
    # Dataset 2: Credit Card Fraud by Kartik
    try:
        print("\nDownloading Dataset 2: Credit Card Fraud...")
        kaggle_path_2 = kagglehub.dataset_download("kartik2112/fraud-detection")
        print(f"Path to dataset files: {kaggle_path_2}")
        
        # Find the main CSV file
        for file in os.listdir(kaggle_path_2):
            if file.endswith('.csv'):
                source_file_2 = os.path.join(kaggle_path_2, file)
                df2 = pd.read_csv(source_file_2)
                
                # Check if it has fraud indicators
                if 'is_fraud' in df2.columns:
                    df2.rename(columns={'is_fraud': 'isFraud'}, inplace=True)
                elif 'fraud' in df2.columns:
                    df2.rename(columns={'fraud': 'isFraud'}, inplace=True)
                elif 'class' in df2.columns:
                    df2.rename(columns={'class': 'isFraud'}, inplace=True)
                
                # Add dataset source column
                df2['dataset_source'] = 'credit_card'
                
                print(f"Dataset 2 shape: {df2.shape}")
                print(f"Dataset 2 fraud distribution: \n{df2['isFraud'].value_counts()}")
                
                # Save to data directory
                output_file_2 = os.path.join(data_dir, 'credit_card_fraud.csv')
                df2.to_csv(output_file_2, index=False)
                print(f"Saved Credit Card Fraud dataset to {output_file_2}")
                
                datasets.append(df2)
                break
    except Exception as e:
        print(f"Error downloading Credit Card Fraud dataset: {str(e)}")
    
    # Dataset 3: 2023 Credit Card Fraud
    try:
        print("\nDownloading Dataset 3: 2023 Credit Card Fraud...")
        kaggle_path_3 = kagglehub.dataset_download("nelgiriyewithana/credit-card-fraud-detection-dataset-2023")
        print(f"Path to dataset files: {kaggle_path_3}")
        
        # Find the main CSV file
        for file in os.listdir(kaggle_path_3):
            if file.endswith('.csv'):
                source_file_3 = os.path.join(kaggle_path_3, file)
                df3 = pd.read_csv(source_file_3)
                
                # Check if it has fraud indicators
                if 'is_fraud' in df3.columns:
                    df3.rename(columns={'is_fraud': 'isFraud'}, inplace=True)
                elif 'fraud' in df3.columns:
                    df3.rename(columns={'fraud': 'isFraud'}, inplace=True)
                elif 'class' in df3.columns:
                    df3.rename(columns={'class': 'isFraud'}, inplace=True)
                
                # Add dataset source column
                df3['dataset_source'] = 'cc_fraud_2023'
                
                print(f"Dataset 3 shape: {df3.shape}")
                print(f"Dataset 3 fraud distribution: \n{df3['isFraud'].value_counts()}")
                
                # Save to data directory
                output_file_3 = os.path.join(data_dir, 'cc_fraud_2023.csv')
                df3.to_csv(output_file_3, index=False)
                print(f"Saved 2023 Credit Card Fraud dataset to {output_file_3}")
                
                datasets.append(df3)
                break
    except Exception as e:
        print(f"Error downloading 2023 Credit Card Fraud dataset: {str(e)}")
    
    # Dataset 4: Online Payment Fraud
    try:
        print("\nDownloading Dataset 4: Online Payment Fraud...")
        kaggle_path_4 = kagglehub.dataset_download("jainilcoder/online-payment-fraud-detection")
        print(f"Path to dataset files: {kaggle_path_4}")
        
        # Find the main CSV file (we know it's onlinefraud.csv from the previous code)
        source_file_4 = os.path.join(kaggle_path_4, 'onlinefraud.csv')
        if os.path.exists(source_file_4):
            df4 = pd.read_csv(source_file_4)
            
            # Add dataset source column
            df4['dataset_source'] = 'online_payment'
            
            print(f"Dataset 4 shape: {df4.shape}")
            print(f"Dataset 4 fraud distribution: \n{df4['isFraud'].value_counts()}")
            
            # Save to data directory
            output_file_4 = os.path.join(data_dir, 'online_payment_fraud.csv')
            df4.to_csv(output_file_4, index=False)
            print(f"Saved Online Payment Fraud dataset to {output_file_4}")
            
            datasets.append(df4)
    except Exception as e:
        print(f"Error downloading Online Payment Fraud dataset: {str(e)}")
    
    if len(datasets) == 0:
        print("No datasets could be downloaded. Please check your internet connection.")
        return None
    
    return datasets

def normalize_dataset_schema(dataframes):
    """
    Normalize different dataset schemas to create a common format.
    """
    print("\nNormalizing dataset schemas...")
    
    # Ensure all dataframes have the required columns
    required_columns = {'isFraud', 'dataset_source'}
    
    # Identify common features across all datasets
    all_columns = set()
    for df in dataframes:
        all_columns.update(df.columns)
    
    # Process each dataframe to ensure it has required columns
    for i, df in enumerate(dataframes):
        for col in required_columns:
            if col not in df.columns:
                if col == 'isFraud':
                    # This should have been handled during loading
                    raise ValueError(f"Dataset {i} missing required 'isFraud' column")
                elif col == 'dataset_source':
                    # This should have been added during loading
                    df['dataset_source'] = f"unknown_{i}"
        
        # Look for and standardize amount column
        if 'amount' not in df.columns:
            amount_alternatives = ['amt', 'transaction_amount', 'tx_amount', 'Amount']
            found = False
            for alt in amount_alternatives:
                if alt in df.columns:
                    df.rename(columns={alt: 'amount'}, inplace=True)
                    found = True
                    break
            if not found:
                # Create a synthetic amount column
                print(f"Warning: Creating synthetic amount column for dataset {i}")
                df['amount'] = np.random.exponential(100, len(df))
    
    # List of columns to keep in the final datasets
    common_columns = ['isFraud', 'amount', 'dataset_source']
    
    # Add additional useful columns that might be present
    for col in all_columns:
        if col.lower() in ['type', 'transaction_type', 'tx_type']:
            for df in dataframes:
                if col in df.columns:
                    df.rename(columns={col: 'type'}, inplace=True)
            common_columns.append('type')
            break
    
    # Process categorical and numerical columns
    normalized_dfs = []
    for i, df in enumerate(dataframes):
        # Create a copy to avoid modifying the original
        df_copy = df.copy()
        
        # Keep track of columns to include
        columns_to_keep = [col for col in common_columns if col in df_copy.columns]
        
        # Add balance columns if they exist
        balance_columns = ['oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
        for col in balance_columns:
            if col in df_copy.columns:
                columns_to_keep.append(col)
        
        # Add timestamp related columns
        for col in df_copy.columns:
            if any(time_kw in col.lower() for time_kw in ['time', 'date', 'step', 'hour', 'day']):
                columns_to_keep.append(col)
        
        # Add additional numeric columns
        for col in df_copy.columns:
            if col not in columns_to_keep and df_copy[col].dtype in ['int64', 'float64']:
                columns_to_keep.append(col)
        
        # Add additional categorical columns (limited to those with few unique values)
        for col in df_copy.columns:
            if col not in columns_to_keep and df_copy[col].dtype == 'object' and df_copy[col].nunique() < 50:
                columns_to_keep.append(col)
        
        # Limit total columns to prevent excessive dimensionality
        if len(columns_to_keep) > 30:
            print(f"Warning: Limiting to 30 most important columns for dataset {i}")
            columns_to_keep = columns_to_keep[:30]
        
        # Create normalized dataframe
        normalized_df = df_copy[columns_to_keep].copy()
        normalized_dfs.append(normalized_df)
        
        print(f"Normalized dataset {i} shape: {normalized_df.shape}")
        print(f"Columns: {normalized_df.columns.tolist()}")
    
    # Combine all normalized dataframes
    combined_df = pd.concat(normalized_dfs, ignore_index=True)
    print(f"\nCombined normalized dataframe shape: {combined_df.shape}")
    
    return combined_df

def preprocess_data(df, test_size=0.3, random_state=42):
    """
    Preprocess the data for model training:
    - Handle missing values
    - Feature engineering
    - Encode categorical variables
    - Split into train/test sets
    """
    print("\nPreprocessing data...")
    
    # Fill missing numerical values with median
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        df[col] = df[col].fillna(df[col].median())
    
    # Fill missing categorical values with 'unknown'
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna('unknown')
    
    # Feature engineering
    features_added = []
    
    # Amount-related features
    if 'amount' in df.columns:
        df['amount_log'] = np.log1p(df['amount'])
        features_added.append('amount_log')
    
    # Balance-related features
    if all(col in df.columns for col in ['oldbalanceOrg', 'newbalanceOrig']):
        df['orig_balance_diff'] = df['newbalanceOrig'] - df['oldbalanceOrg']
        df['orig_zero_balance'] = (df['oldbalanceOrg'] == 0).astype(int)
        features_added.extend(['orig_balance_diff', 'orig_zero_balance'])
    
    if all(col in df.columns for col in ['oldbalanceDest', 'newbalanceDest']):
        df['dest_balance_diff'] = df['newbalanceDest'] - df['oldbalanceDest']
        df['dest_zero_balance'] = (df['oldbalanceDest'] == 0).astype(int)
        features_added.extend(['dest_balance_diff', 'dest_zero_balance'])
    
    # Time-related features
    if 'step' in df.columns:
        df['day'] = df['step'] // 24
        df['hour'] = df['step'] % 24
        features_added.extend(['day', 'hour'])
    
    print(f"Added {len(features_added)} engineered features: {features_added}")
    
    # Identify features for preprocessing
    categorical_features = []
    for col in df.columns:
        if df[col].dtype == 'object' or (col == 'dataset_source'):
            categorical_features.append(col)
    
    # Exclude ID-like features and the target
    exclude_features = ['isFraud']
    for col in df.columns:
        if any(id_kw in col.lower() for id_kw in ['id', 'name', 'orig', 'dest']) and col not in categorical_features:
            exclude_features.append(col)
    
    # Remove already excluded columns from categorical features
    categorical_features = [col for col in categorical_features if col not in exclude_features]
    
    # Select numerical features
    numerical_features = [col for col in df.columns if 
                         col not in categorical_features + exclude_features and
                         df[col].dtype in ['int64', 'float64']]
    
    print(f"Categorical features ({len(categorical_features)}): {categorical_features}")
    print(f"Numerical features ({len(numerical_features)}): {numerical_features}")
    print(f"Excluded features ({len(exclude_features)}): {exclude_features}")
    
    # Create preprocessing pipelines
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(drop='first', handle_unknown='ignore')
    
    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'  # Drop other columns not specified
    )
    
    # Prepare features and target
    X = df.drop(columns=exclude_features)
    y = df['isFraud']
    
    # Split the data with stratification to maintain fraud ratio (70-30 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Report class distribution
    print(f"Training set fraud ratio: {y_train.mean():.4f}")
    print(f"Testing set fraud ratio: {y_test.mean():.4f}")
    
    # Fit the preprocessor on training data
    X_train_preprocessed = preprocessor.fit_transform(X_train)
    X_test_preprocessed = preprocessor.transform(X_test)
    
    print(f"Preprocessed training data shape: {X_train_preprocessed.shape}")
    print(f"Preprocessed testing data shape: {X_test_preprocessed.shape}")
    
    return X_train_preprocessed, X_test_preprocessed, y_train, y_test, preprocessor, X.columns

def train_model(X_train, y_train, X_test, y_test):
    """
    Train an XGBoost classifier and evaluate its performance.
    """
    print("\nTraining XGBoost model...")
    
    # Create XGBoost classifier with parameters for imbalanced data
    model = xgb.XGBClassifier(
        scale_pos_weight=len(y_train) / sum(y_train),  # Handle class imbalance
        learning_rate=0.1,
        n_estimators=100,
        max_depth=4,
        use_label_encoder=False,
        eval_metric='auc',
        random_state=42
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate on training data
    train_preds = model.predict(X_train)
    train_probs = model.predict_proba(X_train)[:, 1]
    
    print("\nTraining performance:")
    print(classification_report(y_train, train_preds))
    print(f"ROC-AUC score: {roc_auc_score(y_train, train_probs):.4f}")
    
    # Evaluate on test data
    test_preds = model.predict(X_test)
    test_probs = model.predict_proba(X_test)[:, 1]
    
    print("\nTest performance:")
    print(classification_report(y_test, test_preds))
    print(f"ROC-AUC score: {roc_auc_score(y_test, test_probs):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, test_preds))
    
    return model

def save_model(model, preprocessor, feature_names, model_dir='models/saved_models'):
    """
    Save the trained model, preprocessor, and feature names to disk.
    """
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(model_dir, 'xgboost.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save preprocessor
    preprocessor_path = os.path.join(model_dir, 'xgboost_preprocessor.pkl')
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    # Save feature names
    feature_names_path = os.path.join(model_dir, 'xgboost_feature_names.pkl')
    with open(feature_names_path, 'wb') as f:
        pickle.dump(feature_names, f)
    
    print(f"\nModel, preprocessor, and feature names saved to {model_dir}")

def main():
    """
    Main function to execute the workflow:
    1. Download datasets
    2. Normalize schemas
    3. Preprocess data
    4. Train model
    5. Save model
    """
    print("=== Fraud Detection System: Download and Training ===")
    
    # Step 1: Download datasets
    datasets = download_datasets()
    if not datasets:
        print("Error: No datasets were downloaded. Exiting.")
        return
    
    # Step 2: Normalize schemas
    combined_df = normalize_dataset_schema(datasets)
    
    # Step 3: Preprocess data with 70-30 train-test split
    X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_data(
        combined_df, test_size=0.3, random_state=42
    )
    
    # Step 4: Train model
    model = train_model(X_train, y_train, X_test, y_test)
    
    # Step 5: Save model
    save_model(model, preprocessor, feature_names)
    
    print("\n=== Training process completed successfully ===")

if __name__ == "__main__":
    main() 