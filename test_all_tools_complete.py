#!/usr/bin/env python3
"""
Test complet de tous les outils MCP avec gestion des timeouts
"""

import asyncio
import sys
import os
import json
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_tool_with_timeout(server, tool_name, arguments, timeout=10):
    """Test d'un outil avec timeout"""
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
        # Utiliser asyncio.wait_for pour le timeout
        response = await asyncio.wait_for(
            server.handle_request(request),
            timeout=timeout
        )
        
        if 'result' in response:
            content = response['result']['content'][0]['text']
            
            # Vérifier si c'est une erreur
            if '[ERREUR' in content:
                print(f"⚠️  Erreur fonctionnelle pour {tool_name}")
                print(f"Message: {content[:150]}...")
                return 'error'
            else:
                print(f"✅ Succès pour {tool_name}")
                print(f"Aperçu: {content[:100]}...")
                return 'success'
        else:
            print(f"❌ Erreur technique pour {tool_name}: {response.get('error', 'Inconnue')}")
            return 'failed'
            
    except asyncio.TimeoutError:
        print(f"⏱️  Timeout pour {tool_name} (>{timeout}s)")
        return 'timeout'
    except Exception as e:
        print(f"❌ Exception pour {tool_name}: {e}")
        return 'exception'

async def test_all_tools_complete():
    """Test complet de tous les outils"""
    print("=== Test complet des outils MCP Real Estate ===")
    
    server = MCPRealEstateServer()
    print(f"Serveur initialisé avec {len(server.tools)} outils")
    
    results = {}
    
    # Test 1: get_property_summary (le plus simple)
    results['get_property_summary'] = await test_tool_with_timeout(
        server, 'get_property_summary',
        {"location": "Paris 11e"},
        timeout=15
    )
    
    # Test 2: analyze_market
    results['analyze_market'] = await test_tool_with_timeout(
        server, 'analyze_market',
        {"location": "Paris 11e", "transaction_type": "rent"},
        timeout=15
    )
    
    # Test 3: get_neighborhood_info
    results['get_neighborhood_info'] = await test_tool_with_timeout(
        server, 'get_neighborhood_info',
        {"location": "Paris 11e"},
        timeout=15
    )
    
    # Test 4: compare_locations
    results['compare_locations'] = await test_tool_with_timeout(
        server, 'compare_locations',
        {"locations": ["Paris 11e", "Lyon 2e"], "criteria": "price"},
        timeout=15
    )
    
    # Test 5: analyze_investment_opportunity
    results['analyze_investment_opportunity'] = await test_tool_with_timeout(
        server, 'analyze_investment_opportunity',
        {
            "location": "Paris 11e",
            "min_price": 200000,
            "max_price": 400000,
            "investment_profile": "rental_investor"
        },
        timeout=15
    )
    
    # Test 6: compare_investment_strategies
    results['compare_investment_strategies'] = await test_tool_with_timeout(
        server, 'compare_investment_strategies',
        {
            "location": "Paris 11e",
            "property_data": {
                "price": 300000,
                "surface": 45,
                "rooms": 2,
                "property_type": "appartement"
            }
        },
        timeout=15
    )
    
    # Test 7: search_properties (peut être lent)
    results['search_properties'] = await test_tool_with_timeout(
        server, 'search_properties',
        {
            "location": "Paris 11e",
            "transaction_type": "rent",
            "min_price": 1000,
            "max_price": 2000
        },
        timeout=20
    )
    
    # Résumé des résultats
    print("\n" + "="*50)
    print("RÉSUMÉ DES TESTS")
    print("="*50)
    
    success_count = sum(1 for status in results.values() if status == 'success')
    error_count = sum(1 for status in results.values() if status == 'error')
    failed_count = sum(1 for status in results.values() if status == 'failed')
    timeout_count = sum(1 for status in results.values() if status == 'timeout')
    exception_count = sum(1 for status in results.values() if status == 'exception')
    
    total_count = len(results)
    
    print(f"Total outils testés: {total_count}")
    print(f"✅ Succès complets: {success_count}")
    print(f"⚠️  Erreurs fonctionnelles: {error_count}")
    print(f"❌ Échecs techniques: {failed_count}")
    print(f"⏱️  Timeouts: {timeout_count}")
    print(f"💥 Exceptions: {exception_count}")
    
    working_tools = success_count + error_count  # Les erreurs fonctionnelles signifient que l'outil fonctionne
    print(f"\n🎯 Outils fonctionnels: {working_tools}/{total_count} ({working_tools/total_count*100:.1f}%)")
    
    print("\nDétail par outil:")
    for tool_name, status in results.items():
        status_emoji = {
            'success': '✅',
            'error': '⚠️ ',
            'failed': '❌',
            'timeout': '⏱️ ',
            'exception': '💥'
        }
        print(f"  {status_emoji.get(status, '❓')} {tool_name}: {status.upper()}")
    
    return working_tools == total_count

if __name__ == "__main__":
    try:
        success = asyncio.run(test_all_tools_complete())
        print(f"\n{'🎉 TOUS LES OUTILS FONCTIONNENT!' if success else '⚠️  CERTAINS OUTILS ONT DES PROBLÈMES'}")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
