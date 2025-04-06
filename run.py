import os
import subprocess
import sys

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

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        if result.returncode == 0:
            print(f"{description} completed successfully.")
            return True
        else:
            print(f"{description} failed with return code {result.returncode}.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"{description} failed with error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error running {description}: {str(e)}")
        return False

def main():
    """Run the fraud detection pipeline"""
    create_directories()
    
    # Run data download
    if not run_script('src/data/download_data.py', 'Data Download'):
        print("Data download failed. Exiting.")
        return
    
    # Run preprocessing
    if not run_script('src/preprocessing/preprocess.py', 'Data Preprocessing'):
        print("Data preprocessing failed. Exiting.")
        return
    
    # Run model training
    if not run_script('src/models/train_model.py', 'Model Training'):
        print("Model training failed. Exiting.")
        return
    
    # Run API
    print("\n=== API Server ===")
    print("To start the API server, run the following command:")
    print("python -m uvicorn src.api.app:app --reload")
    print("Then access the API at http://localhost:8000/docs")

if __name__ == "__main__":
    main() 