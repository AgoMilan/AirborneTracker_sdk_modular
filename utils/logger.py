# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 23:04:54 2025

@author: Milan
"""

# utils/logger.py
import logging
import os
from datetime import datetime

class Logger:
    """
    Jednoduchý wrapper kolem Python logging modulu.
    Umožňuje logování do konzole i do souboru podle konfigurace.
    """

    def __init__(self, log_to_console=True, log_to_file=True, log_file_path="data/logs/tracker_log.txt"):
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path

        self.logger = logging.getLogger("AirborneTracker")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []  # reset (pro případ opakované inicializace)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # --- Konzolový výstup ---
        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # --- Souborový výstup ---
        if self.log_to_file:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

            # Každý den nový log soubor
            base, ext = os.path.splitext(self.log_file_path)
            dated_file = f"{base}_{datetime.now().strftime('%Y%m%d')}{ext}"

            file_handler = logging.FileHandler(dated_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"[Logger] Logování do souboru: {dated_file}")

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, msg, level="info"):
        """Univerzální logovací metoda kompatibilní s původní verzí."""
        level = level.lower()
        if level == "info":
            self.info(msg)
        elif level == "warning":
            self.warning(msg)
        elif level == "error":
            self.error(msg)
        elif level == "debug":
            self.debug(msg)
        elif level == "critical":
            self.critical(msg)
        else:
            self.logger.info(msg)