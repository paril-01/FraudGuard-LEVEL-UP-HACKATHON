import os
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

class FraudDetectionInterface:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = {}
        self.load_models()
    
    def load_models(self):
        """Load all available saved models"""
        model_dir = 'models'
        if not os.path.exists(model_dir):
            print("Models directory not found. Please run fraud_detection_model.py first.")
            return False
        
        for model_file in os.listdir(model_dir):
            if model_file.endswith('.pkl'):
                model_name = model_file.replace('.pkl', '')
                model_path = os.path.join(model_dir, model_file)
                try:
                    with open(model_path, 'rb') as f:
                        model_data = pickle.load(f)
                        self.models[model_name] = model_data['model']
                        self.scalers[model_name] = model_data['scaler']
                        self.feature_names[model_name] = model_data['feature_names']
                    print(f"Loaded model: {model_name}")
                except Exception as e:
                    print(f"Error loading model {model_name}: {e}")
        
        return len(self.models) > 0
    
    def get_available_models(self):
        """Return list of available models"""
        return list(self.models.keys())
    
    def get_required_features(self, model_name):
        """Return the features required for the specified model"""
        if model_name in self.feature_names:
            return self.feature_names[model_name]
        return None
    
    def predict(self, model_name, input_data):
        """Make a prediction using the specified model
        
        Args:
            model_name (str): The name of the model to use
            input_data (dict): Dictionary containing feature values
            
        Returns:
            dict: Prediction results including probability and classification
        """
        if model_name not in self.models:
            return {"error": f"Model '{model_name}' not found"}
        
        # Check if all required features are provided
        required_features = self.feature_names[model_name]
        missing_features = [f for f in required_features if f not in input_data]
        
        if missing_features:
            return {"error": f"Missing required features: {', '.join(missing_features)}"}
        
        # Convert input data to DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Select only the columns needed for this model
        input_df = input_df[required_features]
        
        # Scale the input data
        scaled_input = self.scalers[model_name].transform(input_df)
        
        # Make prediction
        fraud_probability = self.models[model_name].predict_proba(scaled_input)[0, 1]
        fraud_prediction = fraud_probability > 0.5
        
        return {
            "model_name": model_name,
            "fraud_probability": float(fraud_probability),
            "is_fraud": bool(fraud_prediction),
            "risk_level": self._get_risk_level(fraud_probability)
        }
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability < 0.2:
            return "Low"
        elif probability < 0.5:
            return "Medium"
        elif probability < 0.8:
            return "High"
        else:
            return "Very High"


def main():
    # Update fraud_detection_model.py to save models
    if not os.path.exists('models'):
        print("Models directory not found. Please run the updated fraud_detection_model.py first.")
        print("You need to modify fraud_detection_model.py to save models using pickle/joblib.")
        return
    
    # Example usage
    interface = FraudDetectionInterface()
    
    if not interface.models:
        print("No models loaded. Please train and save models first.")
        return
    
    print("\nAvailable models:")
    for model_name in interface.get_available_models():
        print(f"- {model_name}")
    
    # Example of how to use the interface
    print("\nExample prediction (if online-payment-fraud model is available):")
    if 'online-payment-fraud' in interface.models:
        # Get required features
        required_features = interface.get_required_features('online-payment-fraud')
        print(f"Required features: {required_features}")
        
        # Example input data (this will need to be adjusted based on actual model features)
        example_input = {
            'type': 1,  # Encoded transaction type
            'amount': 10000.0,
            'oldbalanceOrg': 10000.0,
            'newbalanceOrig': 0.0,
            'oldbalanceDest': 0.0,
            'newbalanceDest': 10000.0,
            'balanceDiff': 10000.0,
            'destBalanceDiff': 10000.0
        }
        
        # Make prediction
        result = interface.predict('online-payment-fraud', example_input)
        print("\nPrediction result:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("Example model 'online-payment-fraud' not available")


if __name__ == "__main__":
    main() 