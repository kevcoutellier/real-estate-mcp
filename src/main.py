#!/usr/bin/env python3
"""
Correction SSL et gestion d'erreurs pour le MCP
Remplacez le contenu de src/main.py par ce code corrigé
"""

import asyncio
import json
import logging
import ssl
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import re
import hashlib
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from urllib.parse import urlencode
from playwright.async_api import async_playwright
from .dynamic_data_service import DynamicDataService, get_dynamic_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PropertyListing:
    """Structure standardisée pour les annonces"""
    id: str
    title: str
    price: float
    currency: str = "EUR"
    location: str = ""
    property_type: str = ""
    surface_area: Optional[float] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    description: str = ""
    images: List[str] = None
    source: str = ""
    url: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    coordinates: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class LeBonCoinScraper:
    """Scraper pour LeBonCoin avec correction SSL"""
    
    def __init__(self):
        self.base_url = "https://api.leboncoin.fr/finder/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
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
            surface_area = self._safe_get_numeric(attributes, 'square')
            rooms = self._safe_get_numeric(attributes, 'rooms')
            bedrooms = self._safe_get_numeric(attributes, 'bedrooms')
            
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

    def _safe_get_numeric(self, data: Any, key: str) -> Optional[float]:
        """Extraction sécurisée d'une valeur numérique"""
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
                return self._safe_get_numeric({'temp': value[0]}, 'temp')
            
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
    
    def _validate_listing(self, listing: PropertyListing, search_params: Dict[str, Any]) -> bool:
        """Valide qu'une annonce correspond aux critères de recherche"""
        try:
            # Filtre par localisation (pour éviter les résultats trop éloignés)
            target_location = search_params.get('location', '').lower()
            if target_location:
                # Vérifier si la localisation cible est dans le titre ou la localisation
                if ('paris' in target_location and 
                    'paris' not in listing.location.lower() and 
                    'paris' not in listing.title.lower()):
                    return False
                    
                # Vérifier les arrondissements parisiens
                if 'paris' in target_location and 'e' in target_location:
                    # Extraire le numéro d'arrondissement (ex: "11e" dans "Paris 11e")
                    import re
                    match = re.search(r'(\d+)e', target_location)
                    if match:
                        arr_num = match.group(1)
                        if arr_num not in listing.location.lower() and arr_num not in listing.title.lower():
                            return False
            
            # Filtre par type de transaction (éviter les prix de vente dans les locations)
            if search_params.get('transaction_type') == 'rent':
                # Filtrer les prix trop élevés (probablement des ventes)
                if listing.price > 10000:  # Plus de 10k€ = probablement une vente
                    return False
            
            # Filtre par prix
            min_price = search_params.get('min_price')
            max_price = search_params.get('max_price')
            if min_price and listing.price < min_price:
                return False
            if max_price and listing.price > max_price:
                return False
            
            # Filtre par surface
            min_surface = search_params.get('min_surface')
            max_surface = search_params.get('max_surface')
            if min_surface and listing.surface_area and listing.surface_area < min_surface:
                return False
            if max_surface and listing.surface_area and listing.surface_area > max_surface:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation annonce: {e}")
            return True  # En cas d'erreur, on garde l'annonce
# Classe SeLogerScraper supprimée - ne générait que des données de test
# Utiliser uniquement des sources de données réelles

class SeLogerScraper:
    """Scraper pour SeLoger avec gestion des erreurs"""
    
    def __init__(self):
        self.base_url = "https://api-seloger.tools.svc.prod.di-test.io/api/v2/annonces"
        self.search_url = "https://api-seloger.tools.svc.prod.di-test.io/api/v2/annonces/_search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
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

class GeocodingService:
    """Service de géocodage et enrichissement géographique"""
    
    def __init__(self):
        self.nominatim = Nominatim(user_agent="real-estate-mcp")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache = {}  # Cache en mémoire
        self.rate_limit_delay = 1.0  # Délai entre requêtes
        
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Géocode une adresse et retourne les coordonnées"""
        
        # Vérifier le cache
        cache_key = hashlib.md5(address.lower().encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        coordinates = None
        
        try:
            # Méthode 1: API Adresse française (gratuite et rapide)
            coordinates = await self._geocode_api_adresse(address)
            
            # Méthode 2: Fallback Nominatim
            if not coordinates:
                coordinates = await self._geocode_nominatim(address)
                
        except Exception as e:
            logger.error(f"Erreur géocodage {address}: {e}")
            
        # Cache du résultat
        self.cache[cache_key] = coordinates
        return coordinates
    
    async def _geocode_api_adresse(self, address: str) -> Optional[Dict[str, float]]:
        """Géocodage avec l'API Adresse française"""
        try:
            url = "https://api-adresse.data.gouv.fr/search/"
            params = {
                'q': address,
                'limit': 1,
                'autocomplete': 0
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if features:
                    coords = features[0]['geometry']['coordinates']
                    return {
                        'lat': coords[1],
                        'lon': coords[0]
                    }
                    
        except Exception as e:
            logger.error(f"Erreur API Adresse: {e}")
            
        return None
    
    async def _geocode_nominatim(self, address: str) -> Optional[Dict[str, float]]:
        """Géocodage avec Nominatim (OpenStreetMap)"""
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            location = self.nominatim.geocode(address)
            
            if location:
                return {
                    'lat': location.latitude,
                    'lon': location.longitude
                }
                
        except Exception as e:
            logger.error(f"Erreur Nominatim: {e}")
            
        return None
    
    async def get_neighborhood_info(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Récupère les informations du quartier"""
        
        if not coordinates:
            return {}
        
        lat, lon = coordinates['lat'], coordinates['lon']
        
        # Agrégation des données du quartier
        neighborhood_data = {
            'coordinates': coordinates,
            'transports': await self._get_transport_info(lat, lon),
            'amenities': await self._get_amenities_info(lat, lon),
            'safety': await self._get_safety_info(lat, lon),
            'schools': await self._get_schools_info(lat, lon),
            'score': 0
        }
        
        # Calcul du score d'attractivité
        neighborhood_data['score'] = self._calculate_attractiveness_score(neighborhood_data)
        
        return neighborhood_data
    
    async def _get_transport_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Informations sur les transports"""
        transport_data = {
            'metro_stations': [],
            'bus_stops': [],
            'nearest_metro': None,
            'metro_distance': None
        }
        
        try:
            # Utiliser l'API Overpass pour les transports parisiens
            query = f"""
            [out:json][timeout:10];
            (
                node["public_transport"="station"]["station"="subway"](around:1000,{lat},{lon});
                node["amenity"="bus_station"](around:500,{lat},{lon});
            );
            out geom;
            """
            
            response = await self.client.post(
                "https://overpass-api.de/api/interpreter",
                data=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                metro_stations = []
                bus_stops = []
                
                for element in data.get('elements', []):
                    if element.get('tags', {}).get('station') == 'subway':
                        station_coords = (element['lat'], element['lon'])
                        distance = geodesic((lat, lon), station_coords).meters
                        
                        metro_stations.append({
                            'name': element['tags'].get('name', 'Station inconnue'),
                            'distance': distance,
                            'line': element['tags'].get('line', '')
                        })
                        
                    elif element.get('tags', {}).get('amenity') == 'bus_station':
                        bus_coords = (element['lat'], element['lon'])
                        distance = geodesic((lat, lon), bus_coords).meters
                        
                        bus_stops.append({
                            'name': element['tags'].get('name', 'Arrêt inconnu'),
                            'distance': distance
                        })
                
                # Trier par distance
                metro_stations.sort(key=lambda x: x['distance'])
                bus_stops.sort(key=lambda x: x['distance'])
                
                transport_data['metro_stations'] = metro_stations[:3]
                transport_data['bus_stops'] = bus_stops[:3]
                
                if metro_stations:
                    transport_data['nearest_metro'] = metro_stations[0]['name']
                    transport_data['metro_distance'] = metro_stations[0]['distance']
                    
        except Exception as e:
            logger.error(f"Erreur transport info: {e}")
            
        return transport_data
    
    async def _get_amenities_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Informations sur les commodités"""
        amenities_data = {
            'supermarkets': [],
            'restaurants': [],
            'pharmacies': [],
            'hospitals': [],
            'parks': []
        }
        
        try:
            # Requête Overpass pour les commodités
            query = f"""
            [out:json][timeout:10];
            (
                node["shop"="supermarket"](around:800,{lat},{lon});
                node["amenity"="restaurant"](around:500,{lat},{lon});
                node["amenity"="pharmacy"](around:1000,{lat},{lon});
                node["amenity"="hospital"](around:2000,{lat},{lon});
                node["leisure"="park"](around:1000,{lat},{lon});
            );
            out geom;
            """
            
            response = await self.client.post(
                "https://overpass-api.de/api/interpreter",
                data=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    element_coords = (element['lat'], element['lon'])
                    distance = geodesic((lat, lon), element_coords).meters
                    
                    amenity_info = {
                        'name': tags.get('name', 'Nom inconnu'),
                        'distance': distance
                    }
                    
                    if tags.get('shop') == 'supermarket':
                        amenities_data['supermarkets'].append(amenity_info)
                    elif tags.get('amenity') == 'restaurant':
                        amenities_data['restaurants'].append(amenity_info)
                    elif tags.get('amenity') == 'pharmacy':
                        amenities_data['pharmacies'].append(amenity_info)
                    elif tags.get('amenity') == 'hospital':
                        amenities_data['hospitals'].append(amenity_info)
                    elif tags.get('leisure') == 'park':
                        amenities_data['parks'].append(amenity_info)
                
                # Trier par distance et limiter
                for key in amenities_data:
                    amenities_data[key].sort(key=lambda x: x['distance'])
                    amenities_data[key] = amenities_data[key][:3]
                    
        except Exception as e:
            logger.error(f"Erreur amenities info: {e}")
            
        return amenities_data
    
    async def _get_safety_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Informations sur la sécurité (simulé)"""
        # Pour une vraie application, utiliser des données de criminalité
        # Ici on simule avec des données fictives
        
        safety_data = {
            'crime_rate': 'Moyen',  # Faible, Moyen, Élevé
            'police_stations': [],
            'safety_score': 7  # Sur 10
        }
        
        try:
            # Chercher les commissariats
            query = f"""
            [out:json][timeout:10];
            (
                node["amenity"="police"](around:2000,{lat},{lon});
            );
            out geom;
            """
            
            response = await self.client.post(
                "https://overpass-api.de/api/interpreter",
                data=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    element_coords = (element['lat'], element['lon'])
                    distance = geodesic((lat, lon), element_coords).meters
                    
                    safety_data['police_stations'].append({
                        'name': tags.get('name', 'Commissariat'),
                        'distance': distance
                    })
                
                safety_data['police_stations'].sort(key=lambda x: x['distance'])
                safety_data['police_stations'] = safety_data['police_stations'][:2]
                
        except Exception as e:
            logger.error(f"Erreur safety info: {e}")
            
        return safety_data
    
    async def _get_schools_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Informations sur les écoles"""
        schools_data = {
            'primary_schools': [],
            'secondary_schools': [],
            'universities': []
        }
        
        try:
            query = f"""
            [out:json][timeout:10];
            (
                node["amenity"="school"](around:1500,{lat},{lon});
                node["amenity"="university"](around:5000,{lat},{lon});
            );
            out geom;
            """
            
            response = await self.client.post(
                "https://overpass-api.de/api/interpreter",
                data=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    element_coords = (element['lat'], element['lon'])
                    distance = geodesic((lat, lon), element_coords).meters
                    
                    school_info = {
                        'name': tags.get('name', 'École inconnue'),
                        'distance': distance
                    }
                    
                    if tags.get('amenity') == 'school':
                        schools_data['primary_schools'].append(school_info)
                    elif tags.get('amenity') == 'university':
                        schools_data['universities'].append(school_info)
                
                # Trier par distance
                for key in schools_data:
                    schools_data[key].sort(key=lambda x: x['distance'])
                    schools_data[key] = schools_data[key][:3]
                    
        except Exception as e:
            logger.error(f"Erreur schools info: {e}")
            
        return schools_data
    
    def _calculate_attractiveness_score(self, neighborhood_data: Dict[str, Any]) -> float:
        """Calcule un score d'attractivité du quartier"""
        score = 0
        
        # Transport (40% du score)
        transport = neighborhood_data.get('transports', {})
        if transport.get('metro_distance'):
            if transport['metro_distance'] < 300:
                score += 40
            elif transport['metro_distance'] < 600:
                score += 30
            elif transport['metro_distance'] < 1000:
                score += 20
            else:
                score += 10
        
        # Commodités (30% du score)
        amenities = neighborhood_data.get('amenities', {})
        commodities_score = 0
        
        if amenities.get('supermarkets'):
            commodities_score += 8
        if amenities.get('restaurants'):
            commodities_score += 6
        if amenities.get('pharmacies'):
            commodities_score += 8
        if amenities.get('parks'):
            commodities_score += 8
        
        score += min(commodities_score, 30)
        
        # Sécurité (20% du score)
        safety = neighborhood_data.get('safety', {})
        safety_score = safety.get('safety_score', 5)
        score += (safety_score / 10) * 20
        
        # Éducation (10% du score)
        schools = neighborhood_data.get('schools', {})
        education_score = 0
        
        if schools.get('primary_schools'):
            education_score += 5
        if schools.get('universities'):
            education_score += 5
        
        score += min(education_score, 10)
        
        return round(score, 1)

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
                listing.neighborhood_info = neighborhood_info
            
            enriched_listings.append(listing)
        
        return enriched_listings
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

# Import des analyseurs spécialisés
from enum import Enum
from dataclasses import dataclass, asdict

# Import du service dynamique
try:
    from .dynamic_data_service import get_dynamic_service, MarketData
except ImportError:
    # Import relatif pour exécution directe
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from dynamic_data_service import get_dynamic_service, MarketData

class InvestmentProfile(Enum):
    """Profils d'investissement"""
    RENTAL_INVESTOR = "rental_investor"  # Investisseur locatif
    PROPERTY_DEALER = "property_dealer"   # Marchand de biens
    BOTH = "both"                        # Les deux activités

@dataclass
class RentalAnalysis:
    """Analyse pour l'investissement locatif"""
    gross_yield: float  # Rendement brut (%)
    net_yield: float    # Rendement net (%)
    cash_flow: float    # Cash-flow mensuel (€)
    estimated_rent: float        # Loyer estimé (€/mois)
    rent_per_sqm: float         # Loyer au m² (€/m²/mois)
    monthly_charges: float      # Charges mensuelles estimées
    annual_taxes: float        # Taxes foncières annuelles
    rental_demand: str         # Forte/Moyenne/Faible
    tenant_profile: str        # Profil locataire cible
    vacancy_risk: str         # Risque de vacance
    capital_appreciation: float  # Plus-value estimée sur 10 ans (%)
    investment_score: float    # Score d'investissement (/100)
    pros: list           # Points positifs
    cons: list           # Points négatifs
    recommendations: list # Recommandations d'action

@dataclass
class DealerAnalysis:
    """Analyse pour marchand de biens"""
    renovation_cost: float        # Coût rénovation estimé (€)
    renovation_duration: int      # Durée travaux (semaines)
    market_value_current: float   # Valeur actuelle marché
    market_value_renovated: float # Valeur après rénovation
    gross_margin: float          # Marge brute (€)
    gross_margin_percent: float  # Marge brute (%)
    net_margin: float           # Marge nette après frais (€)
    total_investment: float     # Investissement total requis
    estimated_sale_duration: int  # Durée de revente (mois)
    market_liquidity: str        # Liquidité du marché
    market_risk: str            # Risque marché
    renovation_risk: str        # Risque chantier
    dealer_score: float         # Score marchand de biens (/100)
    opportunity_level: str      # Niveau d'opportunité
    action_plan: list     # Plan d'action recommandé
    alerts: list          # Alertes importantes

# Mise à jour de RealEstateMCP pour utiliser l'agrégateur enrichi
class EnrichedRealEstateMCP(RealEstateMCP):
    """MCP avec enrichissement géographique et analyses d'investissement"""
    
    def __init__(self):
        super().__init__()
        self.aggregator = EnrichedPropertyAggregator()
        
        # SUPPRESSION COMPLÈTE DES DONNÉES HARDCODÉES
        # Toutes les données sont maintenant récupérées dynamiquement
        # via le service DynamicDataService
        
        # Avertissement pour l'ancienne classe
        logger.warning("EnrichedRealEstateMCP utilise des données hardcodées obsolètes.")
        logger.warning("Utilisez DynamicRealEstateMCP pour des données temps réel.")
        
    async def get_neighborhood_analysis(self, location: str) -> Dict[str, Any]:
        """Analyse détaillée d'un quartier"""
        
        # Géocodage de la localisation
        coordinates = await self.aggregator.geocoding_service.geocode_address(location)
        
        if not coordinates:
            return {"error": f"Impossible de géocoder {location}"}
        
        # Analyse du quartier
        neighborhood_info = await self.aggregator.geocoding_service.get_neighborhood_info(coordinates)
        
        # Recherche d'annonces dans le quartier
        search_params = {'location': location}
        listings = await self.aggregator.search_properties(search_params)
        
        # Analyse du marché local
        market_analysis = await self.get_property_summary(location)
        
        return {
            'location': location,
            'coordinates': coordinates,
            'neighborhood_info': neighborhood_info,
            'market_analysis': market_analysis,
            'sample_listings': listings[:5]  # 5 exemples
        }
    
    def _listing_to_dict(self, listing: PropertyListing) -> Dict[str, Any]:
        """Conversion avec données enrichies"""
        data = super()._listing_to_dict(listing)
        
        # Ajouter les données géographiques
        if hasattr(listing, 'neighborhood_info'):
            data['neighborhood_info'] = listing.neighborhood_info
        
        return data
    
    async def analyze_investment_opportunity(self, 
                                           location: str,
                                           min_price: Optional[float] = None,
                                           max_price: Optional[float] = None,
                                           investment_profile: InvestmentProfile = InvestmentProfile.BOTH,
                                           **kwargs) -> Dict[str, Any]:
        """Analyse complète d'opportunité d'investissement"""
        
        # Recherche des biens avec le MCP de base
        search_results = await self.search_properties(
            location=location,
            min_price=min_price,
            max_price=max_price,
            transaction_type="sale",  # Achat pour investissement
            **kwargs
        )
        
        if not search_results:
            return {
                "error": "Aucun bien trouvé pour cette recherche",
                "location": location,
                "search_criteria": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "investment_profile": investment_profile.value
                }
            }
        
        # Analyse de chaque bien selon le profil
        analyzed_opportunities = []
        
        for property_data in search_results[:10]:  # Limite à 10 biens
            opportunity = {
                "property": property_data,
                "analyses": {}
            }
            
            # Analyse locative
            if investment_profile in [InvestmentProfile.RENTAL_INVESTOR, InvestmentProfile.BOTH]:
                try:
                    rental_analysis = await self._analyze_rental_potential(property_data)
                    opportunity["analyses"]["rental"] = asdict(rental_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse locative: {e}")
                    opportunity["analyses"]["rental"] = {"error": str(e)}
            
            # Analyse marchand de biens
            if investment_profile in [InvestmentProfile.PROPERTY_DEALER, InvestmentProfile.BOTH]:
                try:
                    dealer_analysis = await self._analyze_dealer_opportunity(property_data)
                    opportunity["analyses"]["dealer"] = asdict(dealer_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse marchand: {e}")
                    opportunity["analyses"]["dealer"] = {"error": str(e)}
            
            analyzed_opportunities.append(opportunity)
        
        # Tri selon le profil
        sorted_opportunities = self._rank_opportunities(analyzed_opportunities, investment_profile)
        
        # Résumé global
        market_summary = self._generate_market_summary(location, sorted_opportunities, investment_profile)
        
        return {
            "location": location,
            "investment_profile": investment_profile.value,
            "total_opportunities": len(sorted_opportunities),
            "market_summary": market_summary,
            "top_opportunities": sorted_opportunities[:5],  # Top 5
            "analysis_date": datetime.now().isoformat()
        }
    
    async def compare_investment_strategies(self, location: str, 
                                          property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les stratégies d'investissement locatif vs marchand de biens"""
        
        # Analyses des deux stratégies
        rental_analysis = await self._analyze_rental_potential(property_data)
        dealer_analysis = await self._analyze_dealer_opportunity(property_data)
        
        # Comparaison des rendements
        rental_total_return = rental_analysis.net_yield + (rental_analysis.capital_appreciation / 10)
        dealer_annual_return = (dealer_analysis.gross_margin_percent / 
                               (dealer_analysis.renovation_duration / 52 + 
                                dealer_analysis.estimated_sale_duration / 12))
        
        # Recommandation
        if rental_total_return > dealer_annual_return:
            if dealer_analysis.gross_margin_percent > 20:
                recommendation = "Les deux stratégies sont viables - diversifier"
            else:
                recommendation = "Privilégier l'investissement locatif"
        else:
            if dealer_analysis.dealer_score > 70:
                recommendation = "Opportunité marchand de biens intéressante"
            else:
                recommendation = "Analyser d'autres biens"
        
        return {
            "property": property_data,
            "rental_analysis": asdict(rental_analysis),
            "dealer_analysis": asdict(dealer_analysis),
            "comparison": {
                "rental_annual_return": rental_total_return,
                "dealer_annual_return": dealer_annual_return,
                "recommendation": recommendation
            }
        }
    
    async def _analyze_rental_potential(self, property_data: Dict[str, Any]) -> RentalAnalysis:
        """Analyse du potentiel locatif d'un bien"""
        await self._ensure_analyzers_initialized()
        
        # Conversion en PropertyListing
        listing = PropertyListing(
            id=property_data.get('id', ''),
            title=property_data.get('title', ''),
            price=property_data.get('price', 0),
            location=property_data.get('location', ''),
            surface_area=property_data.get('surface_area', 0),
            description=property_data.get('description', ''),
            url=property_data.get('url', ''),
            coordinates=property_data.get('coordinates')
        )
        
        return self.rental_analyzer.analyze_rental_investment(listing)
    
    async def _analyze_dealer_opportunity(self, property_data: Dict[str, Any]) -> DealerAnalysis:
        """Analyse d'opportunité marchand de biens"""
        await self._ensure_analyzers_initialized()
        
        # Conversion en PropertyListing
        listing = PropertyListing(
            id=property_data.get('id', ''),
            title=property_data.get('title', ''),
            price=property_data.get('price', 0),
            location=property_data.get('location', ''),
            surface_area=property_data.get('surface_area', 0),
            description=property_data.get('description', ''),
            url=property_data.get('url', ''),
            coordinates=property_data.get('coordinates')
        )
        
        return self.dealer_analyzer.analyze_dealer_opportunity(listing)
    
    def _rank_opportunities(self, opportunities: List[Dict[str, Any]], 
                          investment_profile: InvestmentProfile) -> List[Dict[str, Any]]:
        """Classe les opportunités selon le profil d'investissement"""
        
        def get_score(opp):
            if investment_profile == InvestmentProfile.RENTAL_INVESTOR:
                return opp.get('analyses', {}).get('rental', {}).get('rental_score', 0)
            elif investment_profile == InvestmentProfile.PROPERTY_DEALER:
                return opp.get('analyses', {}).get('dealer', {}).get('dealer_score', 0)
            else:  # BOTH
                rental_score = opp.get('analyses', {}).get('rental', {}).get('rental_score', 0)
                dealer_score = opp.get('analyses', {}).get('dealer', {}).get('dealer_score', 0)
                return (rental_score + dealer_score) / 2
        
        return sorted(opportunities, key=get_score, reverse=True)
    
    def _generate_market_summary(self, location: str, opportunities: List[Dict[str, Any]], 
                               investment_profile: InvestmentProfile) -> Dict[str, Any]:
        """Génère un résumé du marché"""
        
        if not opportunities:
            return {
                "message": "Aucune opportunité analysée",
                "location": location
            }
        
        # Calculs de base
        total_opportunities = len(opportunities)
        avg_price = sum(opp['property'].get('price', 0) for opp in opportunities) / total_opportunities
        
        summary = {
            "location": location,
            "total_analyzed": total_opportunities,
            "average_price": avg_price,
            "investment_profile": investment_profile.value
        }
        
        # Statistiques spécifiques selon le profil
        if investment_profile in [InvestmentProfile.RENTAL_INVESTOR, InvestmentProfile.BOTH]:
            rental_analyses = [opp['analyses'].get('rental', {}) for opp in opportunities 
                             if 'rental' in opp.get('analyses', {})]
            if rental_analyses:
                avg_yield = sum(r.get('net_yield', 0) for r in rental_analyses) / len(rental_analyses)
                good_opportunities = len([r for r in rental_analyses if r.get('rental_score', 0) > 70])
                summary['rental_stats'] = {
                    "average_net_yield": avg_yield,
                    "good_opportunities": good_opportunities,
                    "percentage_viable": (good_opportunities / len(rental_analyses)) * 100
                }
        
        if investment_profile in [InvestmentProfile.PROPERTY_DEALER, InvestmentProfile.BOTH]:
            dealer_analyses = [opp['analyses'].get('dealer', {}) for opp in opportunities 
                             if 'dealer' in opp.get('analyses', {})]
            if dealer_analyses:
                avg_margin = sum(d.get('gross_margin_percent', 0) for d in dealer_analyses) / len(dealer_analyses)
                profitable_deals = len([d for d in dealer_analyses if d.get('gross_margin_percent', 0) > 15])
                summary['dealer_stats'] = {
                    "average_margin": avg_margin,
                    "profitable_deals": profitable_deals,
                    "percentage_profitable": (profitable_deals / len(dealer_analyses)) * 100
                }
        
        return summary

class DynamicRealEstateMCP(EnrichedRealEstateMCP):
    """MCP avec données dynamiques en temps réel"""
    
    def __init__(self):
        # Initialiser sans les données hardcodées
        super().__init__()
        
        # Vider les données hardcodées
        self.rental_database = {}
        self.renovation_costs = {}
        
        # Service de données dynamiques
        self.dynamic_service = None
        
    async def _ensure_dynamic_service(self):
        """S'assure que le service dynamique est initialisé"""
        if self.dynamic_service is None:
            try:
                self.dynamic_service = await get_dynamic_service()
                logger.info("Service dynamique initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du service dynamique: {e}")
                # Fallback : créer une instance directement
                self.dynamic_service = DynamicDataService()
                logger.info("Service dynamique initialisé en fallback")
    
    async def get_market_data_dynamic(self, location: str, transaction_type: str = 'rent') -> Dict[str, Any]:
        """Récupère les données de marché en temps réel"""
        await self._ensure_dynamic_service()
        
        market_data = await self.dynamic_service.get_market_data(location, transaction_type)
        
        if market_data:
            return {
                'location': market_data.location,
                'avg_rent_sqm': market_data.avg_rent_sqm,
                'avg_sale_sqm': market_data.avg_sale_sqm,
                'market_trend': market_data.market_trend,
                'last_updated': market_data.last_updated.isoformat(),
                'source': market_data.source,
                'confidence_score': market_data.confidence_score,
                'data_type': 'dynamic'
            }
        else:
            return {
                'location': location,
                'error': 'Données non disponibles pour cette localisation',
                'suggestion': 'Essayez avec une ville plus grande ou vérifiez l\'orthographe'
            }
    
    async def get_renovation_costs_dynamic(self, location: str, surface: float) -> Dict[str, Any]:
        """Récupère les coûts de rénovation ajustés par région"""
        await self._ensure_dynamic_service()
        
        return await self.dynamic_service.get_renovation_costs(location, surface)
    
    async def analyze_investment_opportunity_dynamic(self, 
                                                   location: str,
                                                   min_price: Optional[float] = None,
                                                   max_price: Optional[float] = None,
                                                   investment_profile: str = "both",
                                                   **kwargs) -> Dict[str, Any]:
        """Analyse d'opportunité avec données dynamiques"""
        
        # Récupérer les données de marché en temps réel
        market_data = await self.get_market_data_dynamic(location)
        
        if 'error' in market_data:
            return {
                'location': location,
                'error': market_data['error'],
                'suggestion': market_data['suggestion']
            }
        
        # Rechercher des biens
        search_params = {
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            **kwargs
        }
        
        properties = await self.aggregator.search_properties(search_params)
        
        # Analyser chaque bien avec les données dynamiques
        opportunities = []
        
        for prop in properties[:10]:  # Limiter à 10 biens
            prop_data = {
                'price': prop.price,
                'surface': prop.surface_area or 50,  # Surface par défaut
                'location': prop.location,
                'rooms': prop.rooms or 2
            }
            
            # Analyse locative avec données dynamiques
            rental_analysis = await self._analyze_rental_potential_dynamic(prop_data, market_data)
            
            # Analyse marchand de biens avec coûts dynamiques
            dealer_analysis = await self._analyze_dealer_opportunity_dynamic(prop_data, location)
            
            opportunity = {
                'property': self._listing_to_dict(prop),
                'rental_analysis': rental_analysis,
                'dealer_analysis': dealer_analysis,
                'market_data': market_data,
                'recommendation': self._generate_recommendation(rental_analysis, dealer_analysis, investment_profile)
            }
            
            opportunities.append(opportunity)
        
        # Trier par score
        opportunities.sort(key=lambda x: x.get('rental_analysis', {}).get('investment_score', 0) + 
                                        x.get('dealer_analysis', {}).get('dealer_score', 0), reverse=True)
        
        return {
            'location': location,
            'investment_profile': investment_profile,
            'market_data': market_data,
            'opportunities': opportunities,
            'summary': self._generate_dynamic_summary(location, opportunities, investment_profile, market_data)
        }
    
    async def _analyze_rental_potential_dynamic(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du potentiel locatif avec données dynamiques"""
        
        surface = property_data.get('surface', 50)
        price = property_data.get('price', 0)
        
        # Utiliser les données de marché dynamiques
        avg_rent_sqm = market_data.get('avg_rent_sqm', 15)
        
        # Calculs
        estimated_rent = surface * avg_rent_sqm
        annual_rent = estimated_rent * 12
        
        # Charges et taxes (estimations)
        monthly_charges = surface * 2  # 2€/m²/mois
        annual_taxes = price * 0.012  # 1.2% du prix
        
        # Rendements
        gross_yield = (annual_rent / price * 100) if price > 0 else 0
        net_yield = ((annual_rent - monthly_charges * 12 - annual_taxes) / price * 100) if price > 0 else 0
        
        # Cash flow
        cash_flow = estimated_rent - monthly_charges - (annual_taxes / 12)
        
        # Score d'investissement
        investment_score = min(10, max(0, net_yield * 2))  # Score sur 10
        
        return {
            'gross_yield': round(gross_yield, 2),
            'net_yield': round(net_yield, 2),
            'cash_flow': round(cash_flow, 2),
            'estimated_rent': round(estimated_rent, 2),
            'rent_per_sqm': round(avg_rent_sqm, 2),
            'monthly_charges': round(monthly_charges, 2),
            'annual_taxes': round(annual_taxes, 2),
            'investment_score': round(investment_score, 2),
            'data_source': market_data.get('source', 'Données dynamiques'),
            'confidence': market_data.get('confidence_score', 0.5)
        }
    
    async def _analyze_dealer_opportunity_dynamic(self, property_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Analyse marchand de biens avec coûts dynamiques"""
        
        surface = property_data.get('surface', 50)
        price = property_data.get('price', 0)
        
        # Récupérer les coûts de rénovation ajustés
        renovation_costs = await self.get_renovation_costs_dynamic(location, surface)
        
        # Choisir le niveau de rénovation (moyenne)
        renovation_level = 'renovation_complete'
        renovation_cost = renovation_costs.get(renovation_level, {}).get('total_cost', surface * 1000)
        
        # Estimation valeur après rénovation (+20%)
        market_value_renovated = price * 1.2
        
        # Calculs
        total_investment = price + renovation_cost
        gross_margin = market_value_renovated - total_investment
        gross_margin_percent = (gross_margin / total_investment * 100) if total_investment > 0 else 0
        
        # Frais de vente (7%)
        selling_costs = market_value_renovated * 0.07
        net_margin = gross_margin - selling_costs
        
        # Score marchand de biens
        dealer_score = min(10, max(0, gross_margin_percent / 3))  # Score sur 10
        
        return {
            'renovation_cost': round(renovation_cost, 2),
            'renovation_duration': 12,  # semaines
            'market_value_current': round(price, 2),
            'market_value_renovated': round(market_value_renovated, 2),
            'gross_margin': round(gross_margin, 2),
            'gross_margin_percent': round(gross_margin_percent, 2),
            'net_margin': round(net_margin, 2),
            'total_investment': round(total_investment, 2),
            'dealer_score': round(dealer_score, 2),
            'regional_factor': renovation_costs.get(renovation_level, {}).get('regional_factor', 1.0)
        }
    
    def _generate_recommendation(self, rental_analysis: Dict[str, Any], dealer_analysis: Dict[str, Any], 
                               investment_profile: str) -> str:
        """Génère une recommandation basée sur les analyses"""
        
        rental_score = rental_analysis.get('investment_score', 0)
        dealer_score = dealer_analysis.get('dealer_score', 0)
        
        if investment_profile == "rental_investor":
            if rental_score >= 7:
                return "Excellent pour investissement locatif"
            elif rental_score >= 5:
                return "Bon potentiel locatif"
            else:
                return "Rendement locatif faible"
        
        elif investment_profile == "property_dealer":
            if dealer_score >= 7:
                return "Excellente opportunité marchand de biens"
            elif dealer_score >= 5:
                return "Bonne marge potentielle"
            else:
                return "Marge insuffisante"
        
        else:  # "both"
            total_score = (rental_score + dealer_score) / 2
            if total_score >= 7:
                return "Excellente opportunité mixte"
            elif total_score >= 5:
                return "Bon potentiel d'investissement"
            else:
                return "Opportunité limitée"
    
    def _generate_dynamic_summary(self, location: str, opportunities: List[Dict[str, Any]], 
                                investment_profile: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé avec données dynamiques"""
        
        if not opportunities:
            return {
                'message': f'Aucune opportunité trouvée à {location}',
                'market_data': market_data
            }
        
        # Statistiques
        rental_scores = [opp.get('rental_analysis', {}).get('investment_score', 0) for opp in opportunities]
        dealer_scores = [opp.get('dealer_analysis', {}).get('dealer_score', 0) for opp in opportunities]
        
        return {
            'total_opportunities': len(opportunities),
            'avg_rental_score': round(sum(rental_scores) / len(rental_scores), 2) if rental_scores else 0,
            'avg_dealer_score': round(sum(dealer_scores) / len(dealer_scores), 2) if dealer_scores else 0,
            'best_opportunity': opportunities[0] if opportunities else None,
            'market_confidence': market_data.get('confidence_score', 0.5),
            'data_freshness': market_data.get('last_updated', 'Inconnue'),
            'recommendation': f"Marché {location}: {market_data.get('market_trend', 'Données limitées')}"
        }
    
    async def compare_investment_strategies_dynamic(self, location: str, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les stratégies d'investissement avec données dynamiques"""
        try:
            # Récupérer les données de marché
            market_data = await self.get_market_data_dynamic(location)
            
            # Analyser le potentiel locatif
            rental_analysis = await self._analyze_rental_potential_dynamic(property_data, market_data)
            
            # Analyser l'opportunité marchand de biens
            dealer_analysis = await self._analyze_dealer_opportunity_dynamic(property_data, location)
            
            # Comparaison
            comparison = {
                'property_info': property_data,
                'location': location,
                'rental_strategy': rental_analysis,
                'dealer_strategy': dealer_analysis,
                'market_context': market_data,
                'recommendation': self._generate_strategy_recommendation(rental_analysis, dealer_analysis)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erreur compare_investment_strategies_dynamic: {e}")
            return {
                'error': f'Erreur lors de la comparaison: {str(e)}',
                'location': location,
                'property_data': property_data
            }
    
    def _generate_strategy_recommendation(self, rental_analysis: Dict[str, Any], dealer_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère une recommandation basée sur les deux analyses"""
        rental_score = rental_analysis.get('investment_score', 0)
        dealer_score = dealer_analysis.get('dealer_score', 0)
        
        if rental_score > dealer_score:
            strategy = 'rental_investment'
            reason = f'Meilleur rendement locatif (score: {rental_score:.1f} vs {dealer_score:.1f})'
        elif dealer_score > rental_score:
            strategy = 'property_dealing'
            reason = f'Meilleure opportunité marchand de biens (score: {dealer_score:.1f} vs {rental_score:.1f})'
        else:
            strategy = 'both_viable'
            reason = 'Les deux stratégies sont équivalentes'
        
        return {
            'recommended_strategy': strategy,
            'reason': reason,
            'rental_score': rental_score,
            'dealer_score': dealer_score,
            'confidence': 'high' if abs(rental_score - dealer_score) > 1 else 'medium'
        }
    
    async def compare_locations_dynamic(self, locations: List[str], criteria: str = 'all') -> Dict[str, Any]:
        """Compare plusieurs localisations avec données dynamiques"""
        try:
            comparisons = []
            
            for location in locations:
                market_data = await self.get_market_data_dynamic(location)
                
                location_info = {
                    'location': location,
                    'market_data': market_data,
                    'score': self._calculate_location_score(market_data, criteria)
                }
                comparisons.append(location_info)
            
            # Trier par score
            comparisons.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'comparison_criteria': criteria,
                'locations_compared': len(locations),
                'rankings': comparisons,
                'best_location': comparisons[0]['location'] if comparisons else None,
                'summary': self._generate_comparison_summary(comparisons, criteria)
            }
            
        except Exception as e:
            logger.error(f"Erreur compare_locations_dynamic: {e}")
            return {
                'error': f'Erreur lors de la comparaison: {str(e)}',
                'locations': locations
            }
    
    def _calculate_location_score(self, market_data: Dict[str, Any], criteria: str) -> float:
        """Calcule un score pour une localisation selon les critères"""
        if market_data.get('error'):
            return 0.0
        
        score = 0.0
        
        if criteria in ['price', 'all']:
            # Score basé sur le prix (plus bas = meilleur)
            avg_price = market_data.get('avg_sale_sqm', 5000)
            price_score = max(0, (10000 - avg_price) / 10000 * 10)
            score += price_score
        
        if criteria in ['availability', 'all']:
            # Score basé sur la disponibilité (simulé)
            availability_score = market_data.get('confidence_score', 0.5) * 10
            score += availability_score
        
        if criteria in ['quality', 'all']:
            # Score basé sur la qualité du marché
            trend = market_data.get('market_trend', 'stable')
            if trend == 'growing':
                score += 8
            elif trend == 'stable':
                score += 6
            else:
                score += 3
        
        return round(score, 2)
    
    def _generate_comparison_summary(self, comparisons: List[Dict[str, Any]], criteria: str) -> str:
        """Génère un résumé de la comparaison"""
        if not comparisons:
            return "Aucune donnée disponible pour la comparaison"
        
        best = comparisons[0]
        worst = comparisons[-1]
        
        return f"Meilleure localisation: {best['location']} (score: {best['score']:.1f}). " \
               f"Moins favorable: {worst['location']} (score: {worst['score']:.1f}). " \
               f"Critère principal: {criteria}."

# Mise à jour des outils MCP pour utiliser la version dynamique
MCP_TOOLS_DYNAMIC = [
    {
        "name": "search_properties",
        "description": "Recherche des biens immobiliers avec données temps réel",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou arrondissement (ex: 'Paris 11e', 'Lyon', 'Marseille', 'Toulouse')"},
                "min_price": {"type": "number", "description": "Prix minimum en euros"},
                "max_price": {"type": "number", "description": "Prix maximum en euros"},
                "property_type": {"type": "string", "description": "Type de bien ('appartement', 'maison', etc.)"},
                "min_surface": {"type": "number", "description": "Surface minimale en m²"},
                "max_surface": {"type": "number", "description": "Surface maximale en m²"},
                "rooms": {"type": "integer", "description": "Nombre de pièces souhaité"},
                "transaction_type": {"type": "string", "enum": ["rent", "sale"], "description": "Type de transaction"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_market_data_dynamic",
        "description": "Récupère les données de marché en temps réel pour une localisation",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou zone à analyser"},
                "transaction_type": {"type": "string", "enum": ["rent", "sale"], "description": "Type de marché"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "analyze_investment_opportunity_dynamic",
        "description": "Analyse d'opportunités d'investissement avec données temps réel",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou arrondissement à analyser"},
                "min_price": {"type": "number", "description": "Prix minimum en euros"},
                "max_price": {"type": "number", "description": "Prix maximum en euros"},
                "investment_profile": {"type": "string", "enum": ["rental_investor", "property_dealer", "both"], "description": "Profil d'investissement"},
                "min_surface": {"type": "number", "description": "Surface minimale en m²"},
                "rooms": {"type": "integer", "description": "Nombre de pièces souhaité"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_renovation_costs_dynamic",
        "description": "Coûts de rénovation ajustés par région en temps réel",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Localisation du bien"},
                "surface": {"type": "number", "description": "Surface en m²"}
            },
            "required": ["location", "surface"]
        }
    }
]

if __name__ == "__main__":
    asyncio.run(main())
