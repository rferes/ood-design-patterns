# Parking Lot System

Sistema de gerenciamento de estacionamento com suporte para múltiplos tipos de veículos e tamanhos de vagas.

## Funcionalidades

- ✅ Estacionar veículos (Motorcycle, Car, Truck)
- ✅ Gerenciar vagas de diferentes tamanhos (Compact, Regular, Large)
- ✅ Emitir tickets com horário de entrada
- ✅ Calcular taxa de estacionamento na saída
- ✅ Verificar disponibilidade de vagas

## Estrutura de Classes

```
Vehicle (ABC)
├── Motorcycle → Compact spots
├── Car → Regular spots
└── Truck → Large spots

ParkingSpot
├── id: str
├── size: SpotSize
└── is_available: bool

ParkingTicket
├── id: UUID
├── vehicle: Vehicle
├── parking_spot: ParkingSpot
├── start_time: datetime
├── finish_time: datetime | None
└── price: float

ParkingLot
├── spots: dict[str, ParkingSpot]
├── open_tickets: dict[Vehicle, ParkingTicket]
└── close_tickets: list[ParkingTicket]
```

## Regras de Negócio

**Tamanho de Vagas:**
- Motorcycle → Compact (menor)
- Car → Regular (médio)
- Truck → Large (maior)

**Cálculo de Preço:**
- Primeiros 30 minutos: gratuito
- Após isso: cobrado por hora cheia (arredondado para cima)
- Valores por hora:
  - Compact: $5.00
  - Regular: $10.00
  - Large: $20.00

## Como Usar

```python
# Criar estacionamento
parking_lot = ParkingLot("Downtown Parking")

# Adicionar vagas
parking_lot.add_spot(ParkingSpot("C1", SpotSize.COMPACT))
parking_lot.add_spot(ParkingSpot("R1", SpotSize.REGULAR))
parking_lot.add_spot(ParkingSpot("L1", SpotSize.LARGE))

# Estacionar veículo
car = Car("ABC-1234")
ticket = parking_lot.open_ticket(car)

# Retirar veículo e calcular preço
final_ticket = parking_lot.close_ticket(car)
print(f"Total: ${final_ticket.price}")
```

## Executar Demo

```bash
python parking_lot.py
```

## Tecnologias

- Python 3.10+
- Bibliotecas padrão: `enum`, `uuid`, `datetime`, `abc`