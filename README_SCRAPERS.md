# Web Scrapers for Kar-Info-Viewer

Comprehensive web scraping solution with three integrated approaches for extracting car data from your website and organizing it into your 2TB SSD storage.

## 🎯 Three Scraper Approaches

### 1. **Python Web Scraper** (`python_web_scraper.py`)
Direct scraping using Python libraries with Dicloak proxy support.

**Best for:**
- Simple HTML websites
- API endpoints
- Paginated sites without JavaScript
- Fast, lightweight scraping

**Features:**
- Dicloak proxy integration
- HTML parsing with BeautifulSoup
- API JSON fetching
- Pagination support
- Cloudflare bypass with cloudscraper

```python
from scrapers.python_web_scraper import PythonWebScraper

scraper = PythonWebScraper(dicloak_proxy='http://proxy.dicloak:port')
html = scraper.fetch_page('https://example.com/cars')
cars = scraper.parse_html(html, '.car-item', {'make': '.make', 'model': '.model'})
scraper.save_scraped_data('results.json')
```

---

### 2. **Dicloak RPA Scraper** (`dicloak_rpa_scraper.py`)
Uses Dicloak's built-in Robotic Process Automation (RPA) features.

**Best for:**
- JavaScript-heavy websites
- Sites requiring login
- Complex interactions (clicking, form filling)
- Anti-detection requirements
- Multi-page workflows

**Features:**
- Browser session management
- JavaScript execution
- Element interaction (click, fill forms)
- Wait for elements to load
- Infinite scroll handling
- Screenshot/HTML extraction

```python
from scrapers.dicloak_rpa_scraper import DicloakRPAScraper

scraper = DicloakRPAScraper(dicloak_api_url='http://localhost:8080')
scraper.connect()
scraper.create_browser_session()
scraper.navigate_to_url('https://example.com/cars')
scra per.wait_for_element('.car-item')
cars = scraper.scrape_cars('.car-item', {'make': '.make', 'model': '.model'})
scraper.close_session()
```

---

### 3. **Hybrid Scraper** (`hybrid_scraper.py`) - **RECOMMENDED**
Intelligently combines Python and Dicloak scrapers for optimal performance.

**Best for:**
- Most real-world websites
- Mixed JavaScript and HTML sites
- Automatic fallback handling
- Production environments
- Maximum reliability

**Features:**
- Automatic strategy selection
- Python scraper fallback if Dicloak unavailable
- Direct storage integration
- Comprehensive statistics
- Error handling and recovery
- Unified interface

```python
from scrapers.hybrid_scraper import HybridScraper, ScraperMode
from utils.storage_manager import DataStorageManager

storage = DataStorageManager('data/storage')
scraper = HybridScraper(storage_manager=storage, mode=ScraperMode.HYBRID)

config = {
    'url': 'https://example.com/cars',
    'car_selector': '.car-item',
    'field_mapping': {'make': '.make', 'model': '.model'},
    'requires_js': False,
    'paginated': True,
    'next_page_selector': 'a.next'
}

cars = scraper.scrape_website(config)
stats = scraper.get_statistics()
```

---

## 📋 Configuration

Each scraper needs a configuration dictionary:

```python
config = {
    'url': 'https://example.com/cars',           # Starting URL
    'car_selector': '.car-item',                 # CSS selector for car containers
    'field_mapping': {                           # Map field names to selectors
        'make': '.make',
        'model': '.model',
        'year': '.year',
        'price': '.price',
    },
    'requires_js': False,                        # Does page need JavaScript?
    'requires_login': False,                     # Does site require login?
    'paginated': False,                          # Is site paginated?
    'next_page_selector': 'a.next',              # Selector for next page link
    'max_pages': 10,                             # Max pages to scrape
}
```

### Pre-built Configuration Examples

```python
from scrapers.scraper_config_examples import (
    SIMPLE_CAR_SITE_CONFIG,
    PAGINATED_CAR_SITE_CONFIG,
    JAVASCRIPT_HEAVY_SITE_CONFIG,
    LOGIN_REQUIRED_SITE_CONFIG,
    create_custom_config
)
```

---

## 🔌 Dicloak Integration

### Setup Dicloak

1. **Download Dicloak** from https://dicloak.com/
2. **Install and launch** Dicloak application
3. **Configure your proxy** in Dicloak:
   - Add proxy provider (Infatica, Bright Data, etc.)
   - Test proxy connection
4. **Local API** runs at `http://localhost:8080`

### Proxy Configuration

Add proxy details to Dicloak:
- **Host**: proxy.infatica.org (or your provider)
- **Port**: 8080
- **Username**: Your proxy credentials
- **Password**: Your proxy credentials

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install requests beautifulsoup4 cloudscraper

# For Selenium-based scraping (optional)
pip install selenium webdriver-manager
```

### Basic Usage

```python
from scrapers.hybrid_scraper import HybridScraper
from utils.storage_manager import DataStorageManager

# Initialize
storage = DataStorageManager('data/storage')
scraper = HybridScraper(storage_manager=storage)

# Define what to scrape
config = {
    'url': 'https://your-website.com/cars',
    'car_selector': '.car-listing',
    'field_mapping': {
        'make': '.car-make',
        'model': '.car-model',
        'year': '.car-year',
        'price': '.car-price',
    },
    'requires_js': False,
    'paginated': True,
    'next_page_selector': 'a.pagination-next',
    'max_pages': 50,
}

# Scrape
cars = scraper.scrape_website(config)

# Check statistics
stats = scraper.get_statistics()
print(f"Scraped {stats['total_cars']} cars")
```

---

## 📊 Data Import

### Import Scraped Data

```python
from scrapers.data_importer import DataImporter
from utils.storage_manager import DataStorageManager

storage = DataStorageManager('data/storage')
importer = DataImporter(storage)

# Import from JSON
importer.import_from_json('data/scraped_cars.json')

# Import from CSV
importer.import_from_csv('data/cars.csv')

# Get stats
stats = importer.get_import_stats()
print(f"Imported: {stats['total_imported']}, Failed: {stats['total_failed']}")
```

### Export Data

```python
# Export cars to JSON
importer.export_cars_to_json(
    'data/exported/all_cars.json',
    filters={'make': 'Toyota'}
)
```

---

## 🔍 Advanced Examples

### Example 1: Scrape with Pagination

```python
from scrapers.python_web_scraper import PythonWebScraper

scraper = PythonWebScraper()

cars = scraper.scrape_paginated_site(
    base_url='https://example.com/cars?page=1',
    car_selector='.car-item',
    mapping={'make': '.make', 'model': '.model'},
    next_page_selector='a.next-page',
    max_pages=20
)

scraper.save_scraped_data('results.json')
```

### Example 2: Handle JavaScript-Heavy Site

```python
from scrapers.dicloak_rpa_scraper import DicloakRPAScraper

scraper = DicloakRPAScraper()
scraper.connect()
scraper.create_browser_session('my_profile')

# Navigate
scraper.navigate_to_url('https://example.com/cars')

# Wait for JavaScript to render
scraper.wait_for_element('.car-item', timeout=10)

# Scroll to load more
for i in range(5):
    scraper.scroll_to_bottom(pause_time=2)

# Extract
cars = scraper.scrape_cars('.car-item', {'make': '.make', 'model': '.model'})
scraper.close_session()
```

### Example 3: Site with Login

```python
from scrapers.hybrid_scraper import HybridScraper

scraper = HybridScraper()

config = {
    'url': 'https://dealer.example.com/inventory',
    'car_selector': '.vehicle',
    'field_mapping': {'vin': '.vin', 'make': '.make'},
    'requires_login': True,
    'login_script': """
        document.getElementById('email').value = 'your@email.com';
        document.getElementById('password').value = 'password';
        document.getElementById('login-btn').click();
    """,
    'max_pages': 10,
}

cars = scraper.scrape_website(config)
```

### Example 4: API-Based Scraping

```python
from scrapers.python_web_scraper import PythonWebScraper

scraper = PythonWebScraper()

# Scrape API endpoint
api_data = scraper.fetch_json_api(
    'https://api.example.com/v1/cars',
    method='GET',
    params={'limit': 100, 'offset': 0}
)

# Process API response
if api_data and 'cars' in api_data:
    cars = api_data['cars']
    # Now import into storage
```

---

## 🛡️ Dicloak Usage Tips

1. **Use Residential Proxies** - Best for avoiding bans
   - Infatica, Bright Data, MarsProxies, Massive

2. **Rotate Proxies** - Dicloak has built-in rotation
   - Create multiple profiles with different proxies

3. **Set User Agents** - Appear as different browsers
   - Dicloak automatically handles this

4. **Handle Cookies** - Dicloak persists cookies per profile
   - Useful for maintaining logged-in state

5. **Monitor Connection** - Check proxy health
   - Use Dicloak's proxy checker

---

## 📈 Storage & Organization

All scraped data is automatically organized:

```
data/storage/
├── cars.db              # SQLite database
├── cache/               # Search cache
├── images/
│   ├── thumbnails/      # Car images (preview)
│   ├── full/            # Car images (full-res)
│   └── diagrams/        # Car diagrams
└── logs/                # Application logs
```

**Storage Statistics:**
```python
stats = storage.get_storage_stats()
print(f"Total cars: {stats['total_cars']}")
print(f"Database size: {stats['database_size_mb']}MB")
print(f"Images: {stats['images_size_gb']}GB")
print(f"Total storage: {stats['total_storage_gb']}GB")
```

---

## ❌ Troubleshooting

### Dicloak Connection Failed
```
Error: Failed to connect to Dicloak
```
**Solution:** Make sure Dicloak is running at `http://localhost:8080`

### Proxy Connection Failed
```
Error: Proxy connection failed
```
**Solution:** 
- Check proxy credentials
- Verify proxy is working outside Dicloak
- Try different proxy provider

### JavaScript Not Rendering
```
No elements found
```
**Solution:** Increase wait time or use Dicloak RPA

### Import Failed - Validation Error
```
Validation errors: Invalid year
```
**Solution:** Check data format matches field requirements

---

## 📚 Documentation

- **Dicloak Docs:** https://dicloak.com/
- **BeautifulSoup:** https://www.crummy.com/software/BeautifulSoup/
- **Requests:** https://requests.readthedocs.io/
- **Proxy Providers:** Infatica, Bright Data, MarsProxies

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Download and setup Dicloak
3. ✅ Configure proxy in Dicloak
4. ✅ Define scraper configuration for your website
5. ✅ Test with hybrid scraper first
6. ✅ Monitor and adjust as needed
7. ✅ Schedule regular scraping jobs

---

**Ready to scrape your car database? Start with the hybrid scraper!**
