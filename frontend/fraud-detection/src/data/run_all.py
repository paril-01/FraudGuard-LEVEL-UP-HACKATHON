#!/usr/bin/env python
"""
Run all steps of the Ethereum fraud detection extension in sequence.
This script executes setup, data processing, model training, and verification.
"""

import os
import sys
import time
import importlib.util
import json

def import_module_from_file(module_name, file_path):
    """Import a module from file path dynamically."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def print_step(step_number, total_steps, message):
    """Print a formatted step message."""
    print(f"\n[{step_number}/{total_steps}] {message}")
    print("=" * 80)

def run_all():
    """Run all steps of the Ethereum fraud detection extension."""
    total_steps = 4
    start_time = time.time()
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Run setup
    print_step(1, total_steps, "Installing dependencies and checking environment")
    setup_path = os.path.join(current_dir, "setup.py")
    setup_module = import_module_from_file("setup", setup_path)
    setup_module.setup()
    
    # Step 2: Process the Ethereum dataset
    print_step(2, total_steps, "Processing Ethereum transaction dataset")
    processor_path = os.path.join(current_dir, "ethereum_processor.py")
    processor_module = import_module_from_file("ethereum_processor", processor_path)
    processor_module.main()
    
    # Step 3: Train the fraud detection model extension
    print_step(3, total_steps, "Training the fraud detection model extension")
    model_path = os.path.join(current_dir, "fraud_model_extension.py")
    model_module = import_module_from_file("fraud_model_extension", model_path)
    model_module.main()
    
    # Step 4: Verify the results
    print_step(4, total_steps, "Verifying the results")
    
    # Check for the existence of key files
    frontend_data_path = os.path.join(current_dir, "ethereum_frontend.json")
    if os.path.exists(frontend_data_path):
        try:
            with open(frontend_data_path, 'r') as f:
                data = json.load(f)
                num_transactions = len(data)
                print(f"✓ Frontend data created successfully with {num_transactions} transactions")
        except Exception as e:
            print(f"✗ Error reading frontend data: {str(e)}")
    else:
        print("✗ Frontend data file not found")
    
    model_output_dir = os.path.join(current_dir, "models")
    if os.path.exists(model_output_dir):
        model_files = os.listdir(model_output_dir)
        if model_files:
            print(f"✓ Model files created: {', '.join(model_files)}")
        else:
            print("✗ No model files found in the models directory")
    else:
        print("✗ Models directory not found")
    
    # Print completion message and time taken
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"Ethereum fraud detection extension setup completed in {elapsed_time:.2f} seconds")
    print("You can now start the application and view Ethereum transactions in the Blockchain Hub")
    print("=" * 80)

if __name__ == "__main__":
    run_all() 