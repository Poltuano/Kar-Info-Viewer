"""
Scraper Usage Examples - How to use all three scrapers
"""

import logging
from scrapers.python_web_scraper import PythonWebScraper
from scrapers.dicloak_rpa_scraper import DicloakRPAScraper
from scrapers.hybrid_scraper import HybridScraper, ScraperMode
from scrapers.scraper_config_examples import (
    SIMPLE_CAR_SITE_CONFIG,
    PAGINATED_CAR_SITE_CONFIG,
    JAVASCRIPT_HEAVY_SITE_CONFIG,
    LOGIN_REQUIRED_SITE_CONFIG,
    create_custom_config
)
from scrapers.data_importer import DataImporter
from utils.storage_manager import DataStorageManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Simple Python Web Scraper
def example_python_scraper():
    """
    Example: Scrape a simple HTML car listing site
    """
    logger.info("\n=== Example 1: Python Web Scraper ===")
    
    scraper = PythonWebScraper()
    
    # Fetch and parse a website
    config = SIMPLE_CAR_SITE_CONFIG
    html = scraper.fetch_page(config['url'])
    
    if html:
        cars = scraper.parse_html(
            html,
            config['car_selector'],
            config['field_mapping']
        )
        
        logger.info(f"Found {len(cars)} cars")
        
        # Save results
        scraper.save_scraped_data('data/scraped/python_scraper_results.json')
    
    scraper.close()


# Example 2: Python Scraper with Pagination
def example_python_paginated_scraper():
    """
    Example: Scrape a paginated website
    """
    logger.info("\n=== Example 2: Python Paginated Scraper ===")
    
    scraper = PythonWebScraper()
    
    config = PAGINATED_CAR_SITE_CONFIG
    cars = scraper.scrape_paginated_site(
        config['url'],
        config['car_selector'],
        config['field_mapping'],
        config['next_page_selector'],
        config.get('max_pages', 5)
    )
    
    logger.info(f"Total cars scraped: {len(cars)}")
    scraper.save_scraped_data('data/scraped/paginated_results.json')
    scraper.close()


# Example 3: Dicloak RPA Scraper
def example_dicloak_rpa_scraper():
    """
    Example: Use Dicloak RPA for JavaScript-heavy sites
    """
    logger.info("\n=== Example 3: Dicloak RPA Scraper ===")
    
    scraper = DicloakRPAScraper()
    
    # Connect to Dicloak
    if not scraper.connect():
        logger.error("Failed to connect to Dicloak. Make sure it's running at http://localhost:8080")
        return
    
    # Create browser session
    if not scraper.create_browser_session():
        logger.error("Failed to create Dicloak session")
        return
    
    config = JAVASCRIPT_HEAVY_SITE_CONFIG
    
    # Navigate to website
    if scraper.navigate_to_url(config['url']):
        # Wait for elements to load
        scraper.wait_for_element(config['car_selector'])
        
        # Scrape cars
        cars = scraper.scrape_cars(
            config['car_selector'],
            config['field_mapping']
        )
        
        logger.info(f"Scraped {len(cars)} cars from Dicloak")
        scraper.save_scraped_data('data/scraped/dicloak_rpa_results.json')
    
    # Close session
    scraper.close_session()


# Example 4: Dicloak RPA with Login
def example_dicloak_with_login():
    """
    Example: Use Dicloak RPA to handle login
    """
    logger.info("\n=== Example 4: Dicloak with Login ===")
    
    scraper = DicloakRPAScraper()
    
    if not scraper.connect():
        return
    
    if not scraper.create_browser_session():
        return
    
    config = LOGIN_REQUIRED_SITE_CONFIG
    
    # Navigate
    if scraper.navigate_to_url(config['url']):
        # Execute login script
        if config.get('login_script'):
            logger.info("Executing login...")
            scraper.execute_script(config['login_script'])
            import time
            time.sleep(5)  # Wait for login to complete
        
        # Wait for page to load
        scraper.wait_for_element(config['car_selector'])
        
        # Scrape
        cars = scraper.scrape_cars(
            config['car_selector'],
            config['field_mapping']
        )
        
        logger.info(f"Scraped {len(cars)} cars after login")
        scraper.save_scraped_data('data/scraped/login_results.json')
    
    scraper.close_session()


# Example 5: Hybrid Scraper (Best for most use cases)
def example_hybrid_scraper():
    """
    Example: Use hybrid scraper with automatic strategy selection
    """
    logger.info("\n=== Example 5: Hybrid Scraper ===")
    
    # Initialize storage manager
    storage = DataStorageManager('data/storage')
    
    # Create hybrid scraper
    scraper = HybridScraper(
        storage_manager=storage,
        mode=ScraperMode.HYBRID  # Automatically chooses best method
    )
    
    # Define your scraping config
    config = create_custom_config(
        url='https://example.com/cars',
        car_selector='.car-item',
        field_mapping={
            'make': '.make',
            'model': '.model',
            'year': '.year',
            'price': '.price',
            'horsepower': '.hp',
            'torque': '.torque',
        },
        requires_js=False,
        requires_login=False,
        paginated=True,
        next_page_selector='a.next',
        max_pages=5
    )
    
    # Scrape
    cars = scraper.scrape_website(config)
    
    # Get statistics
    stats = scraper.get_statistics()
    logger.info(f"Scraping Statistics: {stats}")
    
    scraper.close()


# Example 6: Hybrid Scraper with Python Fallback
def example_hybrid_with_fallback():
    """
    Example: Hybrid scraper that falls back to Python if Dicloak is unavailable
    """
    logger.info("\n=== Example 6: Hybrid with Fallback ===")
    
    storage = DataStorageManager('data/storage')
    
    scraper = HybridScraper(
        storage_manager=storage,
        mode=ScraperMode.HYBRID
    )
    
    # This config requires JS, but will fallback to Python if Dicloak isn't running
    config = create_custom_config(
        url='https://example.com/dynamic-cars',
        car_selector='[data-car]',
        field_mapping={
            'make': '[data-make]',
            'model': '[data-model]',
            'year': '[data-year]',
        },
        requires_js=True,
        paginated=False
    )
    
    cars = scraper.scrape_website(config)
    logger.info(f"Scraped {len(cars)} cars (with fallback)")


# Example 7: Import Scraped Data
def example_import_data():
    """
    Example: Import scraped data into local storage
    """
    logger.info("\n=== Example 7: Import Data ===")
    
    storage = DataStorageManager('data/storage')
    importer = DataImporter(storage)
    
    # Import from JSON
    importer.import_from_json('data/scraped/hybrid_results.json')
    
    # Import from CSV
    importer.import_from_csv('data/cars.csv')
    
    # Get statistics
    stats = importer.get_import_stats()
    logger.info(f"Import Statistics: {stats}")
    
    # Export to JSON
    importer.export_cars_to_json(
        'data/exported/all_cars.json',
        filters={'make': 'Toyota'}
    )


if __name__ == '__main__':
    # Run examples (uncomment to test)
    
    # example_python_scraper()
    # example_python_paginated_scraper()
    # example_dicloak_rpa_scraper()
    # example_dicloak_with_login()
    
    # The hybrid scraper is recommended for most use cases
    example_hybrid_scraper()
    
    # Import and organize data
    # example_import_data()
    
    logger.info("\n=== Examples completed ===")
