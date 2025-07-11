#!/usr/bin/env python3
"""
Service de géocodage et enrichissement géographique
"""

import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any
import httpx
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


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
        
        return min(score, 100)  # Score maximum de 100
    
    async def close(self):
        """Ferme le client HTTP"""
        await self.client.aclose()
