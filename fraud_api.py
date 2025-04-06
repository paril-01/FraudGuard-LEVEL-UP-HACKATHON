from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from fraud_model_interface import FraudDetectionInterface

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the fraud detection interface
fraud_interface = FraudDetectionInterface()

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get a list of available models with their required features"""
    models = fraud_interface.get_available_models()
    
    # Get details for each model including required features
    model_details = {}
    for model_name in models:
        features = fraud_interface.get_required_features(model_name)
        model_details[model_name] = {
            'features': features
        }
    
    return jsonify({
        'success': True,
        'models': model_details
    })

@app.route('/api/model_accuracies', methods=['GET'])
def get_model_accuracies():
    """Get accuracy metrics for all models"""
    model_dir = 'models'
    if not os.path.exists(model_dir):
        return jsonify({
            'success': False,
            'error': 'Models directory not found'
        })
    
    accuracies = {}
    
    for model_file in os.listdir(model_dir):
        if model_file.endswith('.pkl'):
            model_name = model_file.replace('.pkl', '')
            model_path = os.path.join(model_dir, model_file)
            
            try:
                import pickle
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    accuracies[model_name] = {
                        'accuracy': model_data.get('accuracy', 'N/A'),
                        'auc': model_data.get('auc', 'N/A')
                    }
            except Exception as e:
                accuracies[model_name] = {
                    'error': str(e)
                }
    
    return jsonify({
        'success': True,
        'accuracies': accuracies
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make a prediction using the specified model"""
    # Get the request data
    data = request.json
    
    # Check that required fields are provided
    if not data or 'model_name' not in data or 'input_data' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields: model_name, input_data'
        })
    
    model_name = data['model_name']
    input_data = data['input_data']
    
    # Make the prediction
    result = fraud_interface.predict(model_name, input_data)
    
    # Check for errors
    if 'error' in result:
        return jsonify({
            'success': False,
            'error': result['error']
        })
    
    # Save the test result
    save_dir = 'test_results'
    os.makedirs(save_dir, exist_ok=True)
    
    test_data = {
        'input': input_data,
        'result': result
    }
    
    # Generate a timestamp-based filename
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_dir, f"api_test_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    # Return the prediction result
    return jsonify({
        'success': True,
        'prediction': result
    })

@app.route('/api/example_input', methods=['GET'])
def get_example_input():
    """Get example input values for a specified model"""
    model_name = request.args.get('model_name', '')
    
    if not model_name:
        return jsonify({
            'success': False,
            'error': 'Missing required parameter: model_name'
        })
    
    # Check if the model exists
    if model_name not in fraud_interface.get_available_models():
        return jsonify({
            'success': False,
            'error': f'Model not found: {model_name}'
        })
    
    # Get the required features for this model
    features = fraud_interface.get_required_features(model_name)
    
    # Common example values
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
    
    # Create example input data specific to this model
    example_input = {}
    for feature in features:
        example_input[feature] = example_values.get(feature, 0)
    
    return jsonify({
        'success': True,
        'example_input': example_input
    })

if __name__ == '__main__':
    print("Starting Fraud Detection API...")
    
    # Check if models are loaded
    if not fraud_interface.models:
        print("Warning: No models loaded. Please run fraud_detection_model.py first.")
    else:
        print(f"Loaded {len(fraud_interface.models)} models:")
        for model_name in fraud_interface.get_available_models():
            print(f"- {model_name}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 