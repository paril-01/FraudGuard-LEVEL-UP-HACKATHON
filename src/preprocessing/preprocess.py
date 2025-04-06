import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def load_data(file_path):
    """Load the fraud dataset from CSV file"""
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully with shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def preprocess_data(df, test_size=0.2, random_state=42):
    """Preprocess the fraud dataset for model training"""
    # Display basic information
    print(f"Dataset has {df.shape[0]} rows and {df.shape[1]} columns")
    
    # Check if the expected target column exists
    if 'isFraud' not in df.columns:
        # If not, check for alternatives
        possible_target_columns = [col for col in df.columns if 'fraud' in col.lower()]
        if possible_target_columns:
            target_column = possible_target_columns[0]
            print(f"Using '{target_column}' as target column")
        else:
            # If no obvious target column, create a dummy one for demonstration
            print("No fraud target column found. Creating a dummy target for demonstration purposes.")
            # Assuming the last column might be the target
            target_column = df.columns[-1]
            # Convert to binary for demonstration
            df['isFraud'] = (df[target_column] > df[target_column].median()).astype(int)
            target_column = 'isFraud'
    else:
        target_column = 'isFraud'
    
    # Split features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Print class distribution
    print(f"Class distribution:")
    print(f"  - Non-fraud transactions: {sum(y == 0)} ({sum(y == 0)/len(y):.2%})")
    print(f"  - Fraud transactions: {sum(y == 1)} ({sum(y == 1)/len(y):.2%})")
    
    # Identify numeric and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    print(f"Features:")
    print(f"  - Numeric features: {len(numeric_features)}")
    print(f"  - Categorical features: {len(categorical_features)}")
    
    # Create preprocessing pipelines
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Get feature names after transformation
    feature_names = numeric_features.copy()
    if categorical_features:
        # We would need to fit the preprocessor to get the one-hot encoded feature names
        # This is a placeholder for demonstration
        feature_names += [f"{feat}_encoded" for feat in categorical_features]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Fit and transform the training data
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)
    
    print(f"Preprocessing complete. Training set shape: {X_train.shape}")
    
    return X_train, X_test, y_train, y_test, preprocessor, feature_names

if __name__ == "__main__":
    # Example usage
    file_path = "data/online_fraud.csv"
    df = load_data(file_path)
    X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_data(df)
    print("Preprocessing completed successfully!") 