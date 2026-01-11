"""

Exercício com Abstração, Herança, Encapsulamento e Polimorfismo
Criar um sistema bancário (extremamente simples) que tem clientes, contas e
um banco. A ideia é que o cliente tenha uma conta (poupança ou corrente) e que
possa sacar/depositar nessa conta. Contas corrente tem um limite extra.

Conta (ABC)
    ContaCorrente
    ContaPoupanca

Pessoa (ABC)
    Cliente
        Cliente -> Conta

Banco
    Banco -> Cliente
    Banco -> Conta

Dicas:
Criar classe Cliente que herda da classe Pessoa (Herança)
    Pessoa tem nome e idade (com getters)
    Cliente TEM conta (Agregação da classe ContaCorrente ou ContaPoupanca)
Criar classes ContaPoupanca e ContaCorrente que herdam de Conta
    ContaCorrente deve ter um limite extra
    Contas têm agência, número da conta e saldo
    Contas devem ter método para depósito
    Conta (super classe) deve ter o método sacar abstrato (Abstração e
    polimorfismo - as subclasses que implementam o método sacar)
Criar classe Banco para AGREGAR classes de clientes e de contas (Agregação)
Banco será responsável autenticar o cliente e as contas da seguinte maneira:
    Banco tem contas e clientes (Agregação)
    * Checar se a agência é daquele banco
    * Checar se o cliente é daquele banco
    * Checar se a conta é daquele banco
Só será possível sacar se passar na autenticação do banco (descrita acima)
Banco autentica por um método.


Application Entry Point.

This module serves as the Composition Root of the system. It is responsible for:
1. Displaying the initial UI (Welcome Banner).
2. Resolving the initial dependencies (creating the Bank Model).
3. Injecting the Model into the Controller.
4. Managing the application lifecycle loop, ensuring the system returns
   to the start menu after a session ends unless the user explicitly exits.
"""

import sys
from functools import partial

from app.controllers import BankSystemController
from domain.bank import Bank
from infra import config, verify
from infra.io_utils import get_single_input, validate_entry
from infra.views import bye, welcome
from shared.exceptions import UserAbortError
from shared.validators import ValidatorCallback, boolean_validator_dec

BANK_VALIDATOR: dict[str, ValidatorCallback] = {
    "bank": boolean_validator_dec(
        partial(verify.verify_interval, min_val=1, max_val=2)
    ),
}


def _get_bank_obj() -> Bank | None:
    """
    Prompts the user to select the operating Bank entity.

    Uses the generic I/O utilities (`get_single_input`) to validate the input
    against the configured options (1 or 2). Maps the selection to a concrete
    Bank instance with predefined branch codes.

    Returns:
        Bank | None: The initialized Bank object if selected, or None
                     if the user chooses to abort (UserAbortError).

    Raises:
        RuntimeError: If the input utility returns an unexpected type.
    """
    bank_mapper = {
        1: {"bank_name": "Banco do Dev S.A.", "branch_code": "1234"},
        2: {"bank_name": "Banco do Analista S.A.", "branch_code": "4321"},
    }
    validation_callback = partial(validate_entry, validation_mapper=BANK_VALIDATOR)

    key = "bank"
    field_config = config.initial_config

    try:
        option = get_single_input(key, field_config, validation_callback)
        if isinstance(option, int):
            return Bank(**bank_mapper[option])
        raise RuntimeError("Invalid input type")
    except UserAbortError:
        return None


def main() -> None:
    """
    Main execution loop.

    Orchestrates the high-level application flow:
    1. UI Setup: Shows welcome message via `infra.views`.
    2. Model Instantiation: Calls `_get_bank_obj` to create the Bank.
    3. Exit Check: Terminates the program gracefully (`sys.exit`) if Bank
       selection is aborted.
    4. Controller Execution: Instantiates `BankSystemController` injecting the
       Bank model (Dependency Injection) and runs the application logic.
    5. Loop: Repeats the process when the controller returns control, allowing
       users to switch banks or restart without reloading the script.
    """
    while True:
        welcome()
        bank_obj = _get_bank_obj()
        if bank_obj is None:
            bye()
            sys.exit()

        controller_obj = BankSystemController(bank_obj)
        controller_obj.run_controller()


if __name__ == "__main__":
    main()
