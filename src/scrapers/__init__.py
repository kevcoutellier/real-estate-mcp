"""
Scrapers pour différentes sources immobilières
Contains web scrapers for different real estate platforms
"""

from .base import BaseScraper
from .leboncoin import LeBonCoinScraper
from .seloger import SeLogerScraper

__all__ = [
    'BaseScraper',
    'LeBonCoinScraper',
    'SeLogerScraper'
]
