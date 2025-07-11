"""
Services d'analyse de marché immobilier.

Ce module fournit des services pour analyser les données de marché immobilier,
calculer des statistiques, identifier des tendances et générer des insights.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

from ..models.property import PropertyListing

logger = logging.getLogger(__name__)


@dataclass
class MarketStats:
    """Statistiques de marché pour une zone donnée."""
    location: str
    total_listings: int
    price_stats: Dict[str, float]
    price_per_sqm_stats: Dict[str, float]
    surface_stats: Dict[str, float]
    rooms_distribution: Dict[int, int]
    property_types: Dict[str, int]
    transaction_type: str
    analysis_date: datetime


@dataclass
class MarketTrend:
    """Tendance de marché identifiée."""
    trend_type: str  # 'price_increase', 'price_decrease', 'high_demand', etc.
    description: str
    confidence: float  # 0.0 to 1.0
    supporting_data: Dict[str, Any]


class MarketAnalysisService:
    """Service d'analyse de marché immobilier."""
    
    def __init__(self):
        """Initialise le service d'analyse de marché."""
        self.cache = {}
        self.cache_ttl = 3600  # 1 heure
        
    async def analyze_market(
        self,
        properties: List[PropertyListing],
        location: str,
        transaction_type: str = 'rent'
    ) -> MarketStats:
        """
        Analyse le marché pour une liste de propriétés.
        
        Args:
            properties: Liste des propriétés à analyser
            location: Localisation analysée
            transaction_type: Type de transaction ('rent' ou 'sale')
            
        Returns:
            Statistiques de marché complètes
        """
        logger.info(f"Analyse de marché pour {location} - {len(properties)} propriétés")
        
        if not properties:
            return MarketStats(
                location=location,
                total_listings=0,
                price_stats={},
                price_per_sqm_stats={},
                surface_stats={},
                rooms_distribution={},
                property_types={},
                transaction_type=transaction_type,
                analysis_date=datetime.now()
            )
        
        # Calcul des statistiques de prix
        prices = [p.price for p in properties if p.price and p.price > 0]
        price_stats = self._calculate_stats(prices) if prices else {}
        
        # Calcul des statistiques de prix au m²
        price_per_sqm = [
            p.price / p.surface_area 
            for p in properties 
            if p.price and p.surface_area and p.price > 0 and p.surface_area > 0
        ]
        price_per_sqm_stats = self._calculate_stats(price_per_sqm) if price_per_sqm else {}
        
        # Calcul des statistiques de surface
        surfaces = [p.surface_area for p in properties if p.surface_area and p.surface_area > 0]
        surface_stats = self._calculate_stats(surfaces) if surfaces else {}
        
        # Distribution des nombres de pièces
        rooms_distribution = defaultdict(int)
        for p in properties:
            if p.rooms:
                rooms_distribution[p.rooms] += 1
        
        # Distribution des types de propriétés
        property_types = defaultdict(int)
        for p in properties:
            if p.property_type:
                property_types[p.property_type] += 1
        
        return MarketStats(
            location=location,
            total_listings=len(properties),
            price_stats=price_stats,
            price_per_sqm_stats=price_per_sqm_stats,
            surface_stats=surface_stats,
            rooms_distribution=dict(rooms_distribution),
            property_types=dict(property_types),
            transaction_type=transaction_type,
            analysis_date=datetime.now()
        )
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calcule les statistiques de base pour une liste de valeurs."""
        if not values:
            return {}
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'count': len(values)
        }
    
    async def compare_markets(
        self,
        market_stats: List[MarketStats],
        criteria: str = 'all'
    ) -> Dict[str, Any]:
        """
        Compare plusieurs marchés selon différents critères.
        
        Args:
            market_stats: Liste des statistiques de marché à comparer
            criteria: Critère de comparaison ('price', 'availability', 'quality', 'all')
            
        Returns:
            Résultats de la comparaison
        """
        logger.info(f"Comparaison de {len(market_stats)} marchés selon {criteria}")
        
        if len(market_stats) < 2:
            return {"error": "Il faut au moins 2 marchés pour effectuer une comparaison"}
        
        comparison = {
            'locations': [stats.location for stats in market_stats],
            'criteria': criteria,
            'comparison_data': {},
            'rankings': {},
            'winner': None,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Comparaison des prix
        if criteria in ['price', 'all']:
            price_comparison = self._compare_prices(market_stats)
            comparison['comparison_data']['prices'] = price_comparison
        
        # Comparaison de la disponibilité
        if criteria in ['availability', 'all']:
            availability_comparison = self._compare_availability(market_stats)
            comparison['comparison_data']['availability'] = availability_comparison
        
        # Comparaison de la qualité (basée sur surface moyenne, etc.)
        if criteria in ['quality', 'all']:
            quality_comparison = self._compare_quality(market_stats)
            comparison['comparison_data']['quality'] = quality_comparison
        
        # Détermination du gagnant global
        comparison['winner'] = self._determine_winner(market_stats, criteria)
        
        return comparison
    
    def _compare_prices(self, market_stats: List[MarketStats]) -> Dict[str, Any]:
        """Compare les prix entre différents marchés."""
        price_data = {}
        
        for stats in market_stats:
            if stats.price_stats:
                price_data[stats.location] = {
                    'avg_price': stats.price_stats.get('avg', 0),
                    'median_price': stats.price_stats.get('median', 0),
                    'price_per_sqm': stats.price_per_sqm_stats.get('avg', 0) if stats.price_per_sqm_stats else 0
                }
        
        # Classement par prix moyen (du moins cher au plus cher)
        sorted_by_price = sorted(
            price_data.items(),
            key=lambda x: x[1]['avg_price']
        )
        
        return {
            'price_data': price_data,
            'cheapest': sorted_by_price[0][0] if sorted_by_price else None,
            'most_expensive': sorted_by_price[-1][0] if sorted_by_price else None,
            'ranking': [location for location, _ in sorted_by_price]
        }
    
    def _compare_availability(self, market_stats: List[MarketStats]) -> Dict[str, Any]:
        """Compare la disponibilité entre différents marchés."""
        availability_data = {}
        
        for stats in market_stats:
            availability_data[stats.location] = {
                'total_listings': stats.total_listings,
                'variety_score': len(stats.property_types)  # Diversité des types de biens
            }
        
        # Classement par nombre d'annonces
        sorted_by_availability = sorted(
            availability_data.items(),
            key=lambda x: x[1]['total_listings'],
            reverse=True
        )
        
        return {
            'availability_data': availability_data,
            'most_available': sorted_by_availability[0][0] if sorted_by_availability else None,
            'least_available': sorted_by_availability[-1][0] if sorted_by_availability else None,
            'ranking': [location for location, _ in sorted_by_availability]
        }
    
    def _compare_quality(self, market_stats: List[MarketStats]) -> Dict[str, Any]:
        """Compare la qualité entre différents marchés."""
        quality_data = {}
        
        for stats in market_stats:
            # Score de qualité basé sur surface moyenne et diversité
            avg_surface = stats.surface_stats.get('avg', 0) if stats.surface_stats else 0
            variety_score = len(stats.property_types)
            
            # Score composite (surface pondérée + variété)
            quality_score = (avg_surface * 0.7) + (variety_score * 10 * 0.3)
            
            quality_data[stats.location] = {
                'avg_surface': avg_surface,
                'variety_score': variety_score,
                'quality_score': quality_score
            }
        
        # Classement par score de qualité
        sorted_by_quality = sorted(
            quality_data.items(),
            key=lambda x: x[1]['quality_score'],
            reverse=True
        )
        
        return {
            'quality_data': quality_data,
            'highest_quality': sorted_by_quality[0][0] if sorted_by_quality else None,
            'lowest_quality': sorted_by_quality[-1][0] if sorted_by_quality else None,
            'ranking': [location for location, _ in sorted_by_quality]
        }
    
    def _determine_winner(self, market_stats: List[MarketStats], criteria: str) -> Dict[str, Any]:
        """Détermine le marché gagnant selon les critères."""
        if not market_stats:
            return {}
        
        # Score composite pour chaque marché
        scores = {}
        
        for stats in market_stats:
            score = 0
            factors = []
            
            # Facteur prix (inversé - moins cher = mieux)
            if criteria in ['price', 'all'] and stats.price_stats:
                avg_price = stats.price_stats.get('avg', float('inf'))
                price_score = 1 / (avg_price / 1000) if avg_price > 0 else 0
                score += price_score * 0.4
                factors.append(f"Prix avantageux: {price_score:.2f}")
            
            # Facteur disponibilité
            if criteria in ['availability', 'all']:
                availability_score = min(stats.total_listings / 10, 10)  # Normalisé sur 10
                score += availability_score * 0.3
                factors.append(f"Disponibilité: {availability_score:.2f}")
            
            # Facteur qualité
            if criteria in ['quality', 'all']:
                avg_surface = stats.surface_stats.get('avg', 0) if stats.surface_stats else 0
                variety = len(stats.property_types)
                quality_score = (avg_surface / 10) + variety
                score += quality_score * 0.3
                factors.append(f"Qualité: {quality_score:.2f}")
            
            scores[stats.location] = {
                'total_score': score,
                'factors': factors
            }
        
        # Trouver le gagnant
        winner_location = max(scores.keys(), key=lambda x: scores[x]['total_score'])
        
        return {
            'location': winner_location,
            'score': scores[winner_location]['total_score'],
            'factors': scores[winner_location]['factors'],
            'all_scores': scores
        }
    
    async def identify_trends(
        self,
        market_stats: MarketStats,
        historical_data: Optional[List[MarketStats]] = None
    ) -> List[MarketTrend]:
        """
        Identifie les tendances de marché.
        
        Args:
            market_stats: Statistiques actuelles du marché
            historical_data: Données historiques pour comparaison
            
        Returns:
            Liste des tendances identifiées
        """
        trends = []
        
        # Analyse de la demande basée sur le nombre d'annonces
        if market_stats.total_listings > 100:
            trends.append(MarketTrend(
                trend_type='high_demand',
                description=f"Forte demande détectée avec {market_stats.total_listings} annonces",
                confidence=0.8,
                supporting_data={'total_listings': market_stats.total_listings}
            ))
        elif market_stats.total_listings < 20:
            trends.append(MarketTrend(
                trend_type='low_supply',
                description=f"Offre limitée avec seulement {market_stats.total_listings} annonces",
                confidence=0.7,
                supporting_data={'total_listings': market_stats.total_listings}
            ))
        
        # Analyse des prix
        if market_stats.price_stats:
            avg_price = market_stats.price_stats.get('avg', 0)
            std_dev = market_stats.price_stats.get('std_dev', 0)
            
            # Volatilité des prix
            if std_dev > avg_price * 0.3:  # Écart-type > 30% de la moyenne
                trends.append(MarketTrend(
                    trend_type='price_volatility',
                    description="Forte volatilité des prix détectée",
                    confidence=0.6,
                    supporting_data={
                        'avg_price': avg_price,
                        'std_dev': std_dev,
                        'volatility_ratio': std_dev / avg_price if avg_price > 0 else 0
                    }
                ))
        
        # Analyse de la diversité des biens
        if len(market_stats.property_types) > 5:
            trends.append(MarketTrend(
                trend_type='diverse_market',
                description=f"Marché diversifié avec {len(market_stats.property_types)} types de biens",
                confidence=0.7,
                supporting_data={'property_types': market_stats.property_types}
            ))
        
        return trends
    
    async def generate_market_insights(
        self,
        market_stats: MarketStats,
        trends: Optional[List[MarketTrend]] = None
    ) -> List[str]:
        """
        Génère des insights textuels sur le marché.
        
        Args:
            market_stats: Statistiques du marché
            trends: Tendances identifiées (optionnel)
            
        Returns:
            Liste d'insights textuels
        """
        insights = []
        
        # Insights sur les prix
        if market_stats.price_stats:
            avg_price = market_stats.price_stats.get('avg', 0)
            median_price = market_stats.price_stats.get('median', 0)
            
            if avg_price > median_price * 1.2:
                insights.append(
                    "Le prix moyen est significativement supérieur au prix médian, "
                    "indiquant la présence de biens haut de gamme qui tirent les prix vers le haut."
                )
            
            if market_stats.price_per_sqm_stats:
                price_per_sqm = market_stats.price_per_sqm_stats.get('avg', 0)
                if price_per_sqm > 0:
                    insights.append(f"Prix moyen au m² : {price_per_sqm:.0f} €/m²")
        
        # Insights sur la disponibilité
        if market_stats.total_listings > 50:
            insights.append("Bonne disponibilité de biens sur ce marché.")
        elif market_stats.total_listings < 10:
            insights.append("Marché tendu avec peu de biens disponibles.")
        
        # Insights sur les types de biens
        if market_stats.property_types:
            most_common = max(market_stats.property_types.items(), key=lambda x: x[1])
            insights.append(f"Type de bien le plus courant : {most_common[0]} ({most_common[1]} annonces)")
        
        # Insights basés sur les tendances
        if trends:
            for trend in trends:
                if trend.confidence > 0.7:
                    insights.append(trend.description)
        
        return insights
