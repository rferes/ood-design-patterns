"""
PARKING LOT SYSTEM - 45 MIN LIVE CODING

GOAL: Implement a basic parking lot system

REQUIREMENTS:
- Park vehicles (Car, Motorcycle, Truck)
- Different spot sizes (Compact, Regular, Large)
- Issue tickets with entry time
- Calculate parking fee on exit
- Check spot availability

IMPLEMENT THESE CLASSES:
1. Vehicle (base class + 1-2 subclasses)
2. ParkingSpot
3. ParkingLot (main logic)

BONUS (if time):
- Ticket class
- One design pattern (Factory or Strategy)

FOCUS ON:
- Working code that runs
- Clean class structure
- Explain your design choices as you code

Time: 45-60 minutes
"""

from enum import Enum
from uuid import uuid4
from datetime import datetime
from math import ceil
from abc import ABC


class VehicleType(Enum):
    """Supported Vehicles Types"""
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    TRUCK = "TRUCK"


class SpotSize(Enum):
    """Available parking spot sizes."""
    COMPACT = "COMPACT"
    REGULAR = "REGULAR"
    LARGE = "LARGE"


class Vehicle(ABC):
    """Represents a vehicle in Parking Lot"""
    vehicle_type: VehicleType | None = None

    def __init__(self, license_plate: str) -> None:
        if self.vehicle_type is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define 'vehicle_type' class attribute"
            )
        self.license_plate = license_plate

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vehicle):
            return NotImplemented
        return self.license_plate == other.license_plate

    def __hash__(self) -> int:
        return hash(self.license_plate)

    def __repr__(self) -> str:
        """Return string representation of the vehicle."""
        # Safe access com fallback
        type_value = self.vehicle_type.value if self.vehicle_type else "UNDEFINED"
        return (
            f"{self.__class__.__name__}"
            f"(license_plate='{self.license_plate}', "
            f"type={type_value})"
        )


class Motorcycle(Vehicle):
    """
    Motorcycle vehicle type.
    Requires compact parking spots.
    """
    vehicle_type = VehicleType.MOTORCYCLE

    def __init__(self, license_plate: str) -> None:
        super().__init__(license_plate)


class Car(Vehicle):
    """
    Car vehicle type.
    Requires regular parking spots.
    """
    vehicle_type = VehicleType.CAR

    def __init__(self, license_plate: str) -> None:
        super().__init__(license_plate)


class Truck(Vehicle):
    """
    Truck vehicle type.
    Requires large parking spots.
    """
    vehicle_type = VehicleType.TRUCK

    def __init__(self, license_plate: str) -> None:
        super().__init__(license_plate)


class ParkingSpot:
    """Represents a Parking Spot"""
    VEHICLE_TYPE_TO_SPOT_SIZE = {
        VehicleType.MOTORCYCLE: SpotSize.COMPACT,
        VehicleType.CAR: SpotSize.REGULAR,
        VehicleType.TRUCK: SpotSize.LARGE,
    }
    SPOT_SIZE = {
        SpotSize.COMPACT: 1,
        SpotSize.REGULAR: 2,
        SpotSize.LARGE: 3
    }  # Scale size for comparison

    def __init__(self, id: str, size: SpotSize) -> None:
        self.id = id
        self.size = size
        self.is_available: bool = True

    def __eq__(self, other) -> bool:
        return isinstance(other, ParkingSpot) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def can_fit_spot(self, vehicle: Vehicle) -> bool:
        return self.SPOT_SIZE[self.size] >= self.SPOT_SIZE[self.VEHICLE_TYPE_TO_SPOT_SIZE[vehicle.vehicle_type]]

    def __repr__(self) -> str:
        status = 'Available' if self.is_available else 'Occupied'
        return f"Parking Spot (id: {self.id}, size: {self.size}, status: {status}"


class ParkingTicket:
    """Represents a Parking Ticket"""

    def __init__(self, vehicle: Vehicle, parking_spot: ParkingSpot) -> None:
        self.id = uuid4()
        self.vehicle = vehicle
        self.parking_spot = parking_spot

        self.start_time: datetime = datetime.now()
        self.price: float = 0.0
        self.finish_time: datetime | None = None

    def __eq__(self, other) -> bool:
        return isinstance(other, ParkingTicket) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Parking Ticket (id: {self.id}, "
            f"vehicle: {self.vehicle}, "
            f"parking spot: {self.parking_spot}, "
            f"start time: {self.start_time}, "
            f"price: {self.price}, "
            f"finish time: {self.finish_time})"
        )


class ParkingLot:
    """Parking Lot System, for manage vehicle, spots and tickets"""

    SPOT_FEE_HOUR = {
        SpotSize.COMPACT: 5.0,
        SpotSize.REGULAR: 10.0,
        SpotSize.LARGE: 20.0
        }  # Dollars

    FREE_TIME = 0.5  # Hours

    def __init__(self, name: str) -> None:
        self.name = name

        self.spots: dict[str, ParkingSpot] = {}
        self.open_tickets: dict[Vehicle, ParkingTicket] = {}
        self.close_tickets: list[ParkingTicket] = []

    def __eq__(self, other) -> bool:
        return isinstance(other, ParkingLot) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def add_spot(self, spot: ParkingSpot) -> ParkingSpot:
        """Add a new spot to parking lot."""
        if spot.id in self.spots.keys():
            raise ValueError(f"Spot {spot.id} already exist.")
        self.spots[spot.id] = spot
        return spot

    def remove_spot(self, spot: ParkingSpot) -> ParkingSpot:
        """Remove a spot from parking lot."""
        if spot.id not in self.spots.keys():
            raise ValueError(f"Spot {spot.id} don't exist")
        return self.spots.pop(spot.id)

    def _find_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        """STRICT: Apenas spots EXATAMENTE do tamanho certo"""
        required_size = ParkingSpot.VEHICLE_TYPE_TO_SPOT_SIZE[vehicle.vehicle_type]

        return next(
            (s for s in self.spots.values() if s.is_available and s.size == required_size),
            None
        )

    def _calculate_price(self, ticket) -> float:
        duration = (ticket.finish_time - ticket.start_time).total_seconds() / (60 * 60)
        if duration <= self.FREE_TIME:
            return 0
        else:
            return ceil(duration) * self.SPOT_FEE_HOUR[ticket.parking_spot.size]

    def open_ticket(self, vehicle: Vehicle) -> ParkingTicket | None:
        """Open a parking ticket for a vehicle"""
        if vehicle in self.open_tickets:
            raise ValueError(f"Vehicle {vehicle.license_plate} is already parked")
        spot = self._find_spot(vehicle)
        if not spot:
            return None
        spot.is_available = False
        ticket = ParkingTicket(vehicle, spot)
        self.open_tickets[vehicle] = ticket
        return ticket

    def close_ticket(self, vehicle: Vehicle) -> ParkingTicket:
        """Close a parking ticket for vehicle"""
        if vehicle not in self.open_tickets:
            raise ValueError("This Vehicle is not park here")
        ticket = self.open_tickets.pop(vehicle)
        ticket.finish_time = datetime.now()
        ticket.price = self._calculate_price(ticket)
        ticket.parking_spot.is_available = True
        self.close_tickets.append(ticket)
        return ticket

    def __repr__(self) -> str:
        available = sum(1 for spot in self.spots.values() if spot.is_available)
        return (
                f"Parking Lot {self.name}"
                f"Available Spots: {available}/{len(self.spots)}, "
                f"Vehicles Park Now: {len(self.open_tickets)}, "
                f"Vehicle Parked All Time: {len(self.close_tickets)}."
        )


def demo():
    """Demo For Basic Test"""
    spot1 = ParkingSpot("C1", SpotSize.COMPACT)
    spot2 = ParkingSpot("C2", SpotSize.COMPACT)
    spot3 = ParkingSpot("C3", SpotSize.COMPACT)
    spot4 = ParkingSpot("R1", SpotSize.REGULAR)
    spot5 = ParkingSpot("R2", SpotSize.REGULAR)
    spot6 = ParkingSpot("R3", SpotSize.REGULAR)
    spot7 = ParkingSpot("L3", SpotSize.LARGE)

    parking_lot = ParkingLot("ABC")

    # Test: Add spots
    try:
        parking_lot.add_spot(spot1)
        parking_lot.add_spot(spot2)
        parking_lot.add_spot(spot3)
        parking_lot.add_spot(spot4)
        parking_lot.add_spot(spot5)
        parking_lot.add_spot(spot6)
        parking_lot.add_spot(spot7)
        print("✓ All spots added successfully")
    except ValueError as e:
        print(f"✗ Error adding spot: {e}")

    print(parking_lot)

    # Test: Park vehicle
    vehicle1 = Car("ABC-123")
    print(vehicle1)

    try:
        ticket = parking_lot.open_ticket(vehicle1)
        if ticket:
            print(f"✓ Vehicle parked with ticket: {ticket.id}")
        else:
            print("✗ No spots available for vehicle")
    except ValueError as e:
        print(f"✗ Error parking vehicle: {e}")

    # Test: Try to park same vehicle again (should fail)
    try:
        parking_lot.open_ticket(vehicle1)
        print("✗ Should not allow duplicate parking!")
    except ValueError as e:
        print(f"✓ Correctly rejected duplicate parking: {e}")

    print(parking_lot)

    try:
        parking_lot.close_ticket(vehicle1)
    except ValueError as e:
        print(f"✓ Correctly rejected non exist car in parking lot: {e}")

    print(parking_lot)


if __name__ == '__main__':
    demo()
