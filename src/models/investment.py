#!/usr/bin/env python3
"""
Modèles de données pour l'analyse d'investissement immobilier
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class InvestmentProfile(Enum):
    """Profils d'investissement"""
    RENTAL_INVESTOR = "rental_investor"
    PROPERTY_DEALER = "property_dealer"
    BOTH = "both"


@dataclass
class RentalAnalysis:
    """Analyse pour l'investissement locatif"""
    gross_yield: float
    net_yield: float
    cash_flow: float
    estimated_rent: float
    rent_per_sqm: float
    monthly_charges: float
    annual_taxes: float
    rental_demand: str
    tenant_profile: str
    vacancy_risk: str
    capital_appreciation: float
    investment_score: float
    pros: List[str]
    cons: List[str]
    recommendations: List[str]


@dataclass
class DealerAnalysis:
    """Analyse pour marchand de biens"""
    renovation_cost: float
    renovation_duration: int
    market_value_current: float
    market_value_renovated: float
    gross_margin: float
    gross_margin_percent: float
    net_margin: float
    total_investment: float
    estimated_sale_duration: int
    market_liquidity: str
    market_risk: str
    renovation_risk: str
    dealer_score: float
    opportunity_level: str
    action_plan: List[str]
    alerts: List[str]
