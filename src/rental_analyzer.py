#!/usr/bin/env python3
"""
Analyseur spécialisé pour l'investissement locatif
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from specialized_investment_mcp import RentalAnalysis

class RentalMarketAnalyzer:
    """Analyseur spécialisé pour le marché locatif"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        # Base de données des loyers par ville/quartier (simulée)
        self.rental_database = self._init_rental_database()
        
    def _init_rental_database(self) -> Dict[str, Dict]:
        """Initialise la base de données des loyers de référence"""
        return {
            "paris_11e": {
                "avg_rent_sqm": 35.5,
                "range_min": 30.0,
                "range_max": 42.0,
                "demand": "Forte",
                "tenant_profile": "Jeunes actifs, couples",
                "vacancy_rate": 2.5
            },
            "paris_20e": {
                "avg_rent_sqm": 28.5,
                "range_min": 25.0,
                "range_max": 32.0,
                "demand": "Forte",
                "tenant_profile": "Familles, jeunes actifs",
                "vacancy_rate": 3.0
            },
            "paris_16e": {
                "avg_rent_sqm": 42.0,
                "range_min": 38.0,
                "range_max": 50.0,
                "demand": "Moyenne",
                "tenant_profile": "Cadres supérieurs, familles aisées",
                "vacancy_rate": 4.5
            },
            "lyon": {
                "avg_rent_sqm": 16.5,
                "range_min": 14.0,
                "range_max": 20.0,
                "demand": "Forte",
                "tenant_profile": "Étudiants, jeunes actifs",
                "vacancy_rate": 3.5
            },
            "marseille": {
                "avg_rent_sqm": 14.0,
                "range_min": 11.0,
                "range_max": 18.0,
                "demand": "Moyenne",
                "tenant_profile": "Familles, jeunes actifs",
                "vacancy_rate": 5.0
            }
        }
    
    async def analyze_rental_potential(self, property_listing: Dict[str, Any]) -> RentalAnalysis:
        """Analyse complète du potentiel locatif"""
        
        # Données de base
        purchase_price = property_listing['price']
        surface_area = property_listing.get('surface_area', 50)  # Défaut 50m²
        location = property_listing['location'].lower()
        
        # Estimation du loyer
        rental_data = await self._estimate_rental_income(location, surface_area)
        estimated_rent = rental_data['estimated_rent']
        
        # Calculs de rentabilité
        monthly_charges = self._estimate_monthly_charges(purchase_price, surface_area)
        annual_taxes = self._estimate_annual_taxes(purchase_price)
        
        # Rendement brut : (loyer annuel / prix d'achat) * 100
        gross_yield = (estimated_rent * 12 / purchase_price) * 100
        
        # Rendement net : rendement brut - charges, taxes, frais de gestion
        annual_charges = monthly_charges * 12 + annual_taxes
        management_fees_annual = estimated_rent * 12 * 0.08  # 8% de frais de gestion
        net_annual_income = (estimated_rent * 12) - annual_charges - management_fees_annual
        net_yield = (net_annual_income / purchase_price) * 100
        
        # Cash-flow mensuel
        cash_flow = estimated_rent - monthly_charges - (annual_taxes / 12) - (estimated_rent * 0.08)
        
        # Analyse du quartier
        neighborhood_analysis = await self._analyze_rental_neighborhood(location)
        
        # Projections à long terme
        capital_appreciation = self._estimate_capital_appreciation(location)
        total_return_projection = net_yield + (capital_appreciation / 10)  # Sur 10 ans
        
        # Score et recommandations
        investment_score = self._calculate_investment_score(
            gross_yield, net_yield, neighborhood_analysis, capital_appreciation
        )
        
        pros, cons, recommendations = self._generate_rental_recommendations(
            gross_yield, net_yield, cash_flow, neighborhood_analysis
        )
        
        return RentalAnalysis(
            gross_yield=round(gross_yield, 2),
            net_yield=round(net_yield, 2),
            cash_flow=round(cash_flow, 0),
            estimated_rent=round(estimated_rent, 0),
            rent_per_sqm=round(rental_data['rent_per_sqm'], 1),
            market_rent_range=rental_data['range'],
            monthly_charges=round(monthly_charges, 0),
            annual_taxes=round(annual_taxes, 0),
            management_fees=8.0,  # 8% standard
            rental_demand=neighborhood_analysis['demand'],
            tenant_profile=neighborhood_analysis['tenant_profile'],
            vacancy_risk=neighborhood_analysis['vacancy_risk'],
            capital_appreciation=round(capital_appreciation, 1),
            total_return_projection=round(total_return_projection, 2),
            investment_score=round(investment_score, 1),
            pros=pros,
            cons=cons,
            recommendations=recommendations
        )
    
    async def _estimate_rental_income(self, location: str, surface_area: float) -> Dict[str, Any]:
        """Estime le loyer de marché"""
        
        # Normalisation de la localisation
        location_key = self._normalize_location(location)
        
        # Récupération des données de marché
        market_data = self.rental_database.get(location_key, {
            "avg_rent_sqm": 20.0,  # Valeur par défaut
            "range_min": 16.0,
            "range_max": 25.0
        })
        
        avg_rent_sqm = market_data['avg_rent_sqm']
        
        # Ajustement selon la surface (coefficient de surface)
        surface_coefficient = self._get_surface_coefficient(surface_area)
        adjusted_rent_sqm = avg_rent_sqm * surface_coefficient
        
        estimated_rent = adjusted_rent_sqm * surface_area
        
        return {
            'estimated_rent': estimated_rent,
            'rent_per_sqm': adjusted_rent_sqm,
            'range': {
                'min': market_data['range_min'] * surface_area * surface_coefficient,
                'max': market_data['range_max'] * surface_area * surface_coefficient
            }
        }
    
    def _get_surface_coefficient(self, surface_area: float) -> float:
        """Coefficient d'ajustement selon la surface"""
        if surface_area < 25:
            return 1.15  # Petites surfaces plus chères au m²
        elif surface_area < 40:
            return 1.05
        elif surface_area < 60:
            return 1.0   # Surface de référence
        elif surface_area < 80:
            return 0.95
        else:
            return 0.90  # Grandes surfaces moins chères au m²
    
    def _normalize_location(self, location: str) -> str:
        """Normalise la localisation pour la recherche en base"""
        location = location.lower().strip()
        
        # Mapping des variantes
        mappings = {
            'paris 11': 'paris_11e',
            'paris 11e': 'paris_11e',
            'paris 11ème': 'paris_11e',
            '11e arrondissement': 'paris_11e',
            'paris 20': 'paris_20e',
            'paris 20e': 'paris_20e',
            'paris 16': 'paris_16e',
            'paris 16e': 'paris_16e',
            'lyon': 'lyon',
            'marseille': 'marseille'
        }
        
        for pattern, key in mappings.items():
            if pattern in location:
                return key
        
        # Détection automatique par mots-clés
        if 'lyon' in location:
            return 'lyon'
        elif 'marseille' in location:
            return 'marseille'
        elif 'paris' in location and '11' in location:
            return 'paris_11e'
        elif 'paris' in location and '20' in location:
            return 'paris_20e'
        elif 'paris' in location and '16' in location:
            return 'paris_16e'
        
        return 'default'
    
    def _estimate_monthly_charges(self, purchase_price: float, surface_area: float) -> float:
        """Estime les charges mensuelles"""
        # Copropriété : 3-5€/m²/mois selon le standing
        copro_charges = surface_area * 4.0
        
        # Assurance PNO : ~200-400€/an selon valeur
        insurance_monthly = min(max(purchase_price * 0.0002, 15), 35)
        
        # Entretien et réparations : 0.5% de la valeur par an
        maintenance_monthly = (purchase_price * 0.005) / 12
        
        return copro_charges + insurance_monthly + maintenance_monthly
    
    def _estimate_annual_taxes(self, purchase_price: float) -> float:
        """Estime les taxes foncières annuelles"""
        # Environ 1.2% de la valeur locative cadastrale
        # Valeur locative ~= 8% de la valeur de marché
        estimated_rental_value = purchase_price * 0.08
        return estimated_rental_value * 0.012
    
    async def _analyze_rental_neighborhood(self, location: str) -> Dict[str, str]:
        """Analyse du quartier pour la location"""
        location_key = self._normalize_location(location)
        
        market_data = self.rental_database.get(location_key, {
            "demand": "Moyenne",
            "tenant_profile": "Mixte",
            "vacancy_rate": 4.0
        })
        
        # Détermination du risque de vacance
        vacancy_rate = market_data.get('vacancy_rate', 4.0)
        if vacancy_rate < 3:
            vacancy_risk = "Faible"
        elif vacancy_rate < 5:
            vacancy_risk = "Moyen"
        else:
            vacancy_risk = "Élevé"
        
        return {
            'demand': market_data['demand'],
            'tenant_profile': market_data['tenant_profile'],
            'vacancy_risk': vacancy_risk
        }
    
    def _estimate_capital_appreciation(self, location: str) -> float:
        """Estime la plus-value potentielle sur 10 ans"""
        location_key = self._normalize_location(location)
        
        # Estimations basées sur historique et tendances
        appreciation_rates = {
            'paris_11e': 35.0,   # 3.5% par an
            'paris_20e': 40.0,   # 4.0% par an
            'paris_16e': 25.0,   # 2.5% par an
            'lyon': 30.0,        # 3.0% par an
            'marseille': 25.0,   # 2.5% par an
            'default': 20.0      # 2.0% par an
        }
        
        return appreciation_rates.get(location_key, 20.0)
    
    def _calculate_investment_score(self, gross_yield: float, net_yield: float, 
                                  neighborhood: Dict, capital_appreciation: float) -> float:
        """Calcule un score d'investissement global"""
        score = 0
        
        # Rendement net (40% du score)
        if net_yield >= 6:
            score += 40
        elif net_yield >= 4:
            score += 30
        elif net_yield >= 2:
            score += 20
        else:
            score += 10
        
        # Demande locative (25% du score)
        demand = neighborhood.get('demand', 'Moyenne')
        if demand == 'Forte':
            score += 25
        elif demand == 'Moyenne':
            score += 15
        else:
            score += 5
        
        # Plus-value potentielle (20% du score)
        if capital_appreciation >= 35:
            score += 20
        elif capital_appreciation >= 25:
            score += 15
        elif capital_appreciation >= 20:
            score += 10
        else:
            score += 5
        
        # Risque de vacance (15% du score)
        vacancy_risk = neighborhood.get('vacancy_risk', 'Moyen')
        if vacancy_risk == 'Faible':
            score += 15
        elif vacancy_risk == 'Moyen':
            score += 10
        else:
            score += 0
        
        return min(score, 100)
    
    def _generate_rental_recommendations(self, gross_yield: float, net_yield: float,
                                       cash_flow: float, neighborhood: Dict) -> tuple:
        """Génère les recommandations pour l'investissement locatif"""
        
        pros = []
        cons = []
        recommendations = []
        
        # Analyse du rendement
        if net_yield >= 4:
            pros.append(f"Excellent rendement net de {net_yield:.1f}%")
        elif net_yield >= 2:
            pros.append(f"Rendement net correct de {net_yield:.1f}%")
        else:
            cons.append(f"Rendement net faible de {net_yield:.1f}%")
        
        # Analyse du cash-flow
        if cash_flow > 200:
            pros.append(f"Cash-flow positif de {cash_flow:.0f}€/mois")
        elif cash_flow > 0:
            pros.append(f"Cash-flow légèrement positif ({cash_flow:.0f}€/mois)")
        else:
            cons.append(f"Cash-flow négatif de {abs(cash_flow):.0f}€/mois")
            recommendations.append("Négocier le prix d'achat pour améliorer la rentabilité")
        
        # Analyse du quartier
        demand = neighborhood.get('demand', 'Moyenne')
        if demand == 'Forte':
            pros.append("Forte demande locative dans le quartier")
        else:
            cons.append(f"Demande locative {demand.lower()}")
        
        vacancy_risk = neighborhood.get('vacancy_risk', 'Moyen')
        if vacancy_risk == 'Faible':
            pros.append("Faible risque de vacance")
        elif vacancy_risk == 'Élevé':
            cons.append("Risque de vacance élevé")
            recommendations.append("Prévoir une réserve pour couvrir les périodes de vacance")
        
        # Recommandations générales
        if net_yield < 3:
            recommendations.append("Envisager une négociation du prix ou chercher d'autres opportunités")
        
        if cash_flow < 0:
            recommendations.append("Calculer l'effort d'épargne mensuel nécessaire")
        
        recommendations.append("Vérifier les travaux nécessaires avant achat")
        recommendations.append("Étudier l'évolution du quartier et les projets d'aménagement")
        
        return pros, cons, recommendations
