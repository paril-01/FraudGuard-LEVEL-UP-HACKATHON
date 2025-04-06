import os
import sys
import argparse
import traceback

def create_directories():
    """Create necessary directories for the project"""
    directories = [
        'data',
        'src/models/saved_models',
        'src/visualization/results'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def run_data_download():
    """Run the data download script"""
    print("Starting data download process...")
    # Ensure the import happens cleanly
    try:
        print("Attempting to import download_fraud_dataset...")
        from src.data.download_data import download_fraud_dataset
        print("Successfully imported download_fraud_dataset")
    except SyntaxError as e:
        print(f"SyntaxError during import from src.data.download_data: {e}")
        print(traceback.format_exc())
        sys.exit(1)
    except ImportError as e:
        print(f"ImportError: Could not import download_fraud_dataset. Check src/data/download_data.py: {e}")
        print(traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during import: {e}")
        print(traceback.format_exc())
        sys.exit(1)

    print("Downloading and preparing dataset...")
    try:
        data_path = download_fraud_dataset()
        print(f"download_fraud_dataset returned: {data_path}")
    except Exception as e:
        print(f"Error during download_fraud_dataset execution: {e}")
        print(traceback.format_exc())
        sys.exit(1)
        
    if data_path is None:
        print("Failed to get data path from download script. Exiting.")
        sys.exit(1)
    print(f"Dataset ready at: {data_path}")
    return data_path

def run_preprocessing(data_path=None):
    """Run the preprocessing script"""
    try:
        from src.preprocessing.preprocess import load_data, preprocess_data
    except ImportError as e:
        print(f"ImportError: Could not import from src.preprocessing.preprocess: {e}")
        sys.exit(1)

    if data_path is None:
        data_path = os.path.join('data', 'online_fraud.csv')
    
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Running download script...")
        data_path = run_data_download()
        if data_path is None:
            print("Failed to download data during preprocessing step. Exiting.")
            sys.exit(1)

    print("Preprocessing data...")
    try:
        df = load_data(data_path)
        X_train, X_test, y_train, y_test, preprocessor, feature_names = preprocess_data(df)
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        sys.exit(1)
    
    print(f"Preprocessing complete:")
    print(f"  - Training set shape: {X_train.shape}")
    print(f"  - Testing set shape: {X_test.shape}")
    print(f"  - Positive class proportion in training: {sum(y_train)/len(y_train):.4f}")
    
    return X_train, X_test, y_train, y_test, preprocessor, feature_names

def run_model_training():
    """Run the model training script"""
    try:
        from src.models.train_model import main as train_models
    except ImportError as e:
        print(f"ImportError: Could not import from src.models.train_model: {e}")
        sys.exit(1)

    print("Training and evaluating models...")
    try:
        train_models()
    except Exception as e:
        print(f"Error during model training: {e}")
        sys.exit(1)

def run_api_server():
    """Run the API server"""
    try:
        import uvicorn
        from src.api.app import app
    except ImportError as e:
        print(f"ImportError: Could not import uvicorn or src.api.app: {e}")
        sys.exit(1)

    print("Starting API server...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)

def main():
    """Main function to run the full pipeline"""
    parser = argparse.ArgumentParser(description='Fraud Detection System')
    parser.add_argument('--step', type=str, choices=['all', 'download', 'preprocess', 'train', 'api'], 
                        default='all', help='Step to run')
    
    args = parser.parse_args()
    
    # Create directories
    create_directories()
    
    data_path = None # Initialize data_path

    if args.step == 'all' or args.step == 'download':
        data_path = run_data_download()
        if args.step == 'download': return

    if args.step == 'all' or args.step == 'preprocess':
        run_preprocessing(data_path) # Pass potentially downloaded path
        if args.step == 'preprocess': return

    if args.step == 'all' or args.step == 'train':
        run_model_training()
        if args.step == 'train': return

    if args.step == 'api': # Run API only if explicitly requested
        run_api_server()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")
        sys.exit(1) 