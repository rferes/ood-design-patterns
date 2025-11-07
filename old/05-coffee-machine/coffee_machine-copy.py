"""
Coffee Machine - Python Senior Interview
Classes: Ingredient, Recipe, CoffeeMachine
Patterns: Builder, Decorator
Features: Different coffee types, add-ons

Coffee Machine - Python Senior Interview

CLASSES (3):
    - Ingredient: name, unit, cost_per_unit, quantity_available
    - Recipe: name, ingredients{}, get_cost()
    - CoffeeMachine: _recipes{}, get_recipe(), make_coffee()

PATTERNS (2):
    - Decorator: Coffee(ABC) → BaseCoffee → CoffeeDecorator → Milk/Sugar/ExtraShot/WhippedCream
    - Builder: CoffeeBuilder → add_X() fluent → build() with reset

EXCEPTIONS (3):
    - CoffeeError (base)
    - CoffeeTypeNotFoundError
    - InsufficientIngredientError

FLOW:
    1. Machine loads recipes with ingredients (espresso, cappuccino, latte)
    2. Builder takes recipe → decorates with add-ons → builds Coffee
    3. Machine checks inventory → consumes ingredients → returns order

KEY POINTS:
    - Type hints: Python 3.10+ (from __future__ import annotations)
    - Dataclass: Ingredient, Recipe
    - Logging: machine init, order ready
    - Validation: ingredient availability, recipe existence
"""

# ==================== QUICK REFERENCE ====================
"""
CLASSES: Ingredient, Recipe, CoffeeMachine
PATTERNS: Decorator (Coffee→Base→Decorator→Addons), Builder (fluent+reset)
EXCEPTIONS: CoffeeError, NotFound, Insufficient
FLOW: Load recipes → Build with decorators → Check/consume inventory → Return order
TECH: dataclass, ABC, type hints, logging, Decimal
"""

from decimal import Decimal, ROUND_HALF_UP

DECIMAL_PRECISION = Decimal('0.01')


class CoffeeMachineError(Exception):
    """Coffee Machine Errors"""
    pass


class InsufficientIngredientError(CoffeeMachineError):
    """Don't have sufficient quantity of ingredient"""
    pass


class Ingredient:
    """Ingredient with inventory control."""

    def __init__(
        self,
        name: str,
        unit: str,
        cost_per_unit: Decimal,
        quantity_available: Decimal
    ) -> None:
        # Validação inline
        if not name.strip():
            raise ValueError("Ingredient name can't be empty")
        if not unit.strip():
            raise ValueError("Ingredient unit can't be empty")
        if cost_per_unit < MIN_DEPOSIT_AMOUNT:
            raise ValueError("Cost per unit must be higher than U$ 0.01")
        if quantity_available <= Decimal(0):
            raise ValueError("Quantity must be positive")

        self.name = name
        self.unit = unit
        self.cost_per_unit = cost_per_unit
        self.quantity_available = quantity_available

    def __hash__(self) -> int:
        """Hash based on name and unit."""
        return hash((self.name, self.unit))

    def __eq__(self, other: object) -> bool:
        """Equality based on name and unit."""
        if not isinstance(other, Ingredient):
            return False
        return self.name == other.name and self.unit == other.unit

    def __repr__(self) -> str:
        return (
            f"Ingredient({self.name!r}, {self.unit!r}, "
            f"{self.cost_per_unit}, {self.quantity_available})"
        )

    def has_sufficient(self, amount: Decimal) -> bool:
        """Check if sufficient quantity available."""
        return self.quantity_available >= amount

    def consume(self, amount: Decimal) -> Decimal:
        """Consume ingredient quantity."""
        if not self.has_sufficient(amount):
            raise InsufficientIngredientError(
                f"Insufficient {self.name}. "
                f"Available: {self.quantity_available}{self.unit}, "
                f"needed: {amount}{self.unit}"
            )
        self.quantity_available -= amount
        return self.quantity_available

    def add_insume(self, amount: Decimal) -> Decimal:
        """Add insume of ingredient."""
        self.quantity_available += amount
        return self.quantity_available


class Recipe:
    """Recipe with ingredient amounts."""
    def __init__(self, name: str, ingredients: dict[Ingredient, Decimal], price: Decimal) -> None:
        if not name.strip():
            raise ValueError("Ingredient name can't be empty")
        if not ingredients:
            raise ValueError("They need to have ingredients")
        self.name = name
        self.ingredients = ingredients
        self.price = price.quantize(DECIMAL_PRECISION, ROUND_HALF_UP)

    @property
    def cost(self) -> Decimal:
        """Calculate total recipe cost."""
        cost = sum(
            (ingredient.cost_per_unit * amount)
            for ingredient, amount in self.ingredients.items()
        )
        cost = Decimal(cost).quantize(DECIMAL_PRECISION, ROUND_HALF_UP)
        return cost

