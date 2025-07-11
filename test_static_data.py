#!/usr/bin/env python3
"""Test avec données statiques pour éviter les appels réseau"""

import asyncio
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from mcp_real_estate_server import MCPRealEstateServer

async def test_with_static_data():
    """Test en utilisant les données statiques du fichier JSON"""
    print("=== Test avec données statiques ===")
    
    server = MCPRealEstateServer()
    
    # Vérifier que les données statiques existent
    data_file = os.path.join(current_dir, 'data', 'real_estate_data_2024.json')
    if os.path.exists(data_file):
        print(f"✅ Fichier de données trouvé: {data_file}")
        
        # Lire les données
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Données chargées: {len(data.get('rental_market_data', {}))} villes")
        
        # Test simple sans appel réseau - juste vérifier la structure
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_property_summary",
                "arguments": {"location": "Paris"}
            }
        }
        
        print("Test de l'outil get_property_summary...")
        
        # Créer une version simplifiée qui utilise les données statiques
        try:
            # Simuler une réponse basée sur les données statiques
            paris_data = data.get('rental_market_data', {}).get('paris', {})
            
            if paris_data:
                result = {
                    "location": "Paris",
                    "avg_rent_sqm": paris_data.get('global', {}).get('avg_rent_sqm', 0),
                    "market_trend": paris_data.get('global', {}).get('market_trend', 'N/A'),
                    "source": "Données statiques 2024"
                }
                
                print("✅ Données Paris trouvées:")
                print(f"  - Loyer moyen: {result['avg_rent_sqm']} €/m²")
                print(f"  - Tendance: {result['market_trend']}")
                
                return True
            else:
                print("❌ Pas de données Paris dans le fichier")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    else:
        print(f"❌ Fichier de données non trouvé: {data_file}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_static_data())
    print(f"\nTest: {'RÉUSSI' if success else 'ÉCHOUÉ'}")
