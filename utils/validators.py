"""
Data Validators - Validate car data before processing
"""

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CarDataValidator:
    """Validate car data"""

    @staticmethod
    def validate_vin(vin: str) -> bool:
        """
        Validate VIN (Vehicle Identification Number)
        VIN must be 17 characters
        
        Args:
            vin: VIN string
            
        Returns:
            True if valid, False otherwise
        """
        if not vin:
            return True  # VIN is optional
        return len(vin) == 17 and vin.isalnum()

    @staticmethod
    def validate_year(year: int) -> bool:
        """
        Validate model year
        Year must be between 1900 and current year + 1
        
        Args:
            year: Model year
            
        Returns:
            True if valid, False otherwise
        """
        current_year = datetime.now().year
        return 1900 <= year <= current_year + 1

    @staticmethod
    def validate_horsepower(hp: int) -> bool:
        """
        Validate horsepower
        Must be positive number
        
        Args:
            hp: Horsepower value
            
        Returns:
            True if valid, False otherwise
        """
        return hp > 0

    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Validate price
        Must be positive number
        
        Args:
            price: Price value
            
        Returns:
            True if valid, False otherwise
        """
        return price >= 0

    @classmethod
    def validate_car_data(cls, car_data: dict) -> bool:
        """
        Validate complete car data dictionary
        
        Args:
            car_data: Dictionary containing car data
            
        Returns:
            True if all data is valid, False otherwise
        """
        errors = []

        # Validate year
        if 'year' in car_data:
            if not cls.validate_year(car_data['year']):
                errors.append(f"Invalid year: {car_data['year']}")

        # Validate horsepower
        if 'horsepower' in car_data and car_data['horsepower']:
            if not cls.validate_horsepower(car_data['horsepower']):
                errors.append(f"Invalid horsepower: {car_data['horsepower']}")

        # Validate VIN
        if 'vin' in car_data and car_data['vin']:
            if not cls.validate_vin(car_data['vin']):
                errors.append(f"Invalid VIN: {car_data['vin']}")

        if errors:
            logger.warning(f"Validation errors: {', '.join(errors)}")
            return False

        return True
