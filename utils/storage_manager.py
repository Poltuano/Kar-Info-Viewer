"""
Data Storage Manager - Handle local data organization and caching
"""

import os
import json
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class DataStorageManager:
    """Manage local data storage and organization"""
    
    def __init__(self, storage_path: str = "data/storage"):
        """
        Initialize storage manager
        
        Args:
            storage_path: Base path for data storage
        """
        self.storage_path = Path(storage_path)
        self.db_path = self.storage_path / "cars.db"
        self.cache_path = self.storage_path / "cache"
        self.images_path = self.storage_path / "images"
        self.logs_path = self.storage_path / "logs"
        self.exports_path = self.storage_path / "exports"
        
        # Create directory structure
        self._create_directories()
        self._init_database()
    
    def _create_directories(self):
        """Create all necessary directories"""
        directories = [
            self.storage_path,
            self.cache_path,
            self.images_path,
            self.logs_path,
            self.exports_path,
            self.images_path / "thumbnails",
            self.images_path / "full",
            self.images_path / "diagrams",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    def _init_database(self):
        """Initialize SQLite database for efficient storage"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Cars table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER,
                    body_type TEXT,
                    color TEXT,
                    vin TEXT UNIQUE,
                    license_plate TEXT,
                    purchase_date TEXT,
                    purchase_price REAL,
                    current_mileage INTEGER,
                    image_path TEXT,
                    external_id TEXT UNIQUE,
                    created_at TEXT,
                    updated_at TEXT,
                    last_synced TEXT,
                    INDEX idx_make (make),
                    INDEX idx_model (model),
                    INDEX idx_year (year),
                    INDEX idx_vin (vin)
                )
            ''')
            
            # Specifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS specifications (
                    id INTEGER PRIMARY KEY,
                    car_id INTEGER NOT NULL,
                    engine_type TEXT,
                    horsepower INTEGER,
                    torque INTEGER,
                    transmission TEXT,
                    acceleration_0_100 REAL,
                    top_speed INTEGER,
                    fuel_consumption_combined REAL,
                    fuel_type TEXT,
                    fuel_tank_capacity REAL,
                    cargo_capacity INTEGER,
                    passenger_seats INTEGER,
                    dimensions_length REAL,
                    dimensions_width REAL,
                    dimensions_height REAL,
                    weight INTEGER,
                    wheelbase REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (car_id) REFERENCES cars(id),
                    INDEX idx_car_id (car_id)
                )
            ''')
            
            # Maintenance records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_records (
                    id INTEGER PRIMARY KEY,
                    car_id INTEGER NOT NULL,
                    date TEXT,
                    maintenance_type TEXT,
                    description TEXT,
                    cost REAL,
                    mileage INTEGER,
                    service_provider TEXT,
                    notes TEXT,
                    created_at TEXT,
                    FOREIGN KEY (car_id) REFERENCES cars(id),
                    INDEX idx_car_id (car_id),
                    INDEX idx_date (date)
                )
            ''')
            
            # Cache metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    id INTEGER PRIMARY KEY,
                    cache_key TEXT UNIQUE,
                    cache_type TEXT,
                    expires_at TEXT,
                    created_at TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    INDEX idx_cache_key (cache_key),
                    INDEX idx_expires_at (expires_at)
                )
            ''')
            
            # Search history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY,
                    make TEXT,
                    model TEXT,
                    year INTEGER,
                    results_count INTEGER,
                    search_time TEXT,
                    INDEX idx_search_time (search_time)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_car(self, car_data: Dict) -> Optional[int]:
        """
        Add or update a car in local storage
        
        Args:
            car_data: Dictionary with car information
            
        Returns:
            Car ID or None if failed
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO cars (
                    make, model, year, body_type, color, vin, license_plate,
                    purchase_date, purchase_price, current_mileage, image_path,
                    external_id, created_at, updated_at, last_synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                car_data.get('make'),
                car_data.get('model'),
                car_data.get('year'),
                car_data.get('body_type'),
                car_data.get('color'),
                car_data.get('vin'),
                car_data.get('license_plate'),
                car_data.get('purchase_date'),
                car_data.get('purchase_price'),
                car_data.get('current_mileage'),
                car_data.get('image_path'),
                car_data.get('external_id'),
                now,
                now,
                now
            ))
            
            car_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Added car with ID: {car_id}")
            return car_id
        except Exception as e:
            logger.error(f"Error adding car: {e}")
            return None
    
    def search_cars(self, make: Optional[str] = None,
                   model: Optional[str] = None,
                   year: Optional[int] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Search for cars in local storage
        
        Args:
            make: Car manufacturer
            model: Car model
            year: Model year
            limit: Maximum results
            
        Returns:
            List of car dictionaries
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM cars WHERE 1=1'
            params = []
            
            if make:
                query += ' AND make LIKE ?'
                params.append(f'%{make}%')
            if model:
                query += ' AND model LIKE ?'
                params.append(f'%{model}%')
            if year:
                query += ' AND year = ?'
                params.append(year)
            
            query += ' ORDER BY make, model, year LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            logger.info(f"Found {len(results)} cars")
            return results
        except Exception as e:
            logger.error(f"Error searching cars: {e}")
            return []
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM cars')
            total_cars = cursor.fetchone()[0]
            
            conn.close()
            
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            stats = {
                'total_cars': total_cars,
                'database_size_mb': round(db_size / (1024 * 1024), 2),
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
