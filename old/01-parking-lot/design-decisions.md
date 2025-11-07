# Design Decisions - Parking Lot System

## 1. Arquitetura de Classes

### Vehicle (Abstract Base Class)
**Decisão:** Usar ABC com atributo de classe `vehicle_type`

**Justificativa:**
- Garante que todas as subclasses definam seu tipo
- Evita instanciação direta da classe base
- Facilita extensão para novos tipos de veículos

**Alternativa rejeitada:** Enum simples sem hierarquia de classes (menos flexível para comportamentos específicos)

### ParkingSpot
**Decisão:** Mapeamento direto entre tipo de veículo e tamanho de vaga

**Justificativa:**
- Regra de negócio clara: cada veículo requer um tamanho específico
- Performance O(1) no lookup via dicionário
- Fácil manutenção e extensão

**Trade-off:** Sistema mais rígido (não permite Car em vaga Large), mas mais simples e previsível

### ParkingTicket
**Decisão:** Ticket como entidade independente com UUID

**Justificativa:**
- Rastreabilidade única de cada estacionamento
- Histórico completo (entrada, saída, preço)
- Facilita auditoria e relatórios futuros

### ParkingLot
**Decisão:** Três estruturas de dados separadas (spots, open_tickets, close_tickets)

**Justificativa:**
- `dict[str, ParkingSpot]`: lookup rápido por ID da vaga
- `dict[Vehicle, ParkingTicket]`: verificação O(1) se veículo está estacionado
- `list[ParkingTicket]`: histórico ordenado por tempo

**Alternativa rejeitada:** Tudo em uma única estrutura (mais complexo para queries diferentes)

## 2. Regras de Negócio

### Alocação de Vagas
**Decisão:** Match exato de tamanho (STRICT)

```python
def _find_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
    required_size = ParkingSpot.VEHICLE_TYPE_TO_SPOT_SIZE[vehicle.vehicle_type]
    return next(
        (s for s in self.spots.values() if s.is_available and s.size == required_size),
        None
    )
```

**Justificativa:**
- Evita desperdício de vagas grandes para veículos pequenos
- Previsibilidade nas operações
- Pode ser facilmente modificado para permitir "upgrade" se necessário

### Cálculo de Preço
**Decisão:** 30 minutos grátis + cobrança por hora cheia

```python
if duration <= 0.5:
    return 0
return ceil(duration) * SPOT_FEE_HOUR[spot_size]
```

**Justificativa:**
- Incentiva visitas curtas (clientes rápidos)
- `ceil()` simplifica cobrança (sem centavos)
- Valores diferenciados por tamanho refletem custo real do espaço

## 3. Padrões de Design Aplicados

### Strategy Pattern (Implícito)
- Diferentes preços por tipo de vaga
- Fácil adicionar novas estratégias de pricing (hora do dia, dia da semana)

### Factory Pattern (Potencial)
Pode ser adicionado facilmente:
```python
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str, license_plate: str) -> Vehicle:
        if vehicle_type == "CAR":
            return Car(license_plate)
        # ...
```

## 4. Tratamento de Erros

**Decisão:** Exceções explícitas com mensagens claras

```python
if vehicle in self.open_tickets:
    raise ValueError(f"Vehicle {vehicle.license_plate} is already parked")
```

**Justificativa:**
- Fail-fast: detecta erros imediatamente
- Mensagens informativas para debugging
- Permite tratamento específico pelo cliente

## 5. Type Hints

**Decisão:** Type hints completos em todos os métodos

**Justificativa:**
- Documentação viva do código
- Detecção de erros em tempo de desenvolvimento (mypy)
- Melhor IDE autocomplete