Vending Machine System
Sistema de máquina de vendas implementado com os padrões State e Command em Python.
📦 Componentes

Product: Representa um produto (nome, preço, código)
Inventory: Gerencia estoque dos produtos
VendingMachine: Sistema principal com máquina de estados

🎯 Padrões Implementados
State Pattern
A máquina altera seu comportamento baseado no estado interno:

IdleState: Aguardando inserção de dinheiro
HasMoneyState: Dinheiro inserido, permite seleção
DispensingState: Entregando produto

Command Pattern
Operações encapsuladas em comandos:

InsertMoneyCommand: Inserir dinheiro
SelectProductCommand: Selecionar produto
CancelCommand: Cancelar e devolver dinheiro

📊 Diagrama de Estados
[Idle] --insert_money()--> [HasMoney] --select_product()--> [Dispensing] --> [Idle]
                               ^  |
                               |  | cancel()
                               |  v
                               [Idle]
🚀 Como Usar
pythonfrom vending_machine import VendingMachine, Product

# Criar máquina e adicionar produtos
vm = VendingMachine("Store")
vm.inventory.add_product(Product("Coke", 2.50, "A1"), quantity=10)
vm.inventory.add_product(Product("Water", 1.50, "B1"), quantity=5)

# Comprar produto
vm.insert_money(3.00)
product, change = vm.select_product("A1")
print(f"Product: {product.name}, Change: ${change:.2f}")

# Cancelar transação
vm.insert_money(5.00)
refund = vm.cancel()
print(f"Refund: ${refund:.2f}")
⚠️ Exceções

InvalidStateError: Operação não permitida no estado atual
InsufficientFundsError: Saldo insuficiente
ProductNotFoundError: Código de produto inválido
OutOfStockError: Produto sem estoque

🧪 Testes
bashpython vending_machine.py
Executa 12 testes cobrindo:

Fluxo de compra completo
Estados e transições
Tratamento de erros
Cálculo de troco
Validação de estoque
Cancelamento de transação

📁 Estrutura
Product                     # Produto individual
Inventory                   # Gerenciamento de estoque
VendingMachine             # Sistema principal
├── State (abstract)       # Base para estados
│   ├── IdleState
│   ├── HasMoneyState
│   └── DispensingState
└── Command (abstract)     # Base para comandos
    ├── InsertMoneyCommand
    ├── SelectProductCommand
    └── CancelCommand