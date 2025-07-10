#!/usr/bin/env python3
"""
Test des outils MCP Real Estate
"""

import asyncio
import json
from mcp_real_estate_server import RealEstateMCPServer

async def test_mcp_tools():
    """Test des outils MCP"""
    print("🚀 Initialisation du serveur MCP...")
    server = RealEstateMCPServer()
    
    print("✅ Serveur MCP initialisé")
    
    # Test liste des outils
    print("\n🔧 Outils disponibles :")
    try:
        tools = await server.list_tools()
        print(f"Nombre d'outils : {len(tools.tools)}")
        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print(f"⚠️ Erreur liste outils : {e}")
    
    # Test recherche de propriétés
    print("\n📍 Test outil search_properties...")
    try:
        from mcp.types import CallToolRequest
        request = CallToolRequest(
            name="search_properties",
            arguments={
                "location": "Paris",
                "transaction_type": "rent",
                "max_price": 2000
            }
        )
        result = await server.call_tool(request)
        print(f"✅ Recherche réussie")
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else "Pas de contenu"
            print(f"Résultat : {content[:100]}...")
    except Exception as e:
        print(f"⚠️ Erreur outil search : {e}")
    
    print("\n🎯 Tests outils terminés !")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
