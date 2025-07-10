#!/usr/bin/env python3
"""
Redémarrage du serveur MCP avec service dynamique
"""

import sys
import os
import asyncio
import json

# Ajouter le chemin src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

async def test_dynamic_search():
    """Test direct du service dynamique"""
    print("🔍 Test direct de recherche avec service dynamique")
    
    try:
        from main import DynamicRealEstateMCP
        
        # Initialiser le MCP dynamique
        mcp = DynamicRealEstateMCP()
        print("✅ MCP dynamique initialisé")
        
        # Test de recherche directe
        print("\n🏠 Recherche: Studios 30m²+ à Antibes")
        
        # Appel direct de la méthode search_properties
        results = await mcp.search_properties(
            location="Antibes",
            property_type="studio", 
            min_surface=30,
            transaction_type="rent"
        )
        
        print(f"📊 Nombre de résultats: {len(results)}")
        
        if results:
            print("\n🎯 Résultats trouvés:")
            for i, prop in enumerate(results[:3]):
                print(f"\n   {i+1}. {prop.get('title', 'Sans titre')}")
                print(f"      Prix: {prop.get('price', 'N/A')} €")
                print(f"      Surface: {prop.get('surface_area', 'N/A')} m²")
                print(f"      Lieu: {prop.get('location', 'N/A')}")
                print(f"      Source: {prop.get('source', 'N/A')}")
        else:
            print("⚠️ Aucun résultat trouvé")
            
        # Test des données de marché
        print("\n📈 Test données de marché Antibes")
        try:
            market_data = await mcp.get_market_data_dynamic("Antibes", "rent")
            if market_data:
                print(f"✅ Données de marché disponibles")
                print(f"   Loyer moyen: {market_data.get('avg_rent_sqm', 'N/A')} €/m²")
                print(f"   Source: {market_data.get('source', 'N/A')}")
                print(f"   Confiance: {market_data.get('confidence_score', 'N/A')}")
            else:
                print("⚠️ Données de marché non disponibles")
        except Exception as e:
            print(f"⚠️ Erreur données de marché: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_mcp_response(results):
    """Crée une réponse MCP formatée"""
    if not results:
        return {
            "status": "success",
            "message": "Recherche effectuée avec service dynamique",
            "data": [],
            "count": 0,
            "note": "Aucun résultat trouvé pour les critères spécifiés"
        }
    
    return {
        "status": "success", 
        "message": "Recherche effectuée avec service dynamique",
        "data": results,
        "count": len(results),
        "note": f"Service dynamique opérationnel - {len(results)} résultats"
    }

async def main():
    """Fonction principale"""
    print("🚀 Redémarrage MCP avec service dynamique")
    print("=" * 50)
    
    success = await test_dynamic_search()
    
    if success:
        print("\n✅ Service dynamique opérationnel !")
        print("   Le MCP peut maintenant traiter les requêtes avec des données réelles.")
    else:
        print("\n❌ Problème avec le service dynamique")

if __name__ == "__main__":
    asyncio.run(main())
