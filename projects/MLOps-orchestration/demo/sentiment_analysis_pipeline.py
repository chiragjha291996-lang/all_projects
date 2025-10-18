"""
Sample sentiment analysis pipeline for testing the Conversational MLOps Agent.
This pipeline demonstrates text processing and NLP model training.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import mlflow
import mlflow.sklearn
from prefect import flow, task
from typing import Tuple, Dict, Any
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task
def load_sentiment_data() -> pd.DataFrame:
    """Load and prepare sample sentiment data."""
    logger.info("Loading sample sentiment data...")
    
    # Generate sample text data
    np.random.seed(42)
    n_samples = 500
    
    positive_texts = [
        "I love this product! It's amazing and works perfectly.",
        "Great service, highly recommend to everyone.",
        "Excellent quality and fast delivery.",
        "Outstanding customer support, very helpful.",
        "Perfect! Exactly what I was looking for.",
        "Fantastic experience, will buy again.",
        "Superb quality, exceeded my expectations.",
        "Wonderful product, very satisfied.",
        "Brilliant design and functionality.",
        "Outstanding value for money."
    ]
    
    negative_texts = [
        "Terrible product, waste of money.",
        "Poor quality, broke after one use.",
        "Awful customer service, very disappointed.",
        "Horrible experience, would not recommend.",
        "Bad quality, not worth the price.",
        "Disappointing product, doesn't work.",
        "Worst purchase ever, regret buying.",
        "Poor design, very frustrating to use.",
        "Terrible delivery, arrived damaged.",
        "Bad experience, will not buy again."
    ]
    
    # Create balanced dataset
    texts = []
    labels = []
    
    for _ in range(n_samples // 2):
        texts.append(np.random.choice(positive_texts))
        labels.append(1)
        
        texts.append(np.random.choice(negative_texts))
        labels.append(0)
    
    df = pd.DataFrame({
        'text': texts,
        'sentiment': labels
    })
    
    logger.info(f"Loaded {len(df)} samples with {df['sentiment'].sum()} positive cases")
    
    return df


@task
def preprocess_text(texts: pd.Series) -> pd.Series:
    """Preprocess text data."""
    logger.info("Preprocessing text data...")
    
    def clean_text(text):
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    processed_texts = texts.apply(clean_text)
    logger.info("Text preprocessing completed")
    
    return processed_texts


@task
def vectorize_text(X_train: pd.Series, X_test: pd.Series) -> Tuple[np.ndarray, np.ndarray, TfidfVectorizer]:
    """Vectorize text using TF-IDF."""
    logger.info("Vectorizing text data...")
    
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    logger.info(f"Vectorized data shape: {X_train_vec.shape}")
    
    return X_train_vec, X_test_vec, vectorizer


@task
def train_sentiment_model(X_train: np.ndarray, y_train: pd.Series) -> LogisticRegression:
    """Train a Logistic Regression model for sentiment analysis."""
    logger.info("Training sentiment analysis model...")
    
    model = LogisticRegression(
        random_state=42,
        max_iter=1000
    )
    
    model.fit(X_train, y_train)
    logger.info("Model training completed")
    
    return model


@task
def evaluate_sentiment_model(model: LogisticRegression, X_test: np.ndarray, y_test: pd.Series) -> Dict[str, float]:
    """Evaluate the trained sentiment model."""
    logger.info("Evaluating sentiment model...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Get classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    
    metrics = {
        'accuracy': accuracy,
        'precision': report['1']['precision'],
        'recall': report['1']['recall'],
        'f1_score': report['1']['f1-score'],
        'support': report['1']['support']
    }
    
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info(f"Model precision: {metrics['precision']:.4f}")
    logger.info(f"Model recall: {metrics['recall']:.4f}")
    
    return metrics


@task
def log_sentiment_to_mlflow(model: LogisticRegression, vectorizer: TfidfVectorizer, metrics: Dict[str, float]):
    """Log sentiment model and metrics to MLflow."""
    logger.info("Logging sentiment model to MLflow...")
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            'max_features': 1000,
            'ngram_range': '(1, 2)',
            'random_state': 42,
            'max_iter': 1000
        })
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "sentiment_model",
            registered_model_name="sentiment_analysis_model"
        )
        
        # Log vectorizer
        mlflow.sklearn.log_model(
            vectorizer,
            "text_vectorizer",
            registered_model_name="text_vectorizer"
        )
        
        logger.info("Successfully logged sentiment model to MLflow")


@flow(name="sentiment_analysis_pipeline")
def sentiment_analysis_pipeline():
    """Main pipeline for sentiment analysis."""
    logger.info("Starting sentiment analysis pipeline...")
    
    # Load data
    df = load_sentiment_data()
    
    # Preprocess text
    df['text_processed'] = preprocess_text(df['text'])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text_processed'], df['sentiment'], 
        test_size=0.2, random_state=42, stratify=df['sentiment']
    )
    
    # Vectorize text
    X_train_vec, X_test_vec, vectorizer = vectorize_text(X_train, X_test)
    
    # Train model
    model = train_sentiment_model(X_train_vec, y_train)
    
    # Evaluate model
    metrics = evaluate_sentiment_model(model, X_test_vec, y_test)
    
    # Log to MLflow
    log_sentiment_to_mlflow(model, vectorizer, metrics)
    
    logger.info("Sentiment analysis pipeline completed successfully!")
    
    return {
        'model': model,
        'vectorizer': vectorizer,
        'metrics': metrics,
        'test_size': len(X_test)
    }


if __name__ == "__main__":
    # Run the pipeline
    result = sentiment_analysis_pipeline()
    print(f"Pipeline completed with accuracy: {result['metrics']['accuracy']:.4f}")


