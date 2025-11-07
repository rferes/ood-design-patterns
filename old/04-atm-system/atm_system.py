"""
ATM System - Senior Python Interview Project
============================================
Requirements:
- Implement classes: Account, ATM, Transaction
- Apply patterns: Chain of Responsibility, Strategy
- Features: withdrawal, deposit, balance inquiry
- Simple Tests

Design Patterns:
- Chain of Responsibility: Validation pipeline for transactions
- Strategy: Different transaction execution strategies
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4, UUID
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

# ========== CONSTANTS ==========
MIN_WITHDRAWAL_AMOUNT = Decimal('10.00')
MIN_DEPOSIT_AMOUNT = Decimal('0.01')
DECIMAL_PRECISION = Decimal('0.01')


# ========== EXCEPTIONS ==========
class ATMError(Exception):
    """Base exception for ATM operations"""
    pass


class AccountNotFound(ATMError):
    """Raised when bank account is not found in system"""
    pass


class InvalidAmountError(ATMError):
    """Raised when transaction amount is invalid"""
    pass


class InsufficientFundsError(ATMError):
    """Raised when account has insufficient funds for withdrawal"""
    pass


class ExceededWithdrawLimitError(ATMError):
    """Raised when withdrawal amount exceeds account limit"""
    pass


# ========== ENUMS ==========
class TransactionsType(Enum):
    """Types of transactions supported by the ATM"""
    WITHDRAWAL = 'WITHDRAWAL'
    DEPOSIT = 'DEPOSIT'
    BALANCE_INQUIRY = 'BALANCE_INQUIRY'


# ========== MODELS ==========
class Account:
    """
    Represents a bank account with balance and transaction history.
    """
    
    def __init__(
        self, 
        name: str, 
        account_code: str, 
        withdraw_limit: float = 100.0
    ) -> None:
        """Initialize a new bank account."""
        self.id: UUID = uuid4()
        self.name: str = name
        self.account_code: str = account_code
        self.balance: Decimal = self._to_decimal(0.0)
        self.transactions: dict[UUID, Transaction] = {}
        self.withdraw_limit: Decimal = self._to_decimal(withdraw_limit)

    @staticmethod
    def _to_decimal(value: float) -> Decimal:
        """Convert float to Decimal with proper rounding for currency"""
        return Decimal(str(value)).quantize(DECIMAL_PRECISION, ROUND_HALF_UP)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def debit(self, amount: Decimal) -> Decimal:
        """Subtract amount from account balance."""
        self.balance -= amount
        return self.balance

    def credit(self, amount: Decimal) -> Decimal:
        """Add amount to account balance."""
        self.balance += amount
        return self.balance

    def add_transaction(self, transaction: Transaction) -> None:
        """Add transaction to account history"""
        self.transactions[transaction.id] = transaction

    def __repr__(self) -> str:
        return (
            f"Account(id={self.id}, "
            f"name='{self.name}', "
            f"account_code='{self.account_code}', "
            f"balance={self.balance}, "
            f"withdraw_limit={self.withdraw_limit}, "
            f"transactions={len(self.transactions)})"
        )


@dataclass(frozen=True)
class Transaction:
    """
    Immutable record of a bank transaction.
    """
    type: TransactionsType
    amount: Decimal
    balance_after: Decimal
    account_id: UUID
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id}, "
            f"type={self.type.value}, "
            f"amount={self.amount}, "
            f"balance_after={self.balance_after}, "
            f"created_at={self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
        )


# ========== CHAIN OF RESPONSIBILITY PATTERN ==========
class ValidatorChain(ABC):
    """
    Abstract base class for validation chain.
    
    Implements Chain of Responsibility pattern for validating transactions.
    Each validator can pass the request to the next validator in the chain.
    """
    
    def __init__(self) -> None:
        self._next: ValidatorChain | None = None

    def set_next(self, validator: 'ValidatorChain') -> 'ValidatorChain':
        """Set the next validator in the chain (allows method chaining)."""
        self._next = validator
        return validator

    @abstractmethod
    def validate(self, account: Account, amount: Decimal) -> None:
        """
        Validate the transaction.
        
        Raises:
            ATMError: If validation fails
        """
        pass


class AmountValidatorChain(ValidatorChain):
    """Validates that withdrawal amount meets minimum requirements"""
    
    def validate(self, account: Account, amount: Decimal) -> None:
        """
        Validate withdrawal amount is positive and multiple of minimum.
        
        Raises:
            InvalidAmountError: If amount is invalid
        """
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than 0")

        if amount % MIN_WITHDRAWAL_AMOUNT != 0:
            raise InvalidAmountError(
                f"Amount must be multiple of ${MIN_WITHDRAWAL_AMOUNT}"
            )

        if self._next:
            self._next.validate(account, amount)


class BalanceValidatorChain(ValidatorChain):
    """Validates that account has sufficient funds"""
    
    def validate(self, account: Account, amount: Decimal) -> None:
        """
        Validate account has sufficient balance.
        
        Raises:
            InsufficientFundsError: If balance is insufficient
        """
        if account.balance < amount:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: {account.balance}, "
                f"Requested: {amount}"
            )

        if self._next:
            self._next.validate(account, amount)


class LimitValidatorChain(ValidatorChain):
    """Validates that withdrawal doesn't exceed account limit"""
    
    def validate(self, account: Account, amount: Decimal) -> None:
        """
        Validate withdrawal is within account limit.
        
        Raises:
            ExceededWithdrawLimitError: If amount exceeds limit
        """
        if amount > account.withdraw_limit:
            raise ExceededWithdrawLimitError(
                f"Withdrawal limit exceeded. Limit: {account.withdraw_limit}, "
                f"Requested: {amount}"
            )

        if self._next:
            self._next.validate(account, amount)


class DepositValidatorChain(ValidatorChain):
    """Validates that deposit amount is positive"""

    def validate(self, account: Account, amount: Decimal) -> None:
        """
        Validate deposit amount is positive.

        Raises:
            InvalidAmountError: If amount is invalid
        """
        if amount < MIN_DEPOSIT_AMOUNT:
            raise InvalidAmountError(
                f"Deposit amount must be at least ${MIN_DEPOSIT_AMOUNT}"
            )

        if self._next:
            self._next.validate(account, amount)


# ========== STRATEGY PATTERN ==========
class TransactionStrategy(ABC):
    """
    Abstract base class for transaction strategies.

    Implements Strategy pattern for different transaction types.
    Each strategy encapsulates the logic for executing a specific transaction.
    """

    @abstractmethod
    def execute(
        self, 
        account: Account, 
        amount: Decimal, 
        validator: ValidatorChain | None = None
    ) -> Decimal:
        """
        Execute the transaction and return the new balance.

        Raises:
            ATMError: If transaction fails
        """
        pass


class WithdrawalStrategy(TransactionStrategy):
    """Strategy for executing withdrawal transactions"""

    def execute(
        self, 
        account: Account, 
        amount: Decimal, 
        validator: ValidatorChain | None = None
    ) -> Decimal:
        """Execute withdrawal: validate, debit account, record transaction."""
        if validator:
            validator.validate(account, amount)

        new_balance = account.debit(amount)

        transaction = Transaction(
            type=TransactionsType.WITHDRAWAL,
            amount=amount,
            account_id=account.id,
            balance_after=new_balance
        )
        account.add_transaction(transaction)
        return new_balance


class DepositStrategy(TransactionStrategy):
    """Strategy for executing deposit transactions"""

    def execute(
        self,
        account: Account,
        amount: Decimal,
        validator: ValidatorChain | None = None
    ) -> Decimal:
        """Execute deposit: validate, credit account, record transaction."""
        if validator:
            validator.validate(account, amount)

        new_balance = account.credit(amount)

        transaction = Transaction(
            type=TransactionsType.DEPOSIT,
            amount=amount,
            account_id=account.id,
            balance_after=new_balance
        )
        account.add_transaction(transaction)
        return new_balance


class BalanceInquiryStrategy(TransactionStrategy):
    """Strategy for balance inquiry (no validation needed)"""

    def execute(
        self,
        account: Account,
        amount: Decimal = Decimal('0.00'),
        validator: ValidatorChain | None = None
    ) -> Decimal:
        """Execute balance inquiry: record transaction, return balance."""
        transaction = Transaction(
            type=TransactionsType.BALANCE_INQUIRY,
            amount=Decimal('0.00'),
            account_id=account.id,
            balance_after=account.balance
        )
        account.add_transaction(transaction)
        return account.balance


# ========== ATM MACHINE ==========
class ATMMachine:
    """
    ATM System for performing bank transactions.

    Supports withdrawal, deposit, and balance inquiry operations.
    Uses Chain of Responsibility for validation and Strategy pattern
    for transaction execution.

    Example:
        >>> atm = ATMMachine()
        >>> account = Account("John Doe", "12345", withdraw_limit=500.0)
        >>> account.balance = Decimal('1000.00')
        >>> atm.accounts["12345"] = account
        >>> balance = atm.withdrawal("12345", 100.0)
        >>> print(f"New balance: {balance}")
    """

    def __init__(self) -> None:
        """Initialize ATM with empty account registry and configure validators"""
        self.accounts: dict[str, Account] = {}

        # Configure withdrawal validation chain
        self.withdrawal_validator = AmountValidatorChain()
        self.withdrawal_validator\
            .set_next(BalanceValidatorChain())\
            .set_next(LimitValidatorChain())

        # Configure deposit validation chain
        self.deposit_validator = DepositValidatorChain()

        # Configure transaction strategies
        self.strategies: dict[str, TransactionStrategy] = {
            'withdrawal': WithdrawalStrategy(),
            'deposit': DepositStrategy(),
            'balance': BalanceInquiryStrategy()
        }

    def _get_account(self, account_code: str) -> Account:
        """
        Retrieve account by code.

        Raises:
            AccountNotFound: If account doesn't exist
        """
        account = self.accounts.get(account_code)
        if not account:
            raise AccountNotFound(
                f"Account '{account_code}' not found in bank system"
            )
        return account

    @staticmethod
    def _to_decimal(amount: float) -> Decimal:
        """Convert float to Decimal with proper currency precision"""
        return Decimal(str(amount)).quantize(DECIMAL_PRECISION, ROUND_HALF_UP)

    def withdrawal(self, account_code: str, amount: float) -> Decimal:
        """
        Withdraw money from account and return new balance.

        Raises:
            AccountNotFound: If account doesn't exist
            InvalidAmountError: If amount is invalid
            InsufficientFundsError: If balance is insufficient
            ExceededWithdrawLimitError: If amount exceeds limit
        """
        account = self._get_account(account_code)
        amount_decimal = self._to_decimal(amount)
        return self.strategies['withdrawal'].execute(
            account, amount_decimal, self.withdrawal_validator
        )

    def deposit(self, account_code: str, amount: float) -> Decimal:
        """
        Deposit money to account and return new balance.
        
        Raises:
            AccountNotFound: If account doesn't exist
            InvalidAmountError: If amount is invalid
        """
        account = self._get_account(account_code)
        amount_decimal = self._to_decimal(amount)
        return self.strategies['deposit'].execute(
            account, amount_decimal, self.deposit_validator
        )

    def balance_inquiry(self, account_code: str) -> Decimal:
        """
        Check account balance and return current balance.
        
        Raises:
            AccountNotFound: If account doesn't exist
        """
        account = self._get_account(account_code)
        return self.strategies['balance'].execute(account)

    def register_account(self, account: Account) -> None:
        """Register a new account in the ATM system."""
        self.accounts[account.account_code] = account


# ========== TESTS ==========
def test_atm_system() -> None:
    """
    Comprehensive test suite for ATM System.
    
    Tests all features required by the specification:
    - Withdrawal operations
    - Deposit operations
    - Balance inquiry
    - Error handling (validation chain)
    - Transaction history
    """
    print("=" * 70)
    print("ATM SYSTEM - COMPREHENSIVE TEST SUITE (REFACTORED)")
    print("=" * 70)
    
    # Setup
    atm = ATMMachine()
    account = Account("John Doe", "12345", withdraw_limit=500.0)
    account.balance = Decimal('1000.00')
    atm.register_account(account)
    
    # Test 1: Valid Withdrawal
    print("\n[TEST 1] Valid Withdrawal - $100")
    balance = atm.withdrawal("12345", 100.0)
    assert balance == Decimal('900.00')
    assert len(account.transactions) == 1
    print(f"✅ PASSED - New Balance: ${balance}")
    
    # Test 2: Valid Deposit
    print("\n[TEST 2] Valid Deposit - $200")
    balance = atm.deposit("12345", 200.0)
    assert balance == Decimal('1100.00')
    assert len(account.transactions) == 2
    print(f"✅ PASSED - New Balance: ${balance}")
    
    # Test 3: Balance Inquiry
    print("\n[TEST 3] Balance Inquiry")
    balance = atm.balance_inquiry("12345")
    assert balance == Decimal('1100.00')
    assert len(account.transactions) == 3
    print(f"✅ PASSED - Current Balance: ${balance}")
    
    # Test 4: Invalid Amount (not multiple of 10)
    print("\n[TEST 4] Invalid Amount - Not Multiple of $10")
    try:
        atm.withdrawal("12345", 35.0)
        assert False, "Should raise InvalidAmountError"
    except InvalidAmountError as e:
        print(f"✅ PASSED - Error caught: {e}")
    
    # Test 5: Insufficient Funds
    print("\n[TEST 5] Insufficient Funds")
    try:
        atm.withdrawal("12345", 5000.0)
        assert False, "Should raise InsufficientFundsError"
    except InsufficientFundsError as e:
        print(f"✅ PASSED - Error caught: {e}")
    
    # Test 6: Exceeded Withdraw Limit
    print("\n[TEST 6] Exceeded Withdraw Limit")
    try:
        atm.withdrawal("12345", 600.0)
        assert False, "Should raise ExceededWithdrawLimitError"
    except ExceededWithdrawLimitError as e:
        print(f"✅ PASSED - Error caught: {e}")
    
    # Test 7: Invalid Deposit (negative)
    print("\n[TEST 7] Invalid Deposit - Negative Amount")
    try:
        atm.deposit("12345", -50.0)
        assert False, "Should raise InvalidAmountError"
    except InvalidAmountError as e:
        print(f"✅ PASSED - Error caught: {e}")
    
    # Test 8: Account Not Found
    print("\n[TEST 8] Account Not Found")
    try:
        atm.withdrawal("99999", 100.0)
        assert False, "Should raise AccountNotFound"
    except AccountNotFound as e:
        print(f"✅ PASSED - Error caught: {e}")
    
    # Test 9: Transaction History Verification
    print("\n[TEST 9] Transaction History")
    assert len(account.transactions) == 3
    withdrawal_txs = [t for t in account.transactions.values() 
                      if t.type == TransactionsType.WITHDRAWAL]
    deposit_txs = [t for t in account.transactions.values() 
                   if t.type == TransactionsType.DEPOSIT]
    inquiry_txs = [t for t in account.transactions.values() 
                   if t.type == TransactionsType.BALANCE_INQUIRY]
    
    assert len(withdrawal_txs) == 1
    assert len(deposit_txs) == 1
    assert len(inquiry_txs) == 1
    print(f"✅ PASSED - {len(account.transactions)} transactions recorded")
    print(f"   • Withdrawals: {len(withdrawal_txs)}")
    print(f"   • Deposits: {len(deposit_txs)}")
    print(f"   • Inquiries: {len(inquiry_txs)}")
    
    # Test 10: Chain of Responsibility Order
    print("\n[TEST 10] Validation Chain Order")
    test_account = Account("Test User", "54321", withdraw_limit=100.0)
    test_account.balance = Decimal('50.00')
    atm.register_account(test_account)
    
    # Should fail at BalanceValidator before reaching LimitValidator
    try:
        atm.withdrawal("54321", 200.0)  # Exceeds both balance and limit
        assert False, "Should raise InsufficientFundsError"
    except InsufficientFundsError:
        print("✅ PASSED - Balance check occurs before limit check")
    
    print("\n" + "=" * 70)
    print("ALL 10 TESTS PASSED! ✨")
    print("=" * 70)
    
    # Display transaction details
    print("\n📋 TRANSACTION HISTORY FOR ACCOUNT 12345:")
    print("-" * 70)
    for transaction in account.transactions.values():
        print(f"  {transaction}")
    
    print(f"\n💰 Final Account State:")
    print(f"  {account}")


if __name__ == '__main__':
    test_atm_system()
