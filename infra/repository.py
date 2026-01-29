import json
from pathlib import Path
from typing import Any

from domain.bank import Bank

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class JsonRepository:
    """
    Handles the persistence layer for Bank entities using JSON files.

    This class acts as an interface between the Domain/Application layers and
    the File System. It implements the 'Repository Pattern' using static methods
    to provide stateless access to data storage.

    Responsibility:
        - Path management using pathlib.
        - Serialization (Object -> JSON).
        - Deserialization & Bootstrapping (JSON -> Object).
    """

    @staticmethod
    def _get_file_path(bank_code: str) -> Path:
        """Generates the standardized file path for a given bank branch code."""
        return DATA_DIR / f"{bank_code}.json"

    @staticmethod
    def save(bank: Bank) -> None:
        """
        Serializes the Bank entity and commits it to the disk.

        This method employs a 'Write-Through' strategy, overwriting the existing
        JSON file with the current state of the Bank object. It uses UTF-8
        encoding and indentation for human-readability.

        Args:
            bank (Bank): The bank instance to be persisted.
        """
        file_path = JsonRepository._get_file_path(bank.bank_branch_code)
        bank_dict = bank.to_dict()

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(bank_dict, file, indent=4)

    @staticmethod
    def load(bank_init_data: dict[str, Any]) -> Bank:
        """
        Retrieves a Bank entity from storage or bootstraps a new one.

        This method implements a 'Lazy Initialization' logic:
        1. Checks if a persistence file exists for the given branch code.
        2. If YES: Loads, deserializes, and rehydrates the Bank object.
        3. If NO: Instantiates a fresh Bank using the provided config data,
           immediately persists it to create the file, and returns the new object.

        Args:
            bank_init_data (dict): Configuration dictionary containing keys that
                MUST match the Bank.__init__ arguments (e.g., 'bank_name', 'branch_code').

        Returns:
            Bank: The fully initialized Bank ready for operation.
        """
        branch_code = bank_init_data["branch_code"]
        file_path = JsonRepository._get_file_path(branch_code)

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                bank_data = json.load(file)
                bank_obj = Bank.from_dict(bank_data)
                return bank_obj

        bank_obj = Bank(**bank_init_data)
        JsonRepository.save(bank_obj)
        return bank_obj
