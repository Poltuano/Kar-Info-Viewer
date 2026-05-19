"""
Car Information Viewer - Main Application Entry Point
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('car_viewer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Initialize and run the application"""
    try:
        logger.info("Starting Car Information Viewer")
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("Application window opened")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
