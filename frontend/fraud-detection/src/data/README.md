# Ethereum Fraud Detection Model Extension

This directory contains code to extend the existing fraud detection model to also identify fraudulent Ethereum cryptocurrency transactions.

## Overview

The Ethereum Fraud Detection extension allows the existing ML model to:

1. Analyze Ethereum blockchain transactions
2. Identify potentially fraudulent activity
3. Calculate risk scores for each transaction
4. Display transaction details in the Blockchain Hub UI

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Access to download Kaggle datasets

### Installation

Run the setup script to install all required dependencies and download the dataset:

```bash
python frontend/fraud-detection/src/data/setup.py
```

This will:
- Install required Python packages
- Download the Ethereum transactions dataset from Kaggle
- Process the dataset
- Train and extend the fraud detection model

### Manual Setup

If you prefer to run each step manually:

1. Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn tensorflow kagglehub joblib
```

2. Download the dataset:
```bash
python -c "import kagglehub; kagglehub.dataset_download('chaitya0623/ethereum-transactions-for-fraud-detection')"
```

3. Process the dataset:
```bash
python frontend/fraud-detection/src/data/ethereum_processor.py
```

4. Train the extended model:
```bash
python frontend/fraud-detection/src/data/fraud_model_extension.py
```

## Dataset Information

The Ethereum transactions dataset contains real Ethereum blockchain transactions with features important for fraud detection:

- Transaction hash
- Sender/receiver addresses
- Transaction amount
- Gas price and limits
- Timestamp
- Block information
- Additional features derived from on-chain behavior

## Model Architecture

The extension builds on the existing fraud detection model by:

1. **Adding Ethereum-specific features**: These include wallet reputation, transaction patterns, gas usage, and temporal behaviors.

2. **Transfer learning**: The extended model leverages knowledge from the existing fraud detection model while adding Ethereum-specific patterns.

3. **Feature engineering**: The preprocessor creates additional features like:
   - Address reputation scores
   - Amount anomaly detection
   - Temporal pattern analysis
   - Gas price irregularities

4. **Risk scoring**: Each transaction receives a risk score (0-100) based on:
   - Transaction characteristics
   - Historical patterns
   - Address reputation
   - Amount irregularities
   - Network behavior

## Files and Structure

- **ethereum_processor.py**: Preprocesses the raw Ethereum transaction data
- **fraud_model_extension.py**: Extends the existing model to handle Ethereum transactions
- **setup.py**: Installs dependencies and sets up the environment
- **ethereum_features.json**: Defines feature mapping for the model
- **ethereum_schema.json**: Maps Ethereum transaction fields to frontend display fields
- **ethereum_frontend.json**: Contains processed transactions for UI display

## UI Integration

The model integrates with the Blockchain Hub UI, which displays:

- Transaction details (hash, sender, receiver, amount)
- Transaction status (success/blocked)
- Risk score with color indicators
- Fraud indicators when applicable
- Blockchain statistics

## Troubleshooting

If you encounter issues:

1. **Dataset download fails**: You can manually download from https://www.kaggle.com/datasets/chaitya0623/ethereum-transactions-for-fraud-detection and place it in the `frontend/fraud-detection/src/data` directory.

2. **Model training errors**: Ensure TensorFlow is properly installed and compatible with your system.

3. **UI display issues**: Check browser console for errors. The system will fall back to mock data if the model data isn't available.

## Contact

For questions or issues, please contact the development team. 