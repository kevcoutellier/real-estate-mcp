#!/usr/bin/env python3
"""
MCP avec enrichissement géographique et analyses d'investissement
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime
try:
    from .base_mcp import RealEstateMCP
    from ..models.property import PropertyListing
    from ..models.investment import InvestmentProfile, RentalAnalysis, DealerAnalysis
    from ..aggregators.property_aggregator import EnrichedPropertyAggregator
except ImportError:
    from base_mcp import RealEstateMCP
    from models.property import PropertyListing
    from models.investment import InvestmentProfile, RentalAnalysis, DealerAnalysis
    from aggregators.property_aggregator import EnrichedPropertyAggregator

logger = logging.getLogger(__name__)


class EnrichedRealEstateMCP(RealEstateMCP):
    """MCP avec enrichissement géographique et analyses d'investissement"""
    
    def __init__(self):
        super().__init__()
        self.aggregator = EnrichedPropertyAggregator()
        
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
            'sample_listings': [self._listing_to_dict(l) for l in listings[:5]]  # 5 exemples
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
                                           investment_profile: str = "both",
                                           **kwargs) -> Dict[str, Any]:
        """Analyse complète d'opportunité d'investissement"""
        
        # Convertir le profil en enum
        profile_enum = InvestmentProfile.BOTH
        if investment_profile == "rental_investor":
            profile_enum = InvestmentProfile.RENTAL_INVESTOR
        elif investment_profile == "property_dealer":
            profile_enum = InvestmentProfile.PROPERTY_DEALER
        
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
                    "investment_profile": investment_profile
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
            if profile_enum in [InvestmentProfile.RENTAL_INVESTOR, InvestmentProfile.BOTH]:
                try:
                    rental_analysis = self._analyze_rental_potential_simple(property_data)
                    opportunity["analyses"]["rental"] = asdict(rental_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse locative: {e}")
                    opportunity["analyses"]["rental"] = {"error": str(e)}
            
            # Analyse marchand de biens
            if profile_enum in [InvestmentProfile.PROPERTY_DEALER, InvestmentProfile.BOTH]:
                try:
                    dealer_analysis = self._analyze_dealer_opportunity_simple(property_data)
                    opportunity["analyses"]["dealer"] = asdict(dealer_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse marchand: {e}")
                    opportunity["analyses"]["dealer"] = {"error": str(e)}
            
            analyzed_opportunities.append(opportunity)
        
        # Tri selon le profil
        sorted_opportunities = self._rank_opportunities(analyzed_opportunities, profile_enum)
        
        # Résumé global
        market_summary = self._generate_market_summary(location, sorted_opportunities, profile_enum)
        
        return {
            "location": location,
            "investment_profile": investment_profile,
            "total_opportunities": len(sorted_opportunities),
            "market_summary": market_summary,
            "top_opportunities": sorted_opportunities[:5],  # Top 5
            "analysis_date": datetime.now().isoformat()
        }
    
    async def compare_investment_strategies(self, location: str, 
                                          property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les stratégies d'investissement locatif vs marchand de biens"""
        
        # Analyses des deux stratégies
        rental_analysis = self._analyze_rental_potential_simple(property_data)
        dealer_analysis = self._analyze_dealer_opportunity_simple(property_data)
        
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
    
    def _analyze_rental_potential_simple(self, property_data: Dict[str, Any]) -> RentalAnalysis:
        """Analyse simplifiée du potentiel locatif d'un bien"""
        price = property_data.get('price', 0)
        surface_area = property_data.get('surface_area', 50)
        location = property_data.get('location', '')
        
        # Estimation du loyer (données simplifiées)
        rent_per_sqm = 25  # €/m² par défaut
        if 'paris' in location.lower():
            rent_per_sqm = 35
        elif any(city in location.lower() for city in ['lyon', 'marseille', 'toulouse']):
            rent_per_sqm = 18
        
        estimated_rent = surface_area * rent_per_sqm
        gross_yield = (estimated_rent * 12 / price) * 100 if price > 0 else 0
        
        # Charges et taxes estimées
        monthly_charges = surface_area * 3  # 3€/m²
        annual_taxes = price * 0.01  # 1% du prix
        
        net_yield = gross_yield - ((monthly_charges * 12 + annual_taxes) / price * 100) if price > 0 else 0
        cash_flow = estimated_rent - monthly_charges - (annual_taxes / 12)
        
        # Score d'investissement
        investment_score = min(net_yield * 10, 100)
        
        return RentalAnalysis(
            gross_yield=gross_yield,
            net_yield=net_yield,
            cash_flow=cash_flow,
            estimated_rent=estimated_rent,
            rent_per_sqm=rent_per_sqm,
            monthly_charges=monthly_charges,
            annual_taxes=annual_taxes,
            rental_demand="Moyen",
            tenant_profile="Jeunes actifs",
            vacancy_risk="Faible",
            capital_appreciation=2.5,
            investment_score=investment_score,
            pros=["Bon rendement", "Quartier dynamique"],
            cons=["Charges élevées"],
            recommendations=["Négocier le prix", "Vérifier l'état"]
        )
    
    def _analyze_dealer_opportunity_simple(self, property_data: Dict[str, Any]) -> DealerAnalysis:
        """Analyse simplifiée d'opportunité marchand de biens"""
        price = property_data.get('price', 0)
        surface_area = property_data.get('surface_area', 50)
        
        # Coûts de rénovation estimés
        renovation_cost = surface_area * 800  # 800€/m²
        renovation_duration = max(8, surface_area / 10)  # semaines
        
        # Valeur après rénovation
        market_value_renovated = price * 1.25  # +25%
        gross_margin = market_value_renovated - price - renovation_cost
        gross_margin_percent = (gross_margin / price) * 100 if price > 0 else 0
        
        # Frais de transaction
        transaction_costs = price * 0.08  # 8%
        net_margin = gross_margin - transaction_costs
        
        total_investment = price + renovation_cost + transaction_costs
        
        # Score marchand de biens
        dealer_score = min(gross_margin_percent * 3, 100)
        
        opportunity_level = "Faible"
        if gross_margin_percent > 20:
            opportunity_level = "Excellente"
        elif gross_margin_percent > 15:
            opportunity_level = "Bonne"
        elif gross_margin_percent > 10:
            opportunity_level = "Moyenne"
        
        return DealerAnalysis(
            renovation_cost=renovation_cost,
            renovation_duration=int(renovation_duration),
            market_value_current=price,
            market_value_renovated=market_value_renovated,
            gross_margin=gross_margin,
            gross_margin_percent=gross_margin_percent,
            net_margin=net_margin,
            total_investment=total_investment,
            estimated_sale_duration=6,  # mois
            market_liquidity="Moyenne",
            market_risk="Moyen",
            renovation_risk="Faible",
            dealer_score=dealer_score,
            opportunity_level=opportunity_level,
            action_plan=["Négocier le prix", "Planifier les travaux"],
            alerts=["Vérifier l'état structural"]
        )
    
    def _rank_opportunities(self, opportunities: List[Dict[str, Any]], 
                          investment_profile: InvestmentProfile) -> List[Dict[str, Any]]:
        """Classe les opportunités selon le profil d'investissement"""
        
        def get_score(opp):
            if investment_profile == InvestmentProfile.RENTAL_INVESTOR:
                return opp.get('analyses', {}).get('rental', {}).get('investment_score', 0)
            elif investment_profile == InvestmentProfile.PROPERTY_DEALER:
                return opp.get('analyses', {}).get('dealer', {}).get('dealer_score', 0)
            else:  # BOTH
                rental_score = opp.get('analyses', {}).get('rental', {}).get('investment_score', 0)
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
                good_opportunities = len([r for r in rental_analyses if r.get('investment_score', 0) > 70])
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
    
    async def close(self):
        """Ferme l'agrégateur enrichi"""
        await self.aggregator.close()
