"""
VENDING MACHINE SYSTEM - 45 minutes
Implement a simple vending machine with State and Command patterns.
CLASSES:

Product: name, price, code
Inventory: manage products and stock
VendingMachine: main system

STATES (State Pattern):

Idle: waiting
HasMoney: money inserted
Dispensing: delivering product

OPERATIONS (Command Pattern):

insert_money(amount)
select_product(code)
cancel()

FEATURES:

Return change
Handle out of stock
Validate product codes

EXAMPLE:
vm = VendingMachine()
vm.inventory.add_product(Product("Coke", 2.50, "A1"), quantity=10)
vm.insert_money(3.00)
vm.select_product("A1")  # returns product + $0.50 change
Include basic tests.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP


class VendingMachineError(Exception):
    """Base exception for vending machine errors"""
    pass


class InvalidStateError(VendingMachineError):
    """Operation not allowed in current state"""
    pass


class InsufficientFundsError(VendingMachineError):
    """Not enough money for the operation"""
    pass


class ProductNotFoundError(VendingMachineError):
    """Product code doesn't exist"""
    pass


class OutOfStockError(VendingMachineError):
    """Product is out of stock"""
    pass


class Product:
    """Represents a Product of vending machine"""
    def __init__(self, name: str, price: float | str, code: str) -> None:
        self.name = name
        self.price = Decimal(str(price)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        self.code = code

    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        return (
            f"Product {self.name} "
            f"(price: {self.price}, "
            f"code: {self.code})"
        )


class Inventory:
    """Manage product stock"""
    def __init__(self) -> None:
        self._stock: dict[Product, int] = {}

    def __contains__(self, product):
        return product in self._stock and self._stock[product] > 0

    def add_product(self, product: Product, quantity: int) -> None:
        """Add product to stock"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self._stock[product] = self._stock.get(product, 0) + quantity

    def get_product(self, code: str) -> Product | None:
        """Get product data by code"""
        for product in self._stock:
            if product.code == code:
                return product
        return None

    def get_stock(self, product: Product) -> int:
        """Get quantity of product in stock"""
        return self._stock.get(product, 0)

    def has_stock(self, product: Product) -> bool:
        """Check if has a product in stock"""
        return self._stock.get(product, 0) > 0

    def dispense(self, product: Product) -> bool:
        """Remove 1 item of product from stock"""
        if self._stock.get(product, 0) > 0:
            self._stock[product] -= 1
            return True
        return False

    @property
    def total_items(self) -> int:
        """Total quantity of all items in stock"""
        return sum(self._stock.values())

    def __repr__(self) -> str:
        return (
            f"Inventory("
            f"unique products={len(self._stock)}, "
            f"total items={self.total_items})"
        )


class State(ABC):
    """
    Abstract base class for vending machine states.

    Each state defines behavior for user interactions and transitions.
    Concrete states should implement all abstract methods.
    """
    def __init__(self, machine: VendingMachine) -> None:
        self.machine = machine

    @abstractmethod
    def insert_money(self, amount: float) -> Decimal:
        pass

    @abstractmethod
    def select_product(self, code: str) -> tuple[Product | None, Decimal]:
        pass

    @abstractmethod
    def cancel(self) -> Decimal:
        pass


class IdleState(State):
    """Waiting for money"""
    def insert_money(self, amount: float) -> Decimal:
        if amount <= 0:
            raise ValueError(f"Invalid amount: ${amount:.2f}")
        self.machine.balance += Decimal(str(amount)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        self.machine.state = self.machine.has_money_state
        return self.machine.balance

    def select_product(self, code: str) -> tuple[Product | None, Decimal]:
        raise InvalidStateError("You need to insert money first.")

    def cancel(self) -> Decimal:
        raise InvalidStateError("You don't have any operation to cancel")


class HasMoneyState(State):
    """Select the product or add more money"""
    def insert_money(self, amount: float) -> Decimal:
        if amount <= 0:
            raise ValueError(f"Invalid amount: ${amount:.2f}")
        self.machine.balance += Decimal(str(amount)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        self.machine.state = self.machine.has_money_state
        return self.machine.balance

    def select_product(self, code: str) -> tuple[Product | None, Decimal]:
        product = self.machine.inventory.get_product(code)
        if not product:
            raise ProductNotFoundError("Product not found.")
        if not self.machine.inventory.has_stock(product):
            raise OutOfStockError("Product out of stock.")

        if self.machine.balance < product.price:
            shortage = product.price - self.machine.balance
            raise InsufficientFundsError(f"Funds are insufficient, Need ${shortage} more.")

        self.machine.state = self.machine.dispensing_state
        self.machine.inventory.dispense(product)
        change = self.machine.balance - product.price
        self.machine.total_amount += product.price
        self.machine.balance = Decimal(0.0)
        self.machine.state = self.machine.idle_state

        return (product, change)

    def cancel(self) -> Decimal:
        """Cancel transaction and return money"""
        refund = self.machine.balance
        self.machine.balance = Decimal(0.0)
        self.machine.state = self.machine.idle_state
        return refund


class DispensingState(State):
    """Dispensing product please wait machine process"""
    def insert_money(self, amount: float) -> Decimal:
        raise InvalidStateError("Machine are dispensing a product, please wait.")

    def select_product(self, code: str) -> tuple[Product | None, Decimal]:
        raise InvalidStateError("Machine are dispensing a product, please wait.")

    def cancel(self) -> Decimal:
        raise InvalidStateError("Machine are dispensing a product, please wait.")


class Command(ABC):
    """Abstract base class for commands"""
    @abstractmethod
    def execute(self):
        pass


class InsertMoneyCommand(Command):
    """Command to insert money"""
    def __init__(self, machine: VendingMachine, amount: float) -> None:
        self.machine = machine
        self.amount = amount

    def execute(self) -> Decimal:
        return self.machine.state.insert_money(self.amount)


class SelectProductCommand(Command):
    """Command to select product"""
    def __init__(self, machine: VendingMachine, code: str) -> None:
        self.machine = machine
        self.code = code

    def execute(self) -> tuple[Product | None, Decimal]:
        return self.machine.state.select_product(self.code)


class CancelCommand(Command):
    """Command to cancel transaction"""
    def __init__(self, machine: VendingMachine) -> None:
        self.machine = machine

    def execute(self) -> Decimal:
        return self.machine.state.cancel()


class VendingMachine:
    """Main vending machine system"""
    def __init__(self, name: str) -> None:
        self.name = name
        self.inventory: Inventory = Inventory()
        self.balance: Decimal = Decimal(0.0)
        self.total_amount: Decimal = Decimal(0.0)

        self.idle_state: IdleState = IdleState(self)
        self.has_money_state: HasMoneyState = HasMoneyState(self)
        self.dispensing_state: DispensingState = DispensingState(self)
        self.state: State = self.idle_state

    def insert_money(self, amount: float) -> Decimal:
        """Insert money into the machine"""
        cmd = InsertMoneyCommand(self, amount)
        return cmd.execute()

    def select_product(self, code: str) -> tuple[Product | None, Decimal]:
        """
        Select product by code.
        Returns:
            tuple[Product | None, float]: (product, change)
        """
        cmd = SelectProductCommand(self, code)
        return cmd.execute()

    def cancel(self) -> Decimal:
        """
        Cancel transaction and return money.
        Returns:
            float: Amount refunded
        """
        cmd = CancelCommand(self)
        return cmd.execute()

    def __repr__(self) -> str:
        return (
            f"Vending Machine {self.name} "
            f"(Balance: {self.balance}, "
            f"Total Amount: {self.total_amount}, "
            f"{self.inventory}, "
            f"{self.state.__class__.__name__})"
        )


def develop_test():
    print("=" * 60)
    print("VENDING MACHINE SYSTEM TEST")
    print("=" * 60)

    v = VendingMachine("ABC Store")
    p1 = Product('Coca-Cola', 2.50, 'A1')
    p2 = Product('Pepsi', 2.00, 'A2')
    p3 = Product('Water', 1.50, 'B1')
    
    v.inventory.add_product(p1, 3)
    v.inventory.add_product(p2, 2)
    v.inventory.add_product(p3, 1)
    
    print(f"\n✅ Machine initialized: {v}")
    print(f"   Initial state: {v.state.__class__.__name__}\n")
    
    # Test 1: Try to select product without money
    print("TEST 1: Select product without inserting money")
    print("-" * 60)
    try:
        product, change = v.select_product('A1')
        print(f"Dispensed: {product.name}")
        if change > 0:
            print(f"Change: ${change:.2f}")
    except InvalidStateError as e:
        print(f"❌ Error caught: {e}")
        print(f"   Current state: {v.state.__class__.__name__}")
    
    # Test 2: Insert valid money
    print("\n\nTEST 2: Insert valid money")
    print("-" * 60)
    try:
        msg = v.insert_money(3.00)
        print(msg)
        print(f"   Current state: {v.state.__class__.__name__}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 3: Buy product successfully
    print("\n\nTEST 3: Buy product successfully (with change)")
    print("-" * 60)
    try:
        product, change = v.select_product('A1')
        print(f"✅ Product: {product.name}, Change: ${change:.2f}")
        print(f"   State after purchase: {v.state.__class__.__name__}")
        print(f"   Current balance: ${v.balance:.2f}")
    except (InvalidStateError, ProductNotFoundError, OutOfStockError, InsufficientFundsError) as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Try to buy non-existent product
    print("\n\nTEST 4: Non-existent product")
    print("-" * 60)
    try:
        v.insert_money(5.00)
        print(f"   Balance before attempt: ${v.balance:.2f}")
        product, change = v.select_product('Z9')
        print(f"Dispensed: {product.name}")
        if change > 0:
            print(f"Change: ${change:.2f}")
    except ProductNotFoundError as e:
        print(f"❌ Error caught: {e}")
        print(f"   Balance preserved: ${v.balance:.2f}")
        print(f"   State: {v.state.__class__.__name__}")
    except Exception as e:
        print(f"❌ Other error: {e}")
    
    # Test 5: Insufficient funds (FIXED)
    print("\n\nTEST 5: Insufficient funds")
    print("-" * 60)
    try:
        # Current balance is $5.00 (from previous test)
        print(f"   Available balance: ${v.balance:.2f}")
        print(f"   Trying to buy Coca-Cola (A1): $2.50")
        
        product, change = v.select_product('A1')
        print(f"✅ Product: {product.name}, Change: ${change:.2f}")
        
        # Now try to buy another product without sufficient balance
        print(f"\n   New balance: ${v.balance:.2f}")
        print(f"   Trying to buy Coca-Cola (A1) again without enough money...")
        v.insert_money(1.00)  # Insert only $1.00, insufficient for $2.50
        product, change = v.select_product('A1')
        print(f"Dispensed: {product.name}")
    except InsufficientFundsError as e:
        print(f"❌ Error caught: {e}")
        print(f"   Current balance: ${v.balance:.2f}")
    except Exception as e:
        print(f"❌ Other error: {e}")
    
    # Test 6: Cancel transaction
    print("\n\nTEST 6: Cancel transaction and receive refund")
    print("-" * 60)
    try:
        print(f"   Balance before cancellation: ${v.balance:.2f}")
        refund = v.cancel()
        print(f"✅ Refund: ${refund:.2f}")
        print(f"   State after cancellation: {v.state.__class__.__name__}")
        print(f"   Balance after cancellation: ${v.balance:.2f}")
    except InvalidStateError as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Try to cancel without inserted money
    print("\n\nTEST 7: Try to cancel without active transaction")
    print("-" * 60)
    try:
        v.cancel()
    except InvalidStateError as e:
        print(f"❌ Error caught: {e}")
        print(f"   State: {v.state.__class__.__name__}")
    
    # Test 8: Out of stock product
    print("\n\nTEST 8: Out of stock product")
    print("-" * 60)
    try:
        # Buy all units of Water (B1)
        print(f"   Water stock before: {v.inventory.get_stock(p3)} unit(s)")
        v.insert_money(2.00)
        product, change = v.select_product('B1')
        print(f"✅ Dispensed: {product.name}, Change: ${change:.2f}")
        print(f"   Water stock after: {v.inventory.get_stock(p3)} unit(s)")
        
        # Try to buy again
        print(f"\n   Trying to buy Water again...")
        v.insert_money(2.00)
        product, change = v.select_product('B1')
        print(f"Dispensed: {product.name}")
        if change > 0:
            print(f"Change: ${change:.2f}")
    except OutOfStockError as e:
        print(f"❌ Error caught: {e}")
        print(f"   Balance preserved: ${v.balance:.2f}")
    except Exception as e:
        print(f"❌ Other error: {e}")
    
    # Test 9: Insert invalid amount (IMPROVED)
    print("\n\nTEST 9: Insert invalid amount (negative)")
    print("-" * 60)
    # Clear balance first if there is any
    if v.balance > 0:
        try:
            refund = v.cancel()
            print(f"   Previous balance cancelled: ${refund:.2f}")
        except InvalidStateError as e:
            print(f"   No balance to cancel: {e}")
    
    try:
        v.insert_money(-5.00)
    except ValueError as e:
        print(f"❌ Error caught: {e}")
        print(f"   State preserved: {v.state.__class__.__name__}")
    
    # Test 10: Multiple money insertions
    print("\n\nTEST 10: Multiple money insertions")
    print("-" * 60)
    try:
        msg1 = v.insert_money(1.00)
        print(msg1)
        msg2 = v.insert_money(1.00)
        print(msg2)
        msg3 = v.insert_money(0.50)
        print(msg3)
        print(f"   State: {v.state.__class__.__name__}")
        
        product, change = v.select_product('A2')
        print(f"✅ Dispensed: {product.name}, Change: ${change:.2f}")
        print(f"   Final state: {v.state.__class__.__name__}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 11: Exact purchase (no change)
    print("\n\nTEST 11: Purchase with exact amount (no change)")
    print("-" * 60)
    try:
        print(f"   Pepsi stock: {v.inventory.get_stock(p2)} unit(s)")
        v.insert_money(2.00)
        print(f"   Amount inserted: $2.00 (exact price of Pepsi)")
        
        product, change = v.select_product('A2')
        print(f"✅ Dispensed: {product.name}")
        if change > 0:
            print(f"   Change: ${change:.2f}")
        else:
            print(f"   No change (exact amount)")
        print(f"   Remaining Pepsi stock: {v.inventory.get_stock(p2)} unit(s)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 12: Check total amount collected
    print("\n\nTEST 12: Total amount collected")
    print("-" * 60)
    print(f"✅ Total collected by machine: ${v.total_amount:.2f}")
    print(f"   (Sum of all products sold)")

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Machine: {v.name}")
    print(f"State: {v.state.__class__.__name__}")
    print(f"Current balance: ${v.balance:.2f}")
    print(f"Total collected: ${v.total_amount:.2f}")
    print(f"\nInventory: {v.inventory}")
    print(f"  • Coca-Cola (A1): {v.inventory.get_stock(p1)} unit(s)")
    print(f"  • Pepsi (A2): {v.inventory.get_stock(p2)} unit(s)")
    print(f"  • Water (B1): {v.inventory.get_stock(p3)} unit(s)")
    print("=" * 60)


if __name__ == '__main__':
    develop_test()
