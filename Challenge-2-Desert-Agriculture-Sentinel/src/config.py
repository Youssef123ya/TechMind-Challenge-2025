#!/usr/bin/env python3
"""
Configuration management for Desert Agriculture Sentinel
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional

class Config:
    """Configuration management class"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config_path = config_path
        self.config_data = {}
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.load_config()

        # Set default values if config file doesn't exist
        if not self.config_data:
            self._set_defaults()

    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file {self.config_path} not found. Using defaults.")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config_data = {}

    def _set_defaults(self):
        """Set default configuration values"""
        self.config_data = {
            'satellite': {
                'sentinel2': {
                    'api_url': 'https://scihub.copernicus.eu/dhus',
                    'username': '',
                    'password': '',
                    'download_dir': 'data/sentinel2'
                },
                'landsat': {
                    'api_url': 'https://earthexplorer.usgs.gov',
                    'username': '',
                    'password': '',
                    'download_dir': 'data/landsat'
                }
            },
            'processing': {
                'cloud_threshold': 20,  # Maximum cloud coverage percentage
                'ndvi_threshold': {
                    'bare_soil': 0.1,
                    'sparse_vegetation': 0.3,
                    'moderate_vegetation': 0.6,
                    'dense_vegetation': 0.8
                },
                'output_resolution': 10,  # meters
                'temporal_compositing_days': 16
            },
            'machine_learning': {
                'models_dir': 'models',
                'random_forest': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5
                },
                'svm': {
                    'kernel': 'rbf',
                    'C': 1.0,
                    'gamma': 'scale'
                },
                'cnn': {
                    'input_size': [64, 64, 6],
                    'batch_size': 32,
                    'epochs': 50,
                    'learning_rate': 0.001
                }
            },
            'water_optimization': {
                'efficiency_targets': {
                    'baseline_efficiency': 0.7,
                    'target_efficiency': 0.9,
                    'water_stress_threshold': 0.3,
                    'optimal_soil_moisture': 0.6
                },
                'irrigation_methods': {
                    'flood': 0.45,
                    'sprinkler': 0.75,
                    'drip': 0.90,
                    'micro_sprinkler': 0.85,
                    'subsurface_drip': 0.95
                }
            },
            'alerts': {
                'soil_moisture_threshold': 0.3,
                'unhealthy_crop_threshold': 20,  # percentage
                'notification_email': '',
                'sms_number': ''
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'logs/desert_agriculture_sentinel.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/sentinel.db',
                'backup_interval_days': 7
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            keys = key.split('.')
            value = self.config_data
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config_data

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check required directories
        required_dirs = [
            self.get('satellite.sentinel2.download_dir'),
            self.get('satellite.landsat.download_dir'),
            self.get('machine_learning.models_dir'),
            os.path.dirname(self.get('logging.log_file'))
        ]

        for directory in required_dirs:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    validation_results['warnings'].append(f"Created directory: {directory}")
                except Exception as e:
                    validation_results['errors'].append(f"Cannot create directory {directory}: {str(e)}")
                    validation_results['valid'] = False

        # Validate thresholds
        cloud_threshold = self.get('processing.cloud_threshold')
        if not isinstance(cloud_threshold, (int, float)) or not (0 <= cloud_threshold <= 100):
            validation_results['errors'].append("processing.cloud_threshold must be a number between 0 and 100")
            validation_results['valid'] = False

        # Validate NDVI thresholds
        ndvi_thresholds = self.get('processing.ndvi_threshold')
        if ndvi_thresholds:
            for key, value in ndvi_thresholds.items():
                if not isinstance(value, (int, float)) or not (-1 <= value <= 1):
                    validation_results['errors'].append(f"NDVI threshold {key} must be between -1 and 1")
                    validation_results['valid'] = False

        return validation_results
