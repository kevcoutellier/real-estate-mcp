#!/usr/bin/env python3
"""
Script de test pour vérifier que les outils MCP sont bien disponibles
"""

import asyncio
import json
import sys
import os

# Ajouter le répertoire courant au path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_mcp_tools():
    """Test que les outils MCP sont correctement définis"""
    
    print("=== Test du serveur MCP Real Estate ===")
    
    # Créer une instance du serveur
    server = MCPRealEstateServer()
    
    # Vérifier que les outils sont définis
    print(f"Nombre d'outils définis: {len(server.tools)}")
    
    # Lister tous les outils
    print("\nOutils disponibles:")
    for tool_name, tool_info in server.tools.items():
        print(f"  - {tool_name}: {tool_info['description']}")
    
    # Test de la méthode tools/list
    print("\n=== Test de la méthode tools/list ===")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    response = await server.handle_request(request)
    print(f"Réponse: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    # Vérifier que la réponse contient bien les outils
    if 'result' in response and 'tools' in response['result']:
        tools_count = len(response['result']['tools'])
        print(f"\n✅ Succès! {tools_count} outils retournés par l'API MCP")
        
        # Afficher les noms des outils
        tool_names = [tool['name'] for tool in response['result']['tools']]
        print(f"Outils: {', '.join(tool_names)}")
    else:
        print("❌ Erreur: Aucun outil retourné par l'API MCP")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
