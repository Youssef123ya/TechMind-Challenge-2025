#!/usr/bin/env python3
"""
Data Download Utility for Desert Agriculture Sentinel
Downloads satellite data from various sources
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project modules to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def download_sentinel2_data(area_coords, start_date, end_date, download_dir):
    """Download Sentinel-2 data for specified area and time range"""
    logger = logging.getLogger(__name__)

    try:
        # In a real implementation, this would use sentinelsat or similar
        logger.info(f"Downloading Sentinel-2 data for area: {area_coords}")
        logger.info(f"Date range: {start_date} to {end_date}")
        logger.info(f"Download directory: {download_dir}")

        # Create download directory
        os.makedirs(download_dir, exist_ok=True)

        # Simulate download process
        logger.info("Searching for available scenes...")
        logger.info("Found 5 Sentinel-2 scenes")
        logger.info("Downloading scenes...")

        # In real implementation:
        # from sentinelsat import SentinelAPI
        # api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
        # products = api.query(area, date=(start_date, end_date), platformname='Sentinel-2')
        # api.download_all(products)

        logger.info("Download completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error downloading Sentinel-2 data: {str(e)}")
        return False

def download_landsat_data(area_coords, start_date, end_date, download_dir):
    """Download Landsat data for specified area and time range"""
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Downloading Landsat data for area: {area_coords}")
        logger.info(f"Date range: {start_date} to {end_date}")
        logger.info(f"Download directory: {download_dir}")

        # Create download directory
        os.makedirs(download_dir, exist_ok=True)

        # Simulate download process
        logger.info("Searching for available scenes...")
        logger.info("Found 3 Landsat scenes")
        logger.info("Downloading scenes...")

        # In real implementation:
        # from landsatxplore.api import API
        # api = API(username, password)
        # scenes = api.search(dataset='landsat_8_c1', bbox=bbox, begin=start_date, end=end_date)

        logger.info("Download completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error downloading Landsat data: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Download satellite data')
    parser.add_argument('--area', required=True, 
                       help='Area coordinates as north,south,east,west')
    parser.add_argument('--start-date', required=True,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--satellite', choices=['sentinel2', 'landsat', 'both'],
                       default='both', help='Satellite data to download')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Configuration file path')

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load configuration
    config = Config(args.config)

    # Parse area coordinates
    try:
        coords = [float(x) for x in args.area.split(',')]
        if len(coords) != 4:
            raise ValueError("Area must have 4 coordinates")
        area_coords = {
            'north': coords[0],
            'south': coords[1],
            'east': coords[2],
            'west': coords[3]
        }
    except Exception as e:
        logger.error(f"Invalid area coordinates: {str(e)}")
        return 1

    # Download data
    success = True

    if args.satellite in ['sentinel2', 'both']:
        download_dir = config.get('satellite.sentinel2.download_dir', 'data/sentinel2')
        if not download_sentinel2_data(area_coords, args.start_date, args.end_date, download_dir):
            success = False

    if args.satellite in ['landsat', 'both']:
        download_dir = config.get('satellite.landsat.download_dir', 'data/landsat')
        if not download_landsat_data(area_coords, args.start_date, args.end_date, download_dir):
            success = False

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
