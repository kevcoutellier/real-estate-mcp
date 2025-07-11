#!/usr/bin/env python3
"""
Test du service dynamique pour vérifier son fonctionnement
"""

import asyncio
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import DynamicRealEstateMCP
from src.dynamic_data_service import DynamicDataService

async def test_dynamic_service():
    """Test du service dynamique"""
    print("=== Test du Service Dynamique ===")
    
    # Test 1: Service dynamique de base
    print("\n1. Test DynamicDataService...")
    service = DynamicDataService()
    
    try:
        market_data = await service.get_market_data("Lyon", "rent")
        print(f"Données de marché pour Lyon: {market_data}")
    except Exception as e:
        print(f"Erreur service de base: {e}")
    
    # Test 2: MCP Dynamique
    print("\n2. Test DynamicRealEstateMCP...")
    mcp = DynamicRealEstateMCP()
    
    try:
        # Initialiser le service
        await mcp._ensure_dynamic_service()
        print("Service dynamique initialisé avec succès")
        
        # Test get_market_data_dynamic
        market_data = await mcp.get_market_data_dynamic("Lyon", "rent")
        print(f"Données de marché dynamiques: {market_data}")
        
        # Test analyze_investment_opportunity_dynamic
        print("\n3. Test analyze_investment_opportunity_dynamic...")
        analysis = await mcp.analyze_investment_opportunity_dynamic(
            location="Lyon",
            min_price=300000,
            max_price=500000,
            investment_profile="rental_investor",
            rooms=3
        )
        print(f"Analyse d'investissement: {analysis}")
        
        # Test compare_investment_strategies_dynamic
        print("\n4. Test compare_investment_strategies_dynamic...")
        comparison = await mcp.compare_investment_strategies_dynamic(
            location="Lyon",
            property_data={"price": 400000, "surface": 50, "rooms": 2, "property_type": "appartement"}
        )
        print(f"Comparaison de stratégies: {comparison}")
        
        # Test compare_locations_dynamic
        print("\n5. Test compare_locations_dynamic...")
        location_comparison = await mcp.compare_locations_dynamic(
            locations=["Lyon", "Paris", "Marseille"],
            criteria="price"
        )
        print(f"Comparaison de localisations: {location_comparison}")
        
    except Exception as e:
        print(f"Erreur MCP dynamique: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dynamic_service())
