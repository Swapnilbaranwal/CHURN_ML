"""
Customer Churn Prediction Package
Contains modules for predicting customer churn using machine learning models.
"""

from .main import ChurnPredictor, ChurnAPI, create_app, main

__version__ = "2.0.0"
__author__ = "Mihir Suhanda"

# Export main classes and functions
__all__ = [
    "ChurnPredictor",
    "ChurnAPI", 
    "create_app",
    "main"
]
