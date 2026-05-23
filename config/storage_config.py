"""
Storage Configuration - Configure 2TB SSD storage paths
"""

import os
import platform
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect operating system
SYSTEM = platform.system()

# Storage paths based on OS and mounted SSD
if SYSTEM == "Windows":
    # Windows storage paths (example: D:/, E:/, etc.)
    SSD_MOUNT_POINT = os.getenv('SSD_MOUNT_POINT', 'D:\\')
elif SYSTEM == "Darwin":
    # macOS storage paths (example: /Volumes/ExternalSSD)
    SSD_MOUNT_POINT = os.getenv('SSD_MOUNT_POINT', '/Volumes/ExternalSSD')
else:
    # Linux storage paths (example: /mnt/ssd or /media/username/SSD)
    SSD_MOUNT_POINT = os.getenv('SSD_MOUNT_POINT', '/mnt/ssd')

# Base storage directory on SSD
BASE_STORAGE_PATH = Path(SSD_MOUNT_POINT) / "Kar-Info-Viewer"

# Storage structure
STORAGE_PATHS = {
    'base': BASE_STORAGE_PATH,
    'database': BASE_STORAGE_PATH / 'database',
    'images': BASE_STORAGE_PATH / 'images',
    'images_full': BASE_STORAGE_PATH / 'images' / 'full',
    'images_thumbnails': BASE_STORAGE_PATH / 'images' / 'thumbnails',
    'images_diagrams': BASE_STORAGE_PATH / 'images' / 'diagrams',
    'cache': BASE_STORAGE_PATH / 'cache',
    'backups': BASE_STORAGE_PATH / 'backups',
    'exports': BASE_STORAGE_PATH / 'exports',
    'logs': BASE_STORAGE_PATH / 'logs',
    'temp': BASE_STORAGE_PATH / 'temp',
}

# Database file paths
DATABASE_PATHS = {
    'local_db': STORAGE_PATHS['database'] / 'cars.db',
    'cache_db': STORAGE_PATHS['cache'] / 'cache.db',
    'backup_db': STORAGE_PATHS['backups'] / 'cars_backup.db',
}

# Image storage settings
IMAGE_STORAGE_CONFIG = {
    'full_size_path': STORAGE_PATHS['images_full'],
    'thumbnail_size_path': STORAGE_PATHS['images_thumbnails'],
    'diagram_path': STORAGE_PATHS['images_diagrams'],
    'max_original_size': 50 * 1024 * 1024,  # 50MB for original images
    'thumbnail_dimensions': (200, 150),
    'thumbnail_quality': 85,
    'supported_formats': ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'),
}

# Cache settings
CACHE_CONFIG = {
    'cache_dir': STORAGE_PATHS['cache'],
    'max_cache_size': 100 * 1024 * 1024 * 1024,  # 100GB max cache
    'cache_ttl': 3600 * 24 * 7,  # 7 days default
    'enabled': True,
}

# Backup settings
BACKUP_CONFIG = {
    'backup_dir': STORAGE_PATHS['backups'],
    'auto_backup': True,
    'backup_interval': 3600 * 24,  # Daily backups
    'max_backups': 10,
    'backup_compression': True,
}

# Export settings
EXPORT_CONFIG = {
    'export_dir': STORAGE_PATHS['exports'],
    'export_formats': ['csv', 'json', 'pdf', 'xlsx'],
    'max_export_size': 500 * 1024 * 1024,  # 500MB
}

# Logging settings
LOG_CONFIG = {
    'log_dir': STORAGE_PATHS['logs'],
    'max_log_size': 10 * 1024 * 1024,  # 10MB per log file
    'backup_count': 5,
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
}

# Storage quotas (2TB total)
STORAGE_QUOTAS = {
    'database': 100 * 1024 * 1024 * 1024,  # 100GB for databases
    'images': 1200 * 1024 * 1024 * 1024,  # 1.2TB for images
    'cache': 300 * 1024 * 1024 * 1024,  # 300GB for cache
    'backups': 200 * 1024 * 1024 * 1024,  # 200GB for backups
    'exports': 50 * 1024 * 1024 * 1024,  # 50GB for exports
    'logs': 50 * 1024 * 1024 * 1024,  # 50GB for logs
}

def get_storage_path(path_key: str) -> Path:
    """
    Get storage path by key
    
    Args:
        path_key: Key from STORAGE_PATHS dictionary
        
    Returns:
        Path object for the storage directory
    """
    if path_key not in STORAGE_PATHS:
        raise ValueError(f"Unknown storage path key: {path_key}")
    return STORAGE_PATHS[path_key]

def create_storage_structure() -> bool:
    """
    Create all necessary storage directories
    
    Returns:
        True if successful, False otherwise
    """
    try:
        for path_name, path in STORAGE_PATHS.items():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created/verified directory: {path}")
        return True
    except Exception as e:
        print(f"✗ Error creating storage structure: {e}")
        return False

def verify_ssd_connection() -> bool:
    """
    Verify SSD is connected and accessible
    
    Returns:
        True if SSD is accessible, False otherwise
    """
    try:
        ssd_path = Path(SSD_MOUNT_POINT)
        if ssd_path.exists() and os.access(ssd_path, os.W_OK):
            print(f"✓ SSD connected and accessible: {SSD_MOUNT_POINT}")
            return True
        else:
            print(f"✗ SSD not accessible: {SSD_MOUNT_POINT}")
            return False
    except Exception as e:
        print(f"✗ Error verifying SSD: {e}")
        return False

def get_storage_stats() -> dict:
    """
    Get storage usage statistics
    
    Returns:
        Dictionary with storage information
    """
    try:
        import shutil
        
        stats = {
            'mount_point': SSD_MOUNT_POINT,
            'system': SYSTEM,
        }
        
        # Get disk space info
        disk_usage = shutil.disk_usage(SSD_MOUNT_POINT)
        stats['total_size_gb'] = round(disk_usage.total / (1024**3), 2)
        stats['used_size_gb'] = round(disk_usage.used / (1024**3), 2)
        stats['free_size_gb'] = round(disk_usage.free / (1024**3), 2)
        stats['used_percent'] = round((disk_usage.used / disk_usage.total) * 100, 2)
        
        # Get directory sizes
        for name, path in STORAGE_PATHS.items():
            if path.exists():
                size_bytes = sum(
                    f.stat().st_size for f in path.glob('**/*') if f.is_file()
                )
                stats[f'{name}_size_gb'] = round(size_bytes / (1024**3), 2)
        
        return stats
    except Exception as e:
        print(f"Error getting storage stats: {e}")
        return {}
