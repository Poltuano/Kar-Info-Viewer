"""
Data Importer - Import car data from various sources
"""

import logging
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import requests
from utils.storage_manager import DataStorageManager
from utils.validators import CarDataValidator

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_cars(self) -> List[Dict]:
        """Fetch cars from source"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get source name"""
        pass


class APIDataSource(DataSource):
    """Import data from REST API"""
    
    def __init__(self, api_endpoint: str, api_key: str = None, headers: Dict = None):
        """
        Initialize API data source
        
        Args:
            api_endpoint: Base URL of the API
            api_key: API key for authentication
            headers: Additional headers
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.headers = headers or {}
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def fetch_cars(self, endpoint: str = '/cars', params: Dict = None) -> List[Dict]:
        """
        Fetch cars from API
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            
        Returns:
            List of car data
        """
        try:
            url = f"{self.api_endpoint}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                cars = data
            elif isinstance(data, dict) and 'cars' in data:
                cars = data['cars']
            elif isinstance(data, dict) and 'data' in data:
                cars = data['data']
            else:
                logger.warning("Unexpected API response format")
                cars = []
            
            logger.info(f"Fetched {len(cars)} cars from API")
            return cars
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from API: {e}")
            return []
    
    def get_source_name(self) -> str:
        return "API"


class CSVDataSource(DataSource):
    """Import data from CSV file"""
    
    def __init__(self, file_path: str):
        """
        Initialize CSV data source
        
        Args:
            file_path: Path to CSV file
        """
        self.file_path = Path(file_path)
    
    def fetch_cars(self) -> List[Dict]:
        """
        Read cars from CSV file
        
        Returns:
            List of car data
        """
        try:
            if not self.file_path.exists():
                logger.error(f"CSV file not found: {self.file_path}")
                return []
            
            cars = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cars.append(dict(row))
            
            logger.info(f"Fetched {len(cars)} cars from CSV")
            return cars
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def get_source_name(self) -> str:
        return f"CSV ({self.file_path.name})"


class JSONDataSource(DataSource):
    """Import data from JSON file"""
    
    def __init__(self, file_path: str):
        """
        Initialize JSON data source
        
        Args:
            file_path: Path to JSON file
        """
        self.file_path = Path(file_path)
    
    def fetch_cars(self) -> List[Dict]:
        """
        Read cars from JSON file
        
        Returns:
            List of car data
        """
        try:
            if not self.file_path.exists():
                logger.error(f"JSON file not found: {self.file_path}")
                return []
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON formats
            if isinstance(data, list):
                cars = data
            elif isinstance(data, dict) and 'cars' in data:
                cars = data['cars']
            elif isinstance(data, dict) and 'data' in data:
                cars = data['data']
            else:
                logger.warning("Unexpected JSON format")
                cars = []
            
            logger.info(f"Fetched {len(cars)} cars from JSON")
            return cars
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            return []
    
    def get_source_name(self) -> str:
        return f"JSON ({self.file_path.name})"


class DataImporter:
    """Main data importer class"""
    
    def __init__(self, storage_manager: DataStorageManager):
        """
        Initialize data importer
        
        Args:
            storage_manager: DataStorageManager instance
        """
        self.storage = storage_manager
        self.import_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def import_from_source(self, source: DataSource, 
                          progress_callback: Optional[Callable] = None) -> Dict:
        """
        Import cars from a data source
        
        Args:
            source: DataSource instance
            progress_callback: Callback function for progress updates
            
        Returns:
            Import statistics
        """
        logger.info(f"Starting import from {source.get_source_name()}")
        
        # Reset statistics
        self.import_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'source': source.get_source_name(),
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Fetch data from source
            cars = source.fetch_cars()
            
            if not cars:
                logger.warning("No cars fetched from source")
                self.import_stats['end_time'] = datetime.now().isoformat()
                return self.import_stats
            
            # Process each car
            for idx, car_data in enumerate(cars):
                self.import_stats['total_processed'] += 1
                
                # Call progress callback
                if progress_callback:
                    progress_callback(idx + 1, len(cars))
                
                # Process car
                if self._process_car(car_data):
                    self.import_stats['successful'] += 1
                else:
                    self.import_stats['failed'] += 1
        
        except Exception as e:
            logger.error(f"Error during import: {e}")
            self.import_stats['errors'].append(str(e))
        
        self.import_stats['end_time'] = datetime.now().isoformat()
        logger.info(f"Import complete: {self.import_stats}")
        return self.import_stats
    
    def _process_car(self, car_data: Dict) -> bool:
        """
        Process a single car record
        
        Args:
            car_data: Car data dictionary
            
        Returns:
            True if successful
        """
        try:
            # Validate data
            if not self._validate_car_data(car_data):
                self.import_stats['skipped'] += 1
                return False
            
            # Extract car info
            car_info = {
                'make': car_data.get('make'),
                'model': car_data.get('model'),
                'year': car_data.get('year'),
                'body_type': car_data.get('body_type'),
                'color': car_data.get('color'),
                'vin': car_data.get('vin'),
                'license_plate': car_data.get('license_plate'),
                'purchase_date': car_data.get('purchase_date'),
                'purchase_price': car_data.get('purchase_price'),
                'current_mileage': car_data.get('current_mileage', 0),
                'image_path': car_data.get('image_path'),
                'external_id': car_data.get('id') or car_data.get('external_id')
            }
            
            # Add car to storage
            car_id = self.storage.add_car(car_info)
            if not car_id:
                logger.error(f"Failed to add car: {car_data.get('make')} {car_data.get('model')}")
                return False
            
            # Extract and add specifications if available
            if 'specifications' in car_data:
                specs = car_data['specifications']
                self.storage.add_specifications(car_id, specs)
            
            # Add maintenance records if available
            if 'maintenance_records' in car_data:
                for record in car_data['maintenance_records']:
                    self.storage.add_maintenance_record(car_id, record)
            
            return True
        except Exception as e:
            logger.error(f"Error processing car: {e}")
            self.import_stats['errors'].append(str(e))
            return False
    
    def _validate_car_data(self, car_data: Dict) -> bool:
        """
        Validate car data before import
        
        Args:
            car_data: Car data to validate
            
        Returns:
            True if valid
        """
        # Check required fields
        if not car_data.get('make') or not car_data.get('model'):
            logger.warning(f"Missing required fields: {car_data}")
            return False
        
        # Validate using CarDataValidator
        if not CarDataValidator.validate_car_data(car_data):
            logger.warning(f"Validation failed for car: {car_data}")
            return False
        
        return True
    
    def import_from_csv(self, file_path: str, 
                       progress_callback: Optional[Callable] = None) -> Dict:
        """
        Import cars from CSV file
        
        Args:
            file_path: Path to CSV file
            progress_callback: Progress callback function
            
        Returns:
            Import statistics
        """
        source = CSVDataSource(file_path)
        return self.import_from_source(source, progress_callback)
    
    def import_from_json(self, file_path: str,
                        progress_callback: Optional[Callable] = None) -> Dict:
        """
        Import cars from JSON file
        
        Args:
            file_path: Path to JSON file
            progress_callback: Progress callback function
            
        Returns:
            Import statistics
        """
        source = JSONDataSource(file_path)
        return self.import_from_source(source, progress_callback)
    
    def import_from_api(self, api_endpoint: str, api_key: str = None,
                       params: Dict = None,
                       progress_callback: Optional[Callable] = None) -> Dict:
        """
        Import cars from API
        
        Args:
            api_endpoint: API endpoint URL
            api_key: API key for authentication
            params: Query parameters
            progress_callback: Progress callback function
            
        Returns:
            Import statistics
        """
        source = APIDataSource(api_endpoint, api_key)
        return self.import_from_source(source, progress_callback)
    
    def get_import_stats(self) -> Dict:
        """Get current import statistics"""
        return self.import_stats


class BulkDataImporter:
    """Handle bulk imports from multiple sources"""
    
    def __init__(self, storage_manager: DataStorageManager):
        """
        Initialize bulk importer
        
        Args:
            storage_manager: DataStorageManager instance
        """
        self.storage = storage_manager
        self.importer = DataImporter(storage_manager)
        self.bulk_stats = []
    
    def import_multiple_files(self, file_paths: List[str],
                             progress_callback: Optional[Callable] = None) -> Dict:
        """
        Import from multiple files
        
        Args:
            file_paths: List of file paths
            progress_callback: Progress callback function
            
        Returns:
            Summary statistics
        """
        self.bulk_stats = []
        total_successful = 0
        total_failed = 0
        
        for idx, file_path in enumerate(file_paths):
            logger.info(f"Importing file {idx + 1}/{len(file_paths)}: {file_path}")
            
            if file_path.endswith('.csv'):
                stats = self.importer.import_from_csv(file_path, progress_callback)
            elif file_path.endswith('.json'):
                stats = self.importer.import_from_json(file_path, progress_callback)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                continue
            
            self.bulk_stats.append(stats)
            total_successful += stats.get('successful', 0)
            total_failed += stats.get('failed', 0)
        
        summary = {
            'total_files': len(file_paths),
            'total_successful': total_successful,
            'total_failed': total_failed,
            'per_file_stats': self.bulk_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Bulk import complete: {summary}")
        return summary
