#!/usr/bin/env python3
"""Test rapide d'un outil MCP"""

import asyncio
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_quick():
    server = MCPRealEstateServer()
    print(f"Serveur créé, MCP dynamique: {server.mcp is not None}")
    
    # Test simple avec get_property_summary
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_property_summary",
            "arguments": {"location": "Paris 11e"}
        }
    }
    
    try:
        print("Envoi de la requête...")
        response = await server.handle_request(request)
        
        if 'result' in response:
            print("✅ Outil fonctionne!")
            content = response['result']['content'][0]['text']
            print(f"Aperçu: {content[:100]}...")
        else:
            print(f"❌ Erreur: {response.get('error', 'Inconnue')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quick())
