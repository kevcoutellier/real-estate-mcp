#!/usr/bin/env python3
"""
Classes de base pour les scrapers immobiliers
"""

import asyncio
import ssl
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers"""
    
    def __init__(self):
        self.base_url = ""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Configuration SSL pour éviter les erreurs de certificat
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.client = httpx.AsyncClient(
            headers=self.headers, 
            timeout=30.0,
            verify=False  # Désactive la vérification SSL pour les tests
        )
    
    @abstractmethod
    async def search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Méthode abstraite pour la recherche d'annonces"""
        pass
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.client.aclose()
    
    def _safe_get_numeric(self, data: Any, key: str, default: float = 0.0) -> float:
        """Extraction sécurisée d'une valeur numérique"""
        try:
            if isinstance(data, dict):
                value = data.get(key, default)
            else:
                return default
                
            if value is None:
                return default
                
            if isinstance(value, (int, float)):
                return float(value)
                
            if isinstance(value, str):
                # Nettoyer la chaîne et extraire le nombre
                import re
                cleaned = re.sub(r'[^\d,.]', '', value)
                if cleaned:
                    # Remplacer la virgule par un point pour les décimaux français
                    cleaned = cleaned.replace(',', '.')
                    return float(cleaned)
                    
            return default
        except (ValueError, TypeError, AttributeError):
            return default
