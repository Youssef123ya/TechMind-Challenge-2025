#!/usr/bin/env python3
"""
Desert Agriculture Sentinel - Main Application
Intelligent satellite-based crop health monitoring and water optimization system
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project modules to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.satellite_processor import SatelliteDataProcessor
from src.ml_models import CropHealthClassifier
from src.water_optimizer import WaterOptimizer
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/desert_agriculture_sentinel.log'),
        logging.StreamHandler()
    ]
)

class DesertAgricultureSentinel:
    """Main application class for Desert Agriculture Sentinel system"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config = Config(config_path)
        self.satellite_processor = SatelliteDataProcessor(self.config)
        self.crop_classifier = CropHealthClassifier(self.config)
        self.water_optimizer = WaterOptimizer(self.config)
        self.logger = logging.getLogger(__name__)

    def run_monitoring_cycle(self, area_of_interest: dict):
        """Run complete monitoring cycle for specified area"""
        self.logger.info(f"Starting monitoring cycle for area: {area_of_interest}")

        try:
            # Step 1: Process satellite data
            self.logger.info("Processing satellite imagery...")
            satellite_data = self.satellite_processor.process_area(area_of_interest)

            # Step 2: Calculate vegetation indices
            self.logger.info("Calculating vegetation indices...")
            ndvi_data = self.satellite_processor.calculate_ndvi(satellite_data)
            soil_moisture = self.satellite_processor.calculate_soil_moisture(satellite_data)

            # Step 3: Classify crop health
            self.logger.info("Classifying crop health...")
            health_classification = self.crop_classifier.predict(ndvi_data, satellite_data)

            # Step 4: Optimize water usage
            self.logger.info("Optimizing water usage...")
            irrigation_plan = self.water_optimizer.optimize(
                ndvi_data, soil_moisture, health_classification
            )

            # Step 5: Generate report
            results = {
                'timestamp': datetime.now().isoformat(),
                'area': area_of_interest,
                'ndvi_stats': ndvi_data.get('statistics'),
                'soil_moisture_stats': soil_moisture.get('statistics'),
                'health_classification': health_classification,
                'irrigation_recommendations': irrigation_plan,
                'water_savings_potential': irrigation_plan.get('water_savings', 0)
            }

            self.logger.info("Monitoring cycle completed successfully")
            return results

        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {str(e)}")
            raise

    def generate_alert(self, results: dict):
        """Generate alerts for critical conditions"""
        alerts = []

        # Check for water stress
        if results['soil_moisture_stats']['mean'] < self.config.get('alerts.soil_moisture_threshold', 0.3):
            alerts.append({
                'type': 'water_stress',
                'severity': 'high',
                'message': 'Critical soil moisture levels detected'
            })

        # Check for crop health issues
        unhealthy_percentage = results['health_classification'].get('unhealthy_percentage', 0)
        if unhealthy_percentage > self.config.get('alerts.unhealthy_crop_threshold', 20):
            alerts.append({
                'type': 'crop_health',
                'severity': 'medium',
                'message': f'{unhealthy_percentage}% of crops showing health issues'
            })

        return alerts

def main():
    """Main entry point"""
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    # Initialize system
    sentinel = DesertAgricultureSentinel()

    # Example area of interest (replace with actual coordinates)
    area_of_interest = {
        'name': 'Test Desert Farm',
        'coordinates': {
            'north': 31.5,
            'south': 31.3,
            'east': 35.2,
            'west': 35.0
        }
    }

    try:
        # Run monitoring cycle
        results = sentinel.run_monitoring_cycle(area_of_interest)

        # Generate alerts
        alerts = sentinel.generate_alert(results)

        # Save results
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'results/monitoring_results_{timestamp}.json', 'w') as f:
            json.dump({'results': results, 'alerts': alerts}, f, indent=2)

        print("\n=== Desert Agriculture Sentinel Results ===")
        print(f"NDVI Average: {results['ndvi_stats']['mean']:.3f}")
        print(f"Soil Moisture: {results['soil_moisture_stats']['mean']:.3f}")
        print(f"Water Savings Potential: {results['water_savings_potential']:.1f}%")
        print(f"Alerts Generated: {len(alerts)}")

    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
