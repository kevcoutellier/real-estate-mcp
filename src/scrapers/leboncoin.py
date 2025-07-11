#!/usr/bin/env python3
"""
Scraper pour LeBonCoin avec correction SSL
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from .base import BaseScraper
from ..models.property import PropertyListing

logger = logging.getLogger(__name__)


class LeBonCoinScraper(BaseScraper):
    """Scraper pour LeBonCoin avec correction SSL"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.leboncoin.fr/finder/search"
        self.headers.update({
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
        })
        self._debug_shown = False
    
    async def search(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche d'annonces sur LeBonCoin"""
        listings = []
        
        # Pour les tests, on va simuler quelques annonces si l'API échoue
        try:
            # Géolocaliser la ville d'abord si nécessaire
            location = search_params.get('location', '')
            if location:
                coords = await self._get_city_coordinates(location)
                search_params['_coordinates'] = coords
            
            # Tentative d'appel API réel
            payload = self._build_payload(search_params)
            logger.info(f"Recherche LeBonCoin: {search_params}")
            
            response = await self.client.post(self.base_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                ads = data.get('ads', [])
                
                logger.info(f"Trouvé {len(ads)} annonces sur LeBonCoin")
                
                for ad in ads:
                    try:
                        listing = self._parse_ad(ad)
                        if listing:
                            listings.append(listing)
                    except Exception as e:
                        logger.error(f"Erreur parsing annonce LeBonCoin: {e}")
                        continue
            else:
                logger.warning(f"API LeBonCoin retourne {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erreur API LeBonCoin: {e}")
            logger.info("Utilisation des données de test...")
            
        # Plus de données de test - retourner une liste vide si pas de résultats réels
        if not listings:
            logger.warning(f"Aucune annonce trouvée pour {search_params.get('location', 'localisation inconnue')}")
            logger.info("Aucune donnée de test générée - utilisation exclusive de données réelles")
            
        return listings
    
    async def _get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Récupère les coordonnées d'une ville via l'API Adresse française"""
        try:
            # Utiliser l'API Adresse française pour géolocaliser
            url = f"https://api-adresse.data.gouv.fr/search/?q={city}&limit=1&autocomplete=0"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if features:
                    coords = features[0]['geometry']['coordinates']
                    logger.info(f"Coordonnées {city}: lat={coords[1]}, lng={coords[0]}")
                    return {
                        'lat': coords[1],  # latitude
                        'lng': coords[0]   # longitude
                    }
            
            logger.warning(f"Géolocalisation échouée pour {city}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur géolocalisation {city}: {e}")
            return None
    
    def _build_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le payload pour l'API LeBonCoin"""
        payload = {
            "filters": {
                "category": {"id": "9"},  # Immobilier
                "enums": {
                    "ad_type": ["offer"]
                },
                "location": {
                    "locations": [{"label": params.get('location', '')}]
                },
                "ranges": {}
            },
            "limit": 100,
            "limit_alu": 3,
            "sort_by": "time",
            "sort_order": "desc"
        }
        
        # Type de transaction (vente/location)
        if params.get('transaction_type') == 'rent':
            payload["filters"]["enums"]["real_estate_type"] = ["2"]  # Location
        else:
            payload["filters"]["enums"]["real_estate_type"] = ["1"]  # Vente
        
        # Ajout des filtres de prix
        if params.get('min_price') or params.get('max_price'):
            payload["filters"]["ranges"]["price"] = {
                "min": params.get('min_price', 0),
                "max": params.get('max_price', 999999999)
            }
        
        # Ajout des filtres de surface
        if params.get('min_surface') or params.get('max_surface'):
            payload["filters"]["ranges"]["square"] = {
                "min": params.get('min_surface', 0),
                "max": params.get('max_surface', 999999)
            }
        
        # Filtres géographiques précis pour la localisation
        location = params.get('location', '')
        if location:
            # Utiliser les coordonnées pré-calculées
            coords = params.get('_coordinates')
            if coords:
                payload["filters"]["location"] = {
                    "locations": [{"label": location}],
                    "area": {"lat": coords['lat'], "lng": coords['lng'], "radius": 15000}  # Rayon 15km
                }
                logger.info(f"Filtre géographique {location}: lat={coords['lat']}, lng={coords['lng']}")
            else:
                # Fallback si géolocalisation échoue
                payload["filters"]["location"] = {
                    "locations": [{"label": location}]
                }
                logger.warning(f"Recherche sans coordonnées pour {location}")
        
        return payload
    
    def _parse_ad(self, ad: Any) -> Optional[PropertyListing]:
        """Parse une annonce LeBonCoin avec gestion des différents formats"""
        try:
            # Debug: afficher le type pour comprendre
            if not self._debug_shown:
                logger.info(f"Format d'annonce détecté: {type(ad)}")
                if isinstance(ad, dict):
                    logger.info(f"Clés disponibles: {list(ad.keys())}")
                    # Debug des types des champs problématiques
                    for key in ['attributes', 'images', 'location', 'price']:
                        if key in ad:
                            logger.info(f"Type de {key}: {type(ad[key])}")
                elif isinstance(ad, list):
                    logger.info(f"Liste de {len(ad)} éléments")
                self._debug_shown = True
            
            # Cas 1: Format dictionnaire (attendu)
            if isinstance(ad, dict):
                return self._parse_dict_format(ad)
            
            # Cas 2: Format liste (nouveau format possible)
            elif isinstance(ad, list) and len(ad) > 0:
                return self._parse_list_format(ad)
            
            # Cas 3: Autres formats
            else:
                logger.warning(f"Format non supporté: {type(ad)}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur parsing annonce: {e}")
            return None
    
    def _parse_dict_format(self, ad: Dict[str, Any]) -> Optional[PropertyListing]:
        """Parse le format dictionnaire"""
        try:
            # Extraction des attributs avec gestion du format liste
            attributes = ad.get('attributes', {})
            if isinstance(attributes, list):
                # Convertir la liste d'attributs en dictionnaire
                attributes = self._convert_attributes_list_to_dict(attributes)
            elif not isinstance(attributes, dict):
                attributes = {}
            
            # Images
            images = []
            images_data = ad.get('images', {})
            if isinstance(images_data, dict) and 'urls' in images_data:
                urls = images_data['urls']
                if isinstance(urls, list):
                    for img in urls:
                        if isinstance(img, dict) and 'href' in img:
                            images.append(img['href'])
            elif isinstance(images_data, list):
                # Cas où images est directement une liste
                for img in images_data:
                    if isinstance(img, dict) and 'href' in img:
                        images.append(img['href'])
                    elif isinstance(img, str):
                        images.append(img)
            
            # Prix - gestion de différents formats
            price = 0
            price_data = ad.get('price', [])
            if isinstance(price_data, list) and len(price_data) > 0:
                try:
                    price = float(price_data[0])
                except (ValueError, TypeError):
                    price = 0
            elif isinstance(price_data, (int, float)):
                price = float(price_data)
            elif isinstance(price_data, str):
                # Nettoyer le prix si c'est une chaîne
                price_clean = price_data.replace('€', '').replace(' ', '').replace(',', '.')
                try:
                    price = float(price_clean)
                except (ValueError, TypeError):
                    price = 0
            
            # Essayer aussi price_cents
            if price == 0:
                price_cents = ad.get('price_cents', 0)
                if isinstance(price_cents, (int, float)):
                    price = float(price_cents) / 100
            
            # Location
            location = ""
            location_data = ad.get('location', {})
            if isinstance(location_data, dict):
                location = location_data.get('city', '')
            elif isinstance(location_data, str):
                location = location_data
            elif isinstance(location_data, list) and len(location_data) > 0:
                # Si location est une liste, prendre le premier élément
                if isinstance(location_data[0], dict):
                    location = location_data[0].get('city', '')
                elif isinstance(location_data[0], str):
                    location = location_data[0]
            
            # ID unique
            unique_id = f"leboncoin_{ad.get('list_id', ad.get('id', 'unknown'))}"
            
            # Extraction sécurisée des données d'attributs
            surface_area = self._safe_get_numeric_leboncoin(attributes, 'square')
            rooms = self._safe_get_numeric_leboncoin(attributes, 'rooms')
            bedrooms = self._safe_get_numeric_leboncoin(attributes, 'bedrooms')
            
            listing = PropertyListing(
                id=unique_id,
                title=ad.get('subject', ''),
                price=price,
                currency='EUR',
                location=location,
                property_type=self._extract_property_type(attributes),
                surface_area=surface_area,
                rooms=rooms,
                bedrooms=bedrooms,
                description=ad.get('body', ''),
                images=images,
                source='LeBonCoin',
                url=ad.get('url', ''),
                created_at=self._parse_date(ad.get('index_date'))
            )
            
            return listing
            
        except Exception as e:
            logger.error(f"Erreur parsing dict: {e}")
            return None

    def _parse_list_format(self, ad: List[Any]) -> Optional[PropertyListing]:
        """Parse le format liste"""
        try:
            # Format liste basique
            listing = PropertyListing(
                id=f"leboncoin_list_{ad[0] if len(ad) > 0 else 'unknown'}",
                title=str(ad[1]) if len(ad) > 1 else "Sans titre",
                price=float(ad[2]) if len(ad) > 2 and str(ad[2]).replace('.', '').isdigit() else 0,
                currency='EUR',
                location=str(ad[3]) if len(ad) > 3 else "",
                property_type="Appartement",
                surface_area=None,
                rooms=None,
                bedrooms=None,
                description="",
                images=[],
                source='LeBonCoin',
                url="",
                created_at=datetime.now()
            )
            
            return listing
            
        except Exception as e:
            logger.error(f"Erreur parsing list: {e}")
            return None

    def _convert_attributes_list_to_dict(self, attributes_list: List[Any]) -> Dict[str, Any]:
        """Convertit une liste d'attributs en dictionnaire"""
        try:
            attributes_dict = {}
            
            for attr in attributes_list:
                if isinstance(attr, dict):
                    # Formats possibles pour les attributs LeBonCoin
                    key = attr.get('key', attr.get('name', ''))
                    value = attr.get('value', attr.get('val', ''))
                    
                    if key:
                        attributes_dict[key] = value
                        
                        # Mapping des clés connues
                        if key == 'square':
                            attributes_dict['square'] = value
                        elif key == 'rooms':
                            attributes_dict['rooms'] = value
                        elif key == 'bedrooms':
                            attributes_dict['bedrooms'] = value
                        elif key == 'real_estate_type':
                            attributes_dict['real_estate_type'] = value
            
            return attributes_dict
            
        except Exception as e:
            logger.error(f"Erreur conversion attributs: {e}")
            return {}

    def _safe_get_numeric_leboncoin(self, data: Any, key: str) -> Optional[float]:
        """Extraction sécurisée d'une valeur numérique spécifique à LeBonCoin"""
        try:
            if not isinstance(data, dict):
                return None
            
            value = data.get(key)
            if value is None:
                return None
                
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Nettoyer la chaîne
                clean_value = value.replace('m²', '').replace('m2', '').replace(' ', '').replace(',', '.')
                try:
                    return float(clean_value)
                except (ValueError, TypeError):
                    return None
            elif isinstance(value, list) and len(value) > 0:
                # Si c'est une liste, prendre le premier élément
                return self._safe_get_numeric_leboncoin({'temp': value[0]}, 'temp')
            
            return None
        except:
            return None

    def _parse_date(self, date_str: str) -> datetime:
        """Parse une date"""
        if not date_str:
            return datetime.now()
        try:
            if 'Z' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return datetime.fromisoformat(date_str)
        except:
            return datetime.now()

    def _extract_property_type(self, attributes: Any) -> str:
        """Extrait le type de bien avec gestion d'erreurs"""
        try:
            # Vérifier que attributes est un dictionnaire
            if not isinstance(attributes, dict):
                return 'Inconnu'
            
            type_mapping = {
                '1': 'Maison',
                '2': 'Appartement',
                '3': 'Terrain',
                '4': 'Parking',
                '5': 'Autre'
            }
            
            real_estate_type = attributes.get('real_estate_type', '')
            if isinstance(real_estate_type, list):
                real_estate_type = real_estate_type[0] if real_estate_type else ''
            
            return type_mapping.get(str(real_estate_type), 'Inconnu')
        except:
            return 'Inconnu'
