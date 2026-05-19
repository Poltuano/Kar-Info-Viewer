"""
Car Detail View - Display detailed car information
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QScrollArea,
                             QGridLayout, QPixmap)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from database.models import Car
from utils.image_handler import ImageHandler

logger = logging.getLogger(__name__)


class CarDetailView(QWidget):
    """Display detailed information about a selected car"""
    
    def __init__(self):
        super().__init__()
        self.image_handler = ImageHandler()
        self.current_car = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Car header
        self.header_label = QLabel("No car selected")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        layout.addWidget(self.header_label)
        
        # Tabs for different information
        self.tabs = QTabWidget()
        
        # Overview tab
        self.overview_tab = QWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self.overview_tab, "Overview")
        
        # Specifications tab
        self.specs_tab = QWidget()
        self.tabs.addTab(self.specs_tab, "Specifications")
        
        # Maintenance tab
        self.maintenance_tab = QWidget()
        self.tabs.addTab(self.maintenance_tab, "Maintenance")
        
        # Images tab
        self.images_tab = QWidget()
        self.tabs.addTab(self.images_tab, "Images")
    
    def display_car(self, car: Car):
        """Display car information"""
        self.current_car = car
        self.header_label.setText(car.get_display_name())
        
        # Update tabs
        self.update_overview()
        self.update_specifications()
        self.update_maintenance()
        self.update_images()
        
        logger.info(f"Displaying car: {car}")
    
    def update_overview(self):
        """Update overview tab"""
        if not self.current_car:
            return
        
        layout = QGridLayout(self.overview_tab)
        
        # Basic information
        row = 0
        info = [
            ("Make:", self.current_car.make),
            ("Model:", self.current_car.model),
            ("Year:", str(self.current_car.year)),
            ("Body Type:", self.current_car.body_type),
            ("Color:", self.current_car.color),
            ("VIN:", self.current_car.vin or "N/A"),
            ("Current Mileage:", f"{self.current_car.current_mileage:,} km"),
        ]
        
        for label, value in info:
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
    
    def update_specifications(self):
        """Update specifications tab"""
        if not self.current_car or not self.current_car.specifications:
            layout = QVBoxLayout(self.specs_tab)
            layout.addWidget(QLabel("No specifications available"))
            return
        
        specs = self.current_car.specifications
        layout = QGridLayout(self.specs_tab)
        
        row = 0
        spec_info = [
            ("Engine Type:", specs.engine_type),
            ("Horsepower:", f"{specs.horsepower} hp"),
            ("Torque:", f"{specs.torque} Nm"),
            ("Transmission:", specs.transmission),
            ("Acceleration (0-100):", f"{specs.acceleration_0_100}s"),
            ("Top Speed:", f"{specs.top_speed} km/h"),
            ("Fuel Consumption:", f"{specs.fuel_consumption_combined} L/100km"),
            ("Fuel Type:", specs.fuel_type),
            ("Tank Capacity:", f"{specs.fuel_tank_capacity}L"),
            ("Cargo Capacity:", f"{specs.cargo_capacity}L"),
            ("Passenger Seats:", str(specs.passenger_seats)),
            ("Length:", f"{specs.dimensions_length}mm"),
            ("Width:", f"{specs.dimensions_width}mm"),
            ("Height:", f"{specs.dimensions_height}mm"),
            ("Weight:", f"{specs.weight}kg"),
        ]
        
        for label, value in spec_info:
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(QLabel(str(value)), row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
    
    def update_maintenance(self):
        """Update maintenance tab"""
        if not self.current_car or not self.current_car.maintenance_records:
            layout = QVBoxLayout(self.maintenance_tab)
            layout.addWidget(QLabel("No maintenance records available"))
            return
        
        layout = QVBoxLayout(self.maintenance_tab)
        
        for record in self.current_car.maintenance_records:
            label_text = f"{record.date.strftime('%Y-%m-%d')} - {record.maintenance_type}"
            label = QLabel(label_text)
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            layout.addWidget(label)
            
            details = f"Description: {record.description}\nCost: ${record.cost}\nMileage: {record.mileage}km"
            layout.addWidget(QLabel(details))
            layout.addWidget(QLabel(""))  # Separator
        
        layout.addStretch()
    
    def update_images(self):
        """Update images tab"""
        if not self.current_car or not self.current_car.image_path:
            layout = QVBoxLayout(self.images_tab)
            layout.addWidget(QLabel("No images available"))
            return
        
        layout = QVBoxLayout(self.images_tab)
        
        # Load and display image
        pixmap = self.image_handler.load_image(self.current_car.image_path)
        if pixmap:
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        else:
            layout.addWidget(QLabel("Failed to load image"))
