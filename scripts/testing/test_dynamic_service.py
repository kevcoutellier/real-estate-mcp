#!/usr/bin/env python3
"""
Test du service dynamique
"""

import sys
import os
import asyncio

# Ajouter le chemin src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from main import DynamicRealEstateMCP

async def test_dynamic_service():
    """Test du service dynamique"""
    print("🚀 Test du service dynamique MCP Real Estate")
    
    try:
        # Initialiser le MCP dynamique
        mcp = DynamicRealEstateMCP()
        print("✅ MCP dynamique initialisé")
        
        # Test de recherche de propriétés
        print("\n🔍 Test de recherche - Antibes studios 30m²+")
        
        results = await mcp.search_properties(
            location="Antibes",
            property_type="studio",
            min_surface=30,
            transaction_type="rent"
        )
        
        print(f"📊 Résultats trouvés: {len(results)}")
        
        if results:
            for i, prop in enumerate(results[:3]):  # Afficher les 3 premiers
                print(f"\n🏠 Propriété {i+1}:")
                print(f"   Titre: {prop.get('title', 'N/A')}")
                print(f"   Prix: {prop.get('price', 'N/A')} €")
                print(f"   Surface: {prop.get('surface_area', 'N/A')} m²")
                print(f"   Localisation: {prop.get('location', 'N/A')}")
        else:
            print("❌ Aucun résultat trouvé")
            
        # Test des données de marché
        print("\n📈 Test des données de marché - Antibes")
        
        try:
            market_data = await mcp.get_market_data_dynamic("Antibes", "rent")
            print(f"✅ Données de marché récupérées: {market_data}")
        except Exception as e:
            print(f"⚠️ Données de marché non disponibles: {e}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dynamic_service())
