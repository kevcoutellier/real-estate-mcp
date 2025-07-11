#!/usr/bin/env python3
"""
Agrégateurs pour les annonces immobilières
"""

import asyncio
import json
import hashlib
import logging
from typing import Dict, List, Any
from datetime import datetime
from ..models.property import PropertyListing
from ..scrapers.leboncoin import LeBonCoinScraper
from ..scrapers.seloger import SeLogerScraper
from ..services.geocoding import GeocodingService

logger = logging.getLogger(__name__)


class PropertyAggregator:
    """Agrégateur principal des annonces"""
    
    def __init__(self):
        self.scrapers = {
            'leboncoin': LeBonCoinScraper(),
            'seloger': SeLogerScraper()
        }
        self.cache = {}  # Cache simple en mémoire
    
    async def search_properties(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche agrégée sur toutes les sources"""
        
        # Génération d'une clé de cache
        cache_key = self._generate_cache_key(search_params)
        
        # Vérification du cache (5 minutes)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if (datetime.now() - cached_data['timestamp']).seconds < 300:
                logger.info("Résultat depuis le cache")
                return cached_data['listings']
        
        all_listings = []
        
        # Lancement des scrapers en parallèle
        tasks = []
        for name, scraper in self.scrapers.items():
            tasks.append(scraper.search(search_params))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Agrégation des résultats
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_listings.extend(result)
                logger.info(f"Scraper {list(self.scrapers.keys())[i]}: {len(result)} annonces")
            else:
                logger.error(f"Erreur scraper {list(self.scrapers.keys())[i]}: {result}")
        
        # Déduplication
        deduplicated = self._deduplicate_listings(all_listings)
        
        # Mise en cache
        self.cache[cache_key] = {
            'listings': deduplicated,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Total: {len(deduplicated)} annonces uniques")
        return deduplicated
    
    def _generate_cache_key(self, params: Dict[str, Any]) -> str:
        """Génère une clé de cache basée sur les paramètres"""
        key_string = json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _deduplicate_listings(self, listings: List[PropertyListing]) -> List[PropertyListing]:
        """Supprime les doublons basés sur titre, prix et surface"""
        seen = set()
        unique_listings = []
        
        for listing in listings:
            # Clé de déduplication
            key = (
                listing.title.lower().strip(),
                listing.price,
                listing.surface_area,
                listing.location.lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)
        
        return unique_listings
    
    async def close(self):
        """Ferme tous les scrapers"""
        for scraper in self.scrapers.values():
            await scraper.close()


class EnrichedPropertyAggregator(PropertyAggregator):
    """Agrégateur avec enrichissement géographique"""
    
    def __init__(self):
        super().__init__()
        self.geocoding_service = GeocodingService()
        
    async def search_properties(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche avec enrichissement automatique"""
        
        # Recherche de base
        listings = await super().search_properties(search_params)
        
        # Enrichissement géographique
        enriched_listings = []
        
        for listing in listings:
            # Géocodage
            if not listing.coordinates and listing.location:
                coordinates = await self.geocoding_service.geocode_address(listing.location)
                if coordinates:
                    listing.coordinates = coordinates
            
            # Enrichissement quartier
            if listing.coordinates:
                neighborhood_info = await self.geocoding_service.get_neighborhood_info(listing.coordinates)
                # Ajouter les informations de quartier comme attribut personnalisé
                if not hasattr(listing, 'neighborhood_info'):
                    listing.neighborhood_info = neighborhood_info
            
            enriched_listings.append(listing)
        
        return enriched_listings
    
    async def close(self):
        """Ferme tous les services"""
        await super().close()
        await self.geocoding_service.close()
