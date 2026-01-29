"""
Application Entry Point.

This module serves as the Composition Root of the system. It is responsible for:
1. Displaying the initial UI (Welcome Banner).
2. Resolving the initial dependencies (Configuring the Bank Model).
3. Hydrating the Model via Repository (Load/Bootstrap).
4. Injecting dependencies (Model + Repository) into the Controller.
5. Managing the application lifecycle loop.
"""

import sys
from functools import partial

from app.controllers import BankSystemController
from infra import config, verify
from infra.io_utils import get_single_input, validate_entry
from infra.repository import JsonRepository
from infra.views import bye, welcome
from shared.exceptions import UserAbortError
from shared.validators import ValidatorCallback, boolean_validator_dec

AVAILABLE_BANKS: dict[int, dict[str, str]] = {
    1: {"bank_name": "Banco do Dev S.A.", "branch_code": "1234"},
    2: {"bank_name": "Banco do Analista S.A.", "branch_code": "4321"},
}

BANK_VALIDATOR: dict[str, ValidatorCallback] = {
    "bank": boolean_validator_dec(
        partial(verify.verify_interval, min_val=1, max_val=len(AVAILABLE_BANKS))
    ),
}


def _get_bank_init_data() -> dict[str, str] | None:
    """
    Prompts the user to select the operating Bank entity.

    Interacts with the user to select a valid bank ID and returns the
    corresponding configuration dictionary required to bootstrap the Bank.

    Returns:
        dict[str, str] | None: The bank configuration dictionary (name, branch_code)
                               if selected, or None if aborted.
    """
    validation_callback = partial(validate_entry, validation_mapper=BANK_VALIDATOR)

    key = "bank"
    field_config = config.initial_config

    try:
        option = get_single_input(key, field_config, validation_callback)
        if isinstance(option, int):
            return AVAILABLE_BANKS[option]
        raise RuntimeError("Invalid input type")
    except UserAbortError:
        return None


def main() -> None:
    """
    Main execution loop.

    Orchestrates the high-level application flow:
    1. UI Setup: Shows welcome message.
    2. Configuration: Gets user selection for the Bank.
    3. Hydration: Delegates to `JsonRepository.load` to get the Bank object
       (either loaded from disk or created fresh).
    4. Dependency Injection: Instantiates `BankSystemController`, injecting
       both the `bank_obj` (Model) and `JsonRepository` (Persistence).
    5. Loop: Maintains the session until explicit exit.
    """
    while True:
        welcome()
        init_data = _get_bank_init_data()

        if init_data is None:
            bye()
            sys.exit()

        bank_obj = JsonRepository.load(init_data)
        controller_obj = BankSystemController(bank_obj, JsonRepository)
        controller_obj.run_controller()


if __name__ == "__main__":
    main()
