#!/usr/bin/env python3
"""
Water Usage Report Generator for Desert Agriculture Sentinel
Generates comprehensive water usage and optimization reports
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project modules to path
sys.path.append(str(Path(__file__).parent.parent))
from src.water_optimizer import WaterOptimizer
from src.config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def generate_water_report(area_hectares, crop_type, config):
    """Generate comprehensive water usage report"""
    logger = logging.getLogger(__name__)

    # Initialize water optimizer
    water_optimizer = WaterOptimizer(config)

    # Simulate monitoring data
    ndvi_data = {
        'ndvi_array': None,  # Would contain actual NDVI array
        'statistics': {
            'mean': 0.65,
            'std': 0.15,
            'min': 0.2,
            'max': 0.85,
            'valid_pixel_count': 10000
        }
    }

    soil_moisture_data = {
        'soil_moisture_array': None,  # Would contain actual soil moisture array
        'statistics': {
            'mean': 0.45,
            'std': 0.12,
            'min': 0.2,
            'max': 0.7
        }
    }

    health_classification = {
        'predicted_class': 'moderate_stress',
        'confidence': 0.78,
        'class_probabilities': {
            'healthy': 0.35,
            'water_stress': 0.25,
            'nutrient_deficiency': 0.15,
            'disease': 0.15,
            'pest_damage': 0.10
        }
    }

    logger.info(f"Generating water optimization report for {area_hectares} hectares of {crop_type}")

    # Generate optimization results
    optimization_results = water_optimizer.optimize(
        ndvi_data, soil_moisture_data, health_classification, crop_type
    )

    # Generate comprehensive report
    report = water_optimizer.generate_water_report(optimization_results, area_hectares)

    return report, optimization_results

def save_report_json(report, optimization_results, filename):
    """Save report to JSON file"""
    combined_report = {
        'summary_report': report,
        'detailed_optimization': optimization_results
    }

    with open(filename, 'w') as f:
        json.dump(combined_report, f, indent=2)

def print_report_summary(report, optimization_results):
    """Print formatted report summary to console"""
    print("\n" + "="*60)
    print("   DESERT AGRICULTURE SENTINEL - WATER REPORT")
    print("="*60)

    print(f"\n📊 OVERVIEW")
    print(f"   Report Date: {report['report_date'][:19]}")
    print(f"   Area Monitored: {report['area_hectares']} hectares")

    print(f"\n💧 WATER USAGE ANALYSIS")
    print(f"   Current Weekly Usage: {report['water_usage']['optimized_weekly_m3']:.1f} m³")
    print(f"   Traditional Usage: {report['water_usage']['traditional_weekly_m3']:.1f} m³")
    print(f"   Water Saved: {report['savings']['weekly_water_saved_m3']:.1f} m³/week")
    print(f"   Savings Percentage: {report['savings']['savings_percentage']:.1f}%")

    print(f"\n💰 ECONOMIC IMPACT")
    print(f"   Annual Cost Savings: ${report['savings']['annual_cost_savings']:.2f}")
    print(f"   Annual Water Saved: {report['savings']['annual_water_saved_m3']:.1f} m³")

    print(f"\n🌱 ENVIRONMENTAL IMPACT")
    print(f"   CO₂ Reduction: {report['environmental_impact']['co2_reduction_kg_per_year']:.1f} kg/year")
    print(f"   Conservation Rating: {report['environmental_impact']['water_conservation_rating']}")

    # Soil moisture status
    soil_status = optimization_results.get('soil_moisture_status', {})
    print(f"\n🌾 SOIL CONDITIONS")
    print(f"   Moisture Status: {soil_status.get('status', 'Unknown').replace('_', ' ').title()}")
    print(f"   Moisture Level: {soil_status.get('mean_moisture', 0):.1%}")
    print(f"   Urgency: {soil_status.get('urgency', 'Unknown').title()}")

    # Water stress information
    water_stress = optimization_results.get('water_stress_level', {})
    print(f"\n⚠️  STRESS INDICATORS")
    print(f"   Overall Stress Level: {water_stress.get('stress_level', 'Unknown').title()}")
    print(f"   Stress Index: {water_stress.get('combined_stress_index', 0):.2f}")

    # Irrigation schedule
    irrigation_schedule = optimization_results.get('irrigation_schedule', {})
    print(f"\n🚿 IRRIGATION RECOMMENDATIONS")
    print(f"   Recommended Frequency: {irrigation_schedule.get('frequency', 'Unknown').replace('_', ' ').title()}")
    print(f"   Weekly Water Requirement: {irrigation_schedule.get('total_weekly_water_mm', 0):.1f} mm")
    print(f"   Daily Average: {irrigation_schedule.get('average_daily_water_mm', 0):.1f} mm")

    # Top recommendations
    recommendations = optimization_results.get('efficiency_recommendations', [])
    if recommendations:
        print(f"\n🎯 TOP RECOMMENDATIONS")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.get('recommendation', 'No recommendation')}")
            print(f"      Benefit: {rec.get('benefit', 'Unknown benefit')}")

    # Next steps
    actions = optimization_results.get('recommended_actions', [])
    if actions:
        print(f"\n📋 IMMEDIATE ACTIONS")
        for i, action in enumerate(actions[:3], 1):
            print(f"   {i}. {action.get('description', 'No description')}")
            print(f"      Timeframe: {action.get('timeframe', 'Unknown').replace('_', ' ').title()}")

    print(f"\n📅 Next monitoring date: {report['next_monitoring_date'][:19]}")
    print("="*60)
    print("🌱 Keep growing sustainably! 🌱")
    print("="*60 + "\n")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate water usage report')
    parser.add_argument('--area-hectares', type=float, default=1.0,
                       help='Area in hectares')
    parser.add_argument('--crop-type', default='default',
                       choices=['wheat', 'barley', 'tomatoes', 'dates', 'citrus', 'default'],
                       help='Crop type')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Configuration file path')
    parser.add_argument('--output', default='water_report.json',
                       help='Output JSON file')
    parser.add_argument('--print-only', action='store_true',
                       help='Only print to console, don\'t save file')

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load configuration
    config = Config(args.config)

    try:
        # Generate report
        report, optimization_results = generate_water_report(
            args.area_hectares, args.crop_type, config
        )

        # Print summary
        print_report_summary(report, optimization_results)

        # Save to file if requested
        if not args.print_only:
            # Create results directory
            os.makedirs('results', exist_ok=True)

            # Generate timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"results/water_report_{timestamp}.json"

            save_report_json(report, optimization_results, output_file)
            logger.info(f"Report saved to: {output_file}")
            print(f"📄 Detailed report saved to: {output_file}")

        return 0

    except Exception as e:
        logger.error(f"Error generating water report: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
