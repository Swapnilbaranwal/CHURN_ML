"""
Customer Churn Prediction API
A Flask-based web service for predicting customer churn using machine learning models.
"""

import os
import logging
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
from flask import Flask, request, jsonify


class ChurnPredictor:
    """Handles customer churn prediction logic."""
    
    def __init__(self, model_file: str, transformer_file: str):
        """Initialize the predictor with model and transformer paths."""
        self.model = self._load_model(model_file)
        self.transformer = self._load_transformer(transformer_file)
        self.threshold = 0.5
        
    def _load_model(self, file_path: str):
        """Load the trained machine learning model."""
        try:
            return joblib.load(file_path)
        except Exception as exc:
            logging.error(f"Failed to load model from {file_path}: {exc}")
            raise
            
    def _load_transformer(self, file_path: str):
        """Load the data transformer/preprocessor."""
        try:
            return joblib.load(file_path)
        except Exception as exc:
            logging.error(f"Failed to load transformer from {file_path}: {exc}")
            raise
    
    def to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Convert customer data to DataFrame format."""
        return pd.DataFrame([data])
    
    def get_churn_probability(self, df: pd.DataFrame) -> float:
        """Calculate the probability of customer churn."""
        features = self.transformer.transform(df)
        prob = self.model.predict_proba(features)[0][1]
        return prob
    
    def get_churn_label(self, prob: float) -> str:
        """Make binary churn prediction based on probability threshold."""
        return "Yes" if prob >= self.threshold else "No"
    
    def predict(self, data: Dict[str, Any]) -> Tuple[float, str]:
        """Complete churn prediction pipeline."""
        df = self.to_dataframe(data)
        prob = self.get_churn_probability(df)
        label = self.get_churn_label(prob)
        return prob, label


class ChurnAPI:
    """Flask API wrapper for churn prediction service."""
    
    def __init__(self):
        """Initialize the Flask application and churn predictor."""
        self.app = Flask(__name__)
        self.predictor = ChurnPredictor("app/model.pkl", "app/transformer.pkl")
        self._add_routes()
        self._init_logging()
    
    def _init_logging(self):
        """Configure application logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _add_routes(self):
        """Configure API routes."""
        self.app.add_url_rule('/predict', 'predict', self._predict_endpoint, methods=['POST'])
    
    def _predict_endpoint(self):
        """Handle churn prediction API requests."""
        try:
            req_json = request.get_json()
            
            if not req_json or 'customer' not in req_json:
                return jsonify({"error": "Missing 'customer' data in request"}), 400
            
            customer = req_json['customer']
            prob, label = self.predictor.predict(customer)
            
            resp = {
                "churn_probability": round(prob, 2),
                "churn_prediction": label
            }
            
            logging.info(f"Prediction made: {resp}")
            return jsonify(resp)
            
        except KeyError as exc:
            msg = f"Missing required field: {str(exc)}"
            logging.error(msg)
            return jsonify({"error": msg}), 400
        except Exception as exc:
            msg = f"Prediction failed: {str(exc)}"
            logging.error(msg)
            return jsonify({"error": msg}), 500
    
    def run(self, host: str = 'localhost', port: int = 8000):
        """Start the Flask development server."""
        logging.info(f"Starting churn prediction API on {host}:{port}")
        self.app.run(host=host, port=port)


def create_app():
    """Factory function to create and configure the Flask application."""
    api = ChurnAPI()
    return api.app


def main():
    """Main application entry point."""
    try:
        api = ChurnAPI()
        api.run()
    except Exception as exc:
        logging.error(f"Failed to start application: {exc}")
        raise


if __name__ == "__main__":
    main()
