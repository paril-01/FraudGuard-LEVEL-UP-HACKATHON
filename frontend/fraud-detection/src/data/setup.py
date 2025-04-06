#!/usr/bin/env python
"""
Setup script for installing all required dependencies and downloading the dataset
for the Ethereum transaction fraud detection model
"""

import os
import sys
import subprocess
import platform

# Required packages for data processing and model training
REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "tensorflow",
    "kagglehub",
    "joblib"
]

def check_python_version():
    """Check if Python version is sufficient"""
    required_version = (3, 7)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing required packages...")
    
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Error installing {package}")
            return False
    
    print("All packages installed successfully!")
    return True

def create_directories():
    """Create necessary directories for data and models"""
    dirs = [
        "frontend/fraud-detection/src/data",
        "frontend/fraud-detection/src/models"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")
    
    return True

def download_dataset():
    """Download the Ethereum transactions dataset"""
    print("Downloading Ethereum transactions dataset...")
    
    try:
        import kagglehub
        path = kagglehub.dataset_download("chaitya0623/ethereum-transactions-for-fraud-detection")
        print(f"Dataset downloaded to: {path}")
        return True
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("You can manually download the dataset from:")
        print("https://www.kaggle.com/datasets/chaitya0623/ethereum-transactions-for-fraud-detection")
        return False

def process_dataset():
    """Process the dataset and train the model"""
    print("Processing Ethereum transaction data...")
    
    try:
        # Run the ethereum_processor.py script
        subprocess.check_call([
            sys.executable, 
            "frontend/fraud-detection/src/data/ethereum_processor.py"
        ])
        
        print("Dataset processed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing dataset: {e}")
        return False

def train_model():
    """Train the fraud detection model"""
    print("Training fraud detection model...")
    
    try:
        # Run the fraud_model_extension.py script
        subprocess.check_call([
            sys.executable, 
            "frontend/fraud-detection/src/data/fraud_model_extension.py"
        ])
        
        print("Model trained successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error training model: {e}")
        return False

def setup():
    """Run the full setup process"""
    print("Starting setup for Ethereum fraud detection model...")
    
    if not check_python_version():
        return False
    
    if not create_directories():
        return False
    
    if not install_dependencies():
        return False
    
    if not download_dataset():
        print("Continuing setup without dataset download...")
    
    if not process_dataset():
        print("Continuing setup without dataset processing...")
    
    if not train_model():
        print("Continuing setup without model training...")
    
    print("\nSetup completed!")
    print("\nTo run the Ethereum fraud detection model:")
    print("1. Process data: python frontend/fraud-detection/src/data/ethereum_processor.py")
    print("2. Train model: python frontend/fraud-detection/src/data/fraud_model_extension.py")
    
    return True

if __name__ == "__main__":
    setup() 