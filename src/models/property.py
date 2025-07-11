#!/usr/bin/env python3
"""
Modèles de données pour les propriétés immobilières
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class PropertyListing:
    """Structure standardisée pour les annonces"""
    id: str
    title: str
    price: float
    currency: str = "EUR"
    location: str = ""
    property_type: str = ""
    surface_area: Optional[float] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    description: str = ""
    images: List[str] = None
    source: str = ""
    url: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    coordinates: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'annonce en dictionnaire"""
        data = asdict(self)
        # Convertir les datetime en string pour la sérialisation
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
