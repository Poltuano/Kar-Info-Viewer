"""
Image Handler - Load and process car images/diagrams
"""

import os
import logging
from PyQt5.QtGui import QPixmap
from config.config import IMAGE_CONFIG

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handle loading and processing of car images"""
    
    def __init__(self):
        """Initialize image handler"""
        self.max_width = IMAGE_CONFIG['max_width']
        self.max_height = IMAGE_CONFIG['max_height']
        self.supported_formats = IMAGE_CONFIG['supported_formats']
    
    def load_image(self, image_path: str) -> QPixmap:
        """
        Load an image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            QPixmap object or None if failed
        """
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image not found: {image_path}")
                return self.load_placeholder()
            
            # Check if file format is supported
            ext = os.path.splitext(image_path)[1].lower().lstrip('.')
            if ext not in self.supported_formats:
                logger.warning(f"Unsupported image format: {ext}")
                return None
            
            # Load and scale image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logger.error(f"Failed to load image: {image_path}")
                return self.load_placeholder()
            
            # Scale to max dimensions
            scaled_pixmap = pixmap.scaledToHeight(
                self.max_height,
                1  # Qt.SmoothTransformation
            )
            
            logger.info(f"Loaded image: {image_path}")
            return scaled_pixmap
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def load_placeholder(self) -> QPixmap:
        """
        Load placeholder image
        
        Returns:
            QPixmap placeholder or None
        """
        placeholder_path = IMAGE_CONFIG['default_image']
        if os.path.exists(placeholder_path):
            return QPixmap(placeholder_path)
        
        # Create a solid color placeholder if file doesn't exist
        pixmap = QPixmap(self.max_width, self.max_height)
        pixmap.fill()
        return pixmap
    
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        Check if file is a supported image format
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported, False otherwise
        """
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return ext in IMAGE_CONFIG['supported_formats']
