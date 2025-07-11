#!/usr/bin/env python3
"""Test de recherche de biens immobiliers"""

import asyncio
import json
from src.main import DynamicRealEstateMCP

async def test_search():
    """Test de recherche de biens immobiliers"""
    print("=== Test de recherche de biens immobiliers ===\n")
    
    # Initialiser le MCP
    mcp = DynamicRealEstateMCP()
    await mcp._ensure_dynamic_service()
    
    # Paramètres de recherche
    params = {
        "location": "Antibes",
        "transaction_type": "rent",
        "min_price": 1200,
        "max_price": 1800,
        "min_surface": 40,
        "max_surface": 100,
        "rooms": 2
    }
    
    print(f"Recherche de biens à louer à {params['location']}...")
    print(f"Prix: {params['min_price']}€ - {params['max_price']}€")
    print(f"Surface: {params['min_surface']}m² - {params['max_surface']}m²")
    print(f"Pièces: {params['rooms']}+\n")
    
    try:
        # Effectuer la recherche
        results = await mcp.search_properties(
            location=params["location"],
            transaction_type=params["transaction_type"],
            min_price=params["min_price"],
            max_price=params["max_price"],
            min_surface=params["min_surface"],
            max_surface=params["max_surface"],
            rooms=params["rooms"]
        )
        
        # Afficher les résultats
        if results:
            print(f"\n✅ {len(results)} biens trouvés à {params['location']}:")
            for i, prop in enumerate(results, 1):
                print(f"\n--- Bien {i} ---")
                print(f"Titre: {prop.get('title', 'Non spécifié')}")
                print(f"Prix: {prop.get('price', 'N/A')}€")
                print(f"Surface: {prop.get('surface_area', 'N/A')}m²")
                print(f"Pièces: {prop.get('rooms', 'N/A')}")
                print(f"Description: {prop.get('description', 'Non disponible')[:100]}...")
                print(f"Lien: {prop.get('url', 'Non disponible')}")
        else:
            print("\n❌ Aucun bien trouvé correspondant aux critères.")
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la recherche: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Fin du test ===")

if __name__ == "__main__":
    asyncio.run(test_search())
