"""
Main Application Window
"""

import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from gui.search_widget import SearchWidget
from gui.car_detail_view import CarDetailView
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Connect to database
        if not self.db_manager.connect():
            QMessageBox.warning(self, "Database Error", 
                              "Failed to connect to database. Check your configuration.")
            logger.warning("Failed to connect to database on startup")
        
        self.init_ui()
        self.setWindowTitle("Car Information Viewer")
        self.setGeometry(100, 100, 1200, 800)
    
    def init_ui(self):
        """Initialize user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create left panel (search and filter)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search widget
        self.search_widget = SearchWidget(self.db_manager)
        self.search_widget.car_selected.connect(self.on_car_selected)
        left_layout.addWidget(self.search_widget)
        
        # Create right panel (car details)
        self.detail_view = CarDetailView()
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.detail_view)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)
    
    def on_car_selected(self, car):
        """Handle car selection from search"""
        if car:
            # Get full car details including specifications and maintenance
            car_specs = self.db_manager.get_car_specifications(car.id)
            maintenance = self.db_manager.get_maintenance_records(car.id)
            
            car.specifications = car_specs
            car.maintenance_records = maintenance
            
            self.detail_view.display_car(car)
            logger.info(f"Selected car: {car}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.db_manager.disconnect()
        logger.info("Application closed")
        event.accept()
