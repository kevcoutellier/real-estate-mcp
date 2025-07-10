#!/usr/bin/env python3
"""
MCP Immobilier Spécialisé - Investissement Locatif & Marchand de Biens
Extension du MCP principal avec analyses métier avancées
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import httpx
from bs4 import BeautifulSoup
import re

# Import du MCP de base
from main import PropertyListing, RealEstateMCP, EnrichedRealEstateMCP

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestmentProfile(Enum):
    """Profils d'investissement"""
    RENTAL_INVESTOR = "rental_investor"  # Investisseur locatif
    PROPERTY_DEALER = "property_dealer"   # Marchand de biens
    BOTH = "both"                        # Les deux activités

@dataclass
class RentalAnalysis:
    """Analyse pour l'investissement locatif"""
    # Rentabilité
    gross_yield: float  # Rendement brut (%)
    net_yield: float    # Rendement net (%)
    cash_flow: float    # Cash-flow mensuel (€)
    
    # Estimations loyer
    estimated_rent: float        # Loyer estimé (€/mois)
    rent_per_sqm: float         # Loyer au m² (€/m²/mois)
    market_rent_range: Dict[str, float]  # Fourchette marché
    
    # Charges et fiscalité
    monthly_charges: float      # Charges mensuelles estimées
    annual_taxes: float        # Taxes foncières annuelles
    management_fees: float     # Frais de gestion (%)
    
    # Analyse quartier
    rental_demand: str         # Forte/Moyenne/Faible
    tenant_profile: str        # Profil locataire cible
    vacancy_risk: str         # Risque de vacance
    
    # Projections
    capital_appreciation: float  # Plus-value estimée sur 10 ans (%)
    total_return_projection: float  # Rendement total projeté (%)
    
    # Recommandations
    investment_score: float    # Score d'investissement (/100)
    pros: List[str]           # Points positifs
    cons: List[str]           # Points négatifs
    recommendations: List[str] # Recommandations d'action

@dataclass
class DealerAnalysis:
    """Analyse pour marchand de biens"""
    # Estimation travaux
    renovation_cost: float        # Coût rénovation estimé (€)
    renovation_duration: int      # Durée travaux (semaines)
    renovation_breakdown: Dict[str, float]  # Détail par poste
    
    # Prix de marché
    market_value_current: float   # Valeur actuelle marché
    market_value_renovated: float # Valeur après rénovation
    comparable_sales: List[Dict]  # Ventes comparables
    
    # Rentabilité
    gross_margin: float          # Marge brute (€)
    gross_margin_percent: float  # Marge brute (%)
    net_margin: float           # Marge nette après frais (€)
    total_investment: float     # Investissement total requis
    
    # Timing
    estimated_sale_duration: int  # Durée de revente (mois)
    market_liquidity: str        # Liquidité du marché
    seasonal_factors: str        # Facteurs saisonniers
    
    # Risques
    market_risk: str            # Risque marché
    renovation_risk: str        # Risque chantier
    liquidity_risk: str        # Risque liquidité
    
    # Recommandations
    dealer_score: float         # Score marchand de biens (/100)
    opportunity_level: str      # Niveau d'opportunité
    action_plan: List[str]     # Plan d'action recommandé
    alerts: List[str]          # Alertes importantes

class SpecializedRealEstateMCP:
    """MCP spécialisé pour investissement locatif et marchand de biens"""
    
    def __init__(self, base_mcp: Optional[RealEstateMCP] = None):
        # Utilisation du MCP enrichi si disponible, sinon MCP de base
        self.base_mcp = base_mcp or EnrichedRealEstateMCP()
        
        # Analyseurs spécialisés (importés localement pour éviter les imports circulaires)
        self.rental_analyzer = None
        self.dealer_analyzer = None
        
        # Configuration
        self.name = "specialized-real-estate-mcp"
        self.version = "2.0.0"
    
    def _init_analyzers(self):
        """Initialise les analyseurs de façon lazy"""
        if self.rental_analyzer is None:
            from rental_analyzer import RentalMarketAnalyzer
            self.rental_analyzer = RentalMarketAnalyzer()
        
        if self.dealer_analyzer is None:
            from dealer_analyzer import PropertyDealerAnalyzer
            self.dealer_analyzer = PropertyDealerAnalyzer()
    
    async def analyze_investment_opportunity(self, 
                                           location: str,
                                           min_price: Optional[float] = None,
                                           max_price: Optional[float] = None,
                                           investment_profile: InvestmentProfile = InvestmentProfile.BOTH,
                                           **kwargs) -> Dict[str, Any]:
        """
        Analyse complète d'opportunité d'investissement
        
        Args:
            location: Localisation de recherche
            min_price, max_price: Fourchette de prix
            investment_profile: Type d'analyse (locatif, marchand, ou les deux)
            **kwargs: Autres critères de recherche
        """
        
        # Recherche des biens avec le MCP de base
        search_results = await self.base_mcp.search_properties(
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
        
        # Initialiser les analyseurs
        self._init_analyzers()
        
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
                    rental_analysis = await self.rental_analyzer.analyze_rental_potential(property_data)
                    opportunity["analyses"]["rental"] = asdict(rental_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse locative: {e}")
                    opportunity["analyses"]["rental"] = {"error": str(e)}
            
            # Analyse marchand de biens
            if investment_profile in [InvestmentProfile.PROPERTY_DEALER, InvestmentProfile.BOTH]:
                try:
                    dealer_analysis = await self.dealer_analyzer.analyze_dealer_opportunity(property_data)
                    opportunity["analyses"]["dealer"] = asdict(dealer_analysis)
                except Exception as e:
                    logger.error(f"Erreur analyse marchand: {e}")
                    opportunity["analyses"]["dealer"] = {"error": str(e)}
            
            analyzed_opportunities.append(opportunity)
        
        # Tri selon le profil
        sorted_opportunities = self._rank_opportunities(analyzed_opportunities, investment_profile)
        
        # Résumé global
        market_summary = await self._generate_market_summary(location, sorted_opportunities, investment_profile)
        
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
        """Compare les stratégies locatives vs marchand de biens"""
        
        # Initialiser les analyseurs
        self._init_analyzers()
        
        # Analyses des deux stratégies
        rental_analysis = await self.rental_analyzer.analyze_rental_potential(property_data)
        dealer_analysis = await self.dealer_analyzer.analyze_dealer_opportunity(property_data)
        
        # Comparaison des rendements
        rental_total_return = rental_analysis.total_return_projection
        dealer_annual_return = (dealer_analysis.gross_margin_percent / 
                               (dealer_analysis.renovation_duration / 52 + 
                                dealer_analysis.estimated_sale_duration / 12))
        
        # Comparaison des risques
        risk_comparison = {
            "rental": {
                "market_risk": "Moyen",
                "liquidity_risk": "Faible",
                "management_complexity": "Moyen"
            },
            "dealer": {
                "market_risk": dealer_analysis.market_risk,
                "liquidity_risk": dealer_analysis.liquidity_risk,
                "management_complexity": "Élevé"
            }
        }
        
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
                "risk_comparison": risk_comparison,
                "recommendation": recommendation
            }
        }
    
    def _rank_opportunities(self, opportunities: List[Dict], 
                          investment_profile: InvestmentProfile) -> List[Dict]:
        """Classe les opportunités selon le profil d'investissement"""
        
        def get_score(opportunity):
            if investment_profile == InvestmentProfile.RENTAL_INVESTOR:
                rental = opportunity["analyses"].get("rental", {})
                return rental.get("investment_score", 0)
            elif investment_profile == InvestmentProfile.PROPERTY_DEALER:
                dealer = opportunity["analyses"].get("dealer", {})
                return dealer.get("dealer_score", 0)
            else:  # BOTH
                rental = opportunity["analyses"].get("rental", {})
                dealer = opportunity["analyses"].get("dealer", {})
                rental_score = rental.get("investment_score", 0)
                dealer_score = dealer.get("dealer_score", 0)
                return max(rental_score, dealer_score)  # Meilleur des deux
        
        return sorted(opportunities, key=get_score, reverse=True)
    
    async def _generate_market_summary(self, location: str, opportunities: List[Dict],
                                     investment_profile: InvestmentProfile) -> Dict[str, Any]:
        """Génère un résumé du marché selon le profil"""
        
        if not opportunities:
            return {"error": "Pas de données pour générer le résumé"}
        
        summary = {
            "location": location,
            "total_analyzed": len(opportunities),
            "investment_profile": investment_profile.value
        }
        
        if investment_profile in [InvestmentProfile.RENTAL_INVESTOR, InvestmentProfile.BOTH]:
            rental_data = [opp["analyses"].get("rental", {}) for opp in opportunities 
                          if "rental" in opp["analyses"] and "error" not in opp["analyses"]["rental"]]
            
            if rental_data:
                avg_yield = sum(r.get("net_yield", 0) for r in rental_data) / len(rental_data)
                avg_score = sum(r.get("investment_score", 0) for r in rental_data) / len(rental_data)
                
                summary["rental_market"] = {
                    "average_net_yield": round(avg_yield, 2),
                    "average_investment_score": round(avg_score, 1),
                    "opportunities_count": len([r for r in rental_data if r.get("investment_score", 0) > 60])
                }
        
        if investment_profile in [InvestmentProfile.PROPERTY_DEALER, InvestmentProfile.BOTH]:
            dealer_data = [opp["analyses"].get("dealer", {}) for opp in opportunities 
                          if "dealer" in opp["analyses"] and "error" not in opp["analyses"]["dealer"]]
            
            if dealer_data:
                avg_margin = sum(d.get("gross_margin_percent", 0) for d in dealer_data) / len(dealer_data)
                avg_score = sum(d.get("dealer_score", 0) for d in dealer_data) / len(dealer_data)
                
                summary["dealer_market"] = {
                    "average_gross_margin": round(avg_margin, 1),
                    "average_dealer_score": round(avg_score, 1),
                    "opportunities_count": len([d for d in dealer_data if d.get("dealer_score", 0) > 70])
                }
        
        return summary

# Configuration des outils MCP pour Claude
SPECIALIZED_MCP_TOOLS = [
    {
        "name": "analyze_investment_opportunity",
        "description": "Analyse d'opportunités d'investissement immobilier (locatif et/ou marchand de biens)",
        "parameters": {
            "location": {
                "type": "string",
                "description": "Localisation de recherche",
                "required": True
            },
            "min_price": {
                "type": "number",
                "description": "Prix minimum",
                "required": False
            },
            "max_price": {
                "type": "number",
                "description": "Prix maximum",
                "required": False
            },
            "investment_profile": {
                "type": "string",
                "description": "Profil d'investissement: 'rental_investor', 'property_dealer', ou 'both'",
                "required": False,
                "default": "both"
            },
            "surface_area": {
                "type": "number",
                "description": "Surface minimale en m²",
                "required": False
            }
        }
    },
    {
        "name": "compare_investment_strategies",
        "description": "Compare les stratégies locatives vs marchand de biens pour un bien",
        "parameters": {
            "location": {
                "type": "string",
                "description": "Localisation du bien",
                "required": True
            },
            "property_data": {
                "type": "object",
                "description": "Données du bien immobilier",
                "required": True
            }
        }
    }
]
