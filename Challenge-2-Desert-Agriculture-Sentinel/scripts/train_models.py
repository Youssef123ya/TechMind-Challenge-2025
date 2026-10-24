#!/usr/bin/env python3
"""
Model Training Script for Desert Agriculture Sentinel
Train machine learning models for crop health classification
"""

import os
import sys
import logging
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# Add project modules to path
sys.path.append(str(Path(__file__).parent.parent))
from src.ml_models import CropHealthClassifier
from src.config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def generate_sample_training_data(output_file='training_data.csv', num_samples=1000):
    """Generate sample training data for demonstration"""
    logger = logging.getLogger(__name__)

    np.random.seed(42)

    # Generate synthetic features
    data = []
    health_classes = ['healthy', 'water_stress', 'nutrient_deficiency', 'disease', 'pest_damage']

    for i in range(num_samples):
        # Simulate spectral band values
        b04_red = np.random.uniform(0.05, 0.15)  # Red band
        b08_nir = np.random.uniform(0.3, 0.6)    # NIR band
        b03_green = np.random.uniform(0.04, 0.12) # Green band
        b11_swir1 = np.random.uniform(0.1, 0.3)  # SWIR1 band
        b12_swir2 = np.random.uniform(0.05, 0.2) # SWIR2 band

        # Calculate indices
        ndvi = (b08_nir - b04_red) / (b08_nir + b04_red)
        gndvi = (b08_nir - b03_green) / (b08_nir + b03_green)

        # Assign health class based on characteristics
        if ndvi > 0.6 and b08_nir > 0.5:
            health_class = 'healthy'
        elif ndvi < 0.3:
            health_class = np.random.choice(['water_stress', 'disease'])
        elif b11_swir1 > 0.25:
            health_class = 'water_stress'
        elif b03_green > 0.1:
            health_class = 'nutrient_deficiency'
        else:
            health_class = np.random.choice(health_classes)

        # Create feature vector
        features = {
            'b04_mean': b04_red,
            'b04_std': np.random.uniform(0.01, 0.03),
            'b04_min': b04_red * 0.8,
            'b04_max': b04_red * 1.2,
            'b08_mean': b08_nir,
            'b08_std': np.random.uniform(0.05, 0.1),
            'b08_min': b08_nir * 0.8,
            'b08_max': b08_nir * 1.2,
            'b03_mean': b03_green,
            'b03_std': np.random.uniform(0.01, 0.02),
            'b03_min': b03_green * 0.8,
            'b03_max': b03_green * 1.2,
            'b11_mean': b11_swir1,
            'b11_std': np.random.uniform(0.02, 0.05),
            'b11_min': b11_swir1 * 0.8,
            'b11_max': b11_swir1 * 1.2,
            'b12_mean': b12_swir2,
            'b12_std': np.random.uniform(0.01, 0.03),
            'b12_min': b12_swir2 * 0.8,
            'b12_max': b12_swir2 * 1.2,
            'ndvi_mean': ndvi,
            'ndvi_std': np.random.uniform(0.02, 0.05),
            'ndvi_min': ndvi * 0.9,
            'ndvi_max': ndvi * 1.1,
            'gndvi_mean': gndvi,
            'gndvi_std': np.random.uniform(0.02, 0.05),
            'health_class': health_class
        }

        data.append(features)

    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)

    logger.info(f"Generated {num_samples} training samples")
    logger.info(f"Class distribution:")
    for class_name, count in df['health_class'].value_counts().items():
        logger.info(f"  {class_name}: {count} ({count/num_samples*100:.1f}%)")

    return df

def train_models(training_data_file, config):
    """Train all machine learning models"""
    logger = logging.getLogger(__name__)

    # Load training data
    if not os.path.exists(training_data_file):
        logger.info(f"Training data file not found. Generating sample data...")
        training_data = generate_sample_training_data(training_data_file)
    else:
        training_data = pd.read_csv(training_data_file)

    logger.info(f"Loaded training data: {len(training_data)} samples")

    # Initialize classifier
    classifier = CropHealthClassifier(config)

    # Train Random Forest
    logger.info("Training Random Forest model...")
    classifier.train_model(training_data, 'random_forest')

    # Train SVM
    logger.info("Training SVM model...")
    classifier.train_model(training_data, 'svm')

    # Print model performance
    for model_name, performance in classifier.model_performance.items():
        logger.info(f"{model_name} Performance:")
        logger.info(f"  Accuracy: {performance['accuracy']:.3f}")
        logger.info(f"  CV Mean: {performance['cv_mean']:.3f} (±{performance['cv_std']:.3f})")

    # Save models
    logger.info("Saving trained models...")
    classifier.save_models()

    logger.info("Model training completed successfully")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Train machine learning models')
    parser.add_argument('--data', default='training_data.csv',
                       help='Training data CSV file')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Configuration file path')
    parser.add_argument('--generate-sample-data', action='store_true',
                       help='Generate sample training data')
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of sample data points to generate')

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load configuration
    config = Config(args.config)

    try:
        if args.generate_sample_data:
            logger.info(f"Generating {args.samples} sample data points...")
            generate_sample_training_data(args.data, args.samples)

        # Train models
        train_models(args.data, config)

        return 0

    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
