#!/usr/bin/env python3
"""
Scraper pour SeLoger avec gestion des erreurs
"""

import logging
from typing import Dict, List, Optional, Any
from .base import BaseScraper
from ..models.property import PropertyListing

logger = logging.getLogger(__name__)


class SeLogerScraper(BaseScraper):
    """Scraper pour SeLoger avec gestion des erreurs"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api-seloger.tools.svc.prod.di-test.io/api/v2/annonces"
        self.search_url = "https://api-seloger.tools.svc.prod.di-test.io/api/v2/annonces/_search"
        self.headers.update({
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche d'annonces sur SeLoger"""
        listings = []
        
        try:
            # Construction du payload pour l'API SeLoger
            payload = self._build_payload(search_params)
            logger.info(f"Recherche SeLoger: {search_params}")
            
            response = await self.client.post(self.search_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                ads = data.get('items', [])
                
                for ad in ads:
                    try:
                        listing = self._parse_listing(ad)
                        if listing:
                            listings.append(listing)
                    except Exception as e:
                        logger.error(f"Erreur parsing annonce SeLoger: {e}")
                        continue
            
            return listings
            
        except Exception as e:
            logger.error(f"Erreur recherche SeLoger: {e}")
            return []
    
    def _build_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le payload pour l'API SeLoger"""
        payload = {
            "pageIndex": 1,
            "pageSize": 20,
            "query": {
                "criteria": []
            },
            "sortBy": "relevance",
            "sortOrder": "desc"
        }
        
        # Filtres de base
        if params.get('location'):
            payload["query"]["criteria"].append({
                "type": "city",
                "value": params['location']
            })
            
        if params.get('min_price'):
            payload["query"]["criteria"].append({
                "type": "minPrice",
                "value": params['min_price']
            })
            
        if params.get('max_price'):
            payload["query"]["criteria"].append({
                "type": "maxPrice",
                "value": params['max_price']
            })
            
        if params.get('property_type'):
            # Mapper les types de biens (à adapter selon la nomenclature SeLoger)
            property_types = {
                'appartement': 'apartment',
                'maison': 'house',
                'terrain': 'land'
            }
            
            property_type = property_types.get(params['property_type'].lower(), 'apartment')
            payload["query"]["criteria"].append({
                "type": "realtyTypes",
                "value": [property_type]
            })
            
        if params.get('min_surface'):
            payload["query"]["criteria"].append({
                "type": "minSurface",
                "value": params['min_surface']
            })
            
        if params.get('max_surface'):
            payload["query"]["criteria"].append({
                "type": "maxSurface",
                "value": params['max_surface']
            })
            
        if params.get('rooms'):
            payload["query"]["criteria"].append({
                "type": "rooms",
                "value": params['rooms']
            })
            
        # Type de transaction (location/vente)
        transaction_type = params.get('transaction_type', 'rent')
        payload["query"]["criteria"].append({
            "type": "transactionType",
            "value": transaction_type
        })
        
        return payload
    
    def _parse_listing(self, ad_data: Dict[str, Any]) -> Optional[PropertyListing]:
        """Parse les données d'une annonce SeLoger"""
        try:
            # Extraction des données de base
            property_id = str(ad_data.get('id', ''))
            title = ad_data.get('title', 'Sans titre')
            price = float(ad_data.get('price', 0))
            
            # Construction de l'URL de l'annonce
            base_url = "https://www.seloger.com/annonces"
            url = f"{base_url}/{property_id}.htm"
            
            # Extraction des images
            images = []
            if 'photos' in ad_data:
                images = [photo.get('url', '') for photo in ad_data['photos'] if photo.get('url')]
            
            # Création de l'annonce
            listing = PropertyListing(
                id=f"seloger_{property_id}",
                title=title,
                price=price,
                location=ad_data.get('city', {}).get('name', ''),
                property_type=ad_data.get('propertyType', {}).get('label', ''),
                surface_area=ad_data.get('surface', 0),
                rooms=ad_data.get('rooms', 0),
                bedrooms=ad_data.get('bedrooms', 0),
                description=ad_data.get('description', ''),
                images=images,
                source='SeLoger',
                url=url
            )
            
            # Ajout des coordonnées si disponibles
            if 'location' in ad_data and 'latitude' in ad_data['location'] and 'longitude' in ad_data['location']:
                listing.coordinates = {
                    'lat': ad_data['location']['latitude'],
                    'lon': ad_data['location']['longitude']
                }
            
            return listing
            
        except Exception as e:
            logger.error(f"Erreur parsing annonce SeLoger: {e}")
            return None
