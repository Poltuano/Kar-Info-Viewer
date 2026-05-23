"""
SSD Storage Manager - Handle 2TB SSD operations and monitoring
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from config.storage_config import (
    STORAGE_PATHS, STORAGE_QUOTAS, get_storage_path,
    verify_ssd_connection, get_storage_stats
)

logger = logging.getLogger(__name__)


class SSDStorageManager:
    """Manage 2TB SSD storage for Kar-Info-Viewer"""

    def __init__(self):
        """Initialize SSD storage manager"""
        self.storage_paths = STORAGE_PATHS
        self.storage_quotas = STORAGE_QUOTAS
        self.initialized = False

    def initialize(self) -> bool:
        """
        Initialize SSD storage structure
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Verify SSD is connected
            if not verify_ssd_connection():
                logger.error("SSD not connected or not accessible")
                return False

            # Create all directories
            for path_name, path in self.storage_paths.items():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Initialized storage directory: {path}")

            self.initialized = True
            logger.info("SSD storage initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing SSD storage: {e}")
            return False

    def get_storage_usage(self) -> Dict[str, float]:
        """
        Get current storage usage for each directory
        
        Returns:
            Dictionary with storage usage in GB for each directory
        """
        try:
            usage = {}
            for path_name, path in self.storage_paths.items():
                if path.exists():
                    total_size = sum(
                        f.stat().st_size for f in path.glob('**/*') if f.is_file()
                    )
                    usage[path_name] = round(total_size / (1024**3), 2)
                else:
                    usage[path_name] = 0.0

            logger.info(f"Storage usage retrieved: {usage}")
            return usage
        except Exception as e:
            logger.error(f"Error getting storage usage: {e}")
            return {}

    def check_quota(self, path_key: str) -> bool:
        """
        Check if storage quota is exceeded
        
        Args:
            path_key: Storage path key to check
            
        Returns:
            True if within quota, False if exceeded
        """
        try:
            if path_key not in self.storage_quotas:
                logger.warning(f"Unknown storage quota key: {path_key}")
                return True

            usage = self.get_storage_usage()
            current_usage_gb = usage.get(path_key, 0)
            quota_gb = self.storage_quotas[path_key] / (1024**3)

            if current_usage_gb > quota_gb:
                logger.warning(
                    f"Storage quota exceeded for {path_key}: "
                    f"{current_usage_gb}GB / {quota_gb}GB"
                )
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking quota for {path_key}: {e}")
            return True

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up files older than specified days
        
        Args:
            days: Number of days to retain files
            
        Returns:
            Number of files deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0

            # Clean cache and temp directories
            for path_name in ['cache', 'temp']:
                path = self.storage_paths.get(path_name)
                if path and path.exists():
                    for file_path in path.glob('**/*'):
                        if file_path.is_file():
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_time < cutoff_date:
                                file_path.unlink()
                                deleted_count += 1
                                logger.debug(f"Deleted old file: {file_path}")

            logger.info(f"Cleaned up {deleted_count} old files (older than {days} days)")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0

    def backup_database(self, source_db: str) -> Optional[str]:
        """
        Create backup of database file
        
        Args:
            source_db: Path to database file to backup
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            source_path = Path(source_db)
            if not source_path.exists():
                logger.error(f"Database file not found: {source_db}")
                return None

            backup_dir = self.storage_paths['backups']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"cars_backup_{timestamp}.db"
            backup_path = backup_dir / backup_name

            shutil.copy2(source_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return None

    def get_storage_report(self) -> Dict:
        """
        Generate comprehensive storage report
        
        Returns:
            Dictionary with storage statistics and recommendations
        """
        try:
            stats = get_storage_stats()
            usage = self.get_storage_usage()

            report = {
                'timestamp': datetime.now().isoformat(),
                'total_size_gb': stats.get('total_size_gb', 0),
                'used_size_gb': stats.get('used_size_gb', 0),
                'free_size_gb': stats.get('free_size_gb', 0),
                'used_percent': stats.get('used_percent', 0),
                'directories': usage,
                'quotas': {k: round(v / (1024**3), 2) for k, v in self.storage_quotas.items()},
                'warnings': [],
                'recommendations': []
            }

            # Check for quota warnings
            for path_name, current_gb in usage.items():
                quota_gb = round(self.storage_quotas.get(path_name, 0) / (1024**3), 2)
                usage_percent = (current_gb / quota_gb * 100) if quota_gb > 0 else 0

                if usage_percent > 90:
                    report['warnings'].append(
                        f"{path_name}: {usage_percent:.1f}% of quota used"
                    )
                elif usage_percent > 75:
                    report['recommendations'].append(
                        f"Consider cleaning up {path_name} ({usage_percent:.1f}% of quota)"
                    )

            # Overall recommendations
            if report['used_percent'] > 90:
                report['warnings'].append("SSD is nearly full (>90%)")
            elif report['used_percent'] > 75:
                report['recommendations'].append("Consider freeing up space on SSD")

            logger.info("Storage report generated")
            return report
        except Exception as e:
            logger.error(f"Error generating storage report: {e}")
            return {}

    def optimize_images(self) -> int:
        """
        Optimize stored images to free up space
        
        Returns:
            Amount of space freed in bytes
        """
        try:
            # This is a placeholder for image optimization logic
            # In production, implement actual image compression/optimization
            logger.info("Starting image optimization")
            # TODO: Implement image compression/optimization
            return 0
        except Exception as e:
            logger.error(f"Error optimizing images: {e}")
            return 0

    def export_storage_report(self, output_file: str) -> bool:
        """
        Export storage report to JSON file
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            report = self.get_storage_report()
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Storage report exported to: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting storage report: {e}")
            return False

    def get_path(self, path_key: str) -> Path:
        """
        Get storage path by key
        
        Args:
            path_key: Storage path key
            
        Returns:
            Path object
        """
        return get_storage_path(path_key)
