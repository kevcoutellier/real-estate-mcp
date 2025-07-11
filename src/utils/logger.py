#!/usr/bin/env python3
"""
Configuration du système de logging pour le MCP Real Estate
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger avec un format standardisé
    
    Args:
        name: Nom du logger (généralement __name__)
        level: Niveau de logging (par défaut INFO)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Configuration du handler console
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Ajout du handler au logger
    logger.addHandler(handler)
    logger.setLevel(level)
    
    # Éviter la propagation vers le logger parent
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un nouveau
    
    Args:
        name: Nom du logger
    
    Returns:
        Logger configuré
    """
    return setup_logger(name)


# Logger par défaut pour le module
default_logger = setup_logger(__name__)
