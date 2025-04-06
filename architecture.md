# Fraud Detection System Architecture

## System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                           FRAUD DETECTION SYSTEM                              │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                                 DATA PIPELINE                                  │
├───────────────┬───────────────┬───────────────┬──────────────┬────────────────┤
│  Transaction  │               │ Preprocessing │  Feature     │                │
│  Data Source  ├──────►  ETL   ├──────►        ├──────►       ├───────►  Split │
│  (CSV/API)    │               │ (Clean/Fill)  │  Engineering │                │
└───────────────┴───────────────┴───────────────┴──────────────┴────────────────┘
                                                                        │
                                                                        ▼
┌──────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│             MODEL TRAINING               │   │           MODEL EVALUATION               │
├──────────────┬───────────────────────────┤   ├──────────────┬───────────────────────────┤
│ Baseline     │ ┌─────────────────────┐   │   │ Metrics      │ ┌─────────────────────┐   │
│ Models       │ │  Logistic Regression│   │   │ Assessment   │ │  Precision/Recall   │   │
│              │ └─────────────────────┘   │   │              │ └─────────────────────┘   │
│              │ ┌─────────────────────┐   │   │              │ ┌─────────────────────┐   │
│ Advanced     │ │  XGBoost            │   │   │ Visual       │ │  ROC Curves         │   │
│ Models       │ └─────────────────────┘   │   │ Evaluation   │ └─────────────────────┘   │
│              │ ┌─────────────────────┐   │   │              │ ┌─────────────────────┐   │
│              │ │  LightGBM           │   │   │              │ │  Confusion Matrix   │   │
│              │ └─────────────────────┘   │   │              │ └─────────────────────┘   │
│              │ ┌─────────────────────┐   │   │              │                           │
│ Deep         │ │  Neural Network     │   │   │              │                           │
│ Learning     │ └─────────────────────┘   │   │              │                           │
└──────────────┴───────────────────────────┘   └──────────────┴───────────────────────────┘
                           │                                      │
                           └──────────────────┬─────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                             DEPLOYMENT PIPELINE                                │
├───────────────┬───────────────┬───────────────┬──────────────┬────────────────┤
│  Best Model   │  Model        │  API          │  Frontend    │                │
│  Selection    ├──────►  Save  ├──────►  Layer ├──────►       ├───────►  Deploy│
│               │               │  (FastAPI)    │  (HTML/JS)   │                │
└───────────────┴───────────────┴───────────────┴──────────────┴────────────────┘
                                                                        │
                                                                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                             USER INTERACTION                                   │
├───────────────┬───────────────┬───────────────┬──────────────┬────────────────┤
│  Transaction  │  Risk         │  Fraud        │  Alert       │  Feedback      │
│  Submission   ├──────► Score  ├──────► Detect ├──────►       ├───────► Loop   │
│               │               │               │  Generation  │                │
└───────────────┴───────────────┴───────────────┴──────────────┴────────────────┘
```

## Data Flow

1. **Data Ingestion**:
   - Load transaction data from CSV file
   - Clean and preprocess data
   - Feature engineering to create fraud indicators

2. **Model Training**:
   - Train multiple models in parallel
   - Optimize hyperparameters for best performance
   - Evaluate using metrics focused on fraud detection

3. **Deployment**:
   - Save best model and preprocessor
   - Create API endpoints for prediction
   - Develop UI for transaction submission and visualization

4. **Inference Pipeline**:
   - Receive transaction data via API
   - Preprocess using same pipeline as training
   - Generate fraud prediction and risk score
   - Return results with explanatory factors

## Key Components

1. **Data Module**: Handles dataset downloading and preparation
2. **Preprocessing Module**: Implements feature engineering and data transformation
3. **Models Module**: Contains multiple fraud detection models and training logic
4. **API Module**: Provides REST endpoints for transaction analysis
5. **UI Component**: Web interface for submitting transactions and viewing results

## Technology Stack

- **Python**: Core language for ML/data processing
- **Pandas/NumPy**: Data manipulation and numerical operations
- **Scikit-learn**: ML pipeline, preprocessing, and baseline models
- **XGBoost/LightGBM**: Gradient boosting for fraud detection
- **TensorFlow**: Neural network implementation
- **FastAPI**: High-performance API framework
- **HTML/JavaScript**: Frontend UI components
- **Docker**: Containerization for deployment 