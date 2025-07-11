"""
Fonctions utilitaires pour le formatage et la manipulation de données
"""

def format_price(price: float, currency: str = "€") -> str:
    """Formate un prix pour l'affichage"""
    if price >= 1000000:
        return f"{price/1000000:.1f}M{currency}"
    elif price >= 1000:
        return f"{price/1000:.0f}k{currency}"
    else:
        return f"{price:.0f}{currency}"

def format_surface(surface: float) -> str:
    """Formate une surface pour l'affichage"""
    return f"{surface:.0f} m²"

def normalize_location(location: str) -> str:
    """Normalise une localisation"""
    return location.lower().strip()
