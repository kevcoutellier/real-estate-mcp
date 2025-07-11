"""
Intégration de l'architecture flexible avec le système MCP existant.
Remplace les analyses rigides par des approches adaptatives.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from .services.flexible_analysis import FlexibleAnalysisService
from .models.property import PropertyListing
from .scrapers.leboncoin_scraper import LeboncoinScraper
from .scrapers.seloger_scraper import SeLogerScraper
from .services.geocoding import GeocodingService

logger = logging.getLogger(__name__)


class FlexibleMCPService:
    """Service MCP avec architecture flexible et adaptative."""
    
    def __init__(self):
        self.flexible_analyzer = FlexibleAnalysisService()
        self.scrapers = {
            'leboncoin': LeboncoinScraper(),
            'seloger': SeLogerScraper()
        }
        self.geocoding_service = GeocodingService()
        
        # Cache des contextes utilisateur
        self.user_contexts = {}
    
    async def search_properties_flexible(
        self,
        location: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type: Optional[str] = None,
        min_surface: Optional[float] = None,
        max_surface: Optional[float] = None,
        rooms: Optional[int] = None,
        transaction_type: str = "rent",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recherche flexible de propriétés avec adaptation contextuelle.
        
        Args:
            location: Localisation recherchée
            min_price, max_price: Fourchette de prix
            property_type: Type de propriété
            min_surface, max_surface: Fourchette de surface
            rooms: Nombre de pièces
            transaction_type: Type de transaction
            user_context: Contexte utilisateur pour l'adaptation
            
        Returns:
            Résultats adaptés au contexte utilisateur
        """
        logger.info(f"Recherche flexible: {location} - {transaction_type}")
        
        try:
            # Construction des critères de recherche
            search_criteria = {
                'location': location,
                'transaction_type': transaction_type
            }
            
            if min_price is not None:
                search_criteria['min_price'] = min_price
            if max_price is not None:
                search_criteria['max_price'] = max_price
            if property_type:
                search_criteria['property_type'] = property_type
            if min_surface is not None:
                search_criteria['min_surface'] = min_surface
            if max_surface is not None:
                search_criteria['max_surface'] = max_surface
            if rooms is not None:
                search_criteria['rooms'] = rooms
            
            # Recherche multi-sources
            all_properties = []
            
            for scraper_name, scraper in self.scrapers.items():
                try:
                    properties = await scraper.search_properties(**search_criteria)
                    logger.info(f"{scraper_name}: {len(properties)} propriétés trouvées")
                    all_properties.extend(properties)
                except Exception as e:
                    logger.error(f"Erreur scraper {scraper_name}: {e}")
            
            if not all_properties:
                return {
                    'type': 'no_results',
                    'message': f"Aucune propriété trouvée pour {location}",
                    'suggestions': self._generate_search_suggestions(search_criteria)
                }
            
            # Enrichissement géographique
            enriched_properties = await self._enrich_with_geocoding(all_properties)
            
            # Analyse flexible avec contexte
            context = self._build_search_context(search_criteria, user_context)
            analysis_result = await self.flexible_analyzer.analyze_market_flexible(
                enriched_properties,
                location,
                context
            )
            
            # Ajout des propriétés dans la réponse
            analysis_result['properties'] = [prop.to_dict() for prop in enriched_properties[:20]]  # Limite à 20
            analysis_result['total_found'] = len(all_properties)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erreur recherche flexible: {e}")
            return {
                'type': 'error',
                'message': f"Erreur lors de la recherche: {str(e)}",
                'fallback_suggestions': [
                    "Essayez avec des critères moins restrictifs",
                    "Vérifiez l'orthographe de la localisation"
                ]
            }
    
    async def analyze_investment_opportunity_flexible(
        self,
        location: str,
        investment_profile: str = "rental_investor",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_surface: Optional[float] = None,
        rooms: Optional[int] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse flexible d'opportunités d'investissement.
        
        Args:
            location: Zone d'investissement
            investment_profile: Profil d'investisseur
            min_price, max_price: Fourchette de prix
            min_surface: Surface minimale
            rooms: Nombre de pièces
            user_context: Contexte utilisateur
            
        Returns:
            Analyse d'investissement adaptée au profil
        """
        logger.info(f"Analyse d'investissement flexible: {location} - {investment_profile}")
        
        try:
            # Recherche de propriétés pour l'investissement
            search_criteria = {
                'location': location,
                'transaction_type': 'sale'  # Investissement = achat
            }
            
            if min_price is not None:
                search_criteria['min_price'] = min_price
            if max_price is not None:
                search_criteria['max_price'] = max_price
            if min_surface is not None:
                search_criteria['min_surface'] = min_surface
            if rooms is not None:
                search_criteria['rooms'] = rooms
            
            # Recherche multi-sources
            properties = await self._search_all_sources(search_criteria)
            
            if not properties:
                return {
                    'type': 'no_investment_opportunities',
                    'message': f"Aucune opportunité d'investissement trouvée pour {location}",
                    'alternative_suggestions': self._generate_investment_alternatives(location)
                }
            
            # Enrichissement
            enriched_properties = await self._enrich_with_geocoding(properties)
            
            # Contexte d'investissement
            investment_context = self._build_investment_context(
                investment_profile,
                search_criteria,
                user_context
            )
            
            # Analyse d'opportunités flexible
            opportunities = await self.flexible_analyzer.get_investment_opportunities_flexible(
                enriched_properties,
                investment_profile,
                investment_context
            )
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Erreur analyse d'investissement: {e}")
            return {
                'type': 'error',
                'message': f"Erreur lors de l'analyse d'investissement: {str(e)}"
            }
    
    async def compare_locations_flexible(
        self,
        locations: List[str],
        criteria: str = "all",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comparaison flexible de localisations.
        
        Args:
            locations: Localisations à comparer
            criteria: Critères de comparaison
            user_context: Contexte utilisateur
            
        Returns:
            Comparaison adaptée aux critères et contexte
        """
        logger.info(f"Comparaison flexible de {len(locations)} localisations")
        
        try:
            # Analyse de chaque localisation
            location_analyses = {}
            
            for location in locations:
                # Recherche rapide pour chaque localisation
                properties = await self._search_all_sources({
                    'location': location,
                    'transaction_type': 'rent'
                })
                
                if properties:
                    # Analyse contextuelle
                    context = self._build_comparison_context(criteria, user_context)
                    analysis = await self.flexible_analyzer.analyze_market_flexible(
                        properties[:50],  # Limite pour la comparaison
                        location,
                        context
                    )
                    location_analyses[location] = analysis
            
            # Comparaison flexible
            comparison_result = await self.flexible_analyzer.compare_locations_flexible(
                locations,
                criteria,
                user_context
            )
            
            # Enrichissement avec les analyses individuelles
            comparison_result['individual_analyses'] = location_analyses
            comparison_result['comparison_summary'] = self._generate_comparison_summary(
                location_analyses,
                criteria
            )
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Erreur comparaison de localisations: {e}")
            return {
                'type': 'error',
                'message': f"Erreur lors de la comparaison: {str(e)}"
            }
    
    async def get_market_analysis_flexible(
        self,
        location: str,
        transaction_type: str = "rent",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse de marché flexible et contextuelle.
        
        Args:
            location: Zone à analyser
            transaction_type: Type de marché
            user_context: Contexte utilisateur
            
        Returns:
            Analyse de marché adaptée
        """
        logger.info(f"Analyse de marché flexible: {location} - {transaction_type}")
        
        try:
            # Recherche étendue pour l'analyse de marché
            properties = await self._search_all_sources({
                'location': location,
                'transaction_type': transaction_type
            })
            
            if not properties:
                return {
                    'type': 'insufficient_data',
                    'message': f"Données insuffisantes pour analyser le marché de {location}",
                    'suggestions': [
                        "Essayez une zone géographique plus large",
                        "Vérifiez l'orthographe de la localisation"
                    ]
                }
            
            # Enrichissement géographique
            enriched_properties = await self._enrich_with_geocoding(properties)
            
            # Contexte d'analyse de marché
            market_context = self._build_market_context(
                location,
                transaction_type,
                user_context
            )
            
            # Analyse flexible
            market_analysis = await self.flexible_analyzer.analyze_market_flexible(
                enriched_properties,
                location,
                market_context
            )
            
            return market_analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse de marché: {e}")
            return {
                'type': 'error',
                'message': f"Erreur lors de l'analyse de marché: {str(e)}"
            }
    
    async def _search_all_sources(self, criteria: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche dans toutes les sources disponibles."""
        all_properties = []
        
        for scraper_name, scraper in self.scrapers.items():
            try:
                properties = await scraper.search_properties(**criteria)
                all_properties.extend(properties)
                logger.debug(f"{scraper_name}: {len(properties)} propriétés")
            except Exception as e:
                logger.error(f"Erreur scraper {scraper_name}: {e}")
        
        return all_properties
    
    async def _enrich_with_geocoding(self, properties: List[PropertyListing]) -> List[PropertyListing]:
        """Enrichit les propriétés avec des données géographiques."""
        enriched = []
        
        for prop in properties:
            try:
                if not prop.coordinates and prop.location:
                    coordinates = await self.geocoding_service.geocode(prop.location)
                    if coordinates:
                        prop.coordinates = coordinates
                enriched.append(prop)
            except Exception as e:
                logger.debug(f"Erreur géocodage pour {prop.location}: {e}")
                enriched.append(prop)  # Garde la propriété même sans coordonnées
        
        return enriched
    
    def _build_search_context(
        self,
        search_criteria: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construit le contexte pour la recherche."""
        context = {
            'search_criteria': search_criteria,
            'analysis_type': 'property_search'
        }
        
        if user_context:
            context.update(user_context)
        
        # Inférence du niveau d'expertise
        if not context.get('expertise_level'):
            # Logique d'inférence basée sur les critères
            if len(search_criteria) > 5:
                context['expertise_level'] = 'expert'
            elif len(search_criteria) > 3:
                context['expertise_level'] = 'intermediate'
            else:
                context['expertise_level'] = 'beginner'
        
        return context
    
    def _build_investment_context(
        self,
        investment_profile: str,
        search_criteria: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construit le contexte pour l'analyse d'investissement."""
        context = {
            'investment_profile': investment_profile,
            'search_criteria': search_criteria,
            'analysis_type': 'investment_analysis'
        }
        
        if user_context:
            context.update(user_context)
        
        # Paramètres par défaut selon le profil
        profile_defaults = {
            'rental_investor': {
                'risk_tolerance': 'medium',
                'time_horizon': 'long_term',
                'expected_return': 0.05
            },
            'property_dealer': {
                'risk_tolerance': 'high',
                'time_horizon': 'short_term',
                'expected_return': 0.15
            },
            'both': {
                'risk_tolerance': 'medium',
                'time_horizon': 'medium_term',
                'expected_return': 0.08
            }
        }
        
        defaults = profile_defaults.get(investment_profile, {})
        for key, value in defaults.items():
            if key not in context:
                context[key] = value
        
        return context
    
    def _build_comparison_context(
        self,
        criteria: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construit le contexte pour la comparaison."""
        context = {
            'comparison_criteria': criteria,
            'analysis_type': 'location_comparison'
        }
        
        if user_context:
            context.update(user_context)
        
        return context
    
    def _build_market_context(
        self,
        location: str,
        transaction_type: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construit le contexte pour l'analyse de marché."""
        context = {
            'location': location,
            'transaction_type': transaction_type,
            'analysis_type': 'market_analysis'
        }
        
        if user_context:
            context.update(user_context)
        
        return context
    
    def _generate_search_suggestions(self, criteria: Dict[str, Any]) -> List[str]:
        """Génère des suggestions pour améliorer la recherche."""
        suggestions = []
        
        if criteria.get('max_price') and criteria.get('min_price'):
            if criteria['max_price'] - criteria['min_price'] < 50000:
                suggestions.append("Élargissez votre fourchette de prix")
        
        if criteria.get('property_type'):
            suggestions.append("Essayez sans spécifier le type de propriété")
        
        if criteria.get('rooms') and criteria['rooms'] > 3:
            suggestions.append("Réduisez le nombre de pièces recherchées")
        
        return suggestions or ["Essayez avec des critères moins restrictifs"]
    
    def _generate_investment_alternatives(self, location: str) -> List[str]:
        """Génère des alternatives d'investissement."""
        return [
            f"Explorez les zones adjacentes à {location}",
            "Considérez des propriétés à rénover",
            "Regardez les opportunités de location saisonnière"
        ]
    
    def _generate_comparison_summary(
        self,
        analyses: Dict[str, Any],
        criteria: str
    ) -> Dict[str, Any]:
        """Génère un résumé de comparaison."""
        if not analyses:
            return {'message': 'Aucune donnée disponible pour la comparaison'}
        
        summary = {
            'total_locations': len(analyses),
            'criteria_used': criteria,
            'best_location': None,
            'key_differences': []
        }
        
        # Logique de comparaison simplifiée
        if criteria == 'price':
            # Trouve la localisation avec les prix les plus bas
            min_price_location = min(
                analyses.items(),
                key=lambda x: x[1].get('price_analysis', {}).get('mean', float('inf'))
            )
            summary['best_location'] = {
                'name': min_price_location[0],
                'reason': 'Prix moyens les plus bas'
            }
        
        return summary
