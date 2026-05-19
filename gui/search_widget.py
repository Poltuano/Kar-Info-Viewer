"""
Search Widget - Search and filter for cars
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QListWidget, QListWidgetItem)
from PyQt5.QtCore import pyqtSignal
from database.db_manager import DatabaseManager
from database.models import Car

logger = logging.getLogger(__name__)


class SearchWidget(QWidget):
    """Widget for searching and filtering cars"""
    
    # Signal emitted when a car is selected
    car_selected = pyqtSignal(Car)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.cars = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Make filter
        make_layout = QHBoxLayout()
        make_label = QLabel("Make:")
        self.make_combo = QComboBox()
        self.make_combo.addItem("All")
        self.load_makes()
        self.make_combo.currentTextChanged.connect(self.on_filter_changed)
        make_layout.addWidget(make_label)
        make_layout.addWidget(self.make_combo)
        layout.addLayout(make_layout)
        
        # Model search
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter model name...")
        self.model_input.textChanged.connect(self.on_filter_changed)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)
        
        # Year filter
        year_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        self.year_combo = QComboBox()
        self.year_combo.addItem("All")
        # Add years from 1990 to 2030
        for year in range(2030, 1989, -1):
            self.year_combo.addItem(str(year))
        self.year_combo.currentTextChanged.connect(self.on_filter_changed)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.on_search)
        layout.addWidget(search_button)
        
        # Results list
        results_label = QLabel("Results:")
        layout.addWidget(results_label)
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_car_clicked)
        layout.addWidget(self.results_list)
    
    def load_makes(self):
        """Load all car makes from database"""
        makes = self.db_manager.get_all_makes()
        for make in makes:
            self.make_combo.addItem(make)
        logger.info(f"Loaded {len(makes)} car makes")
    
    def on_filter_changed(self):
        """Handle filter changes"""
        self.on_search()
    
    def on_search(self):
        """Perform search"""
        make = self.make_combo.currentText()
        model = self.model_input.text()
        year = self.year_combo.currentText()
        
        # Convert to None if "All" is selected
        make = None if make == "All" else make
        model = model if model else None
        year = int(year) if year != "All" else None
        
        # TODO: Implement search with your database
        self.cars = self.db_manager.search_cars(make=make, model=model, year=year)
        
        # Update results list
        self.results_list.clear()
        for car in self.cars:
            item = QListWidgetItem(car.get_display_name())
            item.setData(0, car)  # Store car object
            self.results_list.addItem(item)
        
        logger.info(f"Found {len(self.cars)} cars matching criteria")
    
    def on_car_clicked(self, item: QListWidgetItem):
        """Handle car selection"""
        car = item.data(0)
        if car:
            self.car_selected.emit(car)
