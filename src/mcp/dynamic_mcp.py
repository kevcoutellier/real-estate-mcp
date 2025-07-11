#!/usr/bin/env python3
"""
MCP avec données dynamiques en temps réel
"""

import logging
from typing import Dict, List, Optional, Any
from .enriched_mcp import EnrichedRealEstateMCP
from ..dynamic_data_service import DynamicDataService, get_dynamic_service

logger = logging.getLogger(__name__)


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
               f"Critères: {criteria}"
