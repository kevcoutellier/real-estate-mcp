#!/usr/bin/env python3
"""
Test rapide du MCP Real Estate
"""

import asyncio
from src.main import DynamicRealEstateMCP

async def test_mcp():
    """Test rapide des fonctionnalités MCP"""
    print("🚀 Initialisation du MCP Real Estate...")
    mcp = DynamicRealEstateMCP()
    
    print("✅ MCP initialisé avec succès")
    
    # Test recherche simple
    print("\n📍 Test recherche de propriétés...")
    try:
        results = await mcp.search_properties(
            location="Paris",
            transaction_type="rent",
            max_price=2000,
            min_surface=30
        )
        print(f"✅ Recherche réussie : {len(results)} résultats trouvés")
        if results:
            print(f"Premier résultat : {results[0].title[:50]}...")
    except Exception as e:
        print(f"⚠️ Erreur recherche : {e}")
    
    # Test analyse de marché
    print("\n📊 Test analyse de marché...")
    try:
        market_analysis = await mcp.analyze_market("Paris", "rent")
        print(f"✅ Analyse de marché réussie")
        print(f"Prix moyen : {market_analysis.get('average_price', 'N/A')}€")
    except Exception as e:
        print(f"⚠️ Erreur analyse : {e}")
    
    print("\n🎯 Tests terminés avec succès !")

if __name__ == "__main__":
    asyncio.run(test_mcp())
