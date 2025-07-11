#!/usr/bin/env python3
"""Test simple pour vérifier les outils MCP"""

import asyncio
import sys
import os
import json

# Ajouter le répertoire courant au path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_tools():
    """Test complet des outils MCP"""
    server = MCPRealEstateServer()
    
    print(f"=== Test du serveur MCP Real Estate ===")
    print(f"Nombre d'outils définis: {len(server.tools)}")
    
    print("\nOutils disponibles:")
    for name in server.tools.keys():
        print(f"- {name}")
    
    # Test de la méthode tools/list du protocole MCP
    print("\n=== Test de la méthode tools/list ===")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = await server.handle_request(request)
        
        if 'result' in response and 'tools' in response['result']:
            tools_count = len(response['result']['tools'])
            print(f"✅ Succès! {tools_count} outils retournés par l'API MCP")
            
            # Afficher les noms des outils retournés
            tool_names = [tool['name'] for tool in response['result']['tools']]
            print(f"Outils MCP: {', '.join(tool_names)}")
            return True
        else:
            print("❌ Erreur: Aucun outil retourné par l'API MCP")
            print(f"Réponse: {json.dumps(response, indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tools())
    print(f"\nTest {'RÉUSSI' if success else 'ÉCHOUÉ'}")
