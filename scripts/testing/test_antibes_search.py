#!/usr/bin/env python3
"""
Test de recherche de studios à Antibes avec la nouvelle architecture
Valide que le MCP organisé fonctionne correctement
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Ajouter les chemins nécessaires
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

async def test_antibes_search():
    """Test de recherche de studios à Antibes"""
    
    print("🏠 Test de recherche de studios à Antibes")
    print("=" * 50)
    
    try:
        # Import du nouveau serveur MCP
        from mcp_server import MCPRealEstateServer
        print("✅ Import du serveur MCP réussi")
        
        # Créer et initialiser le serveur
        server = MCPRealEstateServer()
        await server.initialize()
        print("✅ Serveur MCP initialisé")
        
        # Paramètres de recherche pour studios à Antibes
        search_params = {
            "name": "search_properties",
            "arguments": {
                "location": "Antibes",
                "transaction_type": "rent",
                "property_type": "studio",
                "min_surface": 30
            }
        }
        
        print(f"\n🔍 Recherche avec paramètres:")
        print(f"   📍 Localisation: {search_params['arguments']['location']}")
        print(f"   🏠 Type: {search_params['arguments']['property_type']}")
        print(f"   📐 Surface min: {search_params['arguments']['min_surface']}m²")
        print(f"   💰 Transaction: {search_params['arguments']['transaction_type']}")
        
        # Simuler une requête MCP
        mcp_request = {
            "method": "tools/call",
            "params": search_params
        }
        
        print("\n⏳ Exécution de la recherche...")
        
        # Exécuter la recherche
        response = await server.handle_request(mcp_request)
        
        # Analyser la réponse
        if "error" in response:
            print(f"❌ Erreur: {response['error']}")
            return False
        
        if "content" in response and response["content"]:
            content = response["content"][0]["text"]
            try:
                result = json.loads(content)
                
                print("\n📊 Résultats de la recherche:")
                print(f"   ✅ Succès: {result.get('success', False)}")
                print(f"   📈 Total trouvé: {result.get('total_found', 0)}")
                
                if result.get('properties'):
                    print(f"   🏠 Propriétés affichées: {len(result['properties'])}")
                    
                    # Afficher quelques propriétés
                    for i, prop in enumerate(result['properties'][:3]):
                        print(f"\n   🏠 Propriété {i+1}:")
                        print(f"      📍 Lieu: {prop.get('location', 'N/A')}")
                        print(f"      💰 Prix: {prop.get('price', 'N/A')}€")
                        print(f"      📐 Surface: {prop.get('surface_area', 'N/A')}m²")
                        print(f"      🏠 Type: {prop.get('property_type', 'N/A')}")
                
                if result.get('summary'):
                    summary = result['summary']
                    print(f"\n📈 Résumé statistique:")
                    if 'price_range' in summary:
                        price_range = summary['price_range']
                        print(f"   💰 Prix: {price_range.get('min', 0):.0f}€ - {price_range.get('max', 0):.0f}€")
                        print(f"   📊 Prix moyen: {price_range.get('avg', 0):.0f}€")
                    
                    if 'surface_range' in summary:
                        surface_range = summary['surface_range']
                        print(f"   📐 Surface: {surface_range.get('min', 0):.0f}m² - {surface_range.get('max', 0):.0f}m²")
                        print(f"   📊 Surface moyenne: {surface_range.get('avg', 0):.0f}m²")
                
                return result.get('success', False)
                
            except json.JSONDecodeError:
                print(f"❌ Erreur de décodage JSON: {content}")
                return False
        
        else:
            print("❌ Réponse vide ou invalide")
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_tools():
    """Test de la liste des outils disponibles"""
    
    print("\n🛠️ Test des outils disponibles")
    print("=" * 30)
    
    try:
        from mcp_server import MCPRealEstateServer
        
        server = MCPRealEstateServer()
        
        # Tester la liste des outils
        tools_request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = await server.handle_request(tools_request)
        
        if "tools" in response:
            tools = response["tools"]
            print(f"✅ {len(tools)} outils disponibles:")
            
            for i, tool in enumerate(tools, 1):
                print(f"   {i}. {tool['name']} - {tool['description']}")
            
            return True
        else:
            print("❌ Aucun outil trouvé")
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors du test des outils: {e}")
        return False


async def main():
    """Fonction principale de test"""
    
    print("🧪 TEST DE LA NOUVELLE ARCHITECTURE MCP REAL ESTATE")
    print("=" * 60)
    
    # Test 1: Outils disponibles
    tools_ok = await test_server_tools()
    
    # Test 2: Recherche Antibes
    search_ok = await test_antibes_search()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    print(f"🛠️ Outils MCP: {'✅ OK' if tools_ok else '❌ ÉCHEC'}")
    print(f"🔍 Recherche Antibes: {'✅ OK' if search_ok else '❌ ÉCHEC'}")
    
    if tools_ok and search_ok:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ La nouvelle architecture fonctionne parfaitement")
        print("✅ Le MCP peut rechercher des studios à Antibes")
        print("✅ Prêt pour utilisation en production")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez la configuration et les dépendances")
    
    print("\n💡 Pour utiliser le serveur:")
    print("   python start_server.py")


if __name__ == "__main__":
    asyncio.run(main())
