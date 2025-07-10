#!/usr/bin/env python3
"""
Serveur MCP Immobilier - Version organisée
Point d'entrée principal du serveur MCP Real Estate
"""

import asyncio
import json
import sys
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration du système de chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, project_root)

# Configuration du logging
from utils.logger import setup_logger
logger = setup_logger(__name__)

# Import des modules MCP
try:
    from main import DynamicRealEstateMCP
    logger.info("Module dynamique importé avec succès - données temps réel")
    HAS_MAIN_MODULE = True
except ImportError as e:
    logger.warning(f"Import du module dynamique échoué: {e}")
    logger.info("Impossible d'utiliser les données temps réel")
    HAS_MAIN_MODULE = False

class MCPRealEstateServer:
    """
    Serveur MCP pour l'immobilier - Version organisée
    
    Serveur principal qui expose les outils d'analyse immobilière
    via le protocole Model Context Protocol (MCP).
    """
    
    def __init__(self):
        """Initialise le serveur MCP"""
        self.mcp = None
        self.tools = self._define_tools()
        logger.info("Serveur MCP Real Estate initialisé")
    
    async def initialize(self):
        """Initialise le MCP avec données dynamiques si disponible"""
        if HAS_MAIN_MODULE:
            try:
                self.mcp = DynamicRealEstateMCP()
                await self.mcp._ensure_dynamic_service_initialized()
                logger.info("MCP dynamique initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur initialisation MCP dynamique: {e}")
                self.mcp = None
        else:
            logger.warning("MCP dynamique non disponible")
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Définit les outils disponibles via MCP"""
        return [
            {
                "name": "search_properties",
                "description": "Recherche de biens immobiliers selon différents critères",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Ville ou arrondissement"},
                        "transaction_type": {"type": "string", "enum": ["rent", "sale"], "description": "Type de transaction"},
                        "property_type": {"type": "string", "description": "Type de bien"},
                        "min_price": {"type": "number", "description": "Prix minimum"},
                        "max_price": {"type": "number", "description": "Prix maximum"},
                        "min_surface": {"type": "number", "description": "Surface minimale en m²"},
                        "max_surface": {"type": "number", "description": "Surface maximale en m²"},
                        "rooms": {"type": "integer", "description": "Nombre de pièces"}
                    },
                    "required": ["location", "transaction_type"]
                }
            },
            {
                "name": "analyze_market",
                "description": "Analyse complète du marché immobilier d'une zone",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Zone à analyser"},
                        "transaction_type": {"type": "string", "enum": ["rent", "sale"], "description": "Type de marché"}
                    },
                    "required": ["location", "transaction_type"]
                }
            },
            {
                "name": "get_neighborhood_info",
                "description": "Informations détaillées sur un quartier",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Quartier ou adresse"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "compare_locations",
                "description": "Compare plusieurs quartiers ou villes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "locations": {"type": "array", "items": {"type": "string"}, "description": "Liste des localisations"},
                        "criteria": {"type": "string", "enum": ["price", "availability", "quality", "all"], "description": "Critère de comparaison"}
                    },
                    "required": ["locations"]
                }
            },
            {
                "name": "get_property_summary",
                "description": "Résumé du marché immobilier pour une zone",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Ville ou arrondissement"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "analyze_investment_opportunity",
                "description": "Analyse d'opportunités d'investissement immobilier",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Ville ou arrondissement"},
                        "investment_profile": {"type": "string", "enum": ["rental_investor", "property_dealer", "both"], "description": "Profil d'investissement"},
                        "min_price": {"type": "number", "description": "Prix minimum"},
                        "max_price": {"type": "number", "description": "Prix maximum"},
                        "min_surface": {"type": "number", "description": "Surface minimale"},
                        "rooms": {"type": "integer", "description": "Nombre de pièces"}
                    },
                    "required": ["location", "investment_profile"]
                }
            },
            {
                "name": "compare_investment_strategies",
                "description": "Compare les stratégies d'investissement pour un bien",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Localisation du bien"},
                        "property_data": {
                            "type": "object",
                            "properties": {
                                "price": {"type": "number"},
                                "surface": {"type": "number"},
                                "rooms": {"type": "integer"},
                                "property_type": {"type": "string"}
                            }
                        }
                    },
                    "required": ["location", "property_data"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête MCP"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return await self._handle_initialize(params)
            elif method == "tools/list":
                return await self._handle_tools_list()
            elif method == "tools/call":
                return await self._handle_tool_call(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Méthode non supportée: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Erreur traitement requête: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Erreur interne: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gère l'initialisation du serveur"""
        await self.initialize()
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "real-estate-mcp",
                "version": "1.0.0"
            }
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """Retourne la liste des outils disponibles"""
        return {"tools": self.tools}
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un appel d'outil"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not self.mcp:
            return {
                "content": [{
                    "type": "text",
                    "text": "Erreur: Service dynamique non disponible. Veuillez configurer le MCP dynamique."
                }]
            }
        
        try:
            if tool_name == "search_properties":
                result = await self._search_properties(arguments)
            elif tool_name == "analyze_market":
                result = await self._analyze_market(arguments)
            elif tool_name == "get_neighborhood_info":
                result = await self._get_neighborhood_info(arguments)
            elif tool_name == "compare_locations":
                result = await self._compare_locations(arguments)
            elif tool_name == "get_property_summary":
                result = await self._get_property_summary(arguments)
            elif tool_name == "analyze_investment_opportunity":
                result = await self._analyze_investment_opportunity(arguments)
            elif tool_name == "compare_investment_strategies":
                result = await self._compare_investment_strategies(arguments)
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Outil non reconnu: {tool_name}"
                    }]
                }
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
            
        except Exception as e:
            logger.error(f"Erreur exécution outil {tool_name}: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Erreur lors de l'exécution de {tool_name}: {str(e)}"
                }]
            }
    
    async def _search_properties(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Recherche de propriétés"""
        logger.info(f"Recherche de propriétés pour: {args}")
        
        if self.mcp:
            try:
                results = await self.mcp.search_properties(
                    location=args['location'],
                    min_price=args.get('min_price'),
                    max_price=args.get('max_price'),
                    property_type=args.get('property_type'),
                    min_surface=args.get('min_surface'),
                    rooms=args.get('rooms'),
                    transaction_type=args.get('transaction_type', 'rent')
                )
                
                return {
                    "success": True,
                    "tool": "search_properties",
                    "location": args['location'],
                    "total_found": len(results),
                    "properties": results[:10],
                    "summary": self._calculate_search_summary(results)
                }
            except Exception as e:
                logger.error(f"Erreur recherche réelle: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnée réelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des données temps réel"
        }
    
    def _calculate_search_summary(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule un résumé statistique des résultats de recherche"""
        if not properties:
            return {"message": "Aucune propriété trouvée"}
        
        prices = [p.get('price', 0) for p in properties if p.get('price', 0) > 0]
        surfaces = [p.get('surface_area', 0) for p in properties if p.get('surface_area', 0) > 0]
        
        summary = {
            "total_count": len(properties),
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            }
        }
        
        if surfaces:
            summary["surface_range"] = {
                "min": min(surfaces),
                "max": max(surfaces),
                "avg": sum(surfaces) / len(surfaces)
            }
        
        return summary
    
    # Méthodes pour les autres outils (analyse de marché, quartiers, etc.)
    async def _analyze_market(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du marché"""
        if self.mcp:
            return await self.mcp.analyze_market(args['location'], args['transaction_type'])
        return {"error": "Service non disponible"}
    
    async def _get_neighborhood_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Informations sur le quartier"""
        if self.mcp:
            return await self.mcp.get_neighborhood_info(args['location'])
        return {"error": "Service non disponible"}
    
    async def _compare_locations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Comparaison de localisations"""
        if self.mcp:
            return await self.mcp.compare_locations(args['locations'], args.get('criteria', 'all'))
        return {"error": "Service non disponible"}
    
    async def _get_property_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Résumé des propriétés"""
        if self.mcp:
            return await self.mcp.get_property_summary(args['location'])
        return {"error": "Service non disponible"}
    
    async def _analyze_investment_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse d'opportunité d'investissement"""
        if self.mcp:
            return await self.mcp.analyze_investment_opportunity(
                location=args['location'],
                investment_profile=args['investment_profile'],
                min_price=args.get('min_price'),
                max_price=args.get('max_price'),
                min_surface=args.get('min_surface'),
                rooms=args.get('rooms')
            )
        return {"error": "Service non disponible"}
    
    async def _compare_investment_strategies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Comparaison de stratégies d'investissement"""
        if self.mcp:
            return await self.mcp.compare_investment_strategies(
                location=args['location'],
                property_data=args['property_data']
            )
        return {"error": "Service non disponible"}


async def main():
    """Point d'entrée principal du serveur"""
    server = MCPRealEstateServer()
    
    try:
        while True:
            try:
                # Lecture de la requête depuis stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                # Envoi de la réponse vers stdout
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Erreur JSON: {e}")
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                break
    
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur MCP")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")


if __name__ == "__main__":
    asyncio.run(main())
