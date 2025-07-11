"""
Service d'analyse flexible intégrant les nouvelles capacités adaptatives.
Remplace les analyses rigides par des approches contextuelles.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.flexible_models import FlexibleProperty, ContextualMarketAnalyzer
from ..core.dynamic_responses import ContextualResponseSystem
from ..core.adaptive_engine import AdaptiveEngine, AdaptationContext, ContextualDataEnricher
from ..models.property import PropertyListing

logger = logging.getLogger(__name__)


class FlexibleAnalysisService:
    """Service d'analyse flexible et adaptatif."""
    
    def __init__(self):
        self.market_analyzer = ContextualMarketAnalyzer()
        self.response_system = ContextualResponseSystem()
        self.adaptive_engine = AdaptiveEngine()
        self.data_enricher = ContextualDataEnricher()
        
        # Cache adaptatif
        self._cache = {}
        self._cache_strategies = {
            'aggressive': 300,   # 5 minutes
            'moderate': 1800,    # 30 minutes
            'conservative': 3600  # 1 heure
        }
    
    async def analyze_market_flexible(
        self,
        properties: List[PropertyListing],
        location: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse de marché flexible et adaptative.
        
        Args:
            properties: Liste des propriétés à analyser
            location: Localisation analysée
            context: Contexte d'analyse (préférences, historique, etc.)
            
        Returns:
            Analyse adaptée au contexte avec réponses dynamiques
        """
        logger.info(f"Analyse flexible pour {location} - {len(properties)} propriétés")
        
        # Conversion vers le modèle flexible
        flexible_properties = await self._convert_to_flexible(properties)
        
        # Construction du contexte d'adaptation
        adaptation_context = await self._build_adaptation_context(context or {}, location)
        
        # Enrichissement des données
        enriched_data = await self.data_enricher.enrich_data(
            {'properties': flexible_properties, 'location': location},
            adaptation_context
        )
        
        # Analyse contextuelle
        analysis_result = await self.market_analyzer.analyze(
            flexible_properties,
            adaptation_context.__dict__
        )
        
        # Adaptation selon le contexte
        adapted_analysis = await self.adaptive_engine.adapt_analysis(
            analysis_result,
            adaptation_context
        )
        
        # Génération de réponse dynamique
        final_response = self.response_system.generate_response(
            adapted_analysis,
            adaptation_context.__dict__
        )
        
        # Mise en cache adaptative
        cache_key = self._generate_cache_key(location, context)
        cache_strategy = self._determine_cache_strategy(adapted_analysis)
        await self._cache_result(cache_key, final_response, cache_strategy)
        
        return final_response
    
    async def compare_locations_flexible(
        self,
        locations: List[str],
        criteria: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comparaison flexible de localisations.
        
        Args:
            locations: Liste des localisations à comparer
            criteria: Critères de comparaison
            context: Contexte utilisateur
            
        Returns:
            Comparaison adaptée avec insights contextuels
        """
        logger.info(f"Comparaison flexible de {len(locations)} localisations")
        
        # Construction du contexte
        adaptation_context = await self._build_adaptation_context(context or {})
        adaptation_context.geographic_context['focus_areas'] = locations
        
        # Analyse comparative adaptative
        comparison_data = {
            'locations': locations,
            'criteria': criteria or 'all',
            'comparison_type': 'flexible'
        }
        
        # Adaptation selon le contexte
        adapted_comparison = await self.adaptive_engine.adapt_analysis(
            comparison_data,
            adaptation_context
        )
        
        # Génération de réponse contextuelle
        response = self.response_system.generate_response(
            adapted_comparison,
            {'format': 'summary', 'tone': 'conversational'}
        )
        
        return response
    
    async def get_investment_opportunities_flexible(
        self,
        properties: List[PropertyListing],
        investment_profile: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identification flexible d'opportunités d'investissement.
        
        Args:
            properties: Propriétés à analyser
            investment_profile: Profil d'investisseur
            context: Contexte d'investissement
            
        Returns:
            Opportunités adaptées au profil et contexte
        """
        logger.info(f"Recherche d'opportunités pour profil {investment_profile}")
        
        # Conversion et enrichissement
        flexible_properties = await self._convert_to_flexible(properties)
        
        # Contexte d'investissement
        investment_context = await self._build_investment_context(
            investment_profile,
            context or {}
        )
        
        # Analyse d'investissement adaptative
        investment_data = {
            'properties': flexible_properties,
            'investment_profile': investment_profile,
            'analysis_type': 'investment_opportunity'
        }
        
        # Application de l'analyse contextuelle
        analysis_result = await self.market_analyzer.analyze(
            flexible_properties,
            investment_context.__dict__
        )
        
        # Adaptation pour l'investissement
        adapted_analysis = await self.adaptive_engine.adapt_analysis(
            analysis_result,
            investment_context
        )
        
        # Réponse spécialisée investissement
        response = self.response_system.generate_response(
            adapted_analysis,
            {'format': 'investment', 'tone': 'expert'}
        )
        
        return response
    
    async def _convert_to_flexible(self, properties: List[PropertyListing]) -> List[FlexibleProperty]:
        """Convertit les propriétés vers le modèle flexible."""
        flexible_properties = []
        
        for prop in properties:
            # Conversion avec enrichissement automatique
            flexible_prop = FlexibleProperty(
                id=prop.id,
                title=prop.title,
                price=prop.price,
                location=prop.location,
                property_type=prop.property_type,
                surface_area=prop.surface_area,
                rooms=prop.rooms,
                description=prop.description,
                images=prop.images or [],
                source=prop.source,
                url=prop.url
            )
            
            # Enrichissement avec coordonnées si disponibles
            if prop.coordinates:
                flexible_prop.update(coordinates=prop.coordinates)
            
            # Calcul automatique de métriques dérivées
            flexible_prop.set_confidence('price', 0.9 if prop.price > 0 else 0.3)
            flexible_prop.set_confidence('location', 0.8 if prop.location else 0.2)
            
            flexible_properties.append(flexible_prop)
        
        return flexible_properties
    
    async def _build_adaptation_context(
        self,
        context: Dict[str, Any],
        location: Optional[str] = None
    ) -> AdaptationContext:
        """Construit le contexte d'adaptation."""
        adaptation_context = AdaptationContext()
        
        # Préférences utilisateur
        if 'user_preferences' in context:
            adaptation_context.user_preferences = context['user_preferences']
        
        # Niveau d'expertise
        adaptation_context.user_expertise_level = context.get('expertise_level', 'intermediate')
        
        # Contexte géographique
        if location:
            adaptation_context.geographic_context = {
                'primary_location': location,
                'focus_areas': [location]
            }
        
        # Facteurs temporels
        adaptation_context.temporal_factors = {
            'analysis_time': datetime.now(),
            'urgency': context.get('urgency', 'normal'),
            'time_horizon': context.get('time_horizon', 'medium_term')
        }
        
        # Conditions de marché (simulées ou enrichies)
        adaptation_context.market_conditions = {
            'trend': context.get('market_trend', 'stable'),
            'volatility': context.get('market_volatility', 'medium'),
            'segment': self._detect_market_segment(context)
        }
        
        return adaptation_context
    
    async def _build_investment_context(
        self,
        investment_profile: str,
        context: Dict[str, Any]
    ) -> AdaptationContext:
        """Construit un contexte spécialisé pour l'investissement."""
        investment_context = await self._build_adaptation_context(context)
        
        # Enrichissement spécifique à l'investissement
        investment_context.user_preferences.update({
            'investment_profile': investment_profile,
            'risk_tolerance': context.get('risk_tolerance', 'medium'),
            'investment_horizon': context.get('investment_horizon', '5_years'),
            'expected_return': context.get('expected_return', 0.05)
        })
        
        # Expertise adaptée au profil
        expertise_mapping = {
            'rental_investor': 'intermediate',
            'property_dealer': 'expert',
            'both': 'expert',
            'beginner': 'beginner'
        }
        investment_context.user_expertise_level = expertise_mapping.get(
            investment_profile, 
            'intermediate'
        )
        
        return investment_context
    
    def _detect_market_segment(self, context: Dict[str, Any]) -> str:
        """Détecte le segment de marché à partir du contexte."""
        max_price = context.get('max_price', 0)
        min_price = context.get('min_price', 0)
        
        if max_price > 800000:
            return 'luxury'
        elif max_price < 200000:
            return 'budget'
        elif context.get('investment_profile') == 'rental_investor':
            return 'rental'
        else:
            return 'standard'
    
    def _generate_cache_key(self, location: str, context: Optional[Dict[str, Any]]) -> str:
        """Génère une clé de cache contextuelle."""
        context_hash = hash(str(sorted((context or {}).items())))
        return f"flexible_analysis_{location}_{context_hash}"
    
    def _determine_cache_strategy(self, analysis: Dict[str, Any]) -> str:
        """Détermine la stratégie de cache selon l'analyse."""
        total_properties = analysis.get('total_properties', 0)
        
        if total_properties > 100:
            return 'conservative'  # Cache plus long pour les gros volumes
        elif total_properties > 20:
            return 'moderate'
        else:
            return 'aggressive'  # Cache court pour les petits échantillons
    
    async def _cache_result(self, key: str, result: Dict[str, Any], strategy: str):
        """Met en cache le résultat selon la stratégie."""
        ttl = self._cache_strategies.get(strategy, 1800)
        expiry = datetime.now().timestamp() + ttl
        
        self._cache[key] = {
            'data': result,
            'expiry': expiry,
            'strategy': strategy
        }
        
        # Nettoyage périodique du cache
        await self._cleanup_cache()
    
    async def _cleanup_cache(self):
        """Nettoie le cache des entrées expirées."""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, value in self._cache.items()
            if value['expiry'] < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cache nettoyé: {len(expired_keys)} entrées supprimées")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        await self._cleanup_cache()
        
        strategies_count = {}
        for value in self._cache.values():
            strategy = value['strategy']
            strategies_count[strategy] = strategies_count.get(strategy, 0) + 1
        
        return {
            'total_entries': len(self._cache),
            'strategies_distribution': strategies_count,
            'cache_hit_potential': len(self._cache) > 0
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du service."""
        return {
            'adaptive_engine_stats': self.adaptive_engine.get_adaptation_stats(),
            'cache_stats': asyncio.create_task(self.get_cache_stats()),
            'analyzers': {
                'market_analyzer': 'ContextualMarketAnalyzer',
                'response_system': 'ContextualResponseSystem',
                'adaptive_engine': 'AdaptiveEngine'
            }
        }
