# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 11:07:49 2025

@author: Milan
"""

import os
import logging
from datetime import datetime

def setup_logger(log_dir="data/logs", log_filename_prefix="tracker_log"):
    """
    Inicializuje logger pro aplikaci.
    Vytváří adresář pro logy, zapisuje do souboru i do konzole.
    """
    # Vytvoření adresáře pro logy
    os.makedirs(log_dir, exist_ok=True)

    # Název log souboru podle aktuálního data
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{log_filename_prefix}_{timestamp}.txt")

    # Nastavení loggeru
    logger = logging.getLogger("AirborneTracker")
    logger.setLevel(logging.INFO)

    # Odstranění předchozích handlerů, pokud existují
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formát zpráv
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

    # Souborový handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Konzolový handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"[Logger] Logování do souboru: {log_file}")
    return logger
