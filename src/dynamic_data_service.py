#!/usr/bin/env python3
"""
Service de données dynamiques pour le MCP Real Estate
Récupère les données en temps réel depuis des APIs officielles
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Données de marché pour une zone"""
    location: str
    avg_rent_sqm: float
    avg_sale_sqm: float
    market_trend: str
    last_updated: datetime
    source: str
    confidence_score: float

class DynamicDataService:
    """Service pour récupérer des données immobilières en temps réel"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache 6h
        
        # APIs disponibles
        self.apis = {
            'seloger': 'https://www.seloger.com/prix-de-l-immo',
            'leboncoin': 'https://api.leboncoin.fr',
            'dvf': 'https://api.cquest.org/dvf',  # Demandes de valeurs foncières
            'observatoires': 'https://www.observatoires-des-loyers.org',
            'insee': 'https://api.insee.fr/series/BDM/V1'
        }
    
    async def get_market_data(self, location: str, transaction_type: str = 'rent') -> Optional[MarketData]:
        """Récupère les données de marché pour une localisation"""
        logger.info(f"Début de la récupération des données pour {location} (type: {transaction_type})")
        
        if not location:
            logger.error("Aucune localisation fournie")
            return None
            
        # Vérifier le cache
        cache_key = f"{location}_{transaction_type}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Données trouvées dans le cache pour {location}")
            return self.cache[cache_key]
        
        # Essayer plusieurs sources
        market_data = None
        sources_tried = []
        
        try:
            # 1. Essayer DVF (Demandes de Valeurs Foncières) - données officielles
            logger.info("Tentative avec DVF...")
            market_data = await self._get_dvf_data(location, transaction_type)
            sources_tried.append("DVF")
            
            # 2. Fallback: Estimation basée sur données INSEE
            if not market_data:
                logger.info("Échec DVF, tentative avec INSEE...")
                market_data = await self._get_insee_estimation(location, transaction_type)
                sources_tried.append("INSEE")
            
            # 3. Fallback: Estimation par proximité géographique
            if not market_data:
                logger.info("Échec INSEE, tentative par proximité...")
                market_data = await self._get_proximity_estimation(location, transaction_type)
                sources_tried.append("Proximité")
                
            if not market_data:
                logger.warning(f"Aucune donnée trouvée pour {location} après avoir essayé: {', '.join(sources_tried)}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données pour {location}", exc_info=True)
            
        # Mettre en cache même si c'est None pour éviter de surcharger les appels
        logger.info(f"Mise en cache des données pour {location} (trouvé: {market_data is not None})")
        self.cache[cache_key] = market_data
        
        if market_data:
            logger.info(f"Données récupérées pour {location} depuis {market_data.source} (confiance: {market_data.confidence_score})")
        else:
            logger.warning(f"Aucune donnée disponible pour {location} après avoir essayé toutes les sources")
            
        return market_data
    
    async def _get_dvf_data(self, location: str, transaction_type: str) -> Optional[MarketData]:
        """Récupère les données DVF (Demandes de Valeurs Foncières)"""
        try:
            # Géocoder d'abord la localisation
            coords = await self._geocode_location(location)
            if not coords:
                return None
            
            # Requête DVF dans un rayon de 2km
            url = f"{self.apis['dvf']}"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'dist': 2000,  # 2km
                'type_local': 'Appartement',
                'limit': 100
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('features'):
                    # Calculer prix moyen des transactions récentes
                    recent_sales = []
                    for feature in data['features']:
                        props = feature.get('properties', {})
                        if props.get('date_mutation'):
                            # Filtrer les 12 derniers mois
                            sale_date = datetime.strptime(props['date_mutation'], '%Y-%m-%d')
                            if (datetime.now() - sale_date).days <= 365:
                                price_sqm = props.get('valeur_fonciere', 0) / props.get('surface_reelle_bati', 1)
                                if price_sqm > 0:
                                    recent_sales.append(price_sqm)
                    
                    if recent_sales:
                        avg_price = sum(recent_sales) / len(recent_sales)
                        
                        # Estimer le loyer (rendement 3-5%)
                        estimated_rent = avg_price * 0.04 / 12  # 4% annuel / 12 mois
                        
                        return MarketData(
                            location=location,
                            avg_rent_sqm=estimated_rent,
                            avg_sale_sqm=avg_price,
                            market_trend="Données DVF récentes",
                            last_updated=datetime.now(),
                            source="DVF (Données officielles)",
                            confidence_score=0.9
                        )
                        
        except Exception as e:
            logger.error(f"Erreur DVF {location}: {e}")
            
        return None
    
    async def _get_insee_estimation(self, location: str, transaction_type: str) -> Optional[MarketData]:
        """Estimation basée sur les données INSEE"""
        try:
            # Récupérer le code INSEE de la commune
            insee_code = await self._get_insee_code(location)
            if not insee_code:
                return None
            
            # Récupérer les données de revenus moyens
            url = f"{self.apis['insee']}/series"
            params = {
                'idbank': f'001694056',  # Revenus fiscaux
                'startPeriod': '2022',
                'endPeriod': '2024'
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Estimation basée sur le taux d'effort standard (30%)
                if data.get('Obs'):
                    latest_income = data['Obs'][-1]['OBS_VALUE']
                    
                    # Estimation loyer max (30% du revenu)
                    max_rent_budget = latest_income * 0.30 / 12
                    
                    # Estimation surface moyenne (40m²)
                    estimated_rent_sqm = max_rent_budget / 40
                    
                    # Estimation prix vente (rendement 4%)
                    estimated_sale_sqm = estimated_rent_sqm * 12 / 0.04
                    
                    return MarketData(
                        location=location,
                        avg_rent_sqm=estimated_rent_sqm,
                        avg_sale_sqm=estimated_sale_sqm,
                        market_trend="Estimation INSEE",
                        last_updated=datetime.now(),
                        source="INSEE (Estimation)",
                        confidence_score=0.6
                    )
                    
        except Exception as e:
            logger.error(f"Erreur INSEE {location}: {e}")
            
        return None
    
    async def _get_proximity_estimation(self, location: str, transaction_type: str) -> Optional[MarketData]:
        """Estimation par proximité géographique"""
        try:
            coords = await self._geocode_location(location)
            if not coords:
                return None
            
            # Données de référence pour les grandes villes
            reference_cities = {
                'paris': {'coords': (48.8566, 2.3522), 'rent': 25.5, 'sale': 10500},
                'lyon': {'coords': (45.7640, 4.8357), 'rent': 12.3, 'sale': 5500},
                'marseille': {'coords': (43.2965, 5.3698), 'rent': 13.5, 'sale': 4200},
                'toulouse': {'coords': (43.6047, 1.4442), 'rent': 12.8, 'sale': 4800},
                'nice': {'coords': (43.7102, 7.2620), 'rent': 16.5, 'sale': 6800},
                'bordeaux': {'coords': (44.8378, -0.5792), 'rent': 13.5, 'sale': 5200},
                'nantes': {'coords': (47.2184, -1.5536), 'rent': 11.5, 'sale': 4500},
                'lille': {'coords': (50.6292, 3.0573), 'rent': 10.5, 'sale': 3600},
                'strasbourg': {'coords': (48.5734, 7.7521), 'rent': 11.0, 'sale': 4000},
                'montpellier': {'coords': (43.6110, 3.8767), 'rent': 13.0, 'sale': 4600}
            }
            
            # Calculer la distance à chaque ville de référence
            from geopy.distance import geodesic
            
            distances = []
            for city, data in reference_cities.items():
                dist = geodesic(coords, data['coords']).kilometers
                distances.append((dist, data))
            
            # Prendre les 3 villes les plus proches
            distances.sort(key=lambda x: x[0])
            closest_cities = distances[:3]
            
            # Pondération inversement proportionnelle à la distance
            total_weight = 0
            weighted_rent = 0
            weighted_sale = 0
            
            for dist, data in closest_cities:
                weight = 1 / (dist + 1)  # +1 pour éviter division par 0
                total_weight += weight
                weighted_rent += data['rent'] * weight
                weighted_sale += data['sale'] * weight
            
            if total_weight > 0:
                avg_rent = weighted_rent / total_weight
                avg_sale = weighted_sale / total_weight
                
                # Ajustement selon la taille de la commune
                population_factor = await self._get_population_factor(location)
                
                return MarketData(
                    location=location,
                    avg_rent_sqm=avg_rent * population_factor,
                    avg_sale_sqm=avg_sale * population_factor,
                    market_trend="Estimation par proximité",
                    last_updated=datetime.now(),
                    source="Estimation géographique",
                    confidence_score=0.4
                )
                
        except Exception as e:
            logger.error(f"Erreur proximité {location}: {e}")
            
        return None
    
    async def _geocode_location(self, location: str) -> Optional[Dict[str, float]]:
        """Géocode une localisation"""
        try:
            if not location:
                logger.error("Aucune localisation fournie pour le géocodage")
                return None
                
            url = "https://api-adresse.data.gouv.fr/search/"
            params = {'q': location, 'limit': 1}
            
            logger.info(f"Tentative de géocodage pour: {location}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Réponse API géocodage: {data}")
                    
                    if data.get('features') and len(data['features']) > 0:
                        coords = data['features'][0]['geometry']['coordinates']
                        result = {'lat': coords[1], 'lon': coords[0]}
                        logger.info(f"Géocodage réussi pour {location}: {result}")
                        return result
                    else:
                        logger.warning(f"Aucune donnée de géocodage pour: {location}")
                else:
                    logger.error(f"Échec du géocodage - Code HTTP {response.status_code} pour {location}")
                    logger.error(f"Réponse: {response.text}")
                    
        except httpx.RequestError as e:
            logger.error(f"Erreur de requête HTTP lors du géocodage de {location}: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON pour {location}: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du géocodage de {location}: {str(e)}", exc_info=True)
            
        return None
    
    async def _get_insee_code(self, location: str) -> Optional[str]:
        """Récupère le code INSEE d'une commune"""
        try:
            url = "https://api-adresse.data.gouv.fr/search/"
            params = {'q': location, 'limit': 1}
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    return data['features'][0]['properties'].get('citycode')
                    
        except Exception as e:
            logger.error(f"Erreur code INSEE {location}: {e}")
            
        return None
    
    async def _get_population_factor(self, location: str) -> float:
        """Facteur d'ajustement selon la population"""
        try:
            # Estimation basée sur la taille de la commune
            # Plus la commune est petite, plus les prix sont bas
            coords = await self._geocode_location(location)
            if coords:
                # Facteur basé sur la distance aux grandes villes
                # Plus on s'éloigne, plus les prix baissent
                return 1.0  # Facteur neutre pour l'instant
                
        except Exception as e:
            logger.error(f"Erreur facteur population {location}: {e}")
            
        return 1.0
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si le cache est encore valide"""
        if cache_key not in self.cache:
            return False
            
        data = self.cache[cache_key]
        if isinstance(data, MarketData):
            return (datetime.now() - data.last_updated) < self.cache_duration
            
        return False
    
    async def get_renovation_costs(self, location: str, surface: float) -> Dict[str, Any]:
        """Récupère les coûts de rénovation ajustés par région"""
        
        # Facteur régional (Paris plus cher, province moins cher)
        coords = await self._geocode_location(location)
        regional_factor = 1.0
        
        if coords:
            # Distance à Paris
            from geopy.distance import geodesic
            paris_coords = (48.8566, 2.3522)
            distance_to_paris = geodesic(coords, paris_coords).kilometers
            
            # Facteur selon la distance à Paris
            if distance_to_paris < 50:  # Île-de-France
                regional_factor = 1.2
            elif distance_to_paris < 200:  # Région parisienne élargie
                regional_factor = 1.1
            elif distance_to_paris > 500:  # Province éloignée
                regional_factor = 0.85
        
        # Coûts de base (moyennes nationales)
        base_costs = {
            "rafraichissement": 200,
            "renovation_legere": 400,
            "renovation_partielle": 700,
            "renovation_complete": 1000,
            "renovation_lourde": 1500,
            "rehabilitation_complete": 2200
        }
        
        # Ajustement régional
        adjusted_costs = {}
        for level, cost in base_costs.items():
            adjusted_costs[level] = {
                "cost_per_sqm": round(cost * regional_factor),
                "total_cost": round(cost * regional_factor * surface),
                "regional_factor": regional_factor,
                "location": location
            }
        
        return adjusted_costs
    
    async def search_properties(self, location: str, **kwargs) -> Dict[str, Any]:
        """Recherche de propriétés - Interface MCP"""
        logger.info(f"Recherche de propriétés à {location} avec critères: {kwargs}")
        
        try:
            # Récupérer les données de marché
            transaction_type = kwargs.get('transaction_type', 'rent')
            market_data = await self.get_market_data(location, transaction_type)
            
            # Générer des propriétés simulées basées sur les données de marché
            properties = await self._generate_sample_properties(location, market_data, **kwargs)
            
            return {
                "status": "success",
                "location": location,
                "properties": properties,
                "market_data": market_data.__dict__ if market_data else None,
                "message": f"Trouvé {len(properties)} propriétés à {location}"
            }
            
        except Exception as e:
            logger.error(f"Erreur recherche propriétés: {e}")
            return {
                "status": "error",
                "message": f"Erreur lors de la recherche: {str(e)}",
                "properties": []
            }
    
    async def analyze_investment_opportunity(self, location: str, **kwargs) -> Dict[str, Any]:
        """Analyse d'opportunité d'investissement - Interface MCP"""
        logger.info(f"Analyse d'investissement à {location}")
        
        try:
            market_data = await self.get_market_data(location, 'sale')
            rental_data = await self.get_market_data(location, 'rent')
            
            if not market_data or not rental_data:
                return {
                    "status": "error",
                    "message": "Données de marché insuffisantes"
                }
            
            # Calcul de rentabilité estimée
            avg_price = market_data.avg_sale_sqm * kwargs.get('min_surface', 50)
            avg_rent = rental_data.avg_rent_sqm * kwargs.get('min_surface', 50) * 12
            
            yield_rate = (avg_rent / avg_price) * 100 if avg_price > 0 else 0
            
            return {
                "status": "success",
                "location": location,
                "investment_analysis": {
                    "estimated_price": round(avg_price),
                    "estimated_annual_rent": round(avg_rent),
                    "gross_yield": round(yield_rate, 2),
                    "market_trend": market_data.market_trend,
                    "confidence": market_data.confidence_score
                },
                "message": f"Rendement brut estimé: {yield_rate:.2f}%"
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse investissement: {e}")
            return {
                "status": "error",
                "message": f"Erreur lors de l'analyse: {str(e)}"
            }
    
    async def get_property_summary(self, location: str) -> Dict[str, Any]:
        """Résumé du marché immobilier - Interface MCP"""
        logger.info(f"Résumé marché pour {location}")
        
        try:
            sale_data = await self.get_market_data(location, 'sale')
            rent_data = await self.get_market_data(location, 'rent')
            
            return {
                "status": "success",
                "location": location,
                "summary": {
                    "avg_sale_price_sqm": sale_data.avg_sale_sqm if sale_data else "N/A",
                    "avg_rent_price_sqm": rent_data.avg_rent_sqm if rent_data else "N/A",
                    "market_trend": sale_data.market_trend if sale_data else "Inconnu",
                    "last_updated": sale_data.last_updated.isoformat() if sale_data else None
                },
                "message": f"Résumé du marché pour {location}"
            }
            
        except Exception as e:
            logger.error(f"Erreur résumé marché: {e}")
            return {
                "status": "error",
                "message": f"Erreur lors du résumé: {str(e)}"
            }
    
    async def get_neighborhood_info(self, location: str) -> Dict[str, Any]:
        """Informations sur le quartier - Interface MCP"""
        return {
            "status": "success",
            "location": location,
            "neighborhood": {
                "transport": "Données de transport non disponibles",
                "amenities": "Données d'équipements non disponibles",
                "quality_of_life": "Évaluation non disponible"
            },
            "message": f"Informations de base pour {location}"
        }
    
    async def analyze_market(self, location: str, **kwargs) -> Dict[str, Any]:
        """Analyse de marché - Interface MCP"""
        return await self.get_property_summary(location)
    
    async def compare_investment_strategies(self, location: str, **kwargs) -> Dict[str, Any]:
        """Comparaison de stratégies d'investissement - Interface MCP"""
        return {
            "status": "success",
            "location": location,
            "comparison": {
                "rental_investment": "Analyse non disponible",
                "property_dealing": "Analyse non disponible"
            },
            "message": "Comparaison de stratégies non implémentée"
        }
    
    async def compare_locations(self, locations: List[str], **kwargs) -> Dict[str, Any]:
        """Comparaison de localisations - Interface MCP"""
        return {
            "status": "success",
            "locations": locations,
            "comparison": "Comparaison non implémentée",
            "message": f"Comparaison de {len(locations)} localisations"
        }
    
    async def _generate_sample_properties(self, location: str, market_data: Optional[MarketData], **kwargs) -> List[Dict[str, Any]]:
        """Génère des propriétés d'exemple basées sur les données de marché"""
        if not market_data:
            return []
        
        properties = []
        rooms = kwargs.get('rooms', 2)
        min_surface = kwargs.get('min_surface', 30)
        max_surface = kwargs.get('max_surface', 100)
        transaction_type = kwargs.get('transaction_type', 'rent')
        
        # Générer 3-5 propriétés d'exemple
        for i in range(3, 6):
            surface = min_surface + (i * 10)
            if surface > max_surface:
                surface = max_surface
            
            if transaction_type == 'sale':
                price = market_data.avg_sale_sqm * surface
                price_text = f"{int(price):,}€"
            else:
                price = market_data.avg_rent_sqm * surface
                price_text = f"{int(price)}€/mois"
            
            properties.append({
                "title": f"{rooms} pièces - {surface}m² - {location}",
                "price": int(price),
                "price_text": price_text,
                "surface": surface,
                "rooms": rooms,
                "location": location,
                "type": "appartement",
                "source": "estimation"
            })
        
        return properties
    
    async def close(self):
        """Ferme les connexions"""
        await self.client.aclose()

# Service singleton
_dynamic_service = None

async def get_dynamic_service() -> DynamicDataService:
    """Récupère l'instance du service dynamique"""
    global _dynamic_service
    if _dynamic_service is None:
        _dynamic_service = DynamicDataService()
    return _dynamic_service
