"""
Module core - Architecture flexible et adaptative.
"""

from .flexible_models import FlexibleProperty, ContextualMarketAnalyzer, AdaptiveAnalyzer
from .dynamic_responses import ContextualResponseSystem, ResponseFormatter
from .adaptive_engine import AdaptiveEngine, AdaptationContext, ContextualDataEnricher

__all__ = [
    'FlexibleProperty',
    'ContextualMarketAnalyzer', 
    'AdaptiveAnalyzer',
    'ContextualResponseSystem',
    'ResponseFormatter',
    'AdaptiveEngine',
    'AdaptationContext',
    'ContextualDataEnricher'
]
