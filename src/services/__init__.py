"""
Services pour l'analyse immobilière.

Ce package contient les services d'analyse et de traitement des données immobilières.
"""

from .geocoding import GeocodingService
from .market_analysis import MarketAnalysisService, MarketStats, MarketTrend
from .flexible_analysis import FlexibleAnalysisService

__all__ = [
    'GeocodingService',
    'MarketAnalysisService',
    'FlexibleAnalysisService',
    'MarketStats',
    'MarketTrend'
]
