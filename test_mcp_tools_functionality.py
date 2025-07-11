#!/usr/bin/env python3
"""
Test complet des outils MCP pour vérifier leur fonctionnement
"""

import asyncio
import sys
import os
import json

# Ajouter le répertoire courant au path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_tool_call(server, tool_name, arguments):
    """Test d'appel d'un outil spécifique"""
    print(f"\n--- Test de l'outil: {tool_name} ---")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = await server.handle_request(request)
        
        if 'result' in response:
            print(f"✅ Succès pour {tool_name}")
            # Afficher un résumé de la réponse
            if 'content' in response['result']:
                content = response['result']['content']
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get('text', '')
                    # Afficher les premiers 200 caractères
                    preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                    print(f"Réponse: {preview}")
                else:
                    print(f"Réponse: {content}")
            return True
        else:
            print(f"❌ Erreur pour {tool_name}: {response.get('error', 'Erreur inconnue')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception pour {tool_name}: {e}")
        return False

async def test_all_tools():
    """Test de tous les outils MCP"""
    print("=== Test de fonctionnement des outils MCP ===")
    
    server = MCPRealEstateServer()
    
    # Initialiser le service dynamique si possible
    await server.initialize_dynamic_service()
    
    results = {}
    
    # Test 1: search_properties
    results['search_properties'] = await test_tool_call(
        server, 
        'search_properties',
        {
            "location": "Paris 11e",
            "transaction_type": "rent",
            "min_price": 1000,
            "max_price": 2000
        }
    )
    
    # Test 2: get_property_summary
    results['get_property_summary'] = await test_tool_call(
        server,
        'get_property_summary',
        {
            "location": "Paris 11e"
        }
    )
    
    # Test 3: analyze_market
    results['analyze_market'] = await test_tool_call(
        server,
        'analyze_market',
        {
            "location": "Paris 11e",
            "transaction_type": "rent"
        }
    )
    
    # Test 4: compare_locations
    results['compare_locations'] = await test_tool_call(
        server,
        'compare_locations',
        {
            "locations": ["Paris 11e", "Lyon 2e"],
            "criteria": "price"
        }
    )
    
    # Test 5: get_neighborhood_info
    results['get_neighborhood_info'] = await test_tool_call(
        server,
        'get_neighborhood_info',
        {
            "location": "Paris 11e"
        }
    )
    
    # Test 6: analyze_investment_opportunity
    results['analyze_investment_opportunity'] = await test_tool_call(
        server,
        'analyze_investment_opportunity',
        {
            "location": "Paris 11e",
            "min_price": 200000,
            "max_price": 400000,
            "investment_profile": "rental_investor"
        }
    )
    
    # Test 7: compare_investment_strategies
    results['compare_investment_strategies'] = await test_tool_call(
        server,
        'compare_investment_strategies',
        {
            "location": "Paris 11e",
            "property_data": {
                "price": 300000,
                "surface": 45,
                "rooms": 2,
                "property_type": "appartement"
            }
        }
    )
    
    # Résumé des résultats
    print("\n=== RÉSUMÉ DES TESTS ===")
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"Outils testés: {total_count}")
    print(f"Outils fonctionnels: {success_count}")
    print(f"Taux de réussite: {success_count/total_count*100:.1f}%")
    
    print("\nDétail par outil:")
    for tool_name, success in results.items():
        status = "✅ OK" if success else "❌ ERREUR"
        print(f"  {tool_name}: {status}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = asyncio.run(test_all_tools())
    print(f"\nTest global: {'RÉUSSI' if success else 'ÉCHOUÉ'}")
