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
from decimal import Decimal, ROUND_HALF_UP
from abc import ABC, abstractmethod


class VendingMachineError(Exception):
    """Base exception for vending machine errors"""
    pass


class OutOfStockError(VendingMachineError):
    """Product is out of stock"""
    pass


class InvalidStateError(VendingMachineError):
    """State error, invalid operation for this state"""
    pass


class ProductNotFoundError(VendingMachineError):
    """Product code error, not found"""
    pass


class InsufficientFundsError(VendingMachineError):
    """Balance is lower than product price"""
    pass


class ProductCodeAlreadyUsedError(VendingMachineError):
    """Product with diferente name but using the same code already register, please check name and code of product"""
    pass


class Product:
    def __init__(self, name: str, price: float, code: str) -> None:
        if price <= 0.00:
            raise ValueError("Price need to be higher than 0.00")
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
            f"Product: {self.name}, "
            f"(price: {self.price}, "
            f"code: {self.code})"
        )


class Inventory:
    def __init__(self) -> None:
        self._stock: dict[Product, int] = {}

    def __contains__(self, product) -> bool:
        return self.has_stock(product)

    def add_product(self, product: Product, quantity: int) -> tuple[Product, int]:
        """Add product stock to inventary"""
        if quantity <= 0:
            raise ValueError("Quantity of product need to be higher than 0")
        product_in_stock = self.get_product(product.code)
        if product_in_stock:
            if product.name != product_in_stock.name:
                raise ProductCodeAlreadyUsedError("Product with diferente name but using the same code already register, please check name and code of product")
        self._stock[product] = self._stock.get(product, 0) + quantity
        return (product, self._stock[product])

    def get_product(self, code: str) -> Product | None:
        """Get product from inventory using a code of product"""
        for product in self._stock:
            if product.code == code:
                return product
        return None

    def get_product_stock(self, product) -> int:
        """Check how many itens of a product have in stock"""
        return self._stock.get(product, 0)

    def has_stock(self, product) -> bool:
        """Check if have any item of product in stock"""
        return self.get_product_stock(product) > 0

    def dispense_product(self, product) -> tuple[Product, int]:
        """Dispense a product from the stock to consumer"""
        if not self.has_stock(product):
            raise OutOfStockError(f"{product.name} ({product.code}) out of stock.")
        self._stock[product] -= 1
        return (product,  self._stock[product])

    @property
    def total_products(self) -> int:
        return sum(self._stock.values())

    def __repr__(self) -> str:
        return (
            f"Inventory (Unique Products: {len(self._stock)}, "
            f"Total Products: {self.total_products})"
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
    def select_product(self, code: str) -> tuple[Product, Decimal]:
        pass

    @abstractmethod
    def cancel(self) -> Decimal:
        pass


class IdleState(State):
    """Waiting for user interaction"""
    def insert_money(self, amount: float) -> Decimal:
        if amount <= 0.00:
            raise ValueError('Amount need to be higher than U$0.00')
        self.machine.balance = Decimal(str(amount)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        self.machine.state = self.machine.has_money_state
        return self.machine.balance

    def select_product(self, code: str) -> tuple[Product, Decimal]:
        raise InvalidStateError("You need to add money first.")

    def cancel(self) -> Decimal:
        raise InvalidStateError("You don't have start yet.")


class HasMoneyState(State):
    """Waiting for user interaction"""
    def insert_money(self, amount: float) -> Decimal:
        if amount <= 0.00:
            raise ValueError('Amount need to be higher than U$0.00')
        self.machine.balance += Decimal(str(amount)).quantize(Decimal('0.01'), ROUND_HALF_UP)
        return self.machine.balance

    def select_product(self, code: str) -> tuple[Product, Decimal]:
        product = self.machine.inventory.get_product(code)
        if not product:
            raise ProductNotFoundError("This Product is not in inventary")

        if not self.machine.inventory.has_stock(product):
            raise OutOfStockError(f"Product {product.name} ({product.code}) out of stock.")

        if self.machine.balance < product.price:
            raise InsufficientFundsError(f"Insufficient funds, product {product.name} ({product.code}) price is {self.machine.balance} you need to add more U${product.price - self.machine.balance}")

        self.machine.state = self.machine.dispensing_state
        self.machine.inventory.dispense_product(product)
        change = self.machine.balance - product.price
        self.machine.total_amount += product.price
        self.machine.balance = Decimal('0.00')
        self.machine.state = self.machine.idle_state
        return product, change

    def cancel(self) -> Decimal:
        money_back = self.machine.balance
        self.machine.balance = Decimal('0.00')
        return money_back


class DispensingState(State):
    """Waiting for user interaction"""
    def insert_money(self, amount: float) -> Decimal:
        raise InvalidStateError("Machine is dispensing product, please wait.")

    def select_product(self, code: str) -> tuple[Product, Decimal]:
        raise InvalidStateError("Machine is dispensing product, please wait.")

    def cancel(self) -> Decimal:
        raise InvalidStateError("Machine is dispensing product, please wait.")


class Command(ABC):
    """
    Abstract command class for vending machine states.
    """
    @abstractmethod
    def execute(self) -> Decimal | tuple[Product, Decimal]:
        """Execute command"""


class InsertMoneyCommand(Command):
    """Command to insert money"""
    def __init__(self, machine: VendingMachine, amount: float) -> None:
        self.machine = machine
        self.amount = amount

    def execute(self) -> Decimal:
        return self.machine.state.insert_money(self.amount)


class SelectProductCommand(Command):
    """Command to select product in stock of vending machine"""
    def __init__(self, machine: VendingMachine, code: str) -> None:
        self.machine = machine
        self.code = code

    def execute(self) -> tuple[Product, Decimal]:
        return self.machine.state.select_product(self.code)


class CancelCommand(Command):
    """Command to cancel operation on vending machine"""
    def __init__(self, machine: VendingMachine) -> None:
        self.machine = machine

    def execute(self) -> Decimal:
        return self.machine.state.cancel()


class VendingMachine:
    def __init__(self, name: str) -> None:
        self.name = name
        self.inventory: Inventory = Inventory()
        self.balance: Decimal = Decimal('0.00')
        self.total_amount: Decimal = Decimal('0.00')

        self.idle_state: IdleState = IdleState(self)
        self.has_money_state: HasMoneyState = HasMoneyState(self)
        self.dispensing_state: DispensingState = DispensingState(self)
        self.state: State = self.idle_state

    def insert_money(self, amount: float) -> Decimal:
        cmd = InsertMoneyCommand(self, amount)
        return cmd.execute()

    def select_product(self, code: str) -> tuple[Product, Decimal]:
        cmd = SelectProductCommand(self, code)
        return cmd.execute()

    def cancel(self) -> Decimal:
        cmd = CancelCommand(self)
        return cmd.execute()

    def __repr__(self) -> str:
        state = state = (
                'idle' if self.state == self.idle_state
                else 'has money' if self.state == self.has_money_state
                else 'dispensing'
            )
        return (
            f"{self.name} Vending Machine "
            f"(balance: {self.balance}, "
            f"total amount: {self.total_amount}, "
            f"state: {state}, "
            f"inventory: {self.inventory})"
            )


def comprehensive_test():
    """Teste completo do sistema de vending machine"""
    
    print("=" * 60)
    print("VENDING MACHINE SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 60)
    
    # ========== SETUP ==========
    print("\n[1] SETUP - Criando máquina de venda")
    vm = VendingMachine("ABC Store")
    print(f"✓ Máquina criada: {vm.name}")
    print(f"  Estado inicial: {vm}")
    
    # ========== TESTES DE PRODUTO ==========
    print("\n" + "=" * 60)
    print("[2] TESTES DE PRODUTO")
    print("=" * 60)
    
    print("\n[2.1] Criando produto válido")
    try:
        coke = Product("Coke 1L", 2.50, "A1")
        print(f"✓ Produto criado: {coke}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[2.2] Tentando criar produto com preço negativo")
    try:
        invalid_product = Product("Invalid", -1.00, "Z1")
        print(f"✗ FALHOU - Produto inválido foi criado!")
    except ValueError as e:
        print(f"✓ Erro capturado corretamente: {e}")
    
    print("\n[2.3] Tentando criar produto com preço zero")
    try:
        invalid_product = Product("Free Item", 0.00, "Z2")
        print(f"✗ FALHOU - Produto gratuito foi criado!")
    except ValueError as e:
        print(f"✓ Erro capturado corretamente: {e}")
    
    # ========== TESTES DE INVENTÁRIO ==========
    print("\n" + "=" * 60)
    print("[3] TESTES DE INVENTÁRIO")
    print("=" * 60)
    
    print("\n[3.1] Adicionando produtos ao inventário")
    try:
        product, qty = vm.inventory.add_product(Product("Coke 1L", 2.50, "A1"), 10)
        print(f"✓ Adicionado: {product.name} ({product.code}) - Quantidade: {qty}")
        
        product, qty = vm.inventory.add_product(Product("Pepsi 1L", 2.30, "A2"), 5)
        print(f"✓ Adicionado: {product.name} ({product.code}) - Quantidade: {qty}")
        
        product, qty = vm.inventory.add_product(Product("Water 500ml", 1.50, "B1"), 15)
        print(f"✓ Adicionado: {product.name} ({product.code}) - Quantidade: {qty}")
        
        product, qty = vm.inventory.add_product(Product("Chips", 3.00, "C1"), 0)
        print(f"✗ FALHOU - Quantidade zero foi aceita!")
    except ValueError as e:
        print(f"✓ Erro capturado (quantidade <= 0): {e}")
    
    print(f"\n  Inventário atual: {vm.inventory}")
    
    print("\n[3.2] Adicionando mais estoque de produto existente")
    try:
        product, qty = vm.inventory.add_product(Product("Coke 1L", 2.50, "A1"), 5)
        print(f"✓ Estoque atualizado: {product.name} - Nova quantidade: {qty}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[3.3] Tentando adicionar produto diferente com código duplicado")
    try:
        product, qty = vm.inventory.add_product(Product("Sprite 1L", 2.40, "A1"), 10)
        print(f"✗ FALHOU - Código duplicado foi aceito!")
    except ProductCodeAlreadyUsedError as e:
        print(f"✓ Erro capturado corretamente: {e}")
    
    print("\n[3.4] Verificando estoque de produtos")
    coke = vm.inventory.get_product("A1")
    print(f"✓ Coke em estoque: {vm.inventory.get_product_stock(coke)} unidades")
    print(f"✓ Tem estoque de Coke? {vm.inventory.has_stock(coke)}")
    
    print("\n[3.5] Buscando produto inexistente")
    inexistent = vm.inventory.get_product("Z99")
    print(f"✓ Produto Z99: {inexistent}")
    
    # ========== TESTES DE ESTADOS - IDLE ==========
    print("\n" + "=" * 60)
    print("[4] TESTES DE ESTADO - IDLE")
    print("=" * 60)
    
    print("\n[4.1] Tentando selecionar produto sem inserir dinheiro")
    try:
        product, change = vm.select_product("A1")
        print(f"✗ FALHOU - Compra sem dinheiro foi permitida!")
    except InvalidStateError as e:
        print(f"✓ Erro capturado: {e}")
    
    print("\n[4.2] Tentando cancelar sem ter iniciado")
    try:
        refund = vm.cancel()
        print(f"✗ FALHOU - Cancelamento sem ação foi permitido!")
    except InvalidStateError as e:
        print(f"✓ Erro capturado: {e}")
    
    print("\n[4.3] Tentando inserir valor negativo")
    try:
        balance = vm.insert_money(-5.00)
        print(f"✗ FALHOU - Valor negativo foi aceito!")
    except ValueError as e:
        print(f"✓ Erro capturado: {e}")
    
    print("\n[4.4] Tentando inserir valor zero")
    try:
        balance = vm.insert_money(0.00)
        print(f"✗ FALHOU - Valor zero foi aceito!")
    except ValueError as e:
        print(f"✓ Erro capturado: {e}")
    
    # ========== TESTES DE ESTADOS - HAS MONEY ==========
    print("\n" + "=" * 60)
    print("[5] TESTES DE ESTADO - HAS MONEY")
    print("=" * 60)
    
    print("\n[5.1] Inserindo dinheiro válido")
    try:
        balance = vm.insert_money(5.00)
        print(f"✓ Dinheiro inserido: ${balance}")
        print(f"  Estado atual: {vm.state.__class__.__name__}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[5.2] Inserindo mais dinheiro")
    try:
        balance = vm.insert_money(2.00)
        print(f"✓ Saldo atualizado: ${balance}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[5.3] Tentando selecionar produto inexistente")
    try:
        product, change = vm.select_product("Z99")
        print(f"✗ FALHOU - Produto inexistente foi dispensado!")
    except ProductNotFoundError as e:
        print(f"✓ Erro capturado: {e}")
    
    print("\n[5.4] Cancelando transação e recebendo reembolso")
    try:
        refund = vm.cancel()
        print(f"✓ Reembolso recebido: ${refund}")
        print(f"  Saldo atual: ${vm.balance}")
        print(f"  Estado atual: {vm.state.__class__.__name__}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    # ========== TESTES DE COMPRA BEM-SUCEDIDA ==========
    print("\n" + "=" * 60)
    print("[6] TESTES DE COMPRA BEM-SUCEDIDA")
    print("=" * 60)
    
    print("\n[6.1] Compra com troco")
    try:
        vm.insert_money(3.00)
        product, change = vm.select_product("A1")
        print(f"✓ Produto dispensado: {product.name}")
        print(f"✓ Troco: ${change}")
        print(f"  Saldo final: ${vm.balance}")
        print(f"  Total arrecadado: ${vm.total_amount}")
        print(f"  Estado final: {vm.state.__class__.__name__}")
        print(f"  Estoque restante de {product.name}: {vm.inventory.get_product_stock(product)}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[6.2] Compra com valor exato")
    try:
        vm.insert_money(2.30)
        product, change = vm.select_product("A2")
        print(f"✓ Produto dispensado: {product.name}")
        print(f"✓ Troco: ${change}")
        print(f"  Total arrecadado: ${vm.total_amount}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[6.3] Tentando comprar com dinheiro insuficiente")
    try:
        vm.insert_money(1.00)
        product, change = vm.select_product("A1")
        print(f"✗ FALHOU - Compra com dinheiro insuficiente foi permitida!")
    except InsufficientFundsError as e:
        print(f"✓ Erro capturado: {e}")
        vm.cancel()  # Limpar saldo
    
    # ========== TESTES DE ESTOQUE ==========
    print("\n" + "=" * 60)
    print("[7] TESTES DE ESTOQUE ESGOTADO")
    print("=" * 60)
    
    print("\n[7.1] Esgotando estoque de Pepsi")
    pepsi = vm.inventory.get_product("A2")
    remaining_stock = vm.inventory.get_product_stock(pepsi)
    print(f"  Estoque atual de Pepsi: {remaining_stock}")
    
    for i in range(remaining_stock):
        try:
            vm.insert_money(2.30)
            product, change = vm.select_product("A2")
            print(f"  Compra {i+1}: {product.name} dispensado")
        except Exception as e:
            print(f"✗ Erro na compra {i+1}: {e}")
    
    print(f"\n✓ Estoque de Pepsi após vendas: {vm.inventory.get_product_stock(pepsi)}")
    
    print("\n[7.2] Tentando comprar produto esgotado")
    try:
        vm.insert_money(5.00)
        product, change = vm.select_product("A2")
        print(f"✗ FALHOU - Produto esgotado foi dispensado!")
    except OutOfStockError as e:
        print(f"✓ Erro capturado: {e}")
        vm.cancel()  # Limpar saldo
    
    # ========== TESTES DE MÚLTIPLAS TRANSAÇÕES ==========
    print("\n" + "=" * 60)
    print("[8] TESTES DE MÚLTIPLAS TRANSAÇÕES")
    print("=" * 60)
    
    print("\n[8.1] Realizando 5 compras consecutivas")
    for i in range(5):
        try:
            vm.insert_money(2.00)
            product, change = vm.select_product("B1")
            print(f"  Transação {i+1}: {product.name} - Troco: ${change}")
        except Exception as e:
            print(f"✗ Erro na transação {i+1}: {e}")
    
    print(f"\n✓ Total arrecadado pela máquina: ${vm.total_amount}")
    print(f"✓ Estoque restante de Water: {vm.inventory.get_product_stock(vm.inventory.get_product('B1'))}")
    
    # ========== RESUMO FINAL ==========
    print("\n" + "=" * 60)
    print("[9] RESUMO FINAL")
    print("=" * 60)
    print(f"\n{vm}")
    print("\nEstoque detalhado:")
    for product in vm.inventory._stock:
        qty = vm.inventory.get_product_stock(product)
        status = "✓ Disponível" if qty > 0 else "✗ Esgotado"
        print(f"  {status} - {product.name} ({product.code}): {qty} unidades - ${product.price}")
    
    print("\n" + "=" * 60)
    print("TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 60)


if __name__ == "__main__":
    comprehensive_test()
