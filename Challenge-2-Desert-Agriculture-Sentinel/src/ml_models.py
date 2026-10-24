#!/usr/bin/env python3
"""
Machine Learning Models for Crop Health Classification
Implements Random Forest, SVM, and CNN models for desert agriculture monitoring
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

# Try to import deep learning libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Input
    from tensorflow.keras.optimizers import Adam
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False

class CropHealthClassifier:
    """Machine learning models for crop health classification"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.model_performance = {}

        # Health classification labels
        self.health_classes = ['healthy', 'water_stress', 'nutrient_deficiency', 'disease', 'pest_damage']

        # Initialize models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize machine learning models"""

        # Random Forest Model
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )

        # Support Vector Machine
        self.models['svm'] = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            random_state=42,
            probability=True
        )

        # Scaler for SVM
        self.scalers['svm'] = StandardScaler()

        # CNN Model (if TensorFlow is available)
        if DEEP_LEARNING_AVAILABLE:
            self.models['cnn'] = self._build_cnn_model()

        self.logger.info("Machine learning models initialized")

    def _build_cnn_model(self) -> Optional[Model]:
        """Build CNN model for image-based crop health classification"""
        try:
            model = Sequential([
                Input(shape=(64, 64, 6)),  # 6 spectral bands

                Conv2D(32, (3, 3), activation='relu'),
                MaxPooling2D((2, 2)),

                Conv2D(64, (3, 3), activation='relu'),
                MaxPooling2D((2, 2)),

                Conv2D(128, (3, 3), activation='relu'),
                MaxPooling2D((2, 2)),

                Flatten(),
                Dense(256, activation='relu'),
                Dropout(0.5),
                Dense(128, activation='relu'),
                Dropout(0.3),
                Dense(len(self.health_classes), activation='softmax')
            ])

            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )

            self.logger.info("CNN model built successfully")
            return model

        except Exception as e:
            self.logger.error(f"Error building CNN model: {str(e)}")
            return None

    def prepare_features(self, ndvi_data: Dict, satellite_data: Dict) -> np.ndarray:
        """Prepare feature vectors from satellite data"""

        features = []
        bands = satellite_data['bands']

        # Extract spectral features
        for band_name, band_data in bands.items():
            if isinstance(band_data, np.ndarray):
                # Calculate band statistics
                features.extend([
                    np.mean(band_data[~np.isnan(band_data)]),
                    np.std(band_data[~np.isnan(band_data)]),
                    np.min(band_data[~np.isnan(band_data)]),
                    np.max(band_data[~np.isnan(band_data)])
                ])

        # Add NDVI features
        ndvi_array = ndvi_data['ndvi_array']
        ndvi_stats = ndvi_data['statistics']
        features.extend([
            ndvi_stats['mean'],
            ndvi_stats['std'],
            ndvi_stats['min'],
            ndvi_stats['max']
        ])

        # Add vegetation indices
        if 'B04' in bands and 'B03' in bands:  # Sentinel-2
            red = bands['B04']
            green = bands['B03']
            # Green NDVI
            gndvi = (bands['B08'] - green) / (bands['B08'] + green + 1e-8)
            features.extend([
                np.mean(gndvi[~np.isnan(gndvi)]),
                np.std(gndvi[~np.isnan(gndvi)])
            ])

        return np.array(features).reshape(1, -1)

    def predict(self, ndvi_data: Dict, satellite_data: Dict, 
                model_type: str = 'random_forest') -> Dict:
        """Predict crop health using specified model"""

        try:
            # Prepare features
            features = self.prepare_features(ndvi_data, satellite_data)

            if model_type not in self.models:
                raise ValueError(f"Model {model_type} not available")

            model = self.models[model_type]

            # Scale features for SVM
            if model_type == 'svm' and 'svm' in self.scalers:
                features = self.scalers['svm'].transform(features)

            # Make prediction
            if model_type == 'cnn' and DEEP_LEARNING_AVAILABLE:
                prediction = self._predict_cnn(satellite_data)
            else:
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(features)[0]
                    prediction_idx = np.argmax(probabilities)
                    confidence = probabilities[prediction_idx]
                else:
                    # For models without probability prediction
                    prediction_idx = model.predict(features)[0]
                    confidence = 0.8  # Default confidence
                    probabilities = np.zeros(len(self.health_classes))
                    probabilities[prediction_idx] = confidence

                prediction = {
                    'predicted_class': self.health_classes[prediction_idx],
                    'confidence': float(confidence),
                    'class_probabilities': {
                        class_name: float(prob) 
                        for class_name, prob in zip(self.health_classes, probabilities)
                    }
                }

            # Add health assessment
            health_assessment = self._generate_health_assessment(prediction, ndvi_data)
            prediction.update(health_assessment)

            self.logger.info(f"Prediction completed using {model_type}: {prediction['predicted_class']}")
            return prediction

        except Exception as e:
            self.logger.error(f"Error in prediction: {str(e)}")
            return {
                'predicted_class': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }

    def _predict_cnn(self, satellite_data: Dict) -> Dict:
        """Make prediction using CNN model"""
        try:
            # Prepare image data for CNN
            bands = satellite_data['bands']

            # Stack spectral bands
            band_stack = []
            for band_name in ['B04', 'B08', 'B03', 'B11', 'B12']:  # Add more bands as needed
                if band_name in bands:
                    band_data = bands[band_name]
                    # Resize to 64x64 for CNN input
                    resized_band = np.resize(band_data, (64, 64))
                    band_stack.append(resized_band)

            # Pad to 6 bands if necessary
            while len(band_stack) < 6:
                band_stack.append(np.zeros((64, 64)))

            # Create input tensor
            input_data = np.stack(band_stack, axis=-1)
            input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension

            # Normalize
            input_data = (input_data - np.mean(input_data)) / (np.std(input_data) + 1e-8)

            # Make prediction
            probabilities = self.models['cnn'].predict(input_data)[0]
            prediction_idx = np.argmax(probabilities)
            confidence = probabilities[prediction_idx]

            return {
                'predicted_class': self.health_classes[prediction_idx],
                'confidence': float(confidence),
                'class_probabilities': {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.health_classes, probabilities)
                }
            }

        except Exception as e:
            self.logger.error(f"Error in CNN prediction: {str(e)}")
            return {
                'predicted_class': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }

    def _generate_health_assessment(self, prediction: Dict, ndvi_data: Dict) -> Dict:
        """Generate detailed health assessment"""

        ndvi_mean = ndvi_data['statistics']['mean']
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence']

        # Health score calculation (0-100)
        if predicted_class == 'healthy':
            health_score = min(95, confidence * 100)
        elif predicted_class == 'water_stress':
            health_score = max(30, 60 - confidence * 30)
        elif predicted_class == 'nutrient_deficiency':
            health_score = max(40, 70 - confidence * 30)
        else:
            health_score = max(20, 50 - confidence * 30)

        # Recommendations
        recommendations = self._generate_recommendations(predicted_class, ndvi_mean)

        # Calculate unhealthy percentage
        unhealthy_classes = ['water_stress', 'nutrient_deficiency', 'disease', 'pest_damage']
        unhealthy_prob = sum(
            prediction['class_probabilities'].get(cls, 0) 
            for cls in unhealthy_classes
        )
        unhealthy_percentage = unhealthy_prob * 100

        return {
            'health_score': health_score,
            'unhealthy_percentage': unhealthy_percentage,
            'recommendations': recommendations,
            'ndvi_assessment': self._assess_ndvi(ndvi_mean)
        }

    def _generate_recommendations(self, predicted_class: str, ndvi_mean: float) -> List[str]:
        """Generate actionable recommendations based on prediction"""

        recommendations = []

        if predicted_class == 'water_stress':
            recommendations.extend([
                "Increase irrigation frequency",
                "Check soil moisture levels",
                "Consider drip irrigation systems",
                "Monitor weather forecasts for rainfall"
            ])
        elif predicted_class == 'nutrient_deficiency':
            recommendations.extend([
                "Apply balanced fertilizer",
                "Test soil nutrient levels",
                "Consider foliar feeding",
                "Adjust pH if necessary"
            ])
        elif predicted_class == 'disease':
            recommendations.extend([
                "Apply appropriate fungicides",
                "Remove affected plant material",
                "Improve air circulation",
                "Monitor spread to adjacent areas"
            ])
        elif predicted_class == 'pest_damage':
            recommendations.extend([
                "Identify specific pest species",
                "Apply targeted pest control measures",
                "Consider biological control options",
                "Monitor pest populations"
            ])

        # NDVI-based recommendations
        if ndvi_mean < 0.3:
            recommendations.append("NDVI indicates poor vegetation health - consider immediate intervention")
        elif ndvi_mean > 0.7:
            recommendations.append("Good vegetation health - maintain current practices")

        return recommendations

    def _assess_ndvi(self, ndvi_mean: float) -> str:
        """Assess vegetation health based on NDVI"""

        if ndvi_mean < 0.1:
            return "Very poor - bare soil or severely stressed vegetation"
        elif ndvi_mean < 0.3:
            return "Poor - sparse or stressed vegetation"
        elif ndvi_mean < 0.6:
            return "Moderate - adequate vegetation health"
        elif ndvi_mean < 0.8:
            return "Good - healthy vegetation"
        else:
            return "Excellent - very healthy, dense vegetation"

    def train_model(self, training_data: pd.DataFrame, model_type: str = 'random_forest'):
        """Train specified model with provided data"""

        try:
            # Prepare training data
            X = training_data.drop(['health_class'], axis=1).values
            y = training_data['health_class'].values

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            model = self.models[model_type]

            # Scale data for SVM
            if model_type == 'svm':
                X_train = self.scalers['svm'].fit_transform(X_train)
                X_test = self.scalers['svm'].transform(X_test)

            # Train model
            if model_type == 'cnn' and DEEP_LEARNING_AVAILABLE:
                # CNN training would require image data preparation
                self.logger.warning("CNN training requires specialized image data preparation")
                return
            else:
                model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)

            # Store performance metrics
            self.model_performance[model_type] = {
                'accuracy': accuracy,
                'cv_mean': np.mean(cv_scores),
                'cv_std': np.std(cv_scores),
                'classification_report': classification_report(y_test, y_pred),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }

            self.logger.info(f"Model {model_type} trained successfully. Accuracy: {accuracy:.3f}")

        except Exception as e:
            self.logger.error(f"Error training model {model_type}: {str(e)}")

    def save_models(self, model_dir: str = 'models'):
        """Save trained models to disk"""

        os.makedirs(model_dir, exist_ok=True)

        for model_name, model in self.models.items():
            try:
                if model_name == 'cnn' and DEEP_LEARNING_AVAILABLE:
                    model.save(os.path.join(model_dir, f'{model_name}_model.h5'))
                else:
                    joblib.dump(model, os.path.join(model_dir, f'{model_name}_model.pkl'))

                self.logger.info(f"Model {model_name} saved successfully")

            except Exception as e:
                self.logger.error(f"Error saving model {model_name}: {str(e)}")

        # Save scalers
        for scaler_name, scaler in self.scalers.items():
            try:
                joblib.dump(scaler, os.path.join(model_dir, f'{scaler_name}_scaler.pkl'))
            except Exception as e:
                self.logger.error(f"Error saving scaler {scaler_name}: {str(e)}")

    def load_models(self, model_dir: str = 'models'):
        """Load trained models from disk"""

        for model_name in self.models.keys():
            try:
                if model_name == 'cnn' and DEEP_LEARNING_AVAILABLE:
                    model_path = os.path.join(model_dir, f'{model_name}_model.h5')
                    if os.path.exists(model_path):
                        self.models[model_name] = tf.keras.models.load_model(model_path)
                else:
                    model_path = os.path.join(model_dir, f'{model_name}_model.pkl')
                    if os.path.exists(model_path):
                        self.models[model_name] = joblib.load(model_path)

                self.logger.info(f"Model {model_name} loaded successfully")

            except Exception as e:
                self.logger.error(f"Error loading model {model_name}: {str(e)}")

        # Load scalers
        for scaler_name in self.scalers.keys():
            try:
                scaler_path = os.path.join(model_dir, f'{scaler_name}_scaler.pkl')
                if os.path.exists(scaler_path):
                    self.scalers[scaler_name] = joblib.load(scaler_path)
            except Exception as e:
                self.logger.error(f"Error loading scaler {scaler_name}: {str(e)}")
