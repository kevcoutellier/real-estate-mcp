"""
Modèles de données pour le projet MCP Real Estate
"""

# Models package
# Contains data models and structures for the real estate MCP

# Property models
from .property import PropertyListing

# Investment analysis models  
from .investment import (
    InvestmentProfile,
    RentalAnalysis,
    DealerAnalysis
)

__all__ = [
    'PropertyListing',
    'InvestmentProfile', 
    'RentalAnalysis',
    'DealerAnalysis'
]
