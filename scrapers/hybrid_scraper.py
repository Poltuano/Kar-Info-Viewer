"""
Hybrid Scraper - Combines Python scraping with Dicloak RPA for best results
"""

import logging
import json
import time
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from enum import Enum

from scrapers.python_web_scraper import PythonWebScraper
from scrapers.dicloak_rpa_scraper import DicloakRPAScraper
from utils.storage_manager import DataStorageManager

logger = logging.getLogger(__name__)


class ScraperMode(Enum):
    """Scraper mode selection"""
    PYTHON_ONLY = "python_only"
    DICLOAK_ONLY = "dicloak_only"
    HYBRID = "hybrid"


class HybridScraper:
    """
    Hybrid scraper that intelligently switches between Python scraper and Dicloak RPA
    based on page characteristics and requirements.
    """

    def __init__(self, dicloak_api_url: str = "http://localhost:8080",
                 dicloak_proxy: Optional[str] = None,
                 storage_manager: Optional[DataStorageManager] = None,
                 mode: ScraperMode = ScraperMode.HYBRID):
        """
        Initialize hybrid scraper
        
        Args:
            dicloak_api_url: Dicloak API endpoint
            dicloak_proxy: Dicloak proxy URL
            storage_manager: Storage manager for saving data
            mode: Scraper mode (PYTHON_ONLY, DICLOAK_ONLY, or HYBRID)
        """
        self.dicloak_api_url = dicloak_api_url
        self.dicloak_proxy = dicloak_proxy
        self.storage_manager = storage_manager
        self.mode = mode
        
        self.python_scraper = PythonWebScraper(dicloak_proxy=dicloak_proxy)
        self.dicloak_scraper = DicloakRPAScraper(dicloak_api_url=dicloak_api_url)
        
        self.scrape_stats = {
            'total_cars': 0,
            'total_errors': 0,
            'python_cars': 0,
            'dicloak_cars': 0,
            'start_time': None,
            'end_time': None
        }

    def test_dicloak_connection(self) -> bool:
        """
        Test if Dicloak is available
        
        Returns:
            True if Dicloak is available
        """
        logger.info("Testing Dicloak connection...")
        if self.dicloak_scraper.connect():
            logger.info("✓ Dicloak is available")
            return True
        else:
            logger.warning("✗ Dicloak is not available")
            return False

    def scrape_website(self, config: Dict) -> List[Dict]:
        """
        Scrape a website using optimal strategy
        
        Args:
            config: Scraping configuration with:
                - url: Website URL
                - car_selector: CSS selector for car elements
                - field_mapping: Dictionary mapping field names to selectors
                - requires_js: If page requires JavaScript execution
                - requires_login: If login is required
                - paginated: If site is paginated
                - next_page_selector: CSS selector for next page link
                
        Returns:
            List of scraped car dictionaries
        """
        self.scrape_stats['start_time'] = datetime.now().isoformat()
        all_cars = []
        
        try:
            requires_js = config.get('requires_js', False)
            requires_login = config.get('requires_login', False)
            dicloak_available = self.test_dicloak_connection()
            
            # Decide which scraper to use
            if self.mode == ScraperMode.PYTHON_ONLY:
                logger.info("Using Python scraper only")
                all_cars = self._scrape_with_python(config)
            
            elif self.mode == ScraperMode.DICLOAK_ONLY:
                if dicloak_available:
                    logger.info("Using Dicloak RPA only")
                    all_cars = self._scrape_with_dicloak(config)
                else:
                    logger.error("Dicloak not available, falling back to Python scraper")
                    all_cars = self._scrape_with_python(config)
            
            elif self.mode == ScraperMode.HYBRID:
                if requires_js or requires_login:
                    # Use Dicloak for complex interactions
                    if dicloak_available:
                        logger.info("Page requires JS/login, using Dicloak RPA")
                        all_cars = self._scrape_with_dicloak(config)
                    else:
                        logger.warning("Dicloak not available, trying Python scraper")
                        all_cars = self._scrape_with_python(config)
                else:
                    # Use Python scraper for simple HTML scraping
                    logger.info("Using Python scraper for simple HTML")
                    all_cars = self._scrape_with_python(config)
            
            # Save to storage if available
            if self.storage_manager and all_cars:
                self._save_to_storage(all_cars)
            
            self.scrape_stats['total_cars'] = len(all_cars)
            self.scrape_stats['end_time'] = datetime.now().isoformat()
            
            return all_cars
        
        except Exception as e:
            logger.error(f"Error in hybrid scraper: {e}")
            self.scrape_stats['total_errors'] += 1
            return all_cars

    def _scrape_with_python(self, config: Dict) -> List[Dict]:
        """
        Scrape using Python scraper
        """
        try:
            url = config.get('url')
            car_selector = config.get('car_selector')
            field_mapping = config.get('field_mapping')
            is_paginated = config.get('paginated', False)
            next_page_selector = config.get('next_page_selector')
            max_pages = config.get('max_pages', 10)
            
            if is_paginated and next_page_selector:
                cars = self.python_scraper.scrape_paginated_site(
                    url, car_selector, field_mapping,
                    next_page_selector, max_pages
                )
            else:
                html = self.python_scraper.fetch_page(url)
                if html:
                    cars = self.python_scraper.parse_html(
                        html, car_selector, field_mapping
                    )
                else:
                    cars = []
            
            self.scrape_stats['python_cars'] = len(cars)
            return cars
        
        except Exception as e:
            logger.error(f"Error in Python scraper: {e}")
            return []

    def _scrape_with_dicloak(self, config: Dict) -> List[Dict]:
        """
        Scrape using Dicloak RPA
        """
        try:
            url = config.get('url')
            car_selector = config.get('car_selector')
            field_mapping = config.get('field_mapping')
            profile_name = config.get('profile_name', 'scraper_profile')
            
            # Create session
            if not self.dicloak_scraper.create_browser_session(profile_name):
                logger.error("Failed to create Dicloak session")
                return []
            
            # Navigate to URL
            if not self.dicloak_scraper.navigate_to_url(url):
                logger.error("Failed to navigate to URL")
                self.dicloak_scraper.close_session()
                return []
            
            # Handle login if needed
            login_script = config.get('login_script')
            if login_script:
                logger.info("Executing login script")
                self.dicloak_scraper.execute_script(login_script)
                time.sleep(5)
            
            # Scroll and load more content if needed
            is_paginated = config.get('paginated', False)
            max_pages = config.get('max_pages', 1)
            
            all_cars = []
            
            for page in range(max_pages):
                logger.info(f"Scraping page {page + 1}")
                
                # Wait for elements to load
                self.dicloak_scraper.wait_for_element(car_selector, timeout=10)
                
                # Scroll to bottom to load more
                if page > 0:
                    self.dicloak_scraper.scroll_to_bottom(pause_time=3)
                
                # Extract cars
                cars = self.dicloak_scraper.scrape_cars(car_selector, field_mapping)
                all_cars.extend(cars)
                
                # Click next page if available
                if is_paginated and page < max_pages - 1:
                    next_button = config.get('next_button_selector')
                    if next_button:
                        if not self.dicloak_scraper.click_element(next_button):
                            logger.info("No more pages available")
                            break
                        time.sleep(3)  # Wait for page load
            
            self.dicloak_scraper.close_session()
            self.scrape_stats['dicloak_cars'] = len(all_cars)
            return all_cars
        
        except Exception as e:
            logger.error(f"Error in Dicloak scraper: {e}")
            self.dicloak_scraper.close_session()
            return []

    def _save_to_storage(self, cars: List[Dict]) -> bool:
        """
        Save scraped cars to local storage
        """
        try:
            for car in cars:
                car_id = self.storage_manager.add_car(car)
                
                # Add specifications if available
                specs_keys = ['engine_type', 'horsepower', 'torque', 'transmission',
                             'acceleration_0_100', 'top_speed', 'fuel_consumption_combined',
                             'fuel_type', 'fuel_tank_capacity', 'cargo_capacity',
                             'passenger_seats', 'dimensions_length', 'dimensions_width',
                             'dimensions_height', 'weight', 'wheelbase']
                
                specs = {k: v for k, v in car.items() if k in specs_keys}
                if any(specs.values()):
                    self.storage_manager.add_specifications(car_id, specs)
            
            logger.info(f"Saved {len(cars)} cars to storage")
            return True
        except Exception as e:
            logger.error(f"Error saving to storage: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get scraping statistics
        
        Returns:
            Dictionary with stats
        """
        return self.scrape_stats

    def close(self):
        """
        Clean up resources
        """
        self.python_scraper.close()
        logger.info("Scraper closed")
