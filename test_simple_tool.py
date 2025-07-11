#!/usr/bin/env python3
"""
Test simple d'un outil MCP
"""

import asyncio
import sys
import os

# Ajouter le répertoire courant au path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_single_tool():
    """Test d'un seul outil pour diagnostiquer"""
    print("=== Test simple d'un outil MCP ===")
    
    server = MCPRealEstateServer()
    print(f"Serveur créé avec {len(server.tools)} outils")
    
    # Test de get_property_summary (le plus simple)
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_property_summary",
            "arguments": {
                "location": "Paris 11e"
            }
        }
    }
    
    print("Envoi de la requête...")
    try:
        response = await server.handle_request(request)
        print(f"Réponse reçue: {type(response)}")
        
        if 'result' in response:
            print("✅ Succès!")
            print(f"Contenu: {response['result']}")
        elif 'error' in response:
            print(f"❌ Erreur: {response['error']}")
        else:
            print(f"❓ Réponse inattendue: {response}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_tool())
