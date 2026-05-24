"""
Python Web Scraper - Direct scraping with proxy support for Dicloak
"""

import logging
import json
import time
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import cloudscraper

logger = logging.getLogger(__name__)


class PythonWebScraper:
    """
    Direct web scraper using Python libraries with Dicloak proxy support.
    Suitable for APIs and static HTML scraping.
    """

    def __init__(self, dicloak_proxy: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """
        Initialize Python web scraper
        
        Args:
            dicloak_proxy: Dicloak proxy URL (e.g., 'http://proxy.dicloak:port')
            user_agent: Custom user agent string
        """
        self.dicloak_proxy = dicloak_proxy
        self.session = self._create_session(user_agent)
        self.scraped_data = []
        self.errors = []

    def _create_session(self, user_agent: Optional[str]) -> requests.Session:
        """
        Create a requests session with Dicloak proxy
        
        Args:
            user_agent: Optional custom user agent
            
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Set up proxy if provided
        if self.dicloak_proxy:
            proxies = {
                'http': self.dicloak_proxy,
                'https': self.dicloak_proxy,
            }
            session.proxies.update(proxies)
            logger.info(f"Configured proxy: {self.dicloak_proxy}")
        
        # Set user agent
        headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        session.headers.update(headers)
        
        return session

    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch a web page
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content or None
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            logger.info(f"Successfully fetched: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching {url}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return None

    def fetch_json_api(self, url: str, method: str = 'GET',
                       params: Optional[Dict] = None,
                       json_data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Fetch JSON from an API endpoint
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            json_data: JSON payload for POST requests
            
        Returns:
            Parsed JSON or None
        """
        try:
            logger.info(f"{method} {url}")
            
            if method.upper() == 'POST':
                response = self.session.post(
                    url,
                    params=params,
                    json=json_data,
                    timeout=10
                )
            else:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=10
                )
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched JSON from: {url}")
            return data
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching API {url}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return None

    def parse_html(self, html: str, car_selector: str,
                   mapping: Dict[str, str]) -> List[Dict]:
        """
        Parse HTML and extract car data
        
        Args:
            html: HTML content
            car_selector: CSS selector for car containers
            mapping: Dictionary mapping field names to CSS selectors
            
        Returns:
            List of car dictionaries
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            cars = []
            
            car_elements = soup.select(car_selector)
            logger.info(f"Found {len(car_elements)} car elements")
            
            for element in car_elements:
                car = {}
                for field_name, selector in mapping.items():
                    el = element.select_one(selector)
                    car[field_name] = el.get_text(strip=True) if el else None
                
                if any(car.values()):  # Only add if has some data
                    cars.append(car)
            
            self.scraped_data.extend(cars)
            logger.info(f"Parsed {len(cars)} cars")
            return cars
        except Exception as e:
            error_msg = f"Error parsing HTML: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return []

    def scrape_paginated_site(self, base_url: str, car_selector: str,
                              mapping: Dict[str, str],
                              next_page_selector: str,
                              max_pages: int = 10) -> List[Dict]:
        """
        Scrape paginated website
        
        Args:
            base_url: Starting URL
            car_selector: CSS selector for car elements
            mapping: Field mapping dictionary
            next_page_selector: CSS selector for next page link
            max_pages: Maximum pages to scrape
            
        Returns:
            List of all scraped cars
        """
        all_cars = []
        current_url = base_url
        page_count = 0
        
        while page_count < max_pages and current_url:
            logger.info(f"Scraping page {page_count + 1}: {current_url}")
            
            # Fetch page
            html = self.fetch_page(current_url)
            if not html:
                break
            
            # Parse cars
            cars = self.parse_html(html, car_selector, mapping)
            all_cars.extend(cars)
            
            # Find next page
            soup = BeautifulSoup(html, 'html.parser')
            next_link = soup.select_one(next_page_selector)
            
            if next_link:
                href = next_link.get('href')
                if href:
                    # Handle relative URLs
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        current_url = urljoin(base_url, href)
                    elif href.startswith('http'):
                        current_url = href
                    else:
                        current_url = base_url + href
                else:
                    break
            else:
                break
            
            page_count += 1
            time.sleep(2)  # Respectful delay
        
        logger.info(f"Completed scraping {page_count} pages with {len(all_cars)} cars")
        return all_cars

    def scrape_with_cloudscraper(self, url: str) -> Optional[str]:
        """
        Scrape using cloudscraper (handles Cloudflare protection)
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None
        """
        try:
            logger.info(f"Scraping with cloudscraper: {url}")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully scraped: {url}")
            return response.text
        except Exception as e:
            error_msg = f"Error with cloudscraper: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return None

    def save_scraped_data(self, filepath: str) -> bool:
        """
        Save scraped data to JSON file
        
        Args:
            filepath: Path to save JSON file
            
        Returns:
            True if successful
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_records': len(self.scraped_data),
                    'errors': len(self.errors),
                    'data': self.scraped_data,
                    'error_log': self.errors
                }, f, indent=2)
            logger.info(f"Saved {len(self.scraped_data)} cars to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False

    def close(self):
        """
        Clean up resources
        """
        self.session.close()
        logger.info("Scraper session closed")
