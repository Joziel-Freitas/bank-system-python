"""
Bank Management Module.

This module defines the central 'Bank' class, which acts as an aggregate root
for Clients and Accounts. It is responsible for:
1. Storing and managing the lifecycle of Client and Account entities.
2. Validating business rules regarding account ownership and access.
3. Authenticating users and granting access to sensitive operations.

The Bank enforces strict consistency rules, ensuring that every client is
properly linked to their accounts and that security credentials (passwords)
are validated before access is granted.
"""

from typing import NamedTuple

from infra import verify
from shared.exceptions import (
    AccountAlreadyActiveError,
    AccountNotFoundError,
    BankPasswordError,
    BankSecurityError,
    BlockedAccountError,
    ClientNotFoundError,
    DuplicatedAccountError,
    DuplicatedClientError,
    NotEmptyAccountError,
)

from .account import Account
from .person import AccountCard, Client, Person


class AuthToken(NamedTuple):
    """
    Represents a secure access token for stateless authentication.

    Attributes:
        client_cpf (str): The client's unique identifier.
        branch_code (str): The branch code associated with the session.
        account_num (str): The account number associated with the session.
        signature (bool): A validity flag indicating if the token was formally
            issued by the Bank (True) or instantiated externally (False).
            Defaults to False.
    """

    client_cpf: str
    branch_code: str
    account_num: str
    signature: bool = False


class Bank:
    """
    Represents a banking institution that aggregates Clients and Accounts.

    The Bank maintains the relationships between clients, their accounts, and
    security credentials. It uses a complex internal mapping to allow clients
    to possess multiple accounts, distinguished by unique passwords.

    This class operates in a stateless manner regarding user sessions, issuing
    secure tokens for authentication instead of maintaining internal flags.

    Attributes:
        _bank_name (str): The name of the bank.
        _bank_branch_code (str): The 4-digit branch identifier for this bank instance.
        _bank_clients (dict[str, Client]): Registry of clients indexed by CPF.
        _bank_accounts (dict[tuple[str, str], Account]): Registry of accounts
            indexed by (branch_code, account_number).
        _associated_clients (dict[str, dict[str, tuple[str, str]]]):
            Mapping structure: {client_cpf: {password: (branch, account_num)}}.
            Links a client to specific accounts via passwords.
    """

    _bank_name: str
    _bank_branch_code: str
    _bank_clients: dict[str, Client]
    _bank_accounts: dict[tuple[str, str], Account]
    _associated_clients: dict[str, dict[str, tuple[str, str]]]
    _access_attempts: dict[str, int]

    def __init__(self, bank_name: str, branch_code: str):
        """
        Initializes a new Bank instance.

        Args:
            bank_name (str): The name of the institution.
            branch_code (str): The 4-digit numeric string representing the branch.

        Raises:
            TypeError: If arguments are not strings.
            ValueError: If branch_code does not have exactly 4 digits.
        """
        verify.verify_instance(bank_name, str)
        self._bank_name = bank_name

        verify.verify_instance(branch_code, str)
        verify.verify_digits(branch_code, 4)
        self._bank_branch_code = branch_code

        self._bank_clients = {}
        self._bank_accounts = {}
        self._associated_clients = {}
        self._access_attempts = {}

    def __repr__(self) -> str:
        """
        Returns a summary string representation of the Bank.

        Note: Due to the complexity and potential size of the Bank entity,
        this __repr__ does NOT return a strictly reproducible string (eval-safe).
        Instead, it provides a 'Snapshot' of the bank's current load and identity,
        which is optimized for debugging lifecycle and state issues.
        """

        class_name = type(self).__name__
        num_clients = len(self._bank_clients)
        num_accounts = len(self._bank_accounts)
        num_flagged = len(self._access_attempts)

        return (
            f"{class_name}(name={self._bank_name!r}), "
            f"clients={num_clients!r}, accounts={num_accounts!r}, monitored_users={num_flagged}"
        )

    def __contains__(self, item: Client | Account) -> bool:
        """
        Checks if a Client or Account is registered in the bank.

        Polymorphic behavior:
        - If item is Client: Checks existence by CPF.
        - If item is Account: Checks existence by (branch, number) key.

        Args:
            item (Client | Account): The entity to check.

        Returns:
            bool: True if registered, False otherwise.
        """
        match item:
            case Client():
                client_cpf = item.client_cpf
                return client_cpf in self._bank_clients
            case Account():
                branch_account = (item.branch_code, item.account_num)
                return branch_account in self._bank_accounts
            case _:
                return False

    @property
    def bank_name(self) -> str:
        """Returns the bank's name."""
        return self._bank_name

    @property
    def bank_branch_code(self) -> str:
        """Returns the bank's branch code."""
        return self._bank_branch_code

    @staticmethod
    def _extract_client_key(client_obj: Client) -> str:
        """Helper to extract the unique key (CPF) from a Client object."""
        return client_obj.client_cpf

    @staticmethod
    def _extract_account_key(account_obj: Account) -> tuple[str, str]:
        """Helper to extract the unique key (Branch, Number) from an Account object."""
        return (account_obj.branch_code, account_obj.account_num)

    @staticmethod
    def validate_password(password: str) -> None:
        """
        Validates the format of a password.

        Args:
            password (str): The password string to validate.

        Raises:
            BankPasswordError: If the password is not a string or not 6 digits.
        """
        try:
            verify.verify_instance(password, str)
            verify.verify_digits(password, 6)
        except verify.VERIFY_ERRORS as e:
            raise BankPasswordError(f"Invalid password. Cause: {e}")

    def _validate_client(self, client: Client) -> None:
        """
        Validates if a client is suitable for registration (not duplicated).

        Args:
            client (Client): The client instance.

        Raises:
            DuplicatedClientError: If the client is already registered.
        """
        verify.verify_instance(client, Client)
        if client in self:
            raise DuplicatedClientError("Client already registered")

    def _validate_account(self, account: Account) -> None:
        """
        Validates if an account is suitable for registration (not duplicated).

        Args:
            account (Account): The account instance.

        Raises:
            DuplicatedAccountError: If the account is already registered.
        """
        verify.verify_instance(account, Account)
        if account in self:
            raise DuplicatedAccountError("Account already registered")

    def _associate(
        self, client_key: str, account_key: tuple[str, str], password: str
    ) -> None:
        """
        Links an account to a client using a password as the unique key.

        Internal method used during aggregation. It ensures that a specific
        password maps to a specific account for a given client.

        Args:
            client_key (str): The client's CPF.
            account_key (tuple[str, str]): The account's (branch, number).
            password (str): The 6-digit password for this specific link.

        Raises:
            BankPasswordError: If the password is already in use for another account
                belonging to this client.
        """

        client_accounts = self._associated_clients.setdefault(client_key, {})

        if password in client_accounts:
            raise BankPasswordError(
                "Password already linked to this CPF. The password must be unique"
            )

        client_accounts[password] = account_key

    def _agg_client(self, client_key: str, client_to_agg: Client) -> None:
        """Stores the client object in the internal registry."""
        self._bank_clients[client_key] = client_to_agg

    def _agg_account(self, account_key, account_to_agg: Account) -> None:
        """Stores the account object in the internal registry."""
        self._bank_accounts[account_key] = account_to_agg

    def _check_access(self, token: AuthToken) -> None:
        """
        Performs preliminary security and integrity checks before password validation.

        Implements the 'Fail Fast' pattern by rejecting invalid tokens, structural
        inconsistencies, or frozen accounts immediately, preventing unnecessary
        processing of passwords.

        Args:
            token (AuthToken): The authentication token to be validated.

        Raises:
            BankSecurityError: If the token signature is missing or invalid.
            RuntimeError: If the client data is corrupted or missing from internal maps.
            BlockedAccountError: If the target account is frozen (is_active=False).
        """
        if not token.signature:
            raise BankSecurityError("Invalid token! The token must be signed by Bank")

        if token.client_cpf not in self._associated_clients:
            raise RuntimeError("No associated account found in _associated_clients.")

        target_key = (token.branch_code, token.account_num)

        if target_key not in self._bank_accounts:
            raise RuntimeError("Token points to a non-existent account (Stale Token).")

        target_account = self._bank_accounts[target_key]

        if not target_account.is_active:
            raise BlockedAccountError(
                "Account is frozen due to security reasons. Access denied"
            )

    def _reset_password(
        self, client_cpf: str, account_key: tuple[str, str], new_password: str
    ) -> None:
        """
        Helper method to safely replace the password linked to a specific account.

        Locates the old password key associated with the given account, removes it,
        and establishes a new association using the provided new password.
        """
        client_accounts = self._associated_clients[client_cpf]
        old_pwd = None

        for pwd, acc_key in client_accounts.items():
            if acc_key == account_key:
                old_pwd = pwd
                break

        if old_pwd:
            del client_accounts[old_pwd]

        self._associate(client_cpf, account_key, new_password)

    def _issue_card(
        self, client_cpf: str, branch_code: str, account_num: str
    ) -> AccountCard:
        """
        Factory method that generates a new access card (Value Object).

        Creates an immutable AccountCard containing the essential credentials
        (CPF, Branch, Account Number) required for future 'Quick Login' operations.

        Args:
            client_cpf (str): The client's unique identifier.
            branch_code (str): The branch code.
            account_num (str): The account number.

        Returns:
            AccountCard: The populated card instance.
        """
        return AccountCard(
            client_cpf=client_cpf,
            branch_code=branch_code,
            account_num=account_num,
        )

    def authenticate(
        self, client_cpf: str, branch_code: str, account_num: str
    ) -> AuthToken | None:
        """
        Verifies credentials and issues a secure access token.

        Checks if the provided branch matches the bank's branch, and if both
        client and account are valid and registered within the system.
        This method is stateless and does not alter the internal state of the Bank.

        Args:
            client_cpf (str): The client's CPF.
            branch_code (str): The specific branch code of the account.
            account_num (str): The account number.

        Returns:
            AuthToken | None: A signed (signature=True) AuthToken object if
            authentication succeeds, None otherwise.
        """
        valid_branch = self._bank_branch_code == branch_code
        registered_client = client_cpf in self._bank_clients
        account_id = (branch_code, account_num)
        registered_account = account_id in self._bank_accounts

        if all([valid_branch, registered_client, registered_account]):
            return AuthToken(
                client_cpf=client_cpf,
                branch_code=branch_code,
                account_num=account_num,
                signature=True,
            )
        return None

    def get_client(self, client_cpf: str) -> Client:
        """
        Retrieves the Client object associated with the provided CPF.

        Args:
            client_cpf (str): The client's unique CPF.

        Returns:
            Client: The registered Client object.

        Raises:
            ClientNotFoundError: If the CPF is not registered in the bank.
        """
        if client_cpf not in self._bank_clients:
            raise ClientNotFoundError(
                "Not client registered under this CPF. Verify CPF"
            )
        client_obj = self._bank_clients[client_cpf]

        return client_obj

    def get_account(self, token: AuthToken, password: str) -> Account:
        """
        Retrieves the Account object associated with the client and password.

        Delegates preliminary security checks to '_check_access()' and focuses
        on password validation and access attempt monitoring. Handles account
        freezing logic upon repeated failed attempts.

        Args:
            token (AuthToken): The security token issued during authentication.
            password (str): The password linked to the desired account.

        Returns:
            Account: The Account object if found and authorized.

        Raises:
            BankSecurityError: If the token signature is invalid or a cross-access
                attempt is detected.
            BlockedAccountError: If the account is frozen due to security.
            AccountNotFoundError: If the password does not match any account.
            RuntimeError: If internal data integrity is compromised.
        """
        self._check_access(token)
        Bank.validate_password(password)

        client_accounts = self._associated_clients[token.client_cpf]
        account_key = client_accounts.get(password)

        self._access_attempts.setdefault(token.client_cpf, 0)

        if account_key is None:
            self._access_attempts[token.client_cpf] += 1
            if self._access_attempts[token.client_cpf] >= 3:
                target_key = (token.branch_code, token.account_num)
                target_account = self._bank_accounts[target_key]
                target_account.freeze()
                raise BlockedAccountError(
                    "Account is frozen due to security reasons. Access denied"
                )

            raise AccountNotFoundError(
                "No account associated to this password in _associated_clients."
            )

        if account_key != (token.branch_code, token.account_num):
            raise BankSecurityError("Cross-access attempt detected!")

        self._access_attempts[token.client_cpf] = 0
        account_obj = self._bank_accounts[account_key]

        return account_obj

    def agg_new_client(
        self, new_client: Client, new_account: Account, password: str
    ) -> None:
        """
        Registers a new Client along with their first Account.

        This method performs an atomic registration operation: validation,
        association, storage of both entities, and bidirectional linking.
        Finally, it issues a 'Quick Access Card' and adds it to the client's wallet.

        Args:
            new_client (Client): The new client instance.
            new_account (Account): The new account instance.
            password (str): The password to access this account.

        Raises:
            DuplicatedClientError: If client already exists.
            DuplicatedAccountError: If account already exists.
            BankPasswordError: If password format is invalid.
        """
        self._validate_client(new_client)
        self._validate_account(new_account)
        Bank.validate_password(password)

        client_obj_key = Bank._extract_client_key(new_client)
        account_obj_key = Bank._extract_account_key(new_account)

        self._associate(client_obj_key, account_obj_key, password)

        self._agg_client(client_obj_key, new_client)
        self._agg_account(account_obj_key, new_account)

        new_card = self._issue_card(
            client_cpf=new_client.client_cpf,
            branch_code=new_account.branch_code,
            account_num=new_account.account_num,
        )

        new_client.add_account(new_account)
        new_client.add_card(new_card)

    def agg_new_account(
        self, client_cpf: str, new_account: Account, password: str
    ) -> None:
        """
        Adds a new Account to an existing Client.

        Validates the client existence, registers the new account in the bank,
        issues a new 'Quick Access Card', and updates the client's internal
        list of accounts and cards.

        Args:
            client_cpf (str): The CPF of the existing client.
            new_account (Account): The new account instance.
            password (str): The password to access this new account.

        Raises:
            ClientNotFoundError: If the client CPF is not found.
            DuplicatedAccountError: If account already exists.
            BankPasswordError: If password is invalid or already used.
        """
        if client_cpf not in self._associated_clients:
            raise ClientNotFoundError(
                "Not client registered under this CPF. Verify CPF"
            )
        self._validate_account(new_account)
        Bank.validate_password(password)

        new_account_key = Bank._extract_account_key(new_account)

        self._associate(client_cpf, new_account_key, password)
        self._agg_account(new_account_key, new_account)

        new_card = self._issue_card(
            client_cpf=client_cpf,
            branch_code=new_account.branch_code,
            account_num=new_account.account_num,
        )
        client_obj = self.get_client(client_cpf)
        client_obj.add_account(new_account)
        client_obj.add_card(new_card)

    def unfreeze_account(
        self, token: AuthToken, client_name: str, birth_date: str, new_password: str
    ) -> bool:
        """
        Unlocks a frozen account and resets its password after verifying personal data.

        Implements Knowledge-Based Authentication (KBA). Verifies the client's
        Identity (Name and Birth Date) before allowing the password reset and
        account reactivation.

        It applies a 'Fail-Fast' check to ensure the account is actually
        frozen before processing any validation logic.

        Args:
            token (AuthToken): The active session token.
            client_name (str): The name provided for verification.
            birth_date (str): The birth date string ('dd/mm/yyyy').
            new_password (str): The new password to be set.

        Returns:
            bool: True if verification succeeds and account is unlocked.
                  False if Name or Birth Date do not match records.

        Raises:
            AccountAlreadyActiveError: If the account is fully operational (not frozen).
            BankPasswordError: If the new password format is invalid.
        """
        account_key = (token.branch_code, token.account_num)
        account_obj = self._bank_accounts[account_key]

        if account_obj.is_active:
            raise AccountAlreadyActiveError("Account is already active.")

        name = Person.validate_name(client_name)
        date = Person.validate_birth_date(birth_date)
        Bank.validate_password(new_password)

        client_obj = self._bank_clients[token.client_cpf]

        if (name, date) != (client_obj.name, client_obj.birth_date):
            return False

        self._reset_password(token.client_cpf, account_key, new_password)

        account_obj.unfreeze()
        self._access_attempts[token.client_cpf] = 0

        return True

    def close_account(self, token: AuthToken, password: str) -> None:
        """
        Permanently closes an account and removes all its system associations.

        This operation enforces strict business rules: the account must have a
        balance of zero (no funds and no debts). It relies on `get_account`
        to validate security credentials (Token + Password).

        Upon closure, the account is removed from the registry, and the
        associated 'Quick Access Card' is automatically identified via the
        session token and removed from the client's wallet.

        If the closed account is the last one associated with the client,
        the client entity is also removed from the bank's registry to maintain
        data consistency.

        Args:
            token (AuthToken): The active session token identifying the account owner.
            password (str): The password linked to the account (required for confirmation).

        Raises:
            NotEmptyAccountError: If the account has a positive balance or negative debt.
            BankSecurityError: If the token is invalid.
            BlockedAccountError: If the account is currently frozen.
            AccountNotFoundError: If the password is incorrect.
            ClientNotFoundError: If the client data is corrupted.
        """

        account_obj = self.get_account(token, password)
        account_key = (token.branch_code, token.account_num)

        if account_obj.balance != 0:
            raise NotEmptyAccountError(
                "Impossible to close an account with non-zero balance"
            )

        client_obj = self.get_client(token.client_cpf)
        client_accounts = self._associated_clients[token.client_cpf]

        client_obj.remove_account(account_obj)
        for card in client_obj.cards:
            if (card.client_cpf, card.branch_code, card.account_num) == (
                token.client_cpf,
                token.branch_code,
                token.account_num,
            ):
                client_obj.remove_card(card)
        del self._bank_accounts[account_key]
        del client_accounts[password]

        if len(client_accounts) == 0:
            del self._bank_clients[token.client_cpf]
            del self._associated_clients[token.client_cpf]
