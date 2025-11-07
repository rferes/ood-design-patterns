"""
Parking Lot System - REAL Senior Interview Approach
Pragmatic, clean, and interview-friendly
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from decimal import Decimal


class VehicleSize(Enum):
    MOTORCYCLE = 1
    COMPACT = 2
    LARGE = 3


class SpotSize(Enum):
    MOTORCYCLE = 1
    COMPACT = 2
    LARGE = 3


# ============================================================================
# CLASSES SIMPLES - ABORDAGEM SENIOR REAL
# Em entrevista, você NÃO perde tempo com over-engineering
# ============================================================================

class Vehicle(ABC):
    """Base class for all vehicles."""

    def __init__(self, license_plate: str, size: VehicleSize):
        self.license_plate = license_plate
        self.size = size

    @abstractmethod
    def can_fit_in_spot(self, spot: 'ParkingSpot') -> bool:
        """Check if vehicle can fit in spot."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.license_plate})"


class Motorcycle(Vehicle):
    """Motorcycle - fits anywhere."""

    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleSize.MOTORCYCLE)

    def can_fit_in_spot(self, spot: 'ParkingSpot') -> bool:
        return True  # Fits anywhere


class Car(Vehicle):
    """Car - fits in compact and large spots."""

    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleSize.COMPACT)

    def can_fit_in_spot(self, spot: 'ParkingSpot') -> bool:
        return spot.size in (SpotSize.COMPACT, SpotSize.LARGE)


class Bus(Vehicle):
    """Bus - needs 5 consecutive large spots."""
    
    SPOTS_NEEDED = 5  # Class constant - clean!
    
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleSize.LARGE)
    
    def can_fit_in_spot(self, spot: 'ParkingSpot') -> bool:
        return spot.size == SpotSize.LARGE


class ParkingSpot:
    """Individual parking spot."""
    
    def __init__(self, spot_number: int, size: SpotSize, level: int):
        self.spot_number = spot_number
        self.size = size
        self.level = level
        self.vehicle: Vehicle | None = None
    
    def is_available(self) -> bool:
        return self.vehicle is None
    
    def park(self, vehicle: Vehicle) -> bool:
        """Park vehicle if possible."""
        if not self.is_available() or not vehicle.can_fit_in_spot(self):
            return False
        
        self.vehicle = vehicle
        return True
    
    def remove_vehicle(self) -> Vehicle | None:
        """Remove and return parked vehicle."""
        vehicle = self.vehicle
        self.vehicle = None
        return vehicle


class ParkingTicket:
    """Ticket issued when parking."""
    
    def __init__(self, ticket_id: str, vehicle: Vehicle, spots: list[ParkingSpot]):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spots = spots
        self.entry_time = datetime.now()
        self.exit_time: datetime | None = None
    
    def calculate_fee(self, hourly_rate: Decimal = Decimal("5.00")) -> Decimal:
        """Calculate parking fee."""
        if not self.exit_time:
            return Decimal("0")
        
        hours = (self.exit_time - self.entry_time).total_seconds() / 3600
        hours_rounded = max(1, int(hours + 0.99))  # Round up
        return Decimal(hours_rounded) * hourly_rate


class Level:
    """Parking level with multiple spots."""
    
    def __init__(self, level_number: int, spots_config: dict[SpotSize, int]):
        self.level_number = level_number
        self.spots: list[ParkingSpot] = []
        
        spot_num = 0
        for size, count in spots_config.items():
            for _ in range(count):
                self.spots.append(ParkingSpot(spot_num, size, level_number))
                spot_num += 1
    
    def find_spots_for_vehicle(self, vehicle: Vehicle) -> list[ParkingSpot] | None:
        """Find available spots for vehicle."""
        if isinstance(vehicle, Bus):
            return self._find_consecutive_large_spots(Bus.SPOTS_NEEDED)
        
        # Regular vehicles - find first available
        for spot in self.spots:
            if spot.is_available() and vehicle.can_fit_in_spot(spot):
                return [spot]
        
        return None
    
    def _find_consecutive_large_spots(self, count: int) -> list[ParkingSpot] | None:
        """Find consecutive large spots for buses."""
        consecutive = []
        
        for spot in self.spots:
            if spot.size == SpotSize.LARGE and spot.is_available():
                consecutive.append(spot)
                if len(consecutive) == count:
                    return consecutive
            else:
                consecutive = []
        
        return None
    
    def park_vehicle(self, vehicle: Vehicle, spots: list[ParkingSpot]) -> bool:
        """Park vehicle in spots."""
        for spot in spots:
            if not spot.park(vehicle):
                # Rollback
                for s in spots[:spots.index(spot)]:
                    s.remove_vehicle()
                return False
        return True
    
    def remove_vehicle_from_spots(self, spots: list[ParkingSpot]) -> None:
        """Remove vehicle from spots."""
        for spot in spots:
            spot.remove_vehicle()
    
    @property
    def available_count(self) -> int:
        """Count available spots."""
        return sum(1 for spot in self.spots if spot.is_available())


class ParkingLot:
    """Main parking lot system."""
    
    def __init__(self, num_levels: int, spots_per_level: dict[SpotSize, int]):
        self.levels = [Level(i, spots_per_level) for i in range(num_levels)]
        self.tickets: dict[str, ParkingTicket] = {}
        self._ticket_counter = 0
    
    def park_vehicle(self, vehicle: Vehicle) -> ParkingTicket | None:
        """Park vehicle and return ticket."""
        for level in self.levels:
            spots = level.find_spots_for_vehicle(vehicle)
            if spots and level.park_vehicle(vehicle, spots):
                ticket = ParkingTicket(
                    ticket_id=self._generate_ticket_id(),
                    vehicle=vehicle,
                    spots=spots
                )
                self.tickets[ticket.ticket_id] = ticket
                return ticket
        
        return None  # Lot is full
    
    def exit_vehicle(self, ticket_id: str) -> tuple[ParkingTicket, Decimal] | None:
        """Process exit and return ticket with fee."""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None
        
        ticket.exit_time = datetime.now()
        fee = ticket.calculate_fee()
        
        # Free up spots
        level = self.levels[ticket.spots[0].level]
        level.remove_vehicle_from_spots(ticket.spots)
        
        del self.tickets[ticket_id]
        return ticket, fee
    
    def get_available_count(self) -> int:
        """Get total available spots."""
        return sum(level.available_count for level in self.levels)
    
    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID."""
        self._ticket_counter += 1
        return f"TKT-{self._ticket_counter:06d}"


# ============================================================================
# DEMO
# ============================================================================

def main():
    # Create parking lot
    lot = ParkingLot(
        num_levels=3,
        spots_per_level={
            SpotSize.MOTORCYCLE: 10,
            SpotSize.COMPACT: 20,
            SpotSize.LARGE: 10
        }
    )
    
    print(f"Total spots: {lot.get_available_count()}\n")
    
    # Park vehicles
    vehicles = [
        Motorcycle("MOTO-123"),
        Car("CAR-456"),
        Car("CAR-789"),
        Bus("BUS-001")
    ]
    
    tickets = []
    for vehicle in vehicles:
        ticket = lot.park_vehicle(vehicle)
        if ticket:
            spots_used = len(ticket.spots)
            print(f"✓ {vehicle} parked: {ticket.ticket_id} ({spots_used} spot{'s' if spots_used > 1 else ''})")
            tickets.append(ticket)
        else:
            print(f"✗ {vehicle} - No space!")
    
    print(f"\nAvailable: {lot.get_available_count()}")
    
    # Exit first car
    if len(tickets) > 1:
        result = lot.exit_vehicle(tickets[1].ticket_id)
        if result:
            _, fee = result
            print(f"\n✓ {tickets[1].vehicle} exited - Fee: ${fee}")
            print(f"Available: {lot.get_available_count()}")


if __name__ == "__main__":
    main()