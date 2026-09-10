from dataclasses import dataclass

from application.services.account_management_service import AccountManagementService
from application.services.auth_service import AuthService
from application.services.banking_operations_service import BankingOperationsService
from application.services.onboarding_service import OnboardingService


@dataclass(frozen=True, slots=True)
class ServiceContainerDTO:
    """Immutable application services registry passed to presentation controllers.

    Defined by the presentation layer to establish the dependency injection contract
    required by the composition root (main.py). Envelops all active application service
    instances needed to orchestrate terminal navigation, authentication, financial
    transactions, and administrative account workflows.

    Attributes:
        account_management_service (AccountManagementService): Application service
            handling password updates, account unfreezing, and closure operations.
        auth_service (AuthService): Application service managing authentication,
            lobby access, and vault authorization workflows.
        banking_service (BankingOperationsService): Application service executing
            deposits, gatekept withdrawals, statements, and summary projections.
        onboarding_service (OnboardingService): Application service orchestrating
            account holder creation and account registration workflows.
    """

    account_management_service: AccountManagementService
    auth_service: AuthService
    banking_service: BankingOperationsService
    onboarding_service: OnboardingService
