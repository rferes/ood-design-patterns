# 🎯 Object-Oriented Design Patterns

> 10 sistemas clássicos de OOD implementados em Python para preparação de entrevistas senior

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)

---

## 📚 Índice de Sistemas

### ⭐ Nível 1: Sistemas Simples (Semana 1)

| # | Sistema | Patterns | Status |
|---|---------|----------|--------|
| 01 | [Parking Lot System](./01-parking-lot) | Strategy, Factory, Singleton | 🔴 Pendente |
| 02 | [Library Management](./02-library-management) | Repository, Observer | 🔴 Pendente |
| 03 | [Vending Machine](./03-vending-machine) | State, Command | 🔴 Pendente |
| 04 | [ATM System](./04-atm-system) | Chain of Responsibility, Strategy | 🔴 Pendente |

### ⭐⭐ Nível 2: Sistemas Intermediários (Semana 2)

| # | Sistema | Patterns | Status |
|---|---------|----------|--------|
| 05 | [Coffee Machine](./05-coffee-machine) | Builder, Decorator | 🔴 Pendente |
| 06 | [Deck of Cards / Blackjack](./06-deck-of-cards) | Template Method, Strategy | 🔴 Pendente |
| 07 | [Movie Ticket Booking](./07-movie-booking) | Facade, Observer | 🔴 Pendente |

### ⭐⭐⭐ Nível 3: Sistemas Complexos (Semana 3)

| # | Sistema | Patterns | Status |
|---|---------|----------|--------|
| 08 | [Elevator System](./08-elevator-system) | Strategy, State, SCAN | 🔴 Pendente |
| 09 | [Uber Design](./09-uber-design) | Strategy, Observer, Matching | 🔴 Pendente |
| 10 | [Social Network](./10-social-network) | Observer, Composite, Proxy | 🔴 Pendente |

**Legenda:** 🔴 Pendente | 🟡 Em andamento | 🟢 Completo

---

## 🎨 Design Patterns Cobertos

| Pattern | Categoria | Usado em | Propósito |
|---------|-----------|----------|-----------|
| **Strategy** | Comportamental | Parking, ATM, Elevator, Uber | Algoritmos intercambiáveis |
| **Factory Method** | Criacional | Parking | Criação de objetos sem especificar classe exata |
| **Singleton** | Criacional | Parking | Garantir única instância |
| **State** | Comportamental | Vending, Elevator | Alterar comportamento baseado em estado |
| **Observer** | Comportamental | Library, Movie, Uber, Social | Notificar dependentes de mudanças |
| **Builder** | Criacional | Coffee | Construir objetos complexos passo a passo |
| **Decorator** | Estrutural | Coffee | Adicionar responsabilidades dinamicamente |
| **Repository** | Arquitetural | Library | Abstração de persistência de dados |
| **Command** | Comportamental | Vending | Encapsular requisições como objetos |
| **Chain of Responsibility** | Comportamental | ATM | Passar requisição por cadeia de handlers |
| **Template Method** | Comportamental | Deck of Cards | Definir esqueleto de algoritmo |
| **Facade** | Estrutural | Movie | Interface simplificada para subsistema |
| **Composite** | Estrutural | Social Network | Tratar objetos individuais e composições uniformemente |
| **Proxy** | Estrutural | Social Network | Controlar acesso a objetos |

---

## 🛠️ Stack Técnica

- **Linguagem:** Python 3.11+
- **Type Hints:** Tipagem completa com `mypy`
- **Testes:** `pytest` com cobertura > 80%
- **Formatação:** `black` + `isort`
- **Linting:** `ruff`
- **Documentação:** Markdown + diagramas Mermaid

---

## 📁 Estrutura Padrão de Cada Sistema

```
XX-nome-sistema/
├── README.md                 # Documentação completa do sistema
├── design-decisions.md       # Decisões arquiteturais e trade-offs
├── diagrams/
│   ├── class-diagram.md     # Diagrama de classes (Mermaid)
│   └── sequence-diagram.md  # Diagramas de sequência
├── src/
│   ├── __init__.py
│   ├── models.py            # Classes de domínio
│   ├── services.py          # Lógica de negócio
│   ├── patterns/            # Implementações de design patterns
│   │   ├── __init__.py
│   │   ├── strategy.py
│   │   └── factory.py
│   └── exceptions.py        # Exceções customizadas
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_integration.py
└── requirements.txt         # Dependências específicas (se houver)
```

---

## 🎯 Objetivos de Aprendizado

- ✅ Identificar quando aplicar cada design pattern
- ✅ Escrever código SOLID, limpo e manutenível
- ✅ Documentar decisões arquiteturais com justificativas
- ✅ Pensar em escalabilidade e extensibilidade
- ✅ Dominar type hints e Python avançado
- ✅ Praticar TDD e testes abrangentes
- ✅ Preparar para system design interviews

---

## 🚀 Quick Start

### Pré-requisitos

```bash
python --version  # Python 3.11 ou superior
```

### Instalação

```bash
# Clonar repositório
git clone https://github.com/seu-username/ood-design-patterns.git
cd ood-design-patterns

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Rodar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Teste específico
pytest 01-parking-lot/tests/ -v
```

### Verificar Code Quality

```bash
# Type checking
mypy .

# Linting
ruff check .

# Formatação
black --check .
isort --check .
```

---

## 📊 Progresso Geral

```
Sistemas Completos: 0/10 (0%)
Testes Escritos: 0/10 (0%)
Documentação: 0/10 (0%)
```

**Última atualização:** 08/10/2025

---

## 📖 Recursos e Referências

### Livros
- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/0596007124/)
- [Design Patterns: Elements of Reusable OO Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612) (Gang of Four)
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) - Robert C. Martin

### Online
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Vídeos
- [NeetCode - Object Oriented Design Interview Questions](https://www.youtube.com/c/NeetCode)
- [Gaurav Sen - System Design](https://www.youtube.com/c/GauravSensei)

---

## 📝 Notas

Este repositório faz parte de um plano estruturado de 45 dias para preparação de entrevistas senior backend (Outubro-Dezembro 2025). Cada sistema é desenvolvido com atenção a:

- **SOLID Principles**
- **Design Patterns apropriados**
- **Type Safety** (mypy strict mode)
- **Testabilidade** (TDD quando possível)
- **Documentação clara**
- **Performance considerations**

---

## 📫 Contato

Se você achou este repositório útil, considere dar uma ⭐!

Para dúvidas ou sugestões:
- Abra uma [issue](https://github.com/seu-username/ood-design-patterns/issues)
- Conecte-se no [LinkedIn](https://linkedin.com/in/seu-perfil)

---

**Status:** 🚧 Em desenvolvimento ativo (Out-Dez 2025)
