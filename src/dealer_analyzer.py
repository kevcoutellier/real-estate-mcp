#!/usr/bin/env python3
"""
Analyseur spécialisé pour marchand de biens
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from specialized_investment_mcp import DealerAnalysis

class PropertyDealerAnalyzer:
    """Analyseur spécialisé pour marchand de biens"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        # Base de coûts de rénovation
        self.renovation_costs = self._init_renovation_costs()
        
    def _init_renovation_costs(self) -> Dict[str, Dict]:
        """Coûts de rénovation par poste et niveau"""
        return {
            "rafraichissement": {
                "description": "Peinture, petites réparations",
                "cost_per_sqm": 150,
                "duration_weeks": 2
            },
            "renovation_legere": {
                "description": "Sol, électricité de base, plomberie simple",
                "cost_per_sqm": 400,
                "duration_weeks": 4
            },
            "renovation_complete": {
                "description": "Tout corps d'état, cuisine, salle de bain",
                "cost_per_sqm": 800,
                "duration_weeks": 8
            },
            "renovation_lourde": {
                "description": "Gros œuvre, restructuration",
                "cost_per_sqm": 1200,
                "duration_weeks": 16
            }
        }
    
    async def analyze_dealer_opportunity(self, property_listing: Dict[str, Any]) -> DealerAnalysis:
        """Analyse complète pour marchand de biens"""
        
        # Données de base
        purchase_price = property_listing['price']
        surface_area = property_listing.get('surface_area', 50)
        location = property_listing['location']
        property_type = property_listing.get('property_type', 'Appartement')
        
        # Estimation des travaux nécessaires
        renovation_level = self._assess_renovation_needs(property_listing)
        renovation_analysis = self._calculate_renovation_costs(renovation_level, surface_area)
        
        # Analyse du marché de revente
        market_analysis = await self._analyze_resale_market(location, surface_area, property_type)
        
        # Calcul de la rentabilité
        total_investment = purchase_price + renovation_analysis['total_cost']
        gross_margin = market_analysis['renovated_value'] - total_investment
        gross_margin_percent = (gross_margin / total_investment) * 100
        
        # Frais de revente (notaire, agence, etc.)
        sale_fees = market_analysis['renovated_value'] * 0.08  # 8% de frais
        net_margin = gross_margin - sale_fees
        
        # Analyse des risques et timing
        risk_analysis = self._assess_risks(renovation_level, location, market_analysis)
        timing_analysis = self._estimate_sale_timing(location, market_analysis)
        
        # Score et recommandations
        dealer_score = self._calculate_dealer_score(
            gross_margin_percent, renovation_level, risk_analysis, timing_analysis
        )
        
        opportunity_level, action_plan, alerts = self._generate_dealer_recommendations(
            gross_margin_percent, renovation_analysis, risk_analysis, timing_analysis
        )
        
        return DealerAnalysis(
            renovation_cost=renovation_analysis['total_cost'],
            renovation_duration=renovation_analysis['duration_weeks'],
            renovation_breakdown=renovation_analysis['breakdown'],
            market_value_current=market_analysis['current_value'],
            market_value_renovated=market_analysis['renovated_value'],
            comparable_sales=market_analysis['comparables'],
            gross_margin=round(gross_margin, 0),
            gross_margin_percent=round(gross_margin_percent, 1),
            net_margin=round(net_margin, 0),
            total_investment=round(total_investment, 0),
            estimated_sale_duration=timing_analysis['sale_duration_months'],
            market_liquidity=timing_analysis['liquidity'],
            seasonal_factors=timing_analysis['seasonal_factors'],
            market_risk=risk_analysis['market_risk'],
            renovation_risk=risk_analysis['renovation_risk'],
            liquidity_risk=risk_analysis['liquidity_risk'],
            dealer_score=round(dealer_score, 1),
            opportunity_level=opportunity_level,
            action_plan=action_plan,
            alerts=alerts
        )
    
    def _assess_renovation_needs(self, property_listing: Dict[str, Any]) -> str:
        """Évalue le niveau de rénovation nécessaire"""
        
        # Analyse basée sur l'âge, la description, les mots-clés
        description = property_listing.get('description', '').lower()
        title = property_listing.get('title', '').lower()
        price = property_listing.get('price', 0)
        surface_area = property_listing.get('surface_area', 50)
        
        # Prix au m² pour évaluer si c'est décoté
        price_per_sqm = price / surface_area if surface_area > 0 else 0
        
        # Mots-clés indicateurs
        keywords = {
            'rafraichissement': ['bon état', 'récent', 'refait', 'rénové'],
            'renovation_legere': ['à rafraîchir', 'quelques travaux', 'potentiel'],
            'renovation_complete': ['à rénover', 'travaux à prévoir', 'ancien'],
            'renovation_lourde': ['gros travaux', 'à restructurer', 'très bon prix']
        }
        
        # Score par niveau
        scores = {level: 0 for level in keywords.keys()}
        
        full_text = f"{title} {description}"
        
        for level, words in keywords.items():
            for word in words:
                if word in full_text:
                    scores[level] += 1
        
        # Ajustement selon le prix
        if price_per_sqm > 0:
            # Comparer avec prix de marché moyen (estimé)
            market_avg = self._get_average_market_price(property_listing.get('location', ''))
            if price_per_sqm < market_avg * 0.7:  # Très décoté
                scores['renovation_lourde'] += 2
            elif price_per_sqm < market_avg * 0.85:  # Décoté
                scores['renovation_complete'] += 1
        
        # Retourner le niveau avec le plus haut score
        max_level = max(scores.items(), key=lambda x: x[1])[0]
        
        # Si pas d'indice, supposer rénovation légère
        if all(score == 0 for score in scores.values()):
            return 'renovation_legere'
        
        return max_level
    
    def _get_average_market_price(self, location: str) -> float:
        """Prix de marché moyen au m² par localisation"""
        market_prices = {
            'paris': 8000,
            'lyon': 4500,
            'marseille': 3500,
            'default': 3000
        }
        
        location_lower = location.lower()
        for key, price in market_prices.items():
            if key in location_lower:
                return price
        
        return market_prices['default']
    
    def _calculate_renovation_costs(self, renovation_level: str, surface_area: float) -> Dict[str, Any]:
        """Calcule les coûts détaillés de rénovation"""
        
        base_costs = self.renovation_costs[renovation_level]
        
        # Coût de base
        base_cost = base_costs['cost_per_sqm'] * surface_area
        
        # Majoration selon complexité
        if surface_area < 30:
            base_cost *= 1.15  # Surcoût petites surfaces
        elif surface_area > 100:
            base_cost *= 0.95  # Économie d'échelle
        
        # Répartition par poste
        breakdown = {}
        
        if renovation_level == 'rafraichissement':
            breakdown = {
                'Peinture': base_cost * 0.6,
                'Nettoyage': base_cost * 0.2,
                'Petites réparations': base_cost * 0.2
            }
        elif renovation_level == 'renovation_legere':
            breakdown = {
                'Sols': base_cost * 0.35,
                'Peinture': base_cost * 0.25,
                'Électricité': base_cost * 0.20,
                'Plomberie': base_cost * 0.20
            }
        elif renovation_level == 'renovation_complete':
            breakdown = {
                'Cuisine': base_cost * 0.25,
                'Salle de bain': base_cost * 0.20,
                'Sols': base_cost * 0.20,
                'Électricité': base_cost * 0.15,
                'Plomberie': base_cost * 0.10,
                'Peinture': base_cost * 0.10
            }
        else:  # renovation_lourde
            breakdown = {
                'Gros œuvre': base_cost * 0.30,
                'Cuisine': base_cost * 0.20,
                'Salle de bain': base_cost * 0.15,
                'Électricité': base_cost * 0.15,
                'Plomberie': base_cost * 0.10,
                'Sols': base_cost * 0.10
            }
        
        # Ajout marge de sécurité (10%)
        total_cost = base_cost * 1.1
        
        return {
            'total_cost': total_cost,
            'duration_weeks': base_costs['duration_weeks'],
            'breakdown': breakdown,
            'cost_per_sqm': total_cost / surface_area
        }
    
    async def _analyze_resale_market(self, location: str, surface_area: float, 
                                   property_type: str) -> Dict[str, Any]:
        """Analyse le marché de revente"""
        
        # Prix actuels du marché (valeur dans l'état)
        current_market_price = self._get_average_market_price(location)
        current_value = current_market_price * surface_area * 0.8  # Décote état moyen
        
        # Prix après rénovation
        renovated_market_price = current_market_price * 1.1  # Prime rénovation
        renovated_value = renovated_market_price * surface_area
        
        # Ventes comparables simulées
        comparables = self._generate_comparable_sales(location, surface_area, property_type)
        
        return {
            'current_value': current_value,
            'renovated_value': renovated_value,
            'price_per_sqm_current': current_market_price * 0.8,
            'price_per_sqm_renovated': renovated_market_price,
            'comparables': comparables
        }
    
    def _generate_comparable_sales(self, location: str, surface_area: float, 
                                 property_type: str) -> List[Dict]:
        """Génère des ventes comparables fictives"""
        base_price = self._get_average_market_price(location)
        
        comparables = []
        
        # Générer 3-5 ventes comparables
        for i in range(3):
            # Variation de surface ±20%
            comp_surface = surface_area * (0.8 + 0.4 * (i / 3))
            
            # Variation de prix ±15%
            comp_price_sqm = base_price * (0.85 + 0.3 * (i / 3))
            
            comp_total_price = comp_surface * comp_price_sqm
            
            # Date de vente récente
            sale_date = datetime.now() - timedelta(days=30 + i * 45)
            
            comparables.append({
                'surface': round(comp_surface, 0),
                'price': round(comp_total_price, 0),
                'price_per_sqm': round(comp_price_sqm, 0),
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'condition': ['Bon état', 'Rénové', 'À rafraîchir'][i % 3]
            })
        
        return comparables
    
    def _assess_risks(self, renovation_level: str, location: str, 
                     market_analysis: Dict) -> Dict[str, str]:
        """Évalue les différents risques"""
        
        # Risque de rénovation
        renovation_risks = {
            'rafraichissement': 'Faible',
            'renovation_legere': 'Faible',
            'renovation_complete': 'Moyen',
            'renovation_lourde': 'Élevé'
        }
        
        # Risque de marché (selon localisation)
        if 'paris' in location.lower():
            market_risk = 'Faible'
        elif any(city in location.lower() for city in ['lyon', 'marseille', 'toulouse']):
            market_risk = 'Moyen'
        else:
            market_risk = 'Élevé'
        
        # Risque de liquidité (selon type de bien et prix)
        renovated_value = market_analysis['renovated_value']
        if renovated_value > 800000:
            liquidity_risk = 'Élevé'
        elif renovated_value > 400000:
            liquidity_risk = 'Moyen'
        else:
            liquidity_risk = 'Faible'
        
        return {
            'renovation_risk': renovation_risks[renovation_level],
            'market_risk': market_risk,
            'liquidity_risk': liquidity_risk
        }
    
    def _estimate_sale_timing(self, location: str, market_analysis: Dict) -> Dict[str, Any]:
        """Estime le timing de revente"""
        
        # Liquidité du marché selon localisation
        if 'paris' in location.lower():
            base_duration = 3  # 3 mois
            liquidity = 'Forte'
        elif any(city in location.lower() for city in ['lyon', 'marseille']):
            base_duration = 5  # 5 mois
            liquidity = 'Moyenne'
        else:
            base_duration = 8  # 8 mois
            liquidity = 'Faible'
        
        # Ajustement selon prix
        renovated_value = market_analysis['renovated_value']
        if renovated_value > 600000:
            base_duration += 2  # Biens chers plus longs à vendre
        
        # Facteurs saisonniers
        current_month = datetime.now().month
        if current_month in [7, 8, 12]:  # Été et décembre
            seasonal_factors = "Période creuse - vente plus lente"
        elif current_month in [3, 4, 5, 9, 10]:  # Printemps et rentrée
            seasonal_factors = "Bonne période - marché actif"
        else:
            seasonal_factors = "Période normale"
        
        return {
            'sale_duration_months': base_duration,
            'liquidity': liquidity,
            'seasonal_factors': seasonal_factors
        }
    
    def _calculate_dealer_score(self, gross_margin_percent: float, renovation_level: str,
                              risk_analysis: Dict, timing_analysis: Dict) -> float:
        """Calcule un score pour l'opportunité marchand de biens"""
        score = 0
        
        # Marge brute (50% du score)
        if gross_margin_percent >= 25:
            score += 50
        elif gross_margin_percent >= 20:
            score += 40
        elif gross_margin_percent >= 15:
            score += 30
        elif gross_margin_percent >= 10:
            score += 20
        else:
            score += 10
        
        # Risques (30% du score)
        risk_scores = {'Faible': 10, 'Moyen': 7, 'Élevé': 3}
        renovation_risk_score = risk_scores.get(risk_analysis['renovation_risk'], 5)
        market_risk_score = risk_scores.get(risk_analysis['market_risk'], 5)
        liquidity_risk_score = risk_scores.get(risk_analysis['liquidity_risk'], 5)
        
        total_risk_score = (renovation_risk_score + market_risk_score + liquidity_risk_score) / 3
        score += total_risk_score
        
        # Liquidité (20% du score)
        if timing_analysis['liquidity'] == 'Forte':
            score += 20
        elif timing_analysis['liquidity'] == 'Moyenne':
            score += 15
        else:
            score += 10
        
        return min(score, 100)
    
    def _generate_dealer_recommendations(self, gross_margin_percent: float,
                                       renovation_analysis: Dict, risk_analysis: Dict,
                                       timing_analysis: Dict) -> tuple:
        """Génère recommandations pour marchand de biens"""
        
        # Niveau d'opportunité
        if gross_margin_percent >= 20:
            opportunity_level = "Excellente"
        elif gross_margin_percent >= 15:
            opportunity_level = "Bonne"
        elif gross_margin_percent >= 10:
            opportunity_level = "Moyenne"
        else:
            opportunity_level = "Faible"
        
        # Plan d'action
        action_plan = []
        
        if gross_margin_percent >= 15:
            action_plan.append("Négocier rapidement le prix d'achat")
            action_plan.append("Planifier les travaux avec 2-3 entreprises")
        else:
            action_plan.append("Négocier fortement le prix pour améliorer la marge")
        
        action_plan.append("Vérifier l'état exact du bien par expertise")
        action_plan.append("Établir un planning de travaux détaillé")
        action_plan.append("Prévoir le marketing de revente en amont")
        
        # Alertes
        alerts = []
        
        if renovation_analysis['duration_weeks'] > 12:
            alerts.append(f"Chantier long ({renovation_analysis['duration_weeks']} semaines) - risque de dérive")
        
        if risk_analysis['market_risk'] == 'Élevé':
            alerts.append("Marché local peu liquide - risque de mévente")
        
        if timing_analysis['sale_duration_months'] > 6:
            alerts.append("Durée de revente longue - prévoir trésorerie suffisante")
        
        if gross_margin_percent < 15:
            alerts.append("Marge faible - risque de perte en cas d'imprévu")
        
        return opportunity_level, action_plan, alerts
