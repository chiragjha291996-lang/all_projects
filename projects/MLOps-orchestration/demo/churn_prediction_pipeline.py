"""
Sample churn prediction pipeline for testing the Conversational MLOps Agent.
This pipeline demonstrates a complete ML workflow with Prefect and MLflow integration.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import mlflow
import mlflow.sklearn
from prefect import flow, task
from typing import Tuple, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task
def load_data() -> pd.DataFrame:
    """Load and prepare sample churn data."""
    logger.info("Loading sample churn data...")
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'customer_id': range(n_samples),
        'age': np.random.randint(18, 80, n_samples),
        'tenure': np.random.randint(0, 10, n_samples),
        'monthly_charges': np.random.uniform(20, 120, n_samples),
        'total_charges': np.random.uniform(100, 8000, n_samples),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples),
        'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples),
        'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n_samples),
        'churn': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    }
    
    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} samples with {df['churn'].sum()} churn cases")
    
    return df


@task
def preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Preprocess the data for modeling."""
    logger.info("Preprocessing data...")
    
    # Create dummy variables for categorical features
    categorical_features = ['contract_type', 'internet_service', 'payment_method']
    df_processed = pd.get_dummies(df, columns=categorical_features, drop_first=True)
    
    # Separate features and target
    feature_columns = [col for col in df_processed.columns if col not in ['customer_id', 'churn']]
    X = df_processed[feature_columns]
    y = df_processed['churn']
    
    logger.info(f"Preprocessed data shape: {X.shape}")
    
    return X, y


@task
def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Train a Random Forest classifier."""
    logger.info("Training Random Forest model...")
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    logger.info("Model training completed")
    
    return model


@task
def evaluate_model(model: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """Evaluate the trained model."""
    logger.info("Evaluating model...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    metrics = {
        'accuracy': accuracy,
        'auc_score': auc_score,
        'precision': classification_report(y_test, y_pred, output_dict=True)['1']['precision'],
        'recall': classification_report(y_test, y_pred, output_dict=True)['1']['recall'],
        'f1_score': classification_report(y_test, y_pred, output_dict=True)['1']['f1-score']
    }
    
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info(f"Model AUC: {auc_score:.4f}")
    
    return metrics


@task
def log_to_mlflow(model: RandomForestClassifier, metrics: Dict[str, float], X_test: pd.DataFrame, y_test: pd.Series):
    """Log model and metrics to MLflow."""
    logger.info("Logging to MLflow...")
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        })
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "churn_model",
            registered_model_name="churn_prediction_model"
        )
        
        logger.info("Successfully logged to MLflow")


@flow(name="churn_prediction_pipeline")
def churn_prediction_pipeline():
    """Main pipeline for churn prediction."""
    logger.info("Starting churn prediction pipeline...")
    
    # Load data
    df = load_data()
    
    # Preprocess data
    X, y = preprocess_data(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Log to MLflow
    log_to_mlflow(model, metrics, X_test, y_test)
    
    logger.info("Churn prediction pipeline completed successfully!")
    
    return {
        'model': model,
        'metrics': metrics,
        'test_size': len(X_test)
    }


if __name__ == "__main__":
    # Run the pipeline
    result = churn_prediction_pipeline()
    print(f"Pipeline completed with accuracy: {result['metrics']['accuracy']:.4f}")


