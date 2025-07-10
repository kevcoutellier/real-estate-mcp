#!/usr/bin/env python3
"""
Serveur MCP pour l'extension spécialisée investissement locatif et marchand de biens
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Optional, Any

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specialized_investment_mcp import SpecializedRealEstateMCP, InvestmentProfile

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpecializedMCPServer:
    """Serveur MCP pour les analyses spécialisées"""
    
    def __init__(self):
        self.mcp = SpecializedRealEstateMCP()
        self.name = "specialized-real-estate-mcp"
        self.version = "2.0.0"
    
    async def handle_analyze_investment_opportunity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour l'analyse d'opportunités d'investissement"""
        try:
            # Extraction des paramètres
            location = params.get('location')
            if not location:
                return {"error": "Le paramètre 'location' est requis"}
            
            min_price = params.get('min_price')
            max_price = params.get('max_price')
            investment_profile_str = params.get('investment_profile', 'both')
            
            # Conversion du profil d'investissement
            try:
                investment_profile = InvestmentProfile(investment_profile_str)
            except ValueError:
                investment_profile = InvestmentProfile.BOTH
            
            # Autres paramètres optionnels
            kwargs = {}
            if 'surface_area' in params:
                kwargs['min_surface'] = params['surface_area']
            if 'rooms' in params:
                kwargs['rooms'] = params['rooms']
            if 'property_type' in params:
                kwargs['property_type'] = params['property_type']
            
            # Exécution de l'analyse
            result = await self.mcp.analyze_investment_opportunity(
                location=location,
                min_price=min_price,
                max_price=max_price,
                investment_profile=investment_profile,
                **kwargs
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur dans analyze_investment_opportunity: {e}")
            return {"error": f"Erreur lors de l'analyse: {str(e)}"}
    
    async def handle_compare_investment_strategies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour la comparaison des stratégies"""
        try:
            location = params.get('location')
            property_data = params.get('property_data')
            
            if not location:
                return {"error": "Le paramètre 'location' est requis"}
            
            if not property_data:
                return {"error": "Le paramètre 'property_data' est requis"}
            
            result = await self.mcp.compare_investment_strategies(location, property_data)
            return result
            
        except Exception as e:
            logger.error(f"Erreur dans compare_investment_strategies: {e}")
            return {"error": f"Erreur lors de la comparaison: {str(e)}"}
    
    async def handle_get_market_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire pour l'analyse de marché simplifiée"""
        try:
            location = params.get('location')
            if not location:
                return {"error": "Le paramètre 'location' est requis"}
            
            # Analyse rapide avec quelques biens
            result = await self.mcp.analyze_investment_opportunity(
                location=location,
                investment_profile=InvestmentProfile.BOTH
            )
            
            # Retourner seulement le résumé de marché
            return {
                "location": location,
                "market_summary": result.get('market_summary', {}),
                "analysis_date": result.get('analysis_date')
            }
            
        except Exception as e:
            logger.error(f"Erreur dans get_market_analysis: {e}")
            return {"error": f"Erreur lors de l'analyse de marché: {str(e)}"}

# Outils disponibles pour le MCP
SPECIALIZED_TOOLS = [
    {
        "name": "analyze_investment_opportunity",
        "description": "Analyse complète d'opportunités d'investissement immobilier (locatif et/ou marchand de biens) avec calculs de rentabilité, estimations de travaux et recommandations personnalisées",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Localisation de recherche (ex: 'Paris 11e', 'Lyon', 'Marseille')"
                },
                "min_price": {
                    "type": "number",
                    "description": "Prix minimum en euros"
                },
                "max_price": {
                    "type": "number",
                    "description": "Prix maximum en euros"
                },
                "investment_profile": {
                    "type": "string",
                    "enum": ["rental_investor", "property_dealer", "both"],
                    "description": "Profil d'investissement: 'rental_investor' pour locatif, 'property_dealer' pour marchand de biens, 'both' pour les deux",
                    "default": "both"
                },
                "surface_area": {
                    "type": "number",
                    "description": "Surface minimale en m²"
                },
                "rooms": {
                    "type": "integer",
                    "description": "Nombre de pièces souhaité"
                },
                "property_type": {
                    "type": "string",
                    "description": "Type de bien ('appartement', 'maison', 'studio')"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "compare_investment_strategies",
        "description": "Compare les stratégies d'investissement locatif vs marchand de biens pour un bien spécifique avec analyse détaillée des rendements et risques",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Localisation du bien"
                },
                "property_data": {
                    "type": "object",
                    "description": "Données du bien immobilier (prix, surface, description, etc.)",
                    "properties": {
                        "price": {"type": "number", "description": "Prix du bien en euros"},
                        "surface_area": {"type": "number", "description": "Surface en m²"},
                        "location": {"type": "string", "description": "Localisation"},
                        "description": {"type": "string", "description": "Description du bien"},
                        "property_type": {"type": "string", "description": "Type de bien"},
                        "rooms": {"type": "integer", "description": "Nombre de pièces"}
                    },
                    "required": ["price", "location"]
                }
            },
            "required": ["location", "property_data"]
        }
    },
    {
        "name": "get_market_analysis",
        "description": "Analyse rapide du marché immobilier d'une zone avec statistiques pour investissement locatif et marchand de biens",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Zone à analyser (ville ou arrondissement)"
                }
            },
            "required": ["location"]
        }
    }
]

async def test_server():
    """Test du serveur MCP spécialisé"""
    print("🚀 Test du serveur MCP spécialisé")
    print("=" * 50)
    
    server = SpecializedMCPServer()
    
    # Test 1: Analyse d'opportunités locatives
    print("\n1️⃣ Test analyse opportunités locatives...")
    params1 = {
        "location": "Paris 11e",
        "min_price": 200000,
        "max_price": 400000,
        "investment_profile": "rental_investor"
    }
    
    result1 = await server.handle_analyze_investment_opportunity(params1)
    if "error" not in result1:
        print(f"✅ Analyse réussie: {result1['total_opportunities']} opportunités trouvées")
        market = result1.get('market_summary', {}).get('rental_market', {})
        if market:
            print(f"   📊 Rendement net moyen: {market.get('average_net_yield', 0)}%")
    else:
        print(f"❌ Erreur: {result1['error']}")
    
    # Test 2: Analyse marchand de biens
    print("\n2️⃣ Test analyse marchand de biens...")
    params2 = {
        "location": "Lyon",
        "min_price": 150000,
        "max_price": 300000,
        "investment_profile": "property_dealer"
    }
    
    result2 = await server.handle_analyze_investment_opportunity(params2)
    if "error" not in result2:
        print(f"✅ Analyse réussie: {result2['total_opportunities']} opportunités trouvées")
        market = result2.get('market_summary', {}).get('dealer_market', {})
        if market:
            print(f"   📊 Marge brute moyenne: {market.get('average_gross_margin', 0)}%")
    else:
        print(f"❌ Erreur: {result2['error']}")
    
    # Test 3: Comparaison de stratégies
    print("\n3️⃣ Test comparaison de stratégies...")
    test_property = {
        "price": 280000,
        "surface_area": 55,
        "location": "Paris 20e",
        "description": "Appartement à rénover avec potentiel",
        "property_type": "Appartement",
        "rooms": 3
    }
    
    params3 = {
        "location": "Paris 20e",
        "property_data": test_property
    }
    
    result3 = await server.handle_compare_investment_strategies(params3)
    if "error" not in result3:
        print("✅ Comparaison réussie")
        comp = result3.get('comparison', {})
        print(f"   🏠 Rendement locatif: {comp.get('rental_annual_return', 0):.1f}%")
        print(f"   🔨 Rendement marchand: {comp.get('dealer_annual_return', 0):.1f}%")
        print(f"   💡 Recommandation: {comp.get('recommendation', 'N/A')}")
    else:
        print(f"❌ Erreur: {result3['error']}")
    
    # Test 4: Analyse de marché
    print("\n4️⃣ Test analyse de marché...")
    params4 = {"location": "Marseille"}
    
    result4 = await server.handle_get_market_analysis(params4)
    if "error" not in result4:
        print("✅ Analyse de marché réussie")
        market_summary = result4.get('market_summary', {})
        print(f"   📍 Zone: {result4.get('location')}")
        if 'rental_market' in market_summary:
            rental = market_summary['rental_market']
            print(f"   🏠 Locatif - Rendement moyen: {rental.get('average_net_yield', 0)}%")
        if 'dealer_market' in market_summary:
            dealer = market_summary['dealer_market']
            print(f"   🔨 Marchand - Marge moyenne: {dealer.get('average_gross_margin', 0)}%")
    else:
        print(f"❌ Erreur: {result4['error']}")
    
    print("\n🎯 Tests terminés avec succès !")
    print("\n📋 Outils disponibles:")
    for tool in SPECIALIZED_TOOLS:
        print(f"   • {tool['name']}: {tool['description']}")

if __name__ == "__main__":
    asyncio.run(test_server())
