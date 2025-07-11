#!/usr/bin/env python3
"""
Interface MCP pour l'immobilier de base
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime
try:
    from ..models.property import PropertyListing
    from ..aggregators.property_aggregator import PropertyAggregator
except ImportError:
    from models.property import PropertyListing
    from aggregators.property_aggregator import PropertyAggregator

logger = logging.getLogger(__name__)


class RealEstateMCP:
    """Interface MCP pour l'immobilier de base"""
    
    def __init__(self):
        self.aggregator = PropertyAggregator()
        self.name = "real-estate-mcp"
        self.version = "1.0.0"
    
    async def search_properties(self, 
                               location: str,
                               min_price: Optional[float] = None,
                               max_price: Optional[float] = None,
                               property_type: Optional[str] = None,
                               min_surface: Optional[float] = None,
                               max_surface: Optional[float] = None,
                               rooms: Optional[int] = None,
                               transaction_type: str = "rent") -> List[Dict[str, Any]]:
        """
        Recherche des propriétés selon les critères spécifiés
        
        Args:
            location: Ville ou arrondissement (ex: "Paris 11e", "Lyon")
            min_price: Prix minimum en euros
            max_price: Prix maximum en euros
            property_type: Type de bien ("appartement", "maison", etc.)
            min_surface: Surface minimale en m²
            max_surface: Surface maximale en m²
            rooms: Nombre de pièces
            transaction_type: "rent" pour location, "sale" pour vente
            
        Returns:
            Liste des annonces trouvées
        """
        
        search_params = {
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'property_type': property_type,
            'min_surface': min_surface,
            'max_surface': max_surface,
            'rooms': rooms,
            'transaction_type': transaction_type
        }
        
        # Filtrage des paramètres None
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        logger.info(f"Recherche avec paramètres: {search_params}")
        
        listings = await self.aggregator.search_properties(search_params)
        
        # Tri par pertinence (prix croissant par défaut)
        listings.sort(key=lambda x: x.price)
        
        # Conversion en dictionnaire pour l'IA
        result = []
        for listing in listings[:50]:  # Limite à 50 résultats
            result.append(self._listing_to_dict(listing))
        
        return result
    
    async def get_property_summary(self, location: str) -> Dict[str, Any]:
        """
        Génère un résumé du marché immobilier pour une zone
        
        Args:
            location: Ville ou arrondissement
            
        Returns:
            Résumé avec statistiques de marché
        """
        
        # Recherche large pour analyse
        try:
            listings = await self.aggregator.search_properties({'location': location})
            
            if not listings:
                return {
                    "error": "Aucune annonce trouvée pour cette localisation",
                    "location": location,
                    "total_listings": 0
                }
            
            # Calcul des statistiques
            prices = [l.price for l in listings if l.price > 0]
            surfaces = [l.surface_area for l in listings if l.surface_area and l.surface_area > 0]
            
            summary = {
                "location": location,
                "total_listings": len(listings),
                "price_stats": {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                    "avg": sum(prices) / len(prices) if prices else 0,
                    "median": sorted(prices)[len(prices)//2] if prices else 0
                },
                "surface_stats": {
                    "min": min(surfaces) if surfaces else 0,
                    "max": max(surfaces) if surfaces else 0,
                    "avg": sum(surfaces) / len(surfaces) if surfaces else 0
                },
                "sources": list(set(l.source for l in listings)),
                "property_types": list(set(l.property_type for l in listings if l.property_type))
            }
            
            # Calcul prix au m²
            if prices and surfaces:
                price_per_sqm = [l.price / l.surface_area for l in listings 
                               if l.surface_area and l.surface_area > 0 and l.price > 0]
                if price_per_sqm:
                    summary["price_per_sqm"] = {
                        "min": min(price_per_sqm),
                        "max": max(price_per_sqm),
                        "avg": sum(price_per_sqm) / len(price_per_sqm)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur dans get_property_summary: {e}")
            return {
                "error": f"Erreur lors de la génération du résumé: {str(e)}",
                "location": location,
                "total_listings": 0
            }
    
    def _listing_to_dict(self, listing: PropertyListing) -> Dict[str, Any]:
        """Convertit une annonce en dictionnaire pour l'IA"""
        data = asdict(listing)
        
        # Formatage des dates
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        # Ajout d'infos calculées
        if listing.price > 0 and listing.surface_area and listing.surface_area > 0:
            data['price_per_sqm'] = round(listing.price / listing.surface_area, 2)
        
        return data
    
    async def close(self):
        """Ferme l'agrégateur"""
        await self.aggregator.close()
