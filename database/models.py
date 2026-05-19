"""
Data Models for Car Information
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class CarSpecifications:
    """Car specifications data model"""
    id: int
    car_id: int
    engine_type: str
    horsepower: int
    torque: int  # in Nm
    transmission: str
    acceleration_0_100: float  # in seconds
    top_speed: int  # in km/h
    fuel_consumption_combined: float  # in L/100km
    fuel_type: str
    fuel_tank_capacity: float  # in liters
    cargo_capacity: int  # in liters
    passenger_seats: int
    dimensions_length: float  # in mm
    dimensions_width: float  # in mm
    dimensions_height: float  # in mm
    weight: int  # in kg
    wheelbase: float  # in mm


@dataclass
class MaintenanceRecord:
    """Maintenance record data model"""
    id: int
    car_id: int
    date: datetime
    maintenance_type: str
    description: str
    cost: float
    mileage: int
    service_provider: str
    notes: Optional[str] = None


@dataclass
class Car:
    """Car information data model"""
    id: int
    make: str
    model: str
    year: int
    body_type: str
    color: str
    vin: Optional[str]
    license_plate: Optional[str]
    purchase_date: Optional[datetime]
    purchase_price: Optional[float]
    current_mileage: int
    image_path: Optional[str]
    specifications: Optional[CarSpecifications] = None
    maintenance_records: Optional[List[MaintenanceRecord]] = None

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    def get_display_name(self):
        """Get formatted display name"""
        return f"{self.year} {self.make} {self.model}"
