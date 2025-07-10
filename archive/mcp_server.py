#!/usr/bin/env python3
"""
Serveur MCP pour Claude - Interface IA
Créez ce fichier: mcp_server.py
"""

import asyncio
import json
import sys
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Ajouter le chemin vers src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import EnrichedRealEstateMCP, PropertyListing

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """Serveur MCP pour l'interface avec Claude"""
    
    def __init__(self):
        self.mcp = EnrichedRealEstateMCP()
        self.tools = {
            "search_properties": self.search_properties,
            "analyze_market": self.analyze_market,
            "compare_locations": self.compare_locations,
            "get_property_details": self.get_property_details,
            "neighborhood_analysis": self.neighborhood_analysis
        }
    
    async def search_properties(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche des biens immobiliers selon les critères
        
        Args:
            location (str): Ville ou arrondissement (ex: "Paris 11e")
            min_price (float, optional): Prix minimum en euros
            max_price (float, optional): Prix maximum en euros
            property_type (str, optional): Type de bien ("appartement", "maison")
            min_surface (float, optional): Surface minimale en m²
            max_surface (float, optional): Surface maximale en m²
            rooms (int, optional): Nombre de pièces
            transaction_type (str, optional): "rent" ou "sale" (défaut: "rent")
        """
        try:
            # Validation des arguments
            if 'location' not in args:
                return {"error": "Le paramètre 'location' est requis"}
            
            # Recherche
            results = await self.mcp.search_properties(
                location=args['location'],
                min_price=args.get('min_price'),
                max_price=args.get('max_price'),
                property_type=args.get('property_type'),
                min_surface=args.get('min_surface'),
                max_surface=args.get('max_surface'),
                rooms=args.get('rooms'),
                transaction_type=args.get('transaction_type', 'rent')
            )
            
            return {
                "success": True,
                "count": len(results),
                "properties": results[:10],  # Limite à 10 pour l'IA
                "summary": {
                    "total_found": len(results),
                    "avg_price": sum(r['price'] for r in results) / len(results) if results else 0,
                    "price_range": {
                        "min": min(r['price'] for r in results) if results else 0,
                        "max": max(r['price'] for r in results) if results else 0
                    },
                    "sources": list(set(r['source'] for r in results))
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur search_properties: {e}")
            return {"error": str(e)}
    
    async def analyze_market(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse du marché immobilier pour une zone
        
        Args:
            location (str): Ville ou arrondissement à analyser
        """
        try:
            if 'location' not in args:
                return {"error": "Le paramètre 'location' est requis"}
            
            # Recherche large pour analyse
            all_properties = await self.mcp.search_properties(
                location=args['location'],
                transaction_type=args.get('transaction_type', 'rent')
            )
            
            if not all_properties:
                return {"error": f"Aucune annonce trouvée pour {args['location']}"}
            
            # Calculs statistiques
            prices = [p['price'] for p in all_properties if p['price'] > 0]
            surfaces = [p.get('surface_area') for p in all_properties if p.get('surface_area')]
            
            analysis = {
                "location": args['location'],
                "total_properties": len(all_properties),
                "market_stats": {
                    "average_price": sum(prices) / len(prices) if prices else 0,
                    "median_price": sorted(prices)[len(prices)//2] if prices else 0,
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0
                    }
                },
                "surface_stats": {
                    "average_surface": sum(surfaces) / len(surfaces) if surfaces else 0,
                    "surface_range": {
                        "min": min(surfaces) if surfaces else 0,
                        "max": max(surfaces) if surfaces else 0
                    }
                } if surfaces else None,
                "sources_breakdown": {},
                "property_types": {}
            }
            
            # Répartition par source
            for prop in all_properties:
                source = prop['source']
                analysis["sources_breakdown"][source] = analysis["sources_breakdown"].get(source, 0) + 1
            
            # Répartition par type
            for prop in all_properties:
                prop_type = prop.get('property_type', 'Inconnu')
                analysis["property_types"][prop_type] = analysis["property_types"].get(prop_type, 0) + 1
            
            # Calcul prix au m² si possible
            if prices and surfaces:
                price_per_sqm = []
                for prop in all_properties:
                    if prop.get('surface_area') and prop['price'] > 0:
                        price_per_sqm.append(prop['price'] / prop['surface_area'])
                
                if price_per_sqm:
                    analysis["price_per_sqm"] = {
                        "average": sum(price_per_sqm) / len(price_per_sqm),
                        "min": min(price_per_sqm),
                        "max": max(price_per_sqm)
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyze_market: {e}")
            return {"error": str(e)}
    
    async def compare_locations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare plusieurs localisations
        
        Args:
            locations (list): Liste des localisations à comparer
            criteria (str, optional): Critère de comparaison ("price", "surface", "availability")
        """
        try:
            if 'locations' not in args:
                return {"error": "Le paramètre 'locations' est requis"}
            
            locations = args['locations']
            if not isinstance(locations, list) or len(locations) < 2:
                return {"error": "Il faut au moins 2 localisations à comparer"}
            
            comparison = {
                "locations_compared": locations,
                "comparison_data": {},
                "recommendations": []
            }
            
            # Analyser chaque localisation
            for location in locations:
                market_data = await self.analyze_market({"location": location})
                
                if "error" not in market_data:
                    comparison["comparison_data"][location] = {
                        "total_properties": market_data["total_properties"],
                        "average_price": market_data["market_stats"]["average_price"],
                        "price_range": market_data["market_stats"]["price_range"],
                        "average_surface": market_data.get("surface_stats", {}).get("average_surface", 0),
                        "price_per_sqm": market_data.get("price_per_sqm", {}).get("average", 0)
                    }
            
            # Générer des recommandations
            if comparison["comparison_data"]:
                # Localisation la moins chère
                cheapest = min(comparison["comparison_data"].items(), 
                             key=lambda x: x[1]["average_price"] if x[1]["average_price"] > 0 else float('inf'))
                comparison["recommendations"].append({
                    "type": "most_affordable",
                    "location": cheapest[0],
                    "reason": f"Prix moyen le plus bas: {cheapest[1]['average_price']:.0f}€"
                })
                
                # Meilleur rapport qualité-prix (prix/m²)
                if any(data["price_per_sqm"] > 0 for data in comparison["comparison_data"].values()):
                    best_value = min(
                        [(loc, data) for loc, data in comparison["comparison_data"].items() if data["price_per_sqm"] > 0],
                        key=lambda x: x[1]["price_per_sqm"]
                    )
                    comparison["recommendations"].append({
                        "type": "best_value_per_sqm",
                        "location": best_value[0],
                        "reason": f"Meilleur prix au m²: {best_value[1]['price_per_sqm']:.0f}€/m²"
                    })
                
                # Plus grand choix
                most_options = max(comparison["comparison_data"].items(), 
                                 key=lambda x: x[1]["total_properties"])
                comparison["recommendations"].append({
                    "type": "most_options",
                    "location": most_options[0],
                    "reason": f"Plus grand choix: {most_options[1]['total_properties']} annonces"
                })
            
            return comparison
            
        except Exception as e:
            logger.error(f"Erreur compare_locations: {e}")
            return {"error": str(e)}
    
    async def get_property_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtient les détails d'une propriété spécifique
        
        Args:
            property_id (str): ID de la propriété
            or
            search_terms (str): Termes de recherche pour identifier la propriété
        """
        try:
            # Pour l'instant, simuler avec une recherche
            if 'search_terms' in args:
                results = await self.mcp.search_properties(
                    location=args['search_terms'],
                    transaction_type='rent'
                )
                
                if results:
                    # Retourner la première propriété avec tous les détails
                    prop = results[0]
                    
                    # Ajouter des analyses supplémentaires
                    details = prop.copy()
                    details['analysis'] = {}
                    
                    # Analyse du prix
                    if prop.get('surface_area') and prop['price'] > 0:
                        details['analysis']['price_per_sqm'] = prop['price'] / prop['surface_area']
                    
                    # Score d'attractivité si disponible
                    if prop.get('neighborhood_info'):
                        details['analysis']['neighborhood_score'] = prop['neighborhood_info'].get('score', 'N/A')
                    
                    return details
                else:
                    return {"error": "Aucune propriété trouvée"}
            
            return {"error": "Paramètres insuffisants"}
            
        except Exception as e:
            logger.error(f"Erreur get_property_details: {e}")
            return {"error": str(e)}
    
    async def neighborhood_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse détaillée d'un quartier
        
        Args:
            location (str): Quartier à analyser
        """
        try:
            if 'location' not in args:
                return {"error": "Le paramètre 'location' est requis"}
            
            # Utiliser la méthode d'analyse de quartier enrichie
            if hasattr(self.mcp, 'get_neighborhood_analysis'):
                analysis = await self.mcp.get_neighborhood_analysis(args['location'])
            else:
                # Fallback vers analyse basique
                analysis = await self.analyze_market(args)
                
                # Ajouter des informations sur le quartier
                analysis['neighborhood_insights'] = {
                    "description": f"Analyse de {args['location']}",
                    "attractiveness_factors": [],
                    "recommendations": []
                }
                
                # Générer des insights basés sur les données
                avg_price = analysis.get('market_stats', {}).get('average_price', 0)
                total_props = analysis.get('total_properties', 0)
                
                if avg_price > 0:
                    if avg_price < 1000:
                        analysis['neighborhood_insights']['attractiveness_factors'].append("Prix abordables")
                    elif avg_price > 2000:
                        analysis['neighborhood_insights']['attractiveness_factors'].append("Quartier haut de gamme")
                
                if total_props > 10:
                    analysis['neighborhood_insights']['attractiveness_factors'].append("Bon choix d'annonces")
                
                analysis['neighborhood_insights']['recommendations'].append(
                    f"Quartier avec {total_props} annonces disponibles, prix moyen {avg_price:.0f}€"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur neighborhood_analysis: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Gestionnaire principal des requêtes"""
        if tool_name not in self.tools:
            return {"error": f"Outil '{tool_name}' non disponible"}
        
        try:
            result = await self.tools[tool_name](args)
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de {tool_name}: {e}")
            return {"error": str(e)}

# Configuration MCP pour Claude
MCP_CONFIG = {
    "name": "real-estate-mcp",
    "version": "2.0.0",
    "description": "MCP pour recherche et analyse immobilière avec IA",
    "tools": [
        {
            "name": "search_properties",
            "description": "Recherche des biens immobiliers avec critères avancés",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Ville ou arrondissement (ex: 'Paris 11e', 'Lyon')"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Prix minimum en euros"
                    },
                    "max_price": {
                        "type": "number", 
                        "description": "Prix maximum en euros"
                    },
                    "property_type": {
                        "type": "string",
                        "description": "Type de bien ('appartement', 'maison')"
                    },
                    "min_surface": {
                        "type": "number",
                        "description": "Surface minimale en m²"
                    },
                    "max_surface": {
                        "type": "number",
                        "description": "Surface maximale en m²"
                    },
                    "rooms": {
                        "type": "integer",
                        "description": "Nombre de pièces"
                    },
                    "transaction_type": {
                        "type": "string",
                        "description": "Type de transaction ('rent' ou 'sale')",
                        "default": "rent"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "analyze_market",
            "description": "Analyse complète du marché immobilier d'une zone",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Zone à analyser"
                    },
                    "transaction_type": {
                        "type": "string",
                        "description": "Type de transaction ('rent' ou 'sale')",
                        "default": "rent"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "compare_locations",
            "description": "Compare plusieurs localisations selon différents critères",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Liste des localisations à comparer"
                    },
                    "criteria": {
                        "type": "string",
                        "description": "Critère de comparaison ('price', 'surface', 'availability')"
                    }
                },
                "required": ["locations"]
            }
        },
        {
            "name": "get_property_details",
            "description": "Obtient les détails complets d'une propriété",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "ID de la propriété"
                    },
                    "search_terms": {
                        "type": "string",
                        "description": "Termes de recherche pour identifier la propriété"
                    }
                }
            }
        },
        {
            "name": "neighborhood_analysis",
            "description": "Analyse détaillée d'un quartier avec insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Quartier à analyser"
                    }
                },
                "required": ["location"]
            }
        }
    ]
}

# Interface de test
async def test_mcp_server():
    """Test du serveur MCP"""
    server = MCPServer()
    
    print("🤖 Test du serveur MCP pour Claude")
    print("=" * 60)
    
    # Test 1: Recherche simple
    print("📍 Test 1: Recherche simple")
    result1 = await server.handle_request("search_properties", {
        "location": "Paris 11e",
        "min_price": 1000,
        "max_price": 2000
    })
    
    if "error" not in result1:
        print(f"✅ Trouvé {result1['count']} annonces")
        print(f"💰 Prix moyen: {result1['summary']['avg_price']:.0f}€")
    else:
        print(f"❌ Erreur: {result1['error']}")
    
    # Test 2: Analyse de marché
    print("\n📊 Test 2: Analyse de marché")
    result2 = await server.handle_request("analyze_market", {
        "location": "Paris 11e"
    })
    
    if "error" not in result2:
        print(f"✅ Marché analysé: {result2['total_properties']} annonces")
        print(f"💰 Prix moyen: {result2['market_stats']['average_price']:.0f}€")
    else:
        print(f"❌ Erreur: {result2['error']}")
    
    # Test 3: Comparaison
    print("\n🔍 Test 3: Comparaison de quartiers")
    result3 = await server.handle_request("compare_locations", {
        "locations": ["Paris 11e", "Paris 20e"]
    })
    
    if "error" not in result3:
        print(f"✅ Comparaison effectuée entre {len(result3['locations_compared'])} quartiers")
        if result3['recommendations']:
            print(f"💡 Recommandation: {result3['recommendations'][0]['reason']}")
    else:
        print(f"❌ Erreur: {result3['error']}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())