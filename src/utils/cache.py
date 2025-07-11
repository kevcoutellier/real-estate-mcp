"""
Gestionnaire de cache simple
"""

import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    """Gestionnaire de cache en mémoire"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if key in self._cache:
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Stocke une valeur en cache"""
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
    
    async def clear(self):
        """Vide le cache"""
        self._cache.clear()
        self._expiry.clear()
