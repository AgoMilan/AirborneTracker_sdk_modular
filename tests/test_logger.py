# tests/test_logger.py
import os
import re
import pytest
from utils.logger import Logger

@pytest.fixture
def setup_logger(tmp_path):
    """Fixture pro vytvoření loggeru v dočasném adresáři."""
    log_file_path = tmp_path / "test_log.txt"
    logger = Logger(
        log_to_console=False,   # nechceme spamovat konzoli během testů
        log_to_file=True,
        log_file_path=str(log_file_path)
    )
    return logger, log_file_path

def test_logger_creates_file(setup_logger):
    """Ověř, že logger vytvoří log soubor."""
    logger, log_file_path = setup_logger
    logger.info("Testovací zpráva - vytvoření souboru")

    # najdi nejnovější soubor (má datum v názvu)
    log_dir = log_file_path.parent
    files = list(log_dir.glob("test_log_*.txt"))
    assert len(files) == 1, "Log soubor nebyl vytvořen!"
    assert files[0].exists(), "Log soubor neexistuje!"

def test_logger_writes_message(setup_logger):
    """Ověř, že logger skutečně zapíše zprávu."""
    logger, log_file_path = setup_logger
    msg = "Testovací zpráva - zápis obsahu"
    logger.info(msg)

    files = list(log_file_path.parent.glob("test_log_*.txt"))
    assert files, "Log soubor nebyl vytvořen."
    with open(files[0], "r", encoding="utf-8") as f:
        content = f.read()

    assert msg in content, "Log zpráva nebyla nalezena v souboru!"

def test_logger_format(setup_logger):
    """Ověř formát log řádku (čas + úroveň + zpráva)."""
    logger, log_file_path = setup_logger
    logger.warning("Formátovací test")

    files = list(log_file_path.parent.glob("test_log_*.txt"))
    with open(files[0], "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Najdi řádek s textem testu
    target_line = None
    for line in lines:
        if "Formátovací test" in line:
            target_line = line.strip()
            break

    assert target_line, "Řádek s testovací zprávou nebyl nalezen v logu."

    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| WARNING\s+\| Formátovací test$"
    assert re.match(pattern, target_line), f"Formát logu je chybný: {target_line}"



