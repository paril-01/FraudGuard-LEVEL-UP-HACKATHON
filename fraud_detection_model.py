import os
import kagglehub
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score, precision_recall_curve
from sklearn.feature_selection import SelectKBest, f_classif
import shutil
import gc
import pickle

# Create a directory for datasets if it doesn't exist
os.makedirs('datasets', exist_ok=True)
# Create a directory for models
os.makedirs('models', exist_ok=True)

# Function to save model to disk
def save_model(model_info, model_name):
    """
    Save the trained model and related data to disk
    
    Args:
        model_info (dict): Dictionary containing model information
        model_name (str): Name to use for the saved model
    """
    model_path = os.path.join('models', f"{model_name}.pkl")
    
    # Create a dictionary with all necessary components for prediction
    model_data = {
        'model': model_info['model'],
        'scaler': model_info['scaler'],
        'feature_names': model_info['feature_names'],
        'accuracy': model_info['accuracy'],
        'auc': model_info['auc'],
        'feature_importances': model_info['feature_importances']
    }
    
    # Save to disk
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"Saved model to {model_path}")

# Function to download datasets
def download_dataset(dataset_id):
    print(f"Downloading dataset: {dataset_id}")
    try:
        path = kagglehub.dataset_download(dataset_id)
        print(f"Path to dataset files: {path}")
        
        # Copy files to our datasets directory
        dataset_name = dataset_id.split('/')[-1]
        dest_dir = os.path.join('datasets', dataset_name)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy all files from downloaded path to our destination
        for root, dirs, files in os.walk(path):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir, file)
                shutil.copy(src_file, dst_file)
                print(f"Copied {file} to {dest_dir}")
        
        return dest_dir
    except Exception as e:
        print(f"Error downloading {dataset_id}: {e}")
        return None

# Train fraud detection model on the online payment fraud dataset (most common fraud dataset)
def train_online_payment_fraud_model():
    dataset_path = "datasets/online-payment-fraud-detection"
    
    # Check if the dataset exists
    if not os.path.exists(dataset_path):
        # Try to download it
        dataset_id = "jainilcoder/online-payment-fraud-detection"
        dataset_path = download_dataset(dataset_id)
        if not dataset_path:
            print("Failed to download online payment fraud dataset")
            return
    
    data_path = os.path.join(dataset_path, "onlinefraud.csv")
    if not os.path.exists(data_path):
        print(f"CSV file not found: {data_path}")
        return
    
    print(f"Loading and processing online payment fraud dataset...")
    
    # Read a sample to understand the schema
    df_sample = pd.read_csv(data_path, nrows=5)
    print(f"Dataset columns: {df_sample.columns.tolist()}")
    
    # Verify the target column exists
    if 'isFraud' not in df_sample.columns:
        print("Target column 'isFraud' not found in the dataset")
        return
    
    # Read the data with chunking and process in chunks
    chunk_size = 100000
    
    # Function to process a chunk
    def process_chunk(df):
        # Handle missing values
        df = df.dropna()
        
        # Select only necessary columns (domain knowledge for fraud detection)
        selected_columns = ['type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 
                           'oldbalanceDest', 'newbalanceDest', 'isFraud']
        df = df[selected_columns]
        
        # Convert 'type' to numerical using label encoding
        le = LabelEncoder()
        df['type'] = le.fit_transform(df['type'])
        
        # Add derived features that might help detect fraud
        df['balanceDiff'] = df['oldbalanceOrg'] - df['newbalanceOrig']
        df['destBalanceDiff'] = df['newbalanceDest'] - df['oldbalanceDest']
        
        # Separate features and target
        X = df.drop(columns=['isFraud'])
        y = df['isFraud']
        
        return X, y
    
    # Read in chunks and collect a balanced sample
    fraud_chunks = []
    non_fraud_chunks = []
    
    # Target numbers for a balanced dataset
    target_fraud_count = 10000
    target_non_fraud_count = 10000
    fraud_count = 0
    non_fraud_count = 0
    
    print("Reading data in chunks and sampling for balanced training set...")
    
    # Read and process chunks
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Process this chunk
        X_chunk, y_chunk = process_chunk(chunk)
        
        # Split fraud and non-fraud data
        fraud_idx = y_chunk == 1
        non_fraud_idx = y_chunk == 0
        
        # Add to collection if needed
        if fraud_count < target_fraud_count:
            fraud_chunks.append((X_chunk[fraud_idx], y_chunk[fraud_idx]))
            fraud_count += sum(fraud_idx)
        
        if non_fraud_count < target_non_fraud_count:
            # Randomly sample non-fraud data to keep things manageable
            if sum(non_fraud_idx) > 1000:
                non_fraud_sample_idx = np.random.choice(np.where(non_fraud_idx)[0], 
                                                       size=min(1000, sum(non_fraud_idx)), 
                                                       replace=False)
                non_fraud_idx = np.zeros_like(non_fraud_idx)
                non_fraud_idx[non_fraud_sample_idx] = True
                
            non_fraud_chunks.append((X_chunk[non_fraud_idx], y_chunk[non_fraud_idx]))
            non_fraud_count += sum(non_fraud_idx)
            
        # Display progress and check if we have enough data
        print(f"Collected {fraud_count} fraud and {non_fraud_count} non-fraud samples")
        
        if fraud_count >= target_fraud_count and non_fraud_count >= target_non_fraud_count:
            break
    
    # Combine chunks for fraud and non-fraud
    X_fraud = pd.concat([chunk[0] for chunk in fraud_chunks])[:target_fraud_count]
    y_fraud = pd.concat([chunk[1] for chunk in fraud_chunks])[:target_fraud_count]
    
    X_non_fraud = pd.concat([chunk[0] for chunk in non_fraud_chunks])[:target_non_fraud_count]
    y_non_fraud = pd.concat([chunk[1] for chunk in non_fraud_chunks])[:target_non_fraud_count]
    
    # Combine to a balanced dataset
    X = pd.concat([X_fraud, X_non_fraud])
    y = pd.concat([y_fraud, y_non_fraud])
    
    # Clear memory
    del fraud_chunks, non_fraud_chunks, X_fraud, X_non_fraud, y_fraud, y_non_fraud
    gc.collect()
    
    print(f"Final dataset shape: {X.shape} with {sum(y == 1)} fraud samples ({sum(y == 1)/len(y)*100:.2f}%)")
    
    # Train-test split (70-30)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC: {auc:.4f}")
    
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Online Payment Fraud')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix_online_payment_fraud.png')
    print(f"Saved confusion matrix to confusion_matrix_online_payment_fraud.png")
    
    # Display classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importances = model.feature_importances_
    feature_names = X.columns
    
    # Sort feature importances in descending order
    sorted_idx = np.argsort(feature_importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(sorted_idx)), feature_importances[sorted_idx])
    plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
    plt.xlabel('Feature Importance')
    plt.title('Feature Importance - Online Payment Fraud')
    plt.tight_layout()
    plt.savefig('feature_importance_online_payment_fraud.png')
    print(f"Saved feature importance plot to feature_importance_online_payment_fraud.png")
    
    # Create a dictionary with model information
    model_info = {
        'name': 'online-payment-fraud',
        'model': model,
        'scaler': scaler,
        'feature_names': X.columns.tolist(),
        'accuracy': accuracy,
        'auc': auc,
        'feature_importances': dict(zip(feature_names, feature_importances))
    }
    
    # Save the model
    save_model(model_info, 'online-payment-fraud')
    
    return model_info

# Train model on the credit card fraud dataset
def train_credit_card_fraud_model():
    dataset_path = "datasets/fraud-detection"
    
    # Check if the dataset exists
    if not os.path.exists(dataset_path):
        # Try to download it
        dataset_id = "kartik2112/fraud-detection"
        dataset_path = download_dataset(dataset_id)
        if not dataset_path:
            print("Failed to download credit card fraud dataset")
            return
    
    # Find CSV files in the dataset directory
    csv_files = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print(f"No CSV files found in {dataset_path}")
        return
    
    # Use the first CSV file (typically fraudTrain.csv)
    data_path = csv_files[0]
    print(f"Loading file: {data_path}")
    
    # Read a sample to understand the schema
    df_sample = pd.read_csv(data_path, nrows=5)
    print(f"Dataset columns: {df_sample.columns.tolist()}")
    
    # Verify the target column exists
    if 'is_fraud' not in df_sample.columns:
        print("Target column 'is_fraud' not found in the dataset")
        return

    # Read data with chunking and select important features for fraud detection
    chunk_size = 50000
    
    # Function to process a chunk
    def process_chunk(df):
        # Handle missing values
        df = df.dropna()
        
        # Select only necessary features for fraud detection
        # Drop irrelevant columns like 'Unnamed: 0', customer identifiers, transaction time
        selected_columns = ['category', 'amt', 'city_pop', 'is_fraud']
        df = df[selected_columns] 
        
        # Convert categorical variables using label encoding to avoid dimensionality explosion
        le = LabelEncoder()
        df['category'] = le.fit_transform(df['category'])
        
        # Separate features and target
        X = df.drop(columns=['is_fraud'])
        y = df['is_fraud']
        
        return X, y
    
    # Read in chunks and collect a balanced sample
    fraud_chunks = []
    non_fraud_chunks = []
    
    # Target numbers for a balanced dataset
    target_fraud_count = 5000
    target_non_fraud_count = 5000
    fraud_count = 0
    non_fraud_count = 0
    
    print("Reading data in chunks and sampling for balanced training set...")
    
    # Read and process chunks
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Process this chunk
        X_chunk, y_chunk = process_chunk(chunk)
        
        # Split fraud and non-fraud data
        fraud_idx = y_chunk == 1
        non_fraud_idx = y_chunk == 0
        
        # Add to collection if needed
        if fraud_count < target_fraud_count:
            fraud_chunks.append((X_chunk[fraud_idx], y_chunk[fraud_idx]))
            fraud_count += sum(fraud_idx)
        
        if non_fraud_count < target_non_fraud_count:
            # Randomly sample non-fraud data to keep things manageable
            if sum(non_fraud_idx) > 1000:
                non_fraud_sample_idx = np.random.choice(np.where(non_fraud_idx)[0], 
                                                       size=min(1000, sum(non_fraud_idx)), 
                                                       replace=False)
                non_fraud_idx = np.zeros_like(non_fraud_idx)
                non_fraud_idx[non_fraud_sample_idx] = True
                
            non_fraud_chunks.append((X_chunk[non_fraud_idx], y_chunk[non_fraud_idx]))
            non_fraud_count += sum(non_fraud_idx)
            
        # Display progress and check if we have enough data
        print(f"Collected {fraud_count} fraud and {non_fraud_count} non-fraud samples")
        
        if fraud_count >= target_fraud_count and non_fraud_count >= target_non_fraud_count:
            break
    
    # Combine chunks for fraud and non-fraud
    X_fraud = pd.concat([chunk[0] for chunk in fraud_chunks])[:target_fraud_count]
    y_fraud = pd.concat([chunk[1] for chunk in fraud_chunks])[:target_fraud_count]
    
    X_non_fraud = pd.concat([chunk[0] for chunk in non_fraud_chunks])[:target_non_fraud_count]
    y_non_fraud = pd.concat([chunk[1] for chunk in non_fraud_chunks])[:target_non_fraud_count]
    
    # Combine to a balanced dataset
    X = pd.concat([X_fraud, X_non_fraud])
    y = pd.concat([y_fraud, y_non_fraud])
    
    # Clear memory
    del fraud_chunks, non_fraud_chunks, X_fraud, X_non_fraud, y_fraud, y_non_fraud
    gc.collect()
    
    print(f"Final dataset shape: {X.shape} with {sum(y == 1)} fraud samples ({sum(y == 1)/len(y)*100:.2f}%)")
    
    # Train-test split (70-30)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC: {auc:.4f}")
    
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Credit Card Fraud')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix_credit_card_fraud.png')
    print(f"Saved confusion matrix to confusion_matrix_credit_card_fraud.png")
    
    # Display classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importances = model.feature_importances_
    feature_names = X.columns
    
    # Sort feature importances in descending order
    sorted_idx = np.argsort(feature_importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(sorted_idx)), feature_importances[sorted_idx])
    plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
    plt.xlabel('Feature Importance')
    plt.title('Feature Importance - Credit Card Fraud')
    plt.tight_layout()
    plt.savefig('feature_importance_credit_card_fraud.png')
    print(f"Saved feature importance plot to feature_importance_credit_card_fraud.png")
    
    # Create a dictionary with model information
    model_info = {
        'name': 'credit-card-fraud',
        'model': model,
        'scaler': scaler,
        'feature_names': X.columns.tolist(),
        'accuracy': accuracy,
        'auc': auc,
        'feature_importances': dict(zip(feature_names, feature_importances))
    }
    
    # Save the model
    save_model(model_info, 'credit-card-fraud')
    
    return model_info

# Train model on the e-commerce transactions dataset
def train_ecommerce_fraud_model():
    dataset_path = "datasets/e-commerce-transactions-dataset"
    
    # Check if the dataset exists
    if not os.path.exists(dataset_path):
        # Try to download it
        dataset_id = "smayanj/e-commerce-transactions-dataset"
        dataset_path = download_dataset(dataset_id)
        if not dataset_path:
            print("Failed to download e-commerce transactions dataset")
            return
    
    # Find CSV files in the dataset directory
    csv_files = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print(f"No CSV files found in {dataset_path}")
        return
    
    # Use the first CSV file
    data_path = csv_files[0]
    print(f"Loading file: {data_path}")
    
    # Read a sample to understand the schema
    df_sample = pd.read_csv(data_path, nrows=5)
    print(f"Dataset columns: {df_sample.columns.tolist()}")
    
    # Check if this is a fraud detection dataset by looking for common fraud indicators
    possible_target_columns = ['fraud', 'is_fraud', 'isFraud', 'fraudulent', 'Class', 'class', 'Target', 'target']
    target_column = None
    
    for col in possible_target_columns:
        if col in df_sample.columns:
            target_column = col
            break
    
    # If no direct fraud column, check if there's a transaction status column that can indicate fraud
    if target_column is None:
        possible_status_columns = ['status', 'transaction_status', 'payment_status']
        for col in possible_status_columns:
            if col in df_sample.columns:
                print(f"Found status column: {col}")
                # Check values to see if we can derive a fraud indicator
                full_sample = pd.read_csv(data_path, usecols=[col], nrows=1000)
                print(f"Status values: {full_sample[col].value_counts()}")
                if 'fraud' in full_sample[col].astype(str).str.lower().values:
                    print(f"Will use {col} to derive fraud indicator")
                    target_column = col
                    break
    
    # Read the dataset and create synthetic fraud for e-commerce transactions
    print("Creating a synthetic fraud target based on anomaly detection...")
    
    # Read the whole dataset or a large sample
    try:
        df = pd.read_csv(data_path)
    except:
        # If file is too large, sample it
        df = pd.read_csv(data_path, nrows=100000)
    
    print(f"Dataset shape: {df.shape}")
    
    # Select numeric columns for anomaly detection
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        print("Not enough numeric features for anomaly detection")
        return
    
    print(f"Using numeric columns for anomaly detection: {numeric_cols}")
    
    # Fill missing values
    df_numeric = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    # Scale the data
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_numeric)
    
    # Use Isolation Forest for anomaly detection
    from sklearn.ensemble import IsolationForest
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    df['fraud_synthetic'] = iso_forest.fit_predict(scaled_data)
    # Convert predictions to binary (1 for fraud, 0 for normal)
    df['fraud_synthetic'] = df['fraud_synthetic'].map({1: 0, -1: 1})
    
    target_column = 'fraud_synthetic'
    print(f"Created synthetic fraud labels with {df[target_column].sum()} potential fraud cases ({df[target_column].mean()*100:.2f}%)")
    
    # Clean categorical columns and convert to numeric
    categorical_cols = []
    for col in df.select_dtypes(include=['object']).columns:
        if col != target_column:
            categorical_cols.append(col)
    
    print(f"Converting categorical columns: {categorical_cols}")
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Check class imbalance
    class_counts = y.value_counts()
    print("Class distribution:")
    for class_label, count in class_counts.items():
        print(f"  Class {class_label}: {count} ({count/len(y)*100:.2f}%)")
    
    # Balance the dataset
    print("Balancing dataset for training...")
    fraud_idx = y == 1
    non_fraud_idx = y == 0
    
    fraud_count = sum(fraud_idx)
    # Use a 1:3 ratio for fraud:non-fraud
    target_non_fraud_count = min(fraud_count * 3, sum(non_fraud_idx))
    
    # Sample non-fraud data
    if sum(non_fraud_idx) > target_non_fraud_count:
        non_fraud_sample_idx = np.random.choice(np.where(non_fraud_idx)[0], 
                                               size=target_non_fraud_count, 
                                               replace=False)
        combined_idx = np.concatenate([np.where(fraud_idx)[0], non_fraud_sample_idx])
        X = X.iloc[combined_idx]
        y = y.iloc[combined_idx]
    
    print(f"Balanced dataset shape: {X.shape} with {sum(y == 1)} fraud samples ({sum(y == 1)/len(y)*100:.2f}%)")
    
    # Train-test split (70-30)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC: {auc:.4f}")
    
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - E-commerce Fraud')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix_ecommerce_fraud.png')
    print(f"Saved confusion matrix to confusion_matrix_ecommerce_fraud.png")
    
    # Display classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importances = model.feature_importances_
    feature_names = X.columns
    
    # Sort feature importances in descending order
    sorted_idx = np.argsort(feature_importances)[::-1]
    
    # Display top 20 features (or all if less than 20)
    top_n = min(20, len(sorted_idx))
    plt.figure(figsize=(12, 8))
    plt.barh(range(top_n), feature_importances[sorted_idx[:top_n]])
    plt.yticks(range(top_n), [feature_names[i] for i in sorted_idx[:top_n]])
    plt.xlabel('Feature Importance')
    plt.title('Top Feature Importance - E-commerce Fraud')
    plt.tight_layout()
    plt.savefig('feature_importance_ecommerce_fraud.png')
    print(f"Saved feature importance plot to feature_importance_ecommerce_fraud.png")
    
    # Create a dictionary with model information
    model_info = {
        'name': 'e-commerce-fraud',
        'model': model,
        'scaler': scaler,
        'feature_names': X.columns.tolist(),
        'accuracy': accuracy,
        'auc': auc,
        'feature_importances': dict(zip(feature_names, feature_importances))
    }
    
    # Save the model
    save_model(model_info, 'e-commerce-fraud')
    
    return model_info

# Train model on the fraud e-commerce dataset
def train_fraud_ecommerce_model():
    dataset_path = "datasets/fraud-ecommerce"
    
    # Check if the dataset exists
    if not os.path.exists(dataset_path):
        # Try to download it
        dataset_id = "vbinh002/fraud-ecommerce"
        dataset_path = download_dataset(dataset_id)
        if not dataset_path:
            print("Failed to download fraud-ecommerce dataset")
            return
    
    # Find CSV files in the dataset directory
    csv_files = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print(f"No CSV files found in {dataset_path}")
        return
    
    # Use the first CSV file
    data_path = csv_files[0]
    print(f"Loading file: {data_path}")
    
    # Read the dataset
    df = pd.read_csv(data_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Dataset columns: {df.columns.tolist()}")
    
    # Identify target column (assuming 'Class' based on typical fraud dataset naming)
    if 'Class' not in df.columns:
        print("Target column 'Class' not found in the dataset")
        return
    target_column = 'Class'
    
    # Handle missing values
    df = df.dropna()
    
    # Convert categorical variables (e.g., 'Gender') to numerical
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    print(f"Converting categorical columns: {categorical_cols}")
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Check class imbalance
    class_counts = y.value_counts()
    print("Class distribution:")
    for class_label, count in class_counts.items():
        print(f"  Class {class_label}: {count} ({count/len(y)*100:.2f}%)")
    
    # Balance the dataset if needed (e.g., 1:3 ratio)
    if y.mean() < 0.1:  # Check if fraud cases are less than 10%
        print("Balancing dataset for training...")
        fraud_idx = y == 1
        non_fraud_idx = y == 0
        
        fraud_count = sum(fraud_idx)
        target_non_fraud_count = min(fraud_count * 3, sum(non_fraud_idx))
        
        # Sample non-fraud data
        if sum(non_fraud_idx) > target_non_fraud_count:
            non_fraud_sample_idx = np.random.choice(np.where(non_fraud_idx)[0], 
                                                   size=target_non_fraud_count, 
                                                   replace=False)
            combined_idx = np.concatenate([np.where(fraud_idx)[0], non_fraud_sample_idx])
            X = X.iloc[combined_idx]
            y = y.iloc[combined_idx]
        
        print(f"Balanced dataset shape: {X.shape} with {sum(y == 1)} fraud samples ({sum(y == 1)/len(y)*100:.2f}%)")
    
    # Train-test split (70-30)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC: {auc:.4f}")
    
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Fraud E-commerce')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix_fraud_ecommerce.png')
    print(f"Saved confusion matrix to confusion_matrix_fraud_ecommerce.png")
    
    # Display classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importances = model.feature_importances_
    feature_names = X.columns
    
    # Sort feature importances in descending order
    sorted_idx = np.argsort(feature_importances)[::-1]
    
    # Display top 20 features
    top_n = min(20, len(sorted_idx))
    plt.figure(figsize=(12, 8))
    plt.barh(range(top_n), feature_importances[sorted_idx[:top_n]])
    plt.yticks(range(top_n), [feature_names[i] for i in sorted_idx[:top_n]])
    plt.xlabel('Feature Importance')
    plt.title('Top Feature Importance - Fraud E-commerce')
    plt.tight_layout()
    plt.savefig('feature_importance_fraud_ecommerce.png')
    print(f"Saved feature importance plot to feature_importance_fraud_ecommerce.png")
    
    # Create a dictionary with model information
    model_info = {
        'name': 'fraud-ecommerce',
        'model': model,
        'scaler': scaler,
        'feature_names': X.columns.tolist(),
        'accuracy': accuracy,
        'auc': auc,
        'feature_importances': dict(zip(feature_names, feature_importances))
    }
    
    # Save the model
    save_model(model_info, 'fraud-ecommerce')
    
    return model_info

# Clean up function to organize directory
def clean_up_directory():
    print("\nCleaning up and organizing directory...")
    
    # Create organized directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('results/plots', exist_ok=True)
    
    # Move plots to results/plots directory
    for file in os.listdir():
        if file.endswith('.png'):
            shutil.move(file, os.path.join('results', 'plots', file))
            print(f"Moved {file} to results/plots/")
    
    # Clean up temporary files and downloaded cache
    temp_dirs = ['.kaggle', '__pycache__', 'tmp', '.ipynb_checkpoints']
    temp_extensions = ['.tmp', '.bak', '.log', '.pyc', '.DS_Store']
    
    # Clean temp files in datasets directory
    print("Cleaning up temporary files...")
    for root, dirs, files in os.walk('./datasets'):
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext in temp_extensions or any(file.endswith(ext) for ext in temp_extensions):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"Deleted temporary file: {os.path.join(root, file)}")
                except Exception as e:
                    print(f"Could not delete {os.path.join(root, file)}: {e}")
    
    # Remove unnecessary directories
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Removed unnecessary directory: {dir_name}")
            except Exception as e:
                print(f"Could not remove directory {dir_name}: {e}")
    
    # Organize dataset files
    print("Organizing dataset files...")
    for dataset_dir in os.listdir('datasets'):
        dataset_path = os.path.join('datasets', dataset_dir)
        if os.path.isdir(dataset_path):
            # Create README file in each dataset directory if it doesn't exist
            readme_path = os.path.join(dataset_path, 'README.md')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as f:
                    f.write(f"# {dataset_dir.replace('-', ' ').title()} Dataset\n\n")
                    f.write("Downloaded for fraud detection model training.\n")
    
    # Create summary file
    with open('results/summary.txt', 'w') as f:
        f.write("# Fraud Detection Models Summary\n\n")
        f.write("This directory contains results from training various fraud detection models.\n\n")
        f.write("## Models Trained\n\n")
        f.write("1. Online Payment Fraud Detection\n")
        f.write("2. Credit Card Fraud Detection\n")
        f.write("3. E-commerce Transactions Fraud Detection\n")
        f.write("4. Fraud E-commerce Detection\n")
        f.write("5. Bitcoin Transaction Fraud Detection\n\n")
        f.write("## Plots\n\n")
        f.write("The 'plots' directory contains confusion matrices and feature importance visualizations.\n")
    
    print("Directory cleanup and organization complete")

# Main execution
def main():
    print("=== Training Fraud Detection Models ===")
    
    results = []
    
    print("\n1. Training Online Payment Fraud Detection Model")
    payment_fraud_results = train_online_payment_fraud_model()
    if payment_fraud_results:
        results.append(payment_fraud_results)
    
    print("\n2. Training Credit Card Fraud Detection Model")
    credit_card_results = train_credit_card_fraud_model()
    if credit_card_results:
        results.append(credit_card_results)
    
    print("\n3. Training E-commerce Transactions Fraud Model (Synthetic)")
    ecommerce_results = train_ecommerce_fraud_model()
    if ecommerce_results:
        results.append(ecommerce_results)
        
    print("\n4. Training Fraud E-commerce Model")
    fraud_ecommerce_results = train_fraud_ecommerce_model()
    if fraud_ecommerce_results:
        results.append(fraud_ecommerce_results)
    
    print("\n=== Model Performance Summary ===")
    for model_info in sorted(results, key=lambda x: x.get('auc', 0), reverse=True):
        print(f"Dataset: {model_info['name']}")
        print(f"Accuracy: {model_info['accuracy']:.4f}")
        print(f"ROC AUC: {model_info.get('auc', 'N/A')}")
        
        print("Top 5 important features:")
        sorted_features = sorted(model_info['feature_importances'].items(), key=lambda x: x[1], reverse=True)[:5]
        for feature, importance in sorted_features:
            print(f"  - {feature}: {importance:.4f}")
        print()
    
    # Clean up the directory
    clean_up_directory()

if __name__ == "__main__":
    main() 