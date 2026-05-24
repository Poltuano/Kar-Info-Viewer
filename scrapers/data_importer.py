"""
Data Importer - Import scraped data into local storage and application
"""

import logging
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from utils.storage_manager import DataStorageManager
from utils.validators import CarDataValidator

logger = logging.getLogger(__name__)


class DataImporter:
    """
    Import scraped or external car data into local storage
    """

    def __init__(self, storage_manager: DataStorageManager):
        """
        Initialize data importer
        
        Args:
            storage_manager: DataStorageManager instance
        """
        self.storage_manager = storage_manager
        self.import_stats = {
            'total_imported': 0,
            'total_updated': 0,
            'total_failed': 0,
            'total_validated': 0,
            'errors': []
        }

    def import_from_json(self, filepath: str) -> bool:
        """
        Import cars from JSON file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                cars = data
            elif isinstance(data, dict) and 'data' in data:
                cars = data['data']
            else:
                logger.error("Invalid JSON structure")
                return False
            
            logger.info(f"Importing {len(cars)} cars from {filepath}")
            return self.import_cars(cars)
        
        except Exception as e:
            logger.error(f"Error importing JSON: {e}")
            self.import_stats['total_failed'] += 1
            self.import_stats['errors'].append(str(e))
            return False

    def import_from_csv(self, filepath: str, delimiter: str = ',') -> bool:
        """
        Import cars from CSV file
        
        Args:
            filepath: Path to CSV file
            delimiter: CSV delimiter
            
        Returns:
            True if successful
        """
        try:
            import csv
            
            cars = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    # Clean up the row
                    car = {k.strip(): v.strip() if v else None for k, v in row.items()}
                    cars.append(car)
            
            logger.info(f"Importing {len(cars)} cars from {filepath}")
            return self.import_cars(cars)
        
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            self.import_stats['total_failed'] += 1
            self.import_stats['errors'].append(str(e))
            return False

    def import_cars(self, cars: List[Dict]) -> bool:
        """
        Import a list of cars into storage
        
        Args:
            cars: List of car dictionaries
            
        Returns:
            True if successful
        """
        logger.info(f"Processing {len(cars)} cars for import")
        
        for idx, car in enumerate(cars):
            try:
                # Validate car data
                if not CarDataValidator.validate_car_data(car):
                    logger.warning(f"Car {idx} failed validation: {car}")
                    self.import_stats['total_failed'] += 1
                    continue
                
                # Add car to storage
                car_id = self.storage_manager.add_car(car)
                
                if car_id:
                    # Add specifications if available
                    specs_keys = ['engine_type', 'horsepower', 'torque', 'transmission',
                                 'acceleration_0_100', 'top_speed', 'fuel_consumption_combined',
                                 'fuel_type', 'fuel_tank_capacity', 'cargo_capacity',
                                 'passenger_seats', 'dimensions_length', 'dimensions_width',
                                 'dimensions_height', 'weight', 'wheelbase']
                    
                    specs = {k: v for k, v in car.items() if k in specs_keys and v}
                    if specs:
                        self.storage_manager.add_specifications(car_id, specs)
                    
                    self.import_stats['total_imported'] += 1
                    
                    if (idx + 1) % 100 == 0:
                        logger.info(f"Imported {idx + 1}/{len(cars)} cars")
                else:
                    self.import_stats['total_failed'] += 1
            
            except Exception as e:
                logger.error(f"Error importing car {idx}: {e}")
                self.import_stats['total_failed'] += 1
                self.import_stats['errors'].append(f"Car {idx}: {str(e)}")
        
        logger.info(f"Import complete: {self.import_stats['total_imported']} imported, "
                   f"{self.import_stats['total_failed']} failed")
        return self.import_stats['total_imported'] > 0

    def import_and_merge(self, new_cars: List[Dict],
                        merge_field: str = 'vin') -> Dict:
        """
        Import cars and merge with existing data
        
        Args:
            new_cars: List of new car data
            merge_field: Field to use for merging (usually 'vin' or 'external_id')
            
        Returns:
            Statistics dictionary
        """
        stats = {'imported': 0, 'updated': 0, 'failed': 0}
        
        for car in new_cars:
            try:
                # Check if car already exists
                existing = self.storage_manager.search_cars()
                
                # If merge_field exists, check for duplicates
                if merge_field in car and car[merge_field]:
                    car_id = self.storage_manager.add_car(car)  # This handles update
                    stats['imported'] += 1
                else:
                    car_id = self.storage_manager.add_car(car)
                    stats['imported'] += 1
            
            except Exception as e:
                logger.error(f"Error in import_and_merge: {e}")
                stats['failed'] += 1
        
        return stats

    def get_import_stats(self) -> Dict:
        """
        Get import statistics
        
        Returns:
            Statistics dictionary
        """
        return self.import_stats

    def export_cars_to_json(self, output_path: str,
                           filters: Optional[Dict] = None) -> bool:
        """
        Export cars to JSON file
        
        Args:
            output_path: Path to save JSON file
            filters: Optional filtering criteria
            
        Returns:
            True if successful
        """
        try:
            # Search cars (with optional filters)
            cars = self.storage_manager.search_cars(
                make=filters.get('make') if filters else None,
                model=filters.get('model') if filters else None,
                year=filters.get('year') if filters else None,
                limit=100000
            )
            
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON
            with open(output_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_records': len(cars),
                    'cars': cars
                }, f, indent=2)
            
            logger.info(f"Exported {len(cars)} cars to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
