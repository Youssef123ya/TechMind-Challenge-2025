#!/usr/bin/env python3
"""
Water Optimizer for Desert Agriculture Sentinel
Optimizes irrigation scheduling and water usage based on satellite data and ML predictions
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

class WaterOptimizer:
    """Optimizes water usage for desert agriculture based on satellite monitoring"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Water optimization parameters
        self.water_efficiency_targets = {
            'baseline_efficiency': 0.7,  # 70% irrigation efficiency
            'target_efficiency': 0.9,    # 90% target efficiency
            'water_stress_threshold': 0.3,
            'optimal_soil_moisture': 0.6
        }

        # Crop water requirements (mm/day)
        self.crop_water_requirements = {
            'wheat': 4.5,
            'barley': 3.8,
            'tomatoes': 6.0,
            'dates': 8.5,
            'citrus': 7.2,
            'default': 5.0
        }

        # Irrigation methods efficiency
        self.irrigation_efficiency = {
            'flood': 0.45,
            'sprinkler': 0.75,
            'drip': 0.90,
            'micro_sprinkler': 0.85,
            'subsurface_drip': 0.95
        }

    def optimize(self, ndvi_data: Dict, soil_moisture_data: Dict, 
                 health_classification: Dict, crop_type: str = 'default') -> Dict:
        """Optimize water usage based on satellite and ML data"""

        self.logger.info("Starting water optimization analysis")

        try:
            # Calculate current water stress level
            water_stress = self._calculate_water_stress(ndvi_data, soil_moisture_data, health_classification)

            # Generate irrigation schedule
            irrigation_schedule = self._generate_irrigation_schedule(
                water_stress, soil_moisture_data, crop_type
            )

            # Calculate water savings potential
            water_savings = self._calculate_water_savings(irrigation_schedule, crop_type)

            # Generate efficiency recommendations
            efficiency_recommendations = self._generate_efficiency_recommendations(
                soil_moisture_data, water_stress
            )

            # Create optimization results
            optimization_results = {
                'timestamp': datetime.now().isoformat(),
                'water_stress_level': water_stress,
                'irrigation_schedule': irrigation_schedule,
                'water_savings': water_savings,
                'efficiency_recommendations': efficiency_recommendations,
                'soil_moisture_status': self._assess_soil_moisture(soil_moisture_data),
                'recommended_actions': self._generate_recommended_actions(
                    water_stress, health_classification
                )
            }

            self.logger.info(f"Water optimization completed. Potential savings: {water_savings['percentage']:.1f}%")
            return optimization_results

        except Exception as e:
            self.logger.error(f"Error in water optimization: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_water_stress(self, ndvi_data: Dict, soil_moisture_data: Dict, 
                               health_classification: Dict) -> Dict:
        """Calculate water stress level from multiple indicators"""

        # NDVI-based stress indicator
        ndvi_mean = ndvi_data['statistics']['mean']
        ndvi_stress = max(0, (0.6 - ndvi_mean) / 0.6)  # 0.6 as healthy threshold

        # Soil moisture stress indicator
        soil_moisture_mean = soil_moisture_data['statistics']['mean']
        moisture_stress = max(0, (self.water_efficiency_targets['water_stress_threshold'] - soil_moisture_mean) / 
                             self.water_efficiency_targets['water_stress_threshold'])

        # ML classification stress indicator
        water_stress_prob = health_classification.get('class_probabilities', {}).get('water_stress', 0)
        ml_stress = water_stress_prob

        # Combined stress index (weighted average)
        weights = {'ndvi': 0.3, 'soil_moisture': 0.5, 'ml_classification': 0.2}

        combined_stress = (
            weights['ndvi'] * ndvi_stress +
            weights['soil_moisture'] * moisture_stress +
            weights['ml_classification'] * ml_stress
        )

        # Classify stress level
        if combined_stress < 0.2:
            stress_level = 'low'
        elif combined_stress < 0.5:
            stress_level = 'moderate'
        elif combined_stress < 0.8:
            stress_level = 'high'
        else:
            stress_level = 'critical'

        return {
            'combined_stress_index': combined_stress,
            'stress_level': stress_level,
            'components': {
                'ndvi_stress': ndvi_stress,
                'moisture_stress': moisture_stress,
                'ml_stress': ml_stress
            }
        }

    def _generate_irrigation_schedule(self, water_stress: Dict, soil_moisture_data: Dict, 
                                    crop_type: str) -> Dict:
        """Generate optimized irrigation schedule"""

        stress_level = water_stress['stress_level']
        stress_index = water_stress['combined_stress_index']
        current_moisture = soil_moisture_data['statistics']['mean']

        # Base water requirement
        base_requirement = self.crop_water_requirements.get(crop_type, 
                                                           self.crop_water_requirements['default'])

        # Adjust requirement based on stress
        if stress_level == 'critical':
            water_multiplier = 1.5
            frequency = 'daily'
        elif stress_level == 'high':
            water_multiplier = 1.3
            frequency = 'every_2_days'
        elif stress_level == 'moderate':
            water_multiplier = 1.1
            frequency = 'every_3_days'
        else:
            water_multiplier = 0.9
            frequency = 'weekly'

        # Calculate irrigation amounts
        daily_requirement = base_requirement * water_multiplier

        # Generate 7-day schedule
        schedule = []
        current_date = datetime.now()

        for i in range(7):
            date = current_date + timedelta(days=i)

            # Determine if irrigation is needed
            need_irrigation = False
            irrigation_amount = 0

            if frequency == 'daily':
                need_irrigation = True
                irrigation_amount = daily_requirement
            elif frequency == 'every_2_days' and i % 2 == 0:
                need_irrigation = True
                irrigation_amount = daily_requirement * 2
            elif frequency == 'every_3_days' and i % 3 == 0:
                need_irrigation = True
                irrigation_amount = daily_requirement * 3
            elif frequency == 'weekly' and i == 0:
                need_irrigation = True
                irrigation_amount = daily_requirement * 7

            schedule.append({
                'date': date.strftime('%Y-%m-%d'),
                'irrigation_needed': need_irrigation,
                'amount_mm': round(irrigation_amount, 2) if need_irrigation else 0,
                'timing': 'early_morning' if need_irrigation else None,
                'method': 'drip' if stress_level in ['high', 'critical'] else 'sprinkler'
            })

        total_weekly_water = sum(day['amount_mm'] for day in schedule)

        return {
            'frequency': frequency,
            'daily_schedule': schedule,
            'total_weekly_water_mm': round(total_weekly_water, 2),
            'average_daily_water_mm': round(total_weekly_water / 7, 2)
        }

    def _calculate_water_savings(self, irrigation_schedule: Dict, crop_type: str) -> Dict:
        """Calculate potential water savings compared to traditional methods"""

        optimized_weekly_water = irrigation_schedule['total_weekly_water_mm']

        # Calculate traditional water usage (flood irrigation)
        base_requirement = self.crop_water_requirements.get(crop_type, 
                                                           self.crop_water_requirements['default'])
        traditional_daily_water = base_requirement / self.irrigation_efficiency['flood']
        traditional_weekly_water = traditional_daily_water * 7

        # Calculate savings
        water_savings_mm = traditional_weekly_water - optimized_weekly_water
        savings_percentage = (water_savings_mm / traditional_weekly_water) * 100

        # Calculate cost savings (example: $0.001 per mm per hectare)
        cost_per_mm_per_ha = 0.001
        weekly_cost_savings_per_ha = water_savings_mm * cost_per_mm_per_ha
        annual_cost_savings_per_ha = weekly_cost_savings_per_ha * 52

        return {
            'water_saved_mm_per_week': round(water_savings_mm, 2),
            'percentage': round(savings_percentage, 1),
            'cost_savings_per_hectare': {
                'weekly': round(weekly_cost_savings_per_ha, 2),
                'annual': round(annual_cost_savings_per_ha, 2)
            },
            'traditional_usage_mm': round(traditional_weekly_water, 2),
            'optimized_usage_mm': round(optimized_weekly_water, 2)
        }

    def _generate_efficiency_recommendations(self, soil_moisture_data: Dict, 
                                           water_stress: Dict) -> List[Dict]:
        """Generate irrigation efficiency recommendations"""

        recommendations = []

        current_moisture = soil_moisture_data['statistics']['mean']
        stress_level = water_stress['stress_level']

        # Irrigation method recommendations
        if stress_level in ['high', 'critical']:
            recommendations.append({
                'category': 'irrigation_method',
                'recommendation': 'Switch to drip irrigation or subsurface drip irrigation',
                'benefit': 'Up to 95% water use efficiency',
                'priority': 'high'
            })

        # Timing recommendations
        recommendations.append({
            'category': 'timing',
            'recommendation': 'Irrigate during early morning hours (4-7 AM)',
            'benefit': 'Reduces evaporation losses by 15-20%',
            'priority': 'medium'
        })

        # Mulching recommendations
        if current_moisture < 0.4:
            recommendations.append({
                'category': 'soil_management',
                'recommendation': 'Apply organic mulch around plants',
                'benefit': 'Reduces soil evaporation by 30-50%',
                'priority': 'medium'
            })

        # Technology recommendations
        recommendations.append({
            'category': 'technology',
            'recommendation': 'Install soil moisture sensors for real-time monitoring',
            'benefit': 'Optimize irrigation timing and reduce over-watering',
            'priority': 'low'
        })

        # Crop selection recommendations
        if stress_level == 'critical':
            recommendations.append({
                'category': 'crop_management',
                'recommendation': 'Consider drought-resistant crop varieties',
                'benefit': 'Reduce water requirements by 20-40%',
                'priority': 'high'
            })

        return recommendations

    def _assess_soil_moisture(self, soil_moisture_data: Dict) -> Dict:
        """Assess current soil moisture status"""

        mean_moisture = soil_moisture_data['statistics']['mean']
        std_moisture = soil_moisture_data['statistics']['std']

        if mean_moisture < 0.2:
            status = 'critically_dry'
            description = 'Immediate irrigation required'
            urgency = 'critical'
        elif mean_moisture < 0.3:
            status = 'dry'
            description = 'Irrigation needed within 24 hours'
            urgency = 'high'
        elif mean_moisture < 0.5:
            status = 'moderate'
            description = 'Monitor closely, irrigation may be needed soon'
            urgency = 'medium'
        elif mean_moisture < 0.7:
            status = 'adequate'
            description = 'Soil moisture levels are satisfactory'
            urgency = 'low'
        else:
            status = 'wet'
            description = 'Soil moisture levels are high, reduce irrigation'
            urgency = 'none'

        # Check moisture uniformity
        uniformity = 'good' if std_moisture < 0.1 else 'poor' if std_moisture > 0.2 else 'fair'

        return {
            'status': status,
            'description': description,
            'urgency': urgency,
            'uniformity': uniformity,
            'mean_moisture': round(mean_moisture, 3),
            'variation': round(std_moisture, 3)
        }

    def _generate_recommended_actions(self, water_stress: Dict, 
                                    health_classification: Dict) -> List[Dict]:
        """Generate specific actionable recommendations"""

        actions = []
        stress_level = water_stress['stress_level']
        predicted_class = health_classification.get('predicted_class', 'unknown')

        # Immediate actions based on stress level
        if stress_level == 'critical':
            actions.append({
                'action': 'emergency_irrigation',
                'description': 'Apply emergency irrigation immediately',
                'timeframe': 'immediate',
                'priority': 1
            })

        # Actions based on health classification
        if predicted_class == 'water_stress':
            actions.append({
                'action': 'increase_irrigation_frequency',
                'description': 'Increase irrigation frequency and check system efficiency',
                'timeframe': 'within_24_hours',
                'priority': 2
            })

        # Preventive actions
        actions.append({
            'action': 'monitor_weather',
            'description': 'Monitor weather forecast for rainfall and adjust irrigation accordingly',
            'timeframe': 'ongoing',
            'priority': 3
        })

        actions.append({
            'action': 'system_maintenance',
            'description': 'Check irrigation system for leaks and blockages',
            'timeframe': 'weekly',
            'priority': 4
        })

        return sorted(actions, key=lambda x: x['priority'])

    def generate_water_report(self, optimization_results: Dict, 
                            area_hectares: float = 1.0) -> Dict:
        """Generate comprehensive water usage report"""

        try:
            water_savings = optimization_results.get('water_savings', {})
            irrigation_schedule = optimization_results.get('irrigation_schedule', {})

            # Scale calculations to actual area
            weekly_water_saved_m3 = (water_savings.get('water_saved_mm_per_week', 0) / 1000) * area_hectares * 10000
            annual_water_saved_m3 = weekly_water_saved_m3 * 52

            # Calculate environmental impact
            co2_reduction_kg = annual_water_saved_m3 * 0.5  # Approximate CO2 reduction from water savings

            report = {
                'report_date': datetime.now().isoformat(),
                'area_hectares': area_hectares,
                'water_usage': {
                    'optimized_weekly_mm': irrigation_schedule.get('total_weekly_water_mm', 0),
                    'optimized_weekly_m3': (irrigation_schedule.get('total_weekly_water_mm', 0) / 1000) * area_hectares * 10000,
                    'traditional_weekly_m3': (water_savings.get('traditional_usage_mm', 0) / 1000) * area_hectares * 10000
                },
                'savings': {
                    'weekly_water_saved_m3': round(weekly_water_saved_m3, 2),
                    'annual_water_saved_m3': round(annual_water_saved_m3, 2),
                    'savings_percentage': water_savings.get('percentage', 0),
                    'annual_cost_savings': round(water_savings.get('cost_savings_per_hectare', {}).get('annual', 0) * area_hectares, 2)
                },
                'environmental_impact': {
                    'co2_reduction_kg_per_year': round(co2_reduction_kg, 2),
                    'water_conservation_rating': self._get_conservation_rating(water_savings.get('percentage', 0))
                },
                'recommendations_summary': len(optimization_results.get('efficiency_recommendations', [])),
                'next_monitoring_date': (datetime.now() + timedelta(days=7)).isoformat()
            }

            return report

        except Exception as e:
            self.logger.error(f"Error generating water report: {str(e)}")
            return {'error': str(e)}

    def _get_conservation_rating(self, savings_percentage: float) -> str:
        """Get water conservation rating based on savings percentage"""

        if savings_percentage >= 40:
            return 'Excellent'
        elif savings_percentage >= 25:
            return 'Good'
        elif savings_percentage >= 15:
            return 'Fair'
        else:
            return 'Needs Improvement'
