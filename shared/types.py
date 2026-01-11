"""
Shared Types and Enumerations Module.

This module defines common type aliases, enumerations, and constants used across
the banking system architecture. It serves as a single source of truth for
domain-specific values (like transaction types) and error context categories,
promoting type safety and reducing the usage of magic strings and numbers.
"""

from enum import IntEnum, StrEnum


class TransactionType(IntEnum):
    """
    Enumeration representing the supported types of financial transactions.

    Attributes:
        WITHDRAW (1): Represents a money withdrawal operation.
        DEPOSIT (2): Represents a money deposit operation.
        STATEMENT (3): Represents a bank statement inquiry.
    """

    WITHDRAW = 1
    DEPOSIT = 2
    STATEMENT = 3


class OperationType(IntEnum):
    """Enumeration representing the high-level operations available in the main system menu.

    Unlike 'TransactionType', which defines specific financial actions within an account,
    this enum controls the primary navigation flow of the application, routing the user
    to different controllers or administrative tasks.

    Attributes:
        TRANSACTION (1): Initiates the financial transaction workflow (Deposit, Withdraw, Statement).
        UNFREEZE (2): Triggers the administrative process to reactivate a frozen account.
        CLOSE (3): Triggers the irreversible process of closing the user's bank account
                   and removing their data (subject to business rules like zero balance).
    """

    TRANSACTION = 1
    UNFREEZE = 2
    CLOSE = 3


class ErrorContext(StrEnum):
    """
    Base enumeration for error mapping contexts.

    Inherits from StrEnum to ensure all members are treated as native strings,
    allowing direct comparison and usage in string-based logic (e.g., dictionary lookups)
    while maintaining the benefits of strict enumeration.
    """

    pass


class ControllerErrorContext(ErrorContext):
    """
    Defines high-level error contexts for the Bank System Controller workflow.

    Used to categorize errors during the main application lifecycle, allowing
    the orchestrator to distinguish between failures in entity creation (onboarding),
    session establishment (login), and service execution (operations).

    Attributes:
        REGISTER: Context for failures during client or account creation/registration.
        LOGIN: Context for authentication failures or session initialization issues.
        OPERATION: Context for failures during the execution of banking services (Transaction, Unfreeze, Close).
    """

    REGISTER = "register"
    LOGIN = "login"
    OPERATION = "operation"


class PersonContext(ErrorContext):
    """
    Defines error contexts for method-level failures in the Person/Client entity.

    Attributes:
        ACCOUNT: Context for errors involving account associations or validation within a Person.
    """

    ACCOUNT = "account"


class AccountContext(ErrorContext):
    """
    Defines error contexts for method-level failures in the Account entity.

    Attributes:
        VALUE: Context for invalid monetary values (e.g., negative deposit, insufficient funds).
        BLOCKED: Context for operations rejected due to the account being frozen or inactive.
    """

    VALUE = "value"
    BLOCKED = "blocked"


class BankContext(ErrorContext):
    """
    Defines error contexts for method-level failures in the Bank service layer.

    Attributes:
        PASSWORD: Context for password validation or authentication errors.
        CLIENT: Context for errors related to Client entity management (e.g., duplication).
        ACCOUNT: Context for errors related to Account entity management (e.g., aggregation).
        TOKEN: Context for security token validation failures or session integrity issues.
    """

    PASSWORD = "password"
    CLIENT = "client"
    ACCOUNT = "account"
    TOKEN = "token"
