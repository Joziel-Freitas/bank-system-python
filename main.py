"""PyBank Application Entry Point (v3.0).

This module serves exclusively as the Composition Root of the system, adhering
strictly to the Dependency Inversion Principle. It contains no business logic,
state management, or I/O loops.

Core Responsibilities:
1. Configuration Binding: Reads environment variables and system settings.
2. Persistence Initialization: Instantiates the MySQL repository connection.
3. Security Bootstrapping: Prepares cryptographic hashers and token services.
4. Application Assembly: Instantiates services and packs them into ServiceContainerDTO.
5. Controller Orchestration: Injects services into TerminalController and runs Kiosk mode.
"""

from application.services.account_management_service import AccountManagementService
from application.services.auth_service import AuthService
from application.services.banking_operations_service import BankingOperationsService
from application.services.onboarding_service import OnboardingService
from infra.mysql_repository import MySQLRepository
from infra.security import PasswordHasher, TokenService
from presentation.controllers.terminal_controller import TerminalController
from presentation.dtos import ServiceContainerDTO
from settings import BANK_SECRET_KEY, LOBBY_TIME_SECONDS, VAULT_TIME_SECONDS


def main() -> None:
    """Bootstraps and executes the application.

    Instantiates the foundational layers (Infrastructure -> Application -> Presentation)
    in a strict 'Bottom-Up' approach, culminating in the execution of the main
    ATM kiosk loop.
    """
    # --------------------------------------------------------------------------
    # 1. Infrastructure Layer Setup
    # --------------------------------------------------------------------------
    pwd_hasher = PasswordHasher()
    token_svc = TokenService(
        secret_key=BANK_SECRET_KEY,
        lobby_time_seconds=LOBBY_TIME_SECONDS,
        vault_time_seconds=VAULT_TIME_SECONDS,
    )
    repository = MySQLRepository()

    # --------------------------------------------------------------------------
    # 2. Application Layer Services Assembly
    # --------------------------------------------------------------------------
    account_management_svc = AccountManagementService(
        hasher=pwd_hasher, repository=repository, token_service=token_svc
    )
    auth_svc = AuthService(
        hasher=pwd_hasher, repository=repository, token_service=token_svc
    )
    banking_svc = BankingOperationsService(
        hasher=pwd_hasher, repository=repository, token_service=token_svc
    )
    onboarding_svc = OnboardingService(hasher=pwd_hasher, repository=repository)

    # --------------------------------------------------------------------------
    # 3. Presentation Layer Dependency Injection & Kiosk Execution
    # --------------------------------------------------------------------------
    terminal = TerminalController(
        services=ServiceContainerDTO(
            account_management_service=account_management_svc,
            auth_service=auth_svc,
            banking_service=banking_svc,
            onboarding_service=onboarding_svc,
        )
    )

    terminal.run_controller()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise RuntimeError(
            "Major system error. Impossible to initialize the system."
        ) from e
