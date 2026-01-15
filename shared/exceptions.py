"""
Central module for all custom exceptions in the banking domain.

This module establishes a clear, hierarchical structure for all custom errors,
allowing consumers (like the Bank service layer or API handlers) to easily catch
and categorize exceptions.

It integrates with `shared.types` to provide context-aware error mapping,
distinguishing between:
1.  **Attribute Errors:** Mapped to raw strings that match configuration keys (e.g., "cpf"),
    enabling direct lookup in validation schemas.
2.  **Method/Logic Errors:** Mapped to typed Enums (e.g., `BankContext.CLIENT`),
    enabling robust control flow decisions in Controllers.
"""

# Imports context enums for method-level error mapping
from shared.types import (
    AccountContext,
    BankContext,
    ControllerErrorContext,
    ErrorContext,
    PersonContext,
)


class DomainError(Exception):
    """Base exception for all domain-specific errors (entities and services)."""


class UserAbortError(Exception):
    """
    Raised when the user intentionally aborts an operation (e.g., types 'S').

    This is a Control Flow exception, not a Business Logic error.
    It should bypass validation retry loops and be caught by the main controller loop.
    """


# --- Module-Level Base Exceptions ---


class ControllerError(DomainError):
    """Base exception for all errors originating from the Controller layer logic."""


class ControllerRegisterError(ControllerError):
    """
    Raised when the entity creation or registration process fails.

    Indicates that the user failed to complete the instantiation of a Person
    or Account, or the Bank rejected the registration (e.g., duplication),
    preventing the system from storing the new data.
    """


class ControllerLoginError(ControllerError):
    """
    Raised when the authentication handshake fails or is aborted.

    Prevents the transition to the authorized session state. This encompasses
    invalid credentials, exhausted retry attempts, frozen account detection
    during login, or user cancellation at the credential prompt.
    """


class ControllerOperationError(ControllerError):
    """
    Raised when a high-level banking operation fails to complete.

    Used to signal that a specific workflow (Transaction, Unfreeze, Close Account)
    was interrupted or encountered a critical state preventing its conclusion,
    requiring control to return to the main session menu.
    """


# --- Service Layer Exceptions (Bank) ---


class BankError(DomainError):
    """Base exception for errors related to the Bank service layer."""


class BankSecurityError(BankError):
    """Raised when the authentication token does not match the target account ID"""


class BankAttributeError(BankError):
    """Base exception for validation errors on Bank attributes (e.g., name)."""


class BankMethodError(BankError):
    """Base exception for errors during Bank operations (e.g., registering entities)."""


class BankNameError(BankAttributeError):
    """Raised when the Bank's name is invalid."""


class DuplicatedClientError(BankMethodError):
    """Raised when a Client is already registered in Bank."""


class DuplicatedAccountError(BankMethodError):
    """Raised when an Account is already registered in the Bank."""


class BankPasswordError(BankMethodError):
    """Raised when a Bank password validation or authentication fails."""


class ClientNotFoundError(BankMethodError):
    """Raised when a client is not found in the Bank's central registry."""


class AccountNotFoundError(BankMethodError):
    """Raised when an account is not found in the Bank's central registry."""


class NotEmptyAccountError(BankMethodError):
    """Raised when attempting to close an account with a non-zero balance."""


class AccountAlreadyActiveError(BankMethodError):
    """Raised when trying to unfreeze an account that is fully operational."""

    pass


# --- Entity Layer Exceptions (Person/Client) ---


class PersonError(DomainError):
    """Base exception for errors related to the Person/Client entity."""


class PersonAttributeError(PersonError):
    """Base exception for validation errors on Person attributes (name, CPF, birth date)."""


class InvalidNameError(PersonAttributeError):
    """Raised when a person's name does not meet validation criteria (e.g., length, characters)."""


class InvalidBirthDateError(PersonAttributeError):
    """Raised when the birth date format or value is invalid (e.g., future date, wrong format)."""


class InvalidCpfError(PersonAttributeError):
    """Raised when a CPF is invalid due to format, type, or checksum failure."""


class PersonMethodError(PersonError):
    """Base exception for errors during Person/Client operations/methods."""


class PersonRegisteredAccountError(PersonMethodError):
    """Raised when an attempt is made to add an Account that is already associated with the Client."""


class PersonInvalidAccountError(PersonMethodError):
    """Raised when a non-Account object is passed where an Account instance is expected."""


class PersonAccountNotFoundError(PersonMethodError):
    """Raised when attempting to access or remove an account not associated with the person."""


class PersonDuplicatedCardError(PersonMethodError):
    """Raised when an attempt is made to add an AccountCard that is already present in the Client's collection."""


class PersonCardNotFoundError(PersonMethodError):
    """Raised when attempting to access or remove an AccountCard that is not found in the Client's collection."""


# --- Entity Layer Exceptions (Account) ---


class AccountError(DomainError):
    """Base exception for errors related to the Account entity."""


class BlockedAccountError(AccountError):
    """Raised when an operation is attempted on a frozen/blocked account."""


class AccountAttributeError(AccountError):
    """Base exception for validation errors on Account attributes (branch, number, balance)."""


class AccountMethodError(AccountError):
    """Base exception for errors during Account operations/methods (deposit, withdraw)."""


class InvalidBranchError(AccountAttributeError):
    """Raised for an invalid branch code (format or length)."""


class InvalidAccountError(AccountAttributeError):
    """Raised for an invalid account number (format or length)."""


class InvalidBalanceError(AccountAttributeError):
    """Raised for an invalid account balance (e.g., negative initial balance)."""


class InvalidWithdrawError(AccountMethodError):
    """Raised when a withdrawal amount is invalid (e.g., insufficient funds or non-positive value)."""


class InvalidDepositError(AccountMethodError):
    """Raised when a deposit amount is invalid (e.g., non-positive value)."""


# --- Error Metadata Mappers (Used for generic error handling/translation) ---

type ErrorMapType = (
    dict[type[DomainError], str] | dict[type[DomainError], dict[type[DomainError], str]]
)
# Maps Bank base errors to the specific attribute/method that caused them
BANK_ERROR_MAP: ErrorMapType = {
    BankAttributeError: {BankNameError: "name"},
    BankMethodError: {
        BankPasswordError: BankContext.PASSWORD,
        DuplicatedClientError: BankContext.CLIENT,
        ClientNotFoundError: BankContext.CLIENT,
        DuplicatedAccountError: BankContext.ACCOUNT,
        AccountNotFoundError: BankContext.ACCOUNT,
        BankSecurityError: BankContext.TOKEN,
    },
}

# Maps Person base errors to the specific attribute/method that caused them
PERSON_ERROR_MAP: ErrorMapType = {
    PersonAttributeError: {
        InvalidNameError: "name",
        InvalidBirthDateError: "birth_date",
        InvalidCpfError: "cpf",
    },
    PersonMethodError: {
        PersonInvalidAccountError: PersonContext.ACCOUNT,
        PersonRegisteredAccountError: PersonContext.ACCOUNT,
        PersonAccountNotFoundError: PersonContext.ACCOUNT,
    },
}

# Maps Account base errors to the specific attribute/method that caused them
ACCOUNT_ERROR_MAP: ErrorMapType = {
    AccountAttributeError: {
        InvalidBranchError: "branch_code",
        InvalidAccountError: "account_num",
        InvalidBalanceError: "balance",
    },
    AccountMethodError: {
        InvalidDepositError: AccountContext.VALUE,
        InvalidWithdrawError: AccountContext.VALUE,
    },
}

# Maps BankSystemController lifecycle errors to specific flow contexts
CONTROLLER_ERROR_MAP: ErrorMapType = {
    ControllerRegisterError: ControllerErrorContext.REGISTER,
    ControllerLoginError: ControllerErrorContext.LOGIN,
    ControllerOperationError: ControllerErrorContext.OPERATION,
}


def map_exceptions(
    exception_instance: DomainError, error_map: ErrorMapType
) -> str | ErrorContext:
    """
    Retrieves the configuration key or context string associated with a specific DomainError.

    This utility allows any component (Controllers, Main, etc.) to identify which
    input field or logic flow caused a domain validation failure.

    **Mapping Strategy:**
    - **Attributes:** Returns raw strings matching `system_config` keys (e.g., "cpf").
    - **Methods:** Returns Enum values (StrEnum) from `shared.types` for logic control.

    Args:
        exception_instance (DomainError): The caught exception instance.
        error_map (ErrorMapType): The mapping dictionary (flat or nested) linking Exceptions to keys/contexts.

    Returns:
        str: The configuration key string (e.g., "cpf") or the ErrorContext value.

    Raises:
        TypeError: If the exception type is not found in the provided map.
    """
    config_key = type(exception_instance)

    mapped_value = error_map.get(config_key)

    if isinstance(mapped_value, str):
        return mapped_value

    for error in error_map.values():
        if isinstance(error, dict) and config_key in error:
            return error[config_key]

    raise TypeError(f"Error not found: {config_key} not in {error_map}")
