"""
Dicloak RPA Scraper - Automate scraping through Dicloak anti-detect browser
"""

import logging
import json
import time
from typing import List, Optional, Dict
from datetime import datetime
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class DicloakRPAScraper:
    """
    Use Dicloak's built-in RPA (Robotic Process Automation) to scrape websites.
    This approach uses Dicloak's browser automation features.
    """

    def __init__(self, dicloak_api_url: str = "http://localhost:8080",
                 dicloak_api_key: Optional[str] = None):
        """
        Initialize Dicloak RPA scraper
        
        Args:
            dicloak_api_url: Dicloak local API endpoint
            dicloak_api_key: API key if required
        """
        self.dicloak_api_url = dicloak_api_url
        self.dicloak_api_key = dicloak_api_key
        self.session_id = None
        self.scraped_data = []

    def connect(self) -> bool:
        """
        Connect to Dicloak API
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(
                f"{self.dicloak_api_url}/health",
                timeout=10
            )
            if response.status_code == 200:
                logger.info("Connected to Dicloak API")
                return True
            else:
                logger.error(f"Dicloak connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Dicloak: {e}")
            logger.info("Make sure Dicloak is running at: http://localhost:8080")
            return False

    def create_browser_session(self, profile_name: str = "scraper_profile") -> Optional[str]:
        """
        Create a new Dicloak browser session
        
        Args:
            profile_name: Name of the Dicloak profile to use
            
        Returns:
            Session ID or None
        """
        try:
            payload = {
                "profile_name": profile_name,
                "headless": False,  # Set to True for headless mode
                "proxy_type": "http",
                "anti_detect": True
            }
            
            response = requests.post(
                f"{self.dicloak_api_url}/sessions",
                json=payload,
                headers={"X-API-Key": self.dicloak_api_key} if self.dicloak_api_key else {},
                timeout=30
            )
            
            if response.status_code == 200:
                session_data = response.json()
                self.session_id = session_data.get('session_id')
                logger.info(f"Created browser session: {self.session_id}")
                return self.session_id
            else:
                logger.error(f"Failed to create session: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error creating browser session: {e}")
            return None

    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to a URL in the Dicloak browser
        
        Args:
            url: Website URL to navigate to
            
        Returns:
            True if successful
        """
        if not self.session_id:
            logger.error("No active session")
            return False
        
        try:
            payload = {"url": url}
            response = requests.post(
                f"{self.dicloak_api_url}/sessions/{self.session_id}/navigate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Navigated to: {url}")
                time.sleep(3)  # Wait for page to load
                return True
            else:
                logger.error(f"Navigation failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error navigating: {e}")
            return False

    def execute_script(self, script: str) -> Optional[str]:
        """
        Execute JavaScript in the Dicloak browser
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script result or None
        """
        if not self.session_id:
            logger.error("No active session")
            return None
        
        try:
            payload = {"script": script}
            response = requests.post(
                f"{self.dicloak_api_url}/sessions/{self.session_id}/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('result')
                logger.info(f"Script executed successfully")
                return result
            else:
                logger.error(f"Script execution failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return None

    def click_element(self, selector: str) -> bool:
        """
        Click an element on the page
        
        Args:
            selector: CSS selector of element to click
            
        Returns:
            True if successful
        """
        script = f"document.querySelector('{selector}').click();"
        result = self.execute_script(script)
        return result is not None

    def fill_form(self, selector: str, value: str) -> bool:
        """
        Fill a form input
        
        Args:
            selector: CSS selector of input
            value: Value to fill
            
        Returns:
            True if successful
        """
        script = f"document.querySelector('{selector}').value = '{value}';"
        result = self.execute_script(script)
        return result is not None

    def extract_html(self) -> Optional[str]:
        """
        Extract the current page HTML
        
        Returns:
            HTML content or None
        """
        script = "document.documentElement.outerHTML"
        return self.execute_script(script)

    def scroll_to_bottom(self, pause_time: float = 2) -> bool:
        """
        Scroll to bottom of page
        
        Args:
            pause_time: Time to wait between scrolls
            
        Returns:
            True if successful
        """
        script = "window.scrollTo(0, document.body.scrollHeight);"
        result = self.execute_script(script)
        if result:
            time.sleep(pause_time)
            return True
        return False

    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        Wait for an element to appear on the page
        
        Args:
            selector: CSS selector to wait for
            timeout: Maximum wait time in seconds
            
        Returns:
            True if element appears
        """
        script = f"""
        let start = Date.now();
        while (!document.querySelector('{selector}') && Date.now() - start < {timeout * 1000}) {{
            // Wait
        }}
        return !!document.querySelector('{selector}');
        """
        result = self.execute_script(script)
        return result is True

    def scrape_cars(self, selector: str, mapping: Dict[str, str]) -> List[Dict]:
        """
        Scrape car data from page elements
        
        Args:
            selector: CSS selector for car containers
            mapping: Dictionary mapping field names to CSS selectors
                    Example: {"make": ".car-make", "model": ".car-model"}
            
        Returns:
            List of car dictionaries
        """
        try:
            # Build script to extract data
            mapping_json = json.dumps(mapping)
            script = f"""
            let cars = [];
            document.querySelectorAll('{selector}').forEach(element => {{
                let car = {{}};
                const mapping = {mapping_json};
                for (const [key, selector] of Object.entries(mapping)) {{
                    const el = element.querySelector(selector);
                    car[key] = el ? el.textContent.trim() : null;
                }}
                cars.push(car);
            }});
            cars
            """
            
            result = self.execute_script(script)
            if result:
                self.scraped_data.extend(result)
                logger.info(f"Scraped {len(result)} cars")
                return result
            return []
        except Exception as e:
            logger.error(f"Error scraping cars: {e}")
            return []

    def close_session(self) -> bool:
        """
        Close the browser session
        
        Returns:
            True if successful
        """
        if not self.session_id:
            return True
        
        try:
            response = requests.delete(
                f"{self.dicloak_api_url}/sessions/{self.session_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Closed session: {self.session_id}")
                self.session_id = None
                return True
            return False
        except Exception as e:
            logger.error(f"Error closing session: {e}")
            return False

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
                json.dump(self.scraped_data, f, indent=2)
            logger.info(f"Saved {len(self.scraped_data)} cars to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
