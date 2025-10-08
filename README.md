# 🎯 Object-Oriented Design Patterns

> 10 classic OOD systems implemented in Python for senior interview preparation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)

---

## 📚 System Index

### ⭐ Level 1: Simple Systems (Week 1)

| # | System | Patterns | Status |
|---|---------|----------|--------|
| 01 | [Parking Lot System](./01-parking-lot) | Strategy, Factory, Singleton | 🟡 In Progress |
| 02 | [Library Management](./02-library-management) | Repository, Observer |  🟢 Complete |
| 03 | [Vending Machine](./03-vending-machine) | State, Command | 🔴 Pending |
| 04 | [ATM System](./04-atm-system) | Chain of Responsibility, Strategy | 🔴 Pending |

### ⭐⭐ Level 2: Intermediate Systems (Week 2)

| # | System | Patterns | Status |
|---|---------|----------|--------|
| 05 | [Coffee Machine](./05-coffee-machine) | Builder, Decorator | 🔴 Pending |
| 06 | [Deck of Cards / Blackjack](./06-deck-of-cards) | Template Method, Strategy | 🔴 Pending |
| 07 | [Movie Ticket Booking](./07-movie-booking) | Facade, Observer | 🔴 Pending |

### ⭐⭐⭐ Level 3: Complex Systems (Week 3)

| # | System | Patterns | Status |
|---|---------|----------|--------|
| 08 | [Elevator System](./08-elevator-system) | Strategy, State, SCAN | 🔴 Pending |
| 09 | [Uber Design](./09-uber-design) | Strategy, Observer, Matching | 🔴 Pending |
| 10 | [Social Network](./10-social-network) | Observer, Composite, Proxy | 🔴 Pending |

**Legend:** 🔴 Pending | 🟡 In Progress | 🟢 Complete

---

## 🎨 Design Patterns Covered

| Pattern | Category | Used In | Purpose |
|---------|-----------|----------|-----------|
| **Strategy** | Behavioral | Parking, ATM, Elevator, Uber | Interchangeable algorithms |
| **Factory Method** | Creational | Parking | Object creation without specifying exact class |
| **Singleton** | Creational | Parking | Ensure single instance |
| **State** | Behavioral | Vending, Elevator | Change behavior based on state |
| **Observer** | Behavioral | Library, Movie, Uber, Social | Notify dependents of changes |
| **Builder** | Creational | Coffee | Build complex objects step by step |
| **Decorator** | Structural | Coffee | Add responsibilities dynamically |
| **Repository** | Architectural | Library | Data persistence abstraction |
| **Command** | Behavioral | Vending | Encapsulate requests as objects |
| **Chain of Responsibility** | Behavioral | ATM | Pass request through handler chain |
| **Template Method** | Behavioral | Deck of Cards | Define algorithm skeleton |
| **Facade** | Structural | Movie | Simplified interface for subsystem |
| **Composite** | Structural | Social Network | Treat individual objects and compositions uniformly |
| **Proxy** | Structural | Social Network | Control access to objects |

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Type Hints:** Full typing with `mypy`
- **Testing:** `pytest` with coverage > 80%
- **Formatting:** `black` + `isort`
- **Linting:** `ruff`
- **Documentation:** Markdown + Mermaid diagrams

---

## 📁 Standard Structure for Each System

```
XX-system-name/
├── README.md                 # Complete system documentation
├── design-decisions.md       # Architectural decisions and trade-offs
├── diagrams/
│   ├── class-diagram.md     # Class diagram (Mermaid)
│   └── sequence-diagram.md  # Sequence diagrams
├── src/
│   ├── __init__.py
│   ├── models.py            # Domain classes
│   ├── services.py          # Business logic
│   ├── patterns/            # Design pattern implementations
│   │   ├── __init__.py
│   │   ├── strategy.py
│   │   └── factory.py
│   └── exceptions.py        # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_integration.py
└── requirements.txt         # Specific dependencies (if any)
```

---

## 🎯 Learning Objectives

- ✅ Identify when to apply each design pattern
- ✅ Write SOLID, clean, and maintainable code
- ✅ Document architectural decisions with justifications
- ✅ Think about scalability and extensibility
- ✅ Master type hints and advanced Python
- ✅ Practice TDD and comprehensive testing
- ✅ Prepare for system design interviews

---

## 🚀 Quick Start

### Prerequisites

```bash
python --version  # Python 3.11 or higher
```

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/ood-design-patterns.git
cd ood-design-patterns

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test
pytest 01-parking-lot/tests/ -v
```

### Check Code Quality

```bash
# Type checking
mypy .

# Linting
ruff check .

# Formatting
black --check .
isort --check .
```

---

## 📊 Overall Progress

```
Complete Systems: 0/10 (0%)
Tests Written: 0/10 (0%)
Documentation: 0/10 (0%)
```

**Last updated:** 10/08/2025

---

## 📖 Resources and References

### Books
- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/0596007124/)
- [Design Patterns: Elements of Reusable OO Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612) (Gang of Four)
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) - Robert C. Martin

### Online
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Videos
- [NeetCode - Object Oriented Design Interview Questions](https://www.youtube.com/c/NeetCode)
- [Gaurav Sen - System Design](https://www.youtube.com/c/GauravSensei)

---

## 📝 Notes

This repository is part of a structured 45-day plan for senior backend interview preparation (October-December 2025). Each system is developed with attention to:

- **SOLID Principles**
- **Appropriate Design Patterns**
- **Type Safety** (mypy strict mode)
- **Testability** (TDD when possible)
- **Clear documentation**
- **Performance considerations**

---

## 📫 Contact

If you found this repository useful, consider giving it a ⭐!

For questions or suggestions:
- Open an [issue](https://github.com/your-username/ood-design-patterns/issues)
- Connect on [LinkedIn](https://linkedin.com/in/your-profile)

---

**Status:** 🚧 Active development (Oct-Dec 2025)
