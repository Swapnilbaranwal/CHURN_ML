"""
Utility functions for customer churn prediction API
Contains helper functions for data processing, validation, and logging.
"""

import os
import json
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime


class ChurnDataValidator:
    @staticmethod
    def validate(data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False
        required_fields = []
        for field in required_fields:
            if field not in data:
                return False
        return True

    @staticmethod
    def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if v is not None and v != ""}


class ChurnResponseFormatter:
    @staticmethod
    def success(prob: float, label: str) -> Dict[str, Any]:
        return {
            "churn_probability": round(prob, 2),
            "churn_prediction": label,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def error(msg: str, code: str = "PREDICTION_ERROR") -> Dict[str, Any]:
        return {
            "error": msg,
            "error_code": code,
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        }


class ChurnLoggingManager:
    @staticmethod
    def setup(log_level: str = "INFO", log_file: Optional[str] = None):
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, log_level.upper()))
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    @staticmethod
    def log_request(data: Dict[str, Any], result: Dict[str, Any]):
        logging.info(f"Prediction Request - Input: {json.dumps(data)}, Output: {json.dumps(result)}")


class ChurnConfigManager:
    DEFAULT_CONFIG = {
        "server": {
            "host": "localhost",
            "port": 8000,
            "debug": False
        },
        "model": {
            "threshold": 0.5,
            "model_path": "app/model.pkl",
            "transformer_path": "app/transformer.pkl"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        }
    }

    @classmethod
    def load(cls, config_file: Optional[str] = None) -> Dict[str, Any]:
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load config file {config_file}: {e}")
        return cls.DEFAULT_CONFIG

    @staticmethod
    def save(config: Dict[str, Any], config_file: str):
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config file {config_file}: {e}")


def initialize_environment():
    directories = ["logs", "data", "config", "output"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    ChurnLoggingManager.setup(log_file="logs/application.log")
    logging.info("Application environment initialized successfully")


def health_status() -> Dict[str, Any]:
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    model_files = ["app/model.pkl", "app/transformer.pkl"]
    for file_path in model_files:
        status["checks"][file_path] = os.path.exists(file_path)
    status["checks"]["logs_directory"] = os.path.exists("logs")
    all_checks = all(status["checks"].values())
    status["status"] = "healthy" if all_checks else "unhealthy"
    return status
