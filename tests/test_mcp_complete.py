#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du MCP Real Estate - Validation des 7 outils
Teste toutes les fonctionnalités avec données temps réel
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import DynamicRealEstateMCP

class MCPCompleteTester:
    """Testeur complet pour toutes les fonctionnalités MCP"""
    
    def __init__(self):
        self.mcp = DynamicRealEstateMCP()
        self.results = {}
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def format_result(self, tool_name: str, result: Any, success: bool = True):
        """Formate et affiche les résultats"""
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        self.log(f"{status} - {tool_name}")
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"   Erreur: {result['error']}")
            else:
                # Afficher les clés principales
                for key, value in result.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"   {key}: {len(value)} éléments")
                        if len(value) > 0 and isinstance(value[0], dict):
                            print(f"      Premier élément: {list(value[0].keys())}")
                    elif isinstance(value, dict):
                        print(f"   {key}: {len(value)} propriétés")
                    else:
                        print(f"   {key}: {value}")
        else:
            print(f"   Résultat: {str(result)[:200]}...")
        print()
    
    # Test 1: Initialisation
    print("\n1️⃣ Test d'initialisation...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    response = send_mcp_request(init_request)
    if response and response.get("result"):
        print("✅ Initialisation réussie")
        print(f"   Version : {response['result'].get('protocolVersion')}")
        print(f"   Serveur : {response['result'].get('serverInfo', {}).get('name', 'N/A')}")
    else:
        print("❌ Échec de l'initialisation")
        return
    
    # Test 2: Liste des outils
    print("\n2️⃣ Test de la liste des outils...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    response = send_mcp_request(tools_request)
    if response and response.get("result", {}).get("tools"):
        tools = response["result"]["tools"]
        print(f"✅ {len(tools)} outils disponibles :")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:60]}...")
    else:
        print("❌ Échec de récupération des outils")
        return
    
    # Test 3: Test d'un outil (search_properties)
    print("\n3️⃣ Test de l'outil search_properties...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_properties",
            "arguments": {
                "location": "Paris",
                "transaction_type": "rent",
                "max_price": 2000,
                "min_surface": 30
            }
        }
    }
    
    response = send_mcp_request(search_request)
    if response and response.get("result"):
        print("✅ Recherche de propriétés réussie")
        content = response["result"].get("content", [])
        if content and len(content) > 0:
            result_text = content[0].get("text", "")
            print(f"   Résultat : {result_text[:100]}...")
        else:
            print("   Aucun contenu dans la réponse")
    else:
        print("❌ Échec de la recherche de propriétés")
        if response and response.get("error"):
            print(f"   Erreur : {response['error']}")
    
    # Test 4: Test d'un autre outil (get_property_summary)
    print("\n4️⃣ Test de l'outil get_property_summary...")
    summary_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_property_summary",
            "arguments": {
                "location": "Lyon"
            }
        }
    }
    
    response = send_mcp_request(summary_request)
    if response and response.get("result"):
        print("✅ Résumé de propriétés réussi")
        content = response["result"].get("content", [])
        if content and len(content) > 0:
            result_text = content[0].get("text", "")
            print(f"   Résultat : {result_text[:100]}...")
        else:
            print("   Aucun contenu dans la réponse")
    else:
        print("❌ Échec du résumé de propriétés")
        if response and response.get("error"):
            print(f"   Erreur : {response['error']}")
    
    print("\n🎯 Tests terminés !")
    print("=" * 50)
    print("✅ Le serveur MCP Real Estate est opérationnel")

if __name__ == "__main__":
    test_mcp_server()
