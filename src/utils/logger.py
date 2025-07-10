"""
Configuration du système de logging pour le MCP Real Estate
"""

import logging
import os
from datetime import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger pour le module spécifié
    
    Args:
        name: Nom du module
        level: Niveau de logging (par défaut INFO)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier
    log_file = os.path.join(logs_dir, f'mcp_real_estate_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler pour console (uniquement pour debug)
    if level == logging.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un nouveau
    
    Args:
        name: Nom du module
    
    Returns:
        Logger configuré
    """
    return setup_logger(name)
