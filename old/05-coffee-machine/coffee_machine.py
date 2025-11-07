from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# ==================== EXCEPTIONS ====================

class CoffeeError(Exception):
    """Base exception for coffee-related errors."""


class CoffeeTypeNotFoundError(CoffeeError):
    """Raised when requested coffee type doesn't exist."""


class InsufficientIngredientError(CoffeeError):
    """Raised when ingredient quantity is insufficient."""


# ==================== INGREDIENT ====================

class Ingredient:
    """Ingredient with inventory control."""

    def __init__(
        self,
        name: str,
        unit: str,
        cost_per_unit: Decimal,
        quantity_available: Decimal
    ) -> None:
        """
        Initialize ingredient with inventory control.
        Raises:
            ValueError: If quantity or cost is negative
        """
        if quantity_available < 0:
            raise ValueError(f"Quantity cannot be negative: {quantity_available}")
        if cost_per_unit < 0:
            raise ValueError(f"Cost cannot be negative: {cost_per_unit}")

        self.name = name
        self.unit = unit
        self.cost_per_unit = cost_per_unit
        self.quantity_available = quantity_available

    def has_sufficient(self, amount: Decimal) -> bool:
        """Check if sufficient quantity available."""
        return self.quantity_available >= amount

    def consume(self, amount: Decimal) -> None:
        """
        Consume ingredient quantity.

        Raises:
            ValueError: If amount is negative
            InsufficientIngredientError: If not enough quantity available
        """
        if amount < 0:
            raise ValueError(f"Cannot consume negative amount: {amount}")
        
        if not self.has_sufficient(amount):
            raise InsufficientIngredientError(
                f"Insufficient {self.name}. "
                f"Available: {self.quantity_available}{self.unit}, "
                f"needed: {amount}{self.unit}"
            )
        self.quantity_available -= amount

    def refill(self, amount: Decimal) -> None:
        """
        Refill ingredient quantity with structured logging.
        
        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError(f"Cannot refill negative amount: {amount}")
        
        old_quantity = self.quantity_available
        self.quantity_available += amount
        
        logger.info(
            "Ingredient refilled: %s +%s%s (before: %s%s, after: %s%s)",
            self.name, amount, self.unit,
            old_quantity, self.unit,
            self.quantity_available, self.unit
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Ingredient(name='{self.name}', "
                f"quantity={self.quantity_available}{self.unit})")


# ==================== RECIPE ====================

class Recipe:
    """Recipe with ingredient amounts and cost calculation."""
    
    def __init__(self, name: str, ingredients: dict[Ingredient, Decimal]) -> None:
        """
        Initialize recipe.
        
        Raises:
            ValueError: If ingredients is empty or any amount is non-positive
        """
        if not ingredients:
            raise ValueError("Recipe must have at least one ingredient")
        
        for ingredient, amount in ingredients.items():
            if amount <= 0:
                raise ValueError(
                    f"Ingredient amount must be positive: {ingredient.name}={amount}"
                )
        
        self.name = name
        self._ingredients = ingredients.copy()  # Defensive copy
    
    def get_ingredients(self) -> dict[Ingredient, Decimal]:
        """Get ingredients dictionary (returns copy for immutability)."""
        return self._ingredients.copy()
    
    def get_cost(self) -> Decimal:
        """Calculate total recipe cost based on ingredients."""
        return sum(
            ingredient.cost_per_unit * amount
            for ingredient, amount in self._ingredients.items()
        )
    
    def check_availability(self) -> bool:
        """Check if all ingredients are available in sufficient quantity."""
        return all(
            ingredient.has_sufficient(amount)
            for ingredient, amount in self._ingredients.items()
        )
    
    def consume_ingredients(self) -> None:
        """
        Consume all recipe ingredients atomically (all-or-nothing).
        
        Raises:
            InsufficientIngredientError: If any ingredient is insufficient
        """
        # First pass: check all ingredients
        if not self.check_availability():
            unavailable = [
                ingredient.name 
                for ingredient, amount in self._ingredients.items()
                if not ingredient.has_sufficient(amount)
            ]
            raise InsufficientIngredientError(
                f"Cannot make {self.name}: insufficient {', '.join(unavailable)}"
            )
        
        # Second pass: consume all ingredients (safe now)
        for ingredient, amount in self._ingredients.items():
            ingredient.consume(amount)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        ingredients_str = ", ".join(
            f"{ing.name}:{amt}{ing.unit}" 
            for ing, amt in self._ingredients.items()
        )
        return f"Recipe(name='{self.name}', ingredients=[{ingredients_str}])"


# ==================== DECORATOR PATTERN ====================

class Coffee(ABC):
    """Abstract base for coffee beverages."""
    
    @abstractmethod
    def get_description(self) -> str:
        """Return coffee description."""
    
    @abstractmethod
    def get_cost(self) -> Decimal:
        """Return total cost."""
    
    @abstractmethod
    def get_base_recipe(self) -> Recipe:
        """Return the base recipe for ingredient consumption."""


class BaseCoffee(Coffee):
    """Concrete base coffee implementation."""
    
    def __init__(self, recipe: Recipe) -> None:
        self._recipe = recipe
    
    def get_description(self) -> str:
        return self._recipe.name
    
    def get_cost(self) -> Decimal:
        return self._recipe.get_cost()
    
    def get_base_recipe(self) -> Recipe:
        return self._recipe


class CoffeeDecorator(Coffee):
    """Abstract decorator for coffee add-ons."""
    
    def __init__(self, coffee: Coffee) -> None:
        self._coffee = coffee
    
    def get_description(self) -> str:
        return self._coffee.get_description()
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost()
    
    def get_base_recipe(self) -> Recipe:
        """Delegate to wrapped coffee to get base recipe."""
        return self._coffee.get_base_recipe()


class MilkDecorator(CoffeeDecorator):
    """Adds milk to coffee."""
    
    COST = Decimal("0.50")
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Milk"
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost() + self.COST


class SugarDecorator(CoffeeDecorator):
    """Adds sugar to coffee."""
    
    COST = Decimal("0.20")
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Sugar"
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost() + self.COST


class ExtraShotDecorator(CoffeeDecorator):
    """Adds extra espresso shot to coffee."""
    
    COST = Decimal("1.00")
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Extra Shot"
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost() + self.COST


class WhippedCreamDecorator(CoffeeDecorator):
    """Adds whipped cream to coffee."""
    
    COST = Decimal("0.75")
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Whipped Cream"
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost() + self.COST


class VanillaDecorator(CoffeeDecorator):
    """Adds vanilla flavor to coffee."""
    
    COST = Decimal("0.60")
    
    def get_description(self) -> str:
        return f"{self._coffee.get_description()} + Vanilla"
    
    def get_cost(self) -> Decimal:
        return self._coffee.get_cost() + self.COST


# ==================== COFFEE MACHINE ====================

class CoffeeMachine:
    """Main coffee machine managing recipes and inventory."""
    
    def __init__(self) -> None:
        self._ingredients = self._initialize_ingredients()
        self._recipes = self._load_recipes()
        logger.info("Coffee machine initialized with %d recipes", len(self._recipes))
    
    def _initialize_ingredients(self) -> dict[str, Ingredient]:
        """Initialize ingredient inventory."""
        return {
            "coffee": Ingredient("Coffee", "g", Decimal("0.028"), Decimal("1000")),
            "water": Ingredient("Water", "ml", Decimal("0.0003"), Decimal("5000")),
            "milk": Ingredient("Milk", "ml", Decimal("0.003"), Decimal("2000"))
        }
    
    def _load_recipes(self) -> dict[str, Recipe]:
        """Load available coffee recipes."""
        coffee = self._ingredients["coffee"]
        water = self._ingredients["water"]
        milk = self._ingredients["milk"]
        
        return {
            "espresso": Recipe(
                name="Espresso",
                ingredients={coffee: Decimal("18"), water: Decimal("30")}
            ),
            "americano": Recipe(
                name="Americano",
                ingredients={coffee: Decimal("18"), water: Decimal("120")}
            ),
            "cappuccino": Recipe(
                name="Cappuccino",
                ingredients={
                    coffee: Decimal("18"),
                    water: Decimal("30"),
                    milk: Decimal("100")
                }
            ),
            "latte": Recipe(
                name="Latte",
                ingredients={
                    coffee: Decimal("18"),
                    water: Decimal("30"),
                    milk: Decimal("200")
                }
            )
        }
    
    def get_available_types(self) -> list[str]:
        """Return list of available coffee types."""
        return sorted(self._recipes.keys())
    
    def create_coffee(self, coffee_type: str) -> Coffee:
        """
        Create a base coffee of the specified type.
        
        Raises:
            CoffeeTypeNotFoundError: If coffee type doesn't exist
        """
        coffee_type = coffee_type.lower().strip()
        if coffee_type not in self._recipes:
            available = ", ".join(self.get_available_types())
            raise CoffeeTypeNotFoundError(
                f"Unknown type: '{coffee_type}'. Available: {available}"
            )
        return BaseCoffee(self._recipes[coffee_type])
    
    def make_coffee(self, coffee: Coffee) -> dict[str, str | float]:
        """
        Prepare coffee and consume ingredients.
        
        Raises:
            InsufficientIngredientError: If ingredients are insufficient
        """
        recipe = coffee.get_base_recipe()
        
        # Consume ingredients (with automatic availability check and atomicity)
        recipe.consume_ingredients()
        
        order = {
            "description": coffee.get_description(),
            "cost": float(coffee.get_cost()),
            "status": "ready"
        }
        
        logger.info(
            "Order completed: %s | Cost: $%.2f | Base: %s",
            order["description"],
            order["cost"],
            recipe.name
        )
        return order
    
    def get_inventory_status(self) -> dict[str, dict[str, str | float]]:
        """Return current inventory status."""
        return {
            name: {
                "quantity": float(ingredient.quantity_available),
                "unit": ingredient.unit
            }
            for name, ingredient in self._ingredients.items()
        }
    
    def refill_ingredient(self, ingredient_name: str, amount: Decimal) -> None:
        """
        Refill ingredient inventory.
        
        Raises:
            ValueError: If ingredient doesn't exist
        """
        ingredient_name = ingredient_name.lower()
        if ingredient_name not in self._ingredients:
            raise ValueError(
                f"Unknown ingredient: '{ingredient_name}'. "
                f"Available: {', '.join(self._ingredients.keys())}"
            )
        self._ingredients[ingredient_name].refill(amount)


# ==================== USAGE EXAMPLES ====================

def main() -> None:
    """
    Demonstrate coffee machine usage with decorator pattern.
    
    Test Coverage Demonstrated:
    1. Simple base coffee creation
    2. Single decorator application
    3. Multiple decorator chaining
    4. Cost calculation through decorator chain
    5. Order processing with ingredient consumption
    6. Multiple decorators of same type (double milk/sugar)
    7. Inventory status monitoring
    8. Error handling for invalid coffee types
    9. Atomic consumption behavior on inventory depletion
    10. Inventory refill and continuation
    11. Available coffee types listing
    
    Key Test Scenarios for Production:
    - Atomic consumption: Verify no partial consumption on failure
    - Thread safety: Multiple concurrent orders (needs locking)
    - Decorator immutability: Ensure decorators don't modify wrapped coffee
    - Cost precision: Decimal arithmetic correctness
    - Recipe immutability: Cannot modify recipe.ingredients externally
    """
    machine = CoffeeMachine()
    
    print("=" * 60)
    print("COFFEE MACHINE - DECORATOR PATTERN DEMO")
    print("=" * 60)
    
    # Example 1: Simple base coffee
    print("\n1. Simple Espresso:")
    espresso = machine.create_coffee("espresso")
    print(f"   {espresso.get_description()} - ${espresso.get_cost():.2f}")
    
    # Example 2: Coffee with single decorator
    print("\n2. Espresso with Milk:")
    espresso_milk = MilkDecorator(machine.create_coffee("espresso"))
    print(f"   {espresso_milk.get_description()} - ${espresso_milk.get_cost():.2f}")
    
    # Example 3: Coffee with multiple decorators
    print("\n3. Cappuccino with extras:")
    cappuccino = machine.create_coffee("cappuccino")
    cappuccino = SugarDecorator(cappuccino)
    cappuccino = ExtraShotDecorator(cappuccino)
    print(f"   {cappuccino.get_description()} - ${cappuccino.get_cost():.2f}")
    
    # Example 4: Chained decorators (fluent style)
    print("\n4. Deluxe Latte:")
    latte = WhippedCreamDecorator(
        VanillaDecorator(
            SugarDecorator(
                machine.create_coffee("latte")
            )
        )
    )
    print(f"   {latte.get_description()} - ${latte.get_cost():.2f}")
    
    # Example 5: Making coffee (consuming ingredients)
    print("\n5. Making coffee orders:")
    order1 = machine.make_coffee(machine.create_coffee("americano"))
    print(f"   Order 1: {order1['description']} - ${order1['cost']:.2f}")
    
    custom_latte = MilkDecorator(SugarDecorator(machine.create_coffee("latte")))
    order2 = machine.make_coffee(custom_latte)
    print(f"   Order 2: {order2['description']} - ${order2['cost']:.2f}")
    
    # Example 6: Multiple decorators of same type
    print("\n6. Double milk, double sugar espresso:")
    extra_sweet = SugarDecorator(
        SugarDecorator(
            MilkDecorator(
                MilkDecorator(
                    machine.create_coffee("espresso")
                )
            )
        )
    )
    print(f"   {extra_sweet.get_description()} - ${extra_sweet.get_cost():.2f}")
    
    # Example 7: Check inventory
    print("\n7. Inventory status:")
    inventory = machine.get_inventory_status()
    for ingredient, status in inventory.items():
        print(f"   {ingredient.capitalize()}: {status['quantity']}{status['unit']}")
    
    # Example 8: Error handling - invalid type
    print("\n8. Error handling - invalid coffee type:")
    try:
        machine.create_coffee("mocha")
    except CoffeeTypeNotFoundError as e:
        print(f"   ✗ {e}")
    
    # Example 9: Test atomic consumption behavior
    print("\n9. Testing atomic consumption (inventory depletion):")
    print("   Attempting to make 11 lattes (will deplete 2200ml milk, only 2000ml available)")
    try:
        for i in range(11):  # 11 lattes = 2200ml milk (exceeds 2000ml available)
            latte = machine.create_coffee("latte")
            machine.make_coffee(latte)
            print(f"   ✓ Latte #{i+1} prepared")
    except InsufficientIngredientError as e:
        print(f"   ✗ {e}")
        print("   → NOTE: Coffee and water were NOT consumed due to atomic operation")
    
    # Example 10: Refill and continue
    print("\n10. Refilling inventory:")
    machine.refill_ingredient("milk", Decimal("1000"))
    
    print("\n11. Order after refill:")
    final_order = machine.make_coffee(
        WhippedCreamDecorator(machine.create_coffee("cappuccino"))
    )
    print(f"   {final_order['description']} - ${final_order['cost']:.2f}")
    
    # Example 13: Available coffee types
    print("\n13. Available coffee types:")
    print(f"   {', '.join(machine.get_available_types())}")
    
    print("\n" + "=" * 60)
    print("\nKey Testing Points Demonstrated:")
    print("  • Decorator pattern composition")
    print("  • Cost calculation through decorator chain")
    print("  • Atomic ingredient consumption (all-or-nothing)")
    print("  • Error handling and validation")
    print("  • Inventory management with refill")
    print("=" * 60)


if __name__ == "__main__":
    main()