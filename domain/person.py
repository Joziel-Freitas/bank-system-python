"""
Person and Client Domain Entities.

Defines the abstract base class Person, the concrete entity Client, and the
AccountCard value object. This module is responsible for validating core
personal attributes (Name, CPF, Birth Date), managing the client's associated
bank accounts, and storing access credentials (cards) for quick login.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import ClassVar, NamedTuple

from infra import verify
from shared import validators
from shared.exceptions import (
    InvalidBirthDateError,
    InvalidNameError,
    PersonAccountNotFoundError,
    PersonCardNotFoundError,
    PersonDuplicatedCardError,
    PersonInvalidAccountError,
    PersonRegisteredAccountError,
)

from .account import Account


class AccountCard(NamedTuple):
    """
    Immutable value object representing the credentials for quick account access.
    Acts as a 'saved card' in the client's wallet.
    """

    client_cpf: str
    branch_code: str
    account_num: str

    def __repr__(self) -> str:
        """Technical representation for debugging."""
        return (
            f"AccountCard(client_cpf={self.client_cpf!r}, "
            f"branch_code={self.branch_code!r}, "
            f"account_num={self.account_num!r})"
        )

    def __str__(self) -> str:
        """User-friendly string representation for UI/Menus."""
        return (
            f"CPF: {self.client_cpf} | Ag: {self.branch_code} Conta: {self.account_num}"
        )


class Person(ABC):
    """
    Abstract Base Class for any person entity in the system.

    Handles the validation and management of core human attributes like
    name, birth date, and CPF (Brazilian Individual Taxpayer Registry).
    """

    MIN_AGE: ClassVar[int] = 18
    MAX_AGE: ClassVar[int] = 120

    # Type hints for the instance's variables
    _name: str
    _birth_date: date
    _cpf: str

    def __init__(self, name: str, birth_date: str, cpf: str):
        """
        Initializes a Person instance with validated attributes.

        Args:
            name (str): The person's full name.
            birth_date (str): The person's date of birth in 'dd/mm/yyyy' string format.
            cpf (str): The person's CPF string (11 digits).

        Raises:
            InvalidNameError: If the name is invalid.
            InvalidBirthDateError: If the date format is wrong or is a future date.
            InvalidCpfError: If the CPF is mathematically invalid or poorly formatted.
        """
        self.name = name
        self._birth_date = Person.validate_birth_date(birth_date)
        self._cpf = validators.validate_cpf(cpf)

    def __repr__(self) -> str:
        """
        Returns the canonical string representation of the Person.

        Converts the internal date object back to the string format required
        by the __init__ method to ensure reproducibility.
        """
        class_name = type(self).__name__
        birth_date_str = self._birth_date.strftime("%d/%m/%Y")

        return f"{class_name}(name={self._name!r}, birth_date={birth_date_str!r}, cpf={self._cpf!r})"

    @property
    def name(self) -> str:
        """Returns the person's name."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets the person's name after validation.

        Args:
            name (str): The new name string.

        Raises:
            InvalidNameError: If the new name fails validation.
        """
        self._name = Person.validate_name(name)

    @property
    def birth_date(self) -> date:
        """Returns the person's birth date"""
        return self._birth_date

    @property
    def age(self) -> int:
        """Returns the person's current age in years."""
        return self._calculate_age(self._birth_date)

    @abstractmethod
    def has_account(self, account: Account) -> bool:
        """
        Abstract method to check if a specific account belongs to this person.

        Concrete implementations must provide the logic to verify the existence
        of the provided account within the person's registry of associated accounts.

        Args:
            acc (Account): The account instance to verify.

        Returns:
            bool: True if the account is associated with this person, False otherwise.
        """
        raise NotImplementedError()

    @staticmethod
    def validate_name(name: str) -> str:
        """
        Validates the provided name string based on length and character type rules.

        Rules:
        - Must be a string.
        - Must have at least three letters.
        - Cannot start or end with a blank space.
        - Must contain only alphabetic characters (spaces allowed internally).

        Args:
            name (str): The name to validate.

        Returns:
            str: The validated name.

        Raises:
            InvalidNameError: If any validation rule is violated.
        """
        error_msg: str | None = None

        if not isinstance(name, str):
            error_msg = f"Value {name} must be a string"
        elif len(name) < 3:
            error_msg = f"Value {name} must have a least three letters"
        elif name.startswith(" ") or name.endswith(" "):
            error_msg = f"Value {name} cannot start or end with blank space"
        elif not name.replace(" ", "").isalpha():
            error_msg = f"Value {name} must have only alphabetic characters"

        if error_msg is not None:
            raise InvalidNameError(error_msg)

        return name

    @staticmethod
    def _calculate_age(birth_date: date) -> int:
        """
        Calculates the person's age in years based on the birth date.
        Returns:
            int: The calculated age.
        """
        today = date.today()
        age = today.year - birth_date.year

        # Adjust age if the birth date for the current year has not yet passed
        if (today.day, today.month) < (birth_date.day, birth_date.month):
            age -= 1

        return age

    @staticmethod
    def validate_birth_date(birth_date: str) -> date:
        """
        Validates and converts the birth date string to a date object.

        This method enforces strict validation rules:
        1. Must be a string in 'dd/mm/yyyy' format.
        2. Cannot be a future date.
        3. The resulting age must be within the allowed range (`Person.MIN_AGE` to `Person.MAX_AGE`).

        Args:
            birth_date (str): The date string to validate.

        Returns:
            date: The validated date object.

        Raises:
            InvalidBirthDateError: If the format is incorrect, the date is in the future,
                                   or the calculated age is outside the valid limits.
        """
        try:
            verify.verify_instance(birth_date, str)
            birth_date_obj = datetime.strptime(birth_date, "%d/%m/%Y").date()
            today = date.today()

            if birth_date_obj > today:
                raise ValueError("Date of birth cannot be in the future")

            age = Person._calculate_age(birth_date_obj)

            if not Person.MIN_AGE <= age <= Person.MAX_AGE:
                raise ValueError(
                    f"Invalid age. Age must be between {Person.MIN_AGE} and {Person.MAX_AGE} (inclusive)"
                )

            return birth_date_obj
        except verify.VERIFY_ERRORS as e:
            raise InvalidBirthDateError(
                f"Value {birth_date} is invalid for date of birth. Cause: {e}"
            ) from e


class Client(Person):
    """
    A concrete implementation of Person, representing a bank client.

    Manages a set of associated accounts and a collection of quick-access
    cards (AccountCard) for streamlined authentication.
    """

    client_personal_accounts: set[Account]
    _account_cards: list[AccountCard]

    def __init__(self, name: str, birth_date: str, cpf: str):
        """
        Initializes a Client instance.

        Initializes the set of personal accounts and the card list as empty.
        """

        super().__init__(name, birth_date, cpf)

        self.client_personal_accounts = set()
        self._account_cards = []

    def __eq__(self, other: object) -> bool:
        """
        Determines equality between Client instances based on their unique CPF.

        Two Client objects are considered equal if they share the same CPF,
        regardless of other attributes. This definition of equality is consistent
        with the `__hash__` method, ensuring reliable behavior when Client objects
        are stored in hash-based collections such as sets or used as dictionary keys.
        """
        if isinstance(other, Client):
            return self._cpf == other._cpf
        return False

    def __hash__(self):
        """
        Returns a hash value for the Client instance based on its unique CPF.

        This ensures that Client objects can be used reliably as keys in
        dictionaries or stored in sets. The hash is consistent with the
        `__eq__` method, which also defines equality by CPF, guaranteeing
        that two Client instances with the same CPF are treated as identical
        in hash-based collections.
        """
        return hash(self._cpf)

    def __contains__(self, account: Account) -> bool:
        """
        Allows checking if an account is registered to this client using the `in` operator.

        The check leverages the O(1) average time complexity of Python's Set
        membership test. The account identity is based on its branch code and
        account number, as defined in Account's `__hash__` and `__eq__`.
        """
        if isinstance(account, Account):
            return account in self.client_personal_accounts
        return False

    @property
    def client_cpf(self) -> str:
        """Returns the client's unique identifier (the CPF)."""
        return self._cpf

    @property
    def cards(self) -> list[AccountCard]:
        """
        Returns a copy of the client's list of saved account cards.

        Returns:
            list[AccountCard]: A shallow copy of the stored cards.
        """
        return self._account_cards.copy()

    def has_account(self, account: Account) -> bool:
        """Checks if a specific account is registered to the client (alias for `__contains__`)."""
        return account in self

    def add_account(self, account: Account) -> None:
        """
        Adds a new unique Account instance to the client's list of personal accounts.

        Internal Logic:
            Uses `self.has_account(account)` to verify if the association already exists
            before attempting to add to the internal set.

        Args:
            account (Account): The account instance to add.

        Raises:
            PersonInvalidAccountError: If the provided object is not an instance of Account.
            PersonRegisteredAccountError: If `has_account()` returns True, indicating the
                account is already associated with this client.
        """
        if not isinstance(account, Account):
            raise PersonInvalidAccountError("Only instances of Account can be added.")

        if self.has_account(account):
            raise PersonRegisteredAccountError(
                f"Account {account} already associated with this client."
            )

        self.client_personal_accounts.add(account)

    def remove_account(self, account) -> None:
        """
        Removes an associated account from the client's registry.

        Args:
            account (Account): The account instance to remove.

        Raises:
            PersonAccountNotFoundError: If the account is not found in the client's list.
        """
        if account not in self.client_personal_accounts:
            raise PersonAccountNotFoundError("Account not found")

        self.client_personal_accounts.remove(account)

    def add_card(self, acc_card: AccountCard):
        """
        Stores a new access card in the client's wallet.

        Args:
            acc_card (AccountCard): The card object containing credentials.

        Raises:
            TypeError: If the input is not an instance of AccountCard.
            PersonDuplicatedCardError: If the card is already present in the wallet.
        """
        if not isinstance(acc_card, AccountCard):
            raise TypeError(
                f"Invalid card type. Expected AccountCard, got {type(acc_card).__name__}"
            )
        if acc_card in self._account_cards:
            raise PersonDuplicatedCardError(
                " Card already present in the Client's card collection"
            )

        self._account_cards.append(acc_card)

    def remove_card(self, acc_card: AccountCard):
        """
        Removes a specific card from the client's wallet.

        Args:
            acc_card (AccountCard): The card to be removed.

        Raises:
            TypeError: If the input is not an instance of AccountCard.
            PersonCardNotFoundError: If the card is not found in the wallet.
        """
        if not isinstance(acc_card, AccountCard):
            raise TypeError(
                f"Invalid card type. Expected AccountCard, got {type(acc_card).__name__}"
            )
        if acc_card not in self._account_cards:
            raise PersonCardNotFoundError(
                "Card not found in the Client's card collection"
            )

        self._account_cards.remove(acc_card)
