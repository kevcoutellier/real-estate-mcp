#!/usr/bin/env python3
"""
Configuration du logging pour le projet MCP Real Estate
"""

import logging
import sys
from datetime import datetime

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger pour le module spécifié
    
    Args:
        name: Nom du module
        level: Niveau de logging (défaut: INFO)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Créer un handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger
