import os
import pickle
import json
import pandas as pd
from fraud_model_interface import FraudDetectionInterface

def display_model_accuracies():
    """Display accuracy metrics for all available models"""
    model_dir = 'models'
    if not os.path.exists(model_dir):
        print("Models directory not found. Please run fraud_detection_model.py first.")
        return
    
    print("\n=== MODEL ACCURACY METRICS ===")
    print("-" * 50)
    print(f"{'MODEL NAME':<25} {'ACCURACY':<10} {'ROC AUC':<10}")
    print("-" * 50)
    
    for model_file in os.listdir(model_dir):
        if model_file.endswith('.pkl'):
            model_name = model_file.replace('.pkl', '')
            model_path = os.path.join(model_dir, model_file)
            
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    accuracy = model_data.get('accuracy', 'N/A')
                    auc = model_data.get('auc', 'N/A')
                    
                    if isinstance(accuracy, float):
                        accuracy = f"{accuracy:.4f}"
                    if isinstance(auc, float):
                        auc = f"{auc:.4f}"
                        
                    print(f"{model_name:<25} {accuracy:<10} {auc:<10}")
            except Exception as e:
                print(f"{model_name:<25} Error loading model: {e}")
    
    print("-" * 50)

def get_model_features(model_name):
    """Get and display required features for a specific model"""
    interface = FraudDetectionInterface()
    
    if not interface.models:
        print("No models loaded. Please run fraud_detection_model.py first.")
        return None
    
    if model_name not in interface.models:
        print(f"Model '{model_name}' not found.")
        print("Available models:")
        for name in interface.get_available_models():
            print(f"- {name}")
        return None
    
    features = interface.get_required_features(model_name)
    print(f"\nRequired features for {model_name}:")
    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature}")
    
    return features

def test_with_custom_input():
    """Test a model with custom input from the user"""
    interface = FraudDetectionInterface()
    
    if not interface.models:
        print("No models loaded. Please run fraud_detection_model.py first.")
        return
    
    # Show available models
    print("\nAvailable models:")
    for i, model_name in enumerate(interface.get_available_models(), 1):
        print(f"{i}. {model_name}")
    
    # Select model
    while True:
        try:
            model_idx = int(input("\nEnter the number of the model you want to test: ")) - 1
            models = interface.get_available_models()
            if 0 <= model_idx < len(models):
                selected_model = models[model_idx]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get required features
    features = get_model_features(selected_model)
    if not features:
        return
    
    # Collect feature values
    input_data = {}
    print("\nEnter values for each feature (press Enter to use default value):")
    
    # Show example values for guidance
    example_values = {
        'type': 1,  # Transaction type (encoded)
        'amount': 10000.0,  # Transaction amount
        'oldbalanceOrg': 15000.0,  # Original account balance before transaction
        'newbalanceOrig': 5000.0,  # New account balance after transaction
        'oldbalanceDest': 0.0,  # Destination account balance before transaction
        'newbalanceDest': 10000.0,  # Destination account balance after transaction
        'balanceDiff': 10000.0,  # Difference in originator account balance
        'destBalanceDiff': 10000.0,  # Difference in destination account balance
        'category': 2,  # Transaction category (encoded)
        'amt': 5000.0,  # Alternative name for amount
        'city_pop': 1000000,  # City population (credit card fraud dataset)
    }
    
    for feature in features:
        default_value = example_values.get(feature, 0)
        
        while True:
            try:
                value_input = input(f"{feature} (default={default_value}): ")
                
                if value_input.strip() == "":
                    input_data[feature] = default_value
                    break
                
                # Try to convert to the appropriate type
                if feature in ['type', 'category']:
                    input_data[feature] = int(value_input)
                elif feature in ['city_pop']:
                    input_data[feature] = int(value_input)
                else:
                    input_data[feature] = float(value_input)
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Make prediction
    result = interface.predict(selected_model, input_data)
    
    # Display result
    print("\n=== PREDICTION RESULT ===")
    print(f"Model: {result.get('model_name')}")
    print(f"Fraud Probability: {result.get('fraud_probability', 'N/A'):.4f}")
    print(f"Is Fraud: {result.get('is_fraud', 'N/A')}")
    print(f"Risk Level: {result.get('risk_level', 'N/A')}")
    
    # Save the input and result for reference
    save_test_result(input_data, result)

def save_test_result(input_data, result):
    """Save the test data and result to a file for reference"""
    save_dir = 'test_results'
    os.makedirs(save_dir, exist_ok=True)
    
    test_data = {
        'input': input_data,
        'result': result
    }
    
    # Generate a timestamp-based filename
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_dir, f"test_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\nTest data and results saved to {filename}")

def main():
    print("=== FRAUD DETECTION MODEL TESTING ===")
    
    while True:
        print("\nOptions:")
        print("1. Display model accuracies")
        print("2. Test with custom input")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            display_model_accuracies()
        elif choice == '2':
            test_with_custom_input()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 