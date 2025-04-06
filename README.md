AI-Driven Fraud Detection System

An ML/AI-based system for detecting fraudulent financial transactions in banking and e-commerce.

Overview

This project implements machine learning and AI-driven risk analysis to identify:
- Fraudulent financial transactions
- Unauthorized account access
- Suspicious user behaviors

The system uses multiple ML models including Logistic Regression, XGBoost, LightGBM, and Neural Networks to detect fraud patterns and provide risk assessments.

Project Structure

```
.
├── data/                   # Stores the datasets
├── src/                    # Source code
│   ├── api/                # FastAPI application with Firebase integration
│   ├── data/               # Data download and preparation
│   ├── models/             # Model training and evaluation
│   ├── preprocessing/      # Data preprocessing
│   └── visualization/      # Visualization utilities
├── firebase-credentials.json # Firebase credentials (add your own)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

Getting Started

Prerequisites

- Python 3.8+
- Pip package manager
- Firebase account (for user authentication and data storage)

Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fraud-detection-system
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Firebase:
   - Create a Firebase project at https://console.firebase.google.com/
   - Generate a service account key from Project Settings > Service Accounts
   - Save the JSON key file as `firebase-credentials.json` in the project root

4. Download the datasets:
   ```
   python src/data/download_data.py
   ```

Running the Pipeline

1. Preprocess the data:
   ```
   python src/preprocessing/preprocess.py
   ```

2. Train and evaluate models:
   ```
   python src/models/train_model.py
   ```

3. Run the API server:
   ```
   cd src/api
   uvicorn app:app --reload
   ```

4. Access the API documentation at: http://localhost:8000/docs
5. Access the UI at: http://localhost:8000/static/index.html

Datasets

The system uses multiple fraud detection datasets:

1. Online Payment Fraud Detection (Kaggle): Transaction data with labeled fraud indicators
2. Credit Card Fraud Detection (Kaggle): Credit card fraud patterns
3. 2023 Credit Card Fraud Detection (Kaggle): Recent fraud patterns and behaviors

The datasets are preprocessed and normalized to create a unified schema for model training.

Models

The system trains and compares multiple models:

1. Logistic Regression: A simple baseline model
2. XGBoost: Gradient boosting for handling imbalanced fraud data
3. LightGBM: Light Gradient Boosting Machine, optimized for performance
4. Neural Network: A deep learning approach with dropout and batch normalization

The best performing model is selected based on AUC-ROC score.

API Usage

The API provides several endpoints:

- `/register`: Register a new user
- `/token`: Login and get access token
- `/predict`: Submit a transaction for fraud analysis
- `/transactions`: Get transaction history for the current user

Authentication is required for all endpoints except registration and login.

Example prediction request:
```json
{
  "transaction_type": "TRANSFER",
  "amount": 181.0,
  "oldbalanceOrg": 181.0,
  "newbalanceOrig": 0.0,
  "oldbalanceDest": 0.0,
  "newbalanceDest": 181.0,
  "step": 1
}
```

Firebase Integration

The system uses Firebase for:

1. User Authentication: Secure login and registration
2. Transaction Storage: Save transaction details and predictions
3. History Tracking: View past transaction analyses

To enable Firebase:
1. Create a Firebase project
2. Enable Authentication with Email/Password
3. Create a Firestore database
4. Generate a service account key
5. Save the key as `firebase-credentials.json` in the project root

Performance Metrics

The models are evaluated based on:
- Precision (avoiding false positives)
- Recall (catching all frauds)
- F1-Score
- AUC-ROC (critical for imbalanced datasets)
- Confusion Matrix 