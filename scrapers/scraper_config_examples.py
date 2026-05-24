"""
Scraper Configuration Examples - Pre-built configs for common websites
"""

# Example 1: Simple HTML Car Listing Site
SIMPLE_CAR_SITE_CONFIG = {
    'url': 'https://example.com/cars',
    'car_selector': '.car-item',
    'field_mapping': {
        'make': '.car-make',
        'model': '.car-model',
        'year': '.car-year',
        'price': '.car-price',
        'mileage': '.car-mileage',
        'color': '.car-color',
    },
    'requires_js': False,
    'requires_login': False,
    'paginated': False,
}

# Example 2: Paginated Car Site
PAGINATED_CAR_SITE_CONFIG = {
    'url': 'https://example.com/cars?page=1',
    'car_selector': '.car-listing',
    'field_mapping': {
        'make': '.make',
        'model': '.model',
        'year': '.year',
        'price': '.price',
        'engine': '.engine',
        'horsepower': '.hp',
        'body_type': '.body',
    },
    'requires_js': False,
    'requires_login': False,
    'paginated': True,
    'next_page_selector': 'a.next-page',
    'max_pages': 10,
}

# Example 3: JavaScript-Heavy Site (Requires Dicloak)
JAVASCRIPT_HEAVY_SITE_CONFIG = {
    'url': 'https://example.com/dynamic-cars',
    'car_selector': '[data-car-id]',
    'field_mapping': {
        'make': '[data-make]',
        'model': '[data-model]',
        'year': '[data-year]',
        'price': '.dynamic-price',
        'image': 'img.car-image',
    },
    'requires_js': True,
    'requires_login': False,
    'paginated': True,
    'next_button_selector': 'button.load-more',
    'max_pages': 5,
    'profile_name': 'scraper_js_profile',
}

# Example 4: Site with Login (Requires Dicloak)
LOGIN_REQUIRED_SITE_CONFIG = {
    'url': 'https://example.com/dealers/inventory',
    'car_selector': '.inventory-item',
    'field_mapping': {
        'vin': '.vin',
        'make': '.make',
        'model': '.model',
        'year': '.year',
        'price': '.price',
        'mileage': '.mileage',
        'specifications': '.specs-dropdown',
    },
    'requires_js': True,
    'requires_login': True,
    'login_script': """
        document.getElementById('username').value = 'YOUR_USERNAME';
        document.getElementById('password').value = 'YOUR_PASSWORD';
        document.getElementById('login-btn').click();
    """,
    'paginated': True,
    'next_page_selector': 'a[rel="next"]',
    'max_pages': 20,
    'profile_name': 'scraper_login_profile',
}

# Example 5: API-Based Car Service
API_BASED_CONFIG = {
    'url': 'https://api.example.com/cars',
    'api_method': 'GET',
    'api_params': {
        'limit': 100,
        'offset': 0,
    },
    'is_api': True,
    'requires_pagination': True,
    'pagination_key': 'offset',
    'pagination_increment': 100,
}


def create_custom_config(url: str, car_selector: str, field_mapping: dict,
                       requires_js: bool = False, requires_login: bool = False,
                       paginated: bool = False, **kwargs):
    """
    Create a custom scraper configuration
    
    Args:
        url: Website URL to scrape
        car_selector: CSS selector for car elements
        field_mapping: Dictionary mapping field names to CSS selectors
        requires_js: If page requires JavaScript
        requires_login: If login is required
        paginated: If site is paginated
        **kwargs: Additional configuration options
        
    Returns:
        Configuration dictionary
    """
    config = {
        'url': url,
        'car_selector': car_selector,
        'field_mapping': field_mapping,
        'requires_js': requires_js,
        'requires_login': requires_login,
        'paginated': paginated,
    }
    
    # Add any additional parameters
    config.update(kwargs)
    
    return config
