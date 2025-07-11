#!/usr/bin/env python3
"""
Serveur MCP Immobilier Compatible Windows
Fichier: mcp_real_estate_server.py

Version corrigée sans problèmes d'encodage Unicode pour assurer
une communication parfaite avec Windsurf sur Windows.
"""

import asyncio
import json
import sys
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration du système de chemins pour permettre les imports locaux
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# Créer un répertoire logs s'il n'existe pas
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mcp_server.log')

# Configuration du logging compatible Windows avec encodage UTF-8
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de log détaillé
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Fichier de log avec encodage UTF-8 explicite
        logging.FileHandler(log_file, encoding='utf-8'),
        # Ajout d'un StreamHandler pour voir les logs dans la console
        logging.StreamHandler()
    ]
)

# Désactiver les logs trop verbeux de certaines bibliothèques
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# Logger principal
logger = logging.getLogger('real_estate_mcp')
logger.info(f'Logs enregistrés dans: {log_file}')

# Import de la version dynamique sans données hardcodées
try:
    from src.main import DynamicRealEstateMCP
    logger.info("Module dynamique importe avec succes - donnees temps reel")
    HAS_MAIN_MODULE = True
except ImportError as e:
    logger.warning(f"Import du module dynamique echoue: {e}")
    logger.info("Impossible d'utiliser les donnees temps reel")
    HAS_MAIN_MODULE = False

class MCPRealEstateServer:
    """
    Serveur MCP pour l'immobilier - Version compatible Windows
    
    Cette version garantit une communication propre avec Windsurf en evitant
    tous les caracteres qui pourraient causer des problemes d'encodage.
    """
    
    def __init__(self):
        """Initialise le serveur MCP avec une approche compatible Windows"""
        
        # Initialisation du module dynamique si disponible
        if HAS_MAIN_MODULE:
            try:
                self.mcp = DynamicRealEstateMCP()
                logger.info("MCP dynamique initialise - donnees temps reel")
            except Exception as e:
                logger.error(f"Erreur initialisation MCP dynamique: {e}")
                self.mcp = None
        else:
            self.mcp = None
        
        # Definition des outils MCP disponibles
        self.tools = {
            "search_properties": {
                "description": "Recherche des biens immobiliers selon differents criteres avec enrichissement geographique",
                "inputSchema": {
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
                            "description": "Type de bien ('appartement', 'maison', etc.)"
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
                            "description": "Nombre de pieces"
                        },
                        "transaction_type": {
                            "type": "string",
                            "description": "Type de transaction ('rent' pour location, 'sale' pour achat)",
                            "enum": ["rent", "sale"]
                        }
                    },
                    "required": ["location"]
                }
            },
            "get_property_summary": {
                "description": "Genere un resume du marche immobilier pour une zone",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Ville ou arrondissement"
                        }
                    },
                    "required": ["location"]
                }
            },
            "analyze_market": {
                "description": "Analyse complete du marche immobilier d'une zone avec statistiques detaillees",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Zone a analyser (ville ou arrondissement)"
                        },
                        "transaction_type": {
                            "type": "string",
                            "description": "Type de marche a analyser ('rent' ou 'sale')",
                            "enum": ["rent", "sale"]
                        }
                    },
                    "required": ["location"]
                }
            },
            "compare_locations": {
                "description": "Compare plusieurs quartiers ou villes selon differents criteres immobiliers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "locations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Liste des localisations a comparer (minimum 2)",
                            "minItems": 2
                        },
                        "criteria": {
                            "type": "string",
                            "description": "Critere principal de comparaison",
                            "enum": ["price", "availability", "quality", "all"]
                        }
                    },
                    "required": ["locations"]
                }
            },
            "get_neighborhood_info": {
                "description": "Analyse detaillee d'un quartier avec informations sur les transports, commodites et qualite de vie",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Quartier ou adresse a analyser"
                        }
                    },
                    "required": ["location"]
                }
            },
            "analyze_investment_opportunity": {
                "description": "Analyse complete d'opportunites d'investissement immobilier (locatif et/ou marchand de biens)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Ville ou arrondissement a analyser"
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
                            "description": "Profil d'investissement ('rental_investor', 'property_dealer', 'both')",
                            "enum": ["rental_investor", "property_dealer", "both"]
                        },
                        "min_surface": {
                            "type": "number",
                            "description": "Surface minimale en m²"
                        },
                        "rooms": {
                            "type": "integer",
                            "description": "Nombre de pieces souhaite"
                        }
                    },
                    "required": ["location"]
                }
            },
            "compare_investment_strategies": {
                "description": "Compare les strategies d'investissement locatif vs marchand de biens pour un bien specifique",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Localisation du bien"
                        },
                        "property_data": {
                            "type": "object",
                            "description": "Donnees du bien immobilier (prix, surface, etc.)",
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
        }
        
        # Compteur pour les IDs de requete MCP
        self.request_counter = 0
        
        logger.info(f"Serveur MCP Immobilier initialise avec {len(self.tools)} outils")
    
    async def initialize_dynamic_service(self):
        """Initialise le service dynamique de manière asynchrone"""
        if self.mcp:
            try:
                await self.mcp._ensure_dynamic_service()
                logger.info("Service dynamique initialise avec succes")
                return True
            except Exception as e:
                logger.error(f"Erreur initialisation service dynamique: {e}")
                return False
        return False

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requete MCP et retourne la reponse appropriee
        
        Cette methode constitue le coeur de notre serveur, dirigeant chaque
        requete vers le bon gestionnaire selon le protocole MCP.
        """
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Requete recue: {method}")
            
            # Routage des requetes selon le protocole MCP
            if method == "initialize":
                return await self._handle_initialize(request_id)
            elif method == "tools/list":
                return await self._handle_tools_list(request_id)
            elif method == "tools/call":
                return await self._handle_tools_call(request_id, params)
            else:
                return self._create_error_response(request_id, -32601, f"Methode '{method}' non supportee")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requete: {e}")
            return self._create_error_response(request.get("id"), -32603, f"Erreur interne: {str(e)}")

    async def _handle_initialize(self, request_id: int) -> Dict[str, Any]:
        """
        Gere la requete d'initialisation MCP
        
        Cette requete etablit la communication et declare les capacites du serveur
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "real-estate-mcp",
                    "version": "1.0.0",
                    "description": "Serveur MCP pour l'analyse immobiliere francaise"
                }
            }
        }

    async def _handle_tools_list(self, request_id: int) -> Dict[str, Any]:
        """
        Retourne la liste complete des outils disponibles
        
        Cette reponse permet a Windsurf de connaitre tous les outils
        qu'il peut utiliser et leurs parametres
        """
        tools_list = []
        for tool_name, tool_info in self.tools.items():
            tools_list.append({
                "name": tool_name,
                "description": tool_info["description"],
                "inputSchema": tool_info["inputSchema"]
            })
        
        logger.info(f"Liste des outils envoyee: {len(tools_list)} outils")
        
        return {
            "jsonrpc": "2.0", 
            "id": request_id,
            "result": {
                "tools": tools_list
            }
        }

    async def _handle_tools_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute un outil specifique avec les parametres fournis
        
        Cette methode traduit les demandes Windsurf en actions concretes
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Execution outil: {tool_name} avec arguments: {arguments}")
        
        if tool_name not in self.tools:
            return self._create_error_response(request_id, -32602, f"Outil '{tool_name}' non trouve")
        
        try:
            # Dispatcher vers la bonne methode
            if tool_name == "search_properties":
                result = await self._search_properties(arguments)
            elif tool_name == "get_property_summary":
                result = await self._get_property_summary(arguments)
            elif tool_name == "analyze_market":
                result = await self._analyze_market(arguments)
            elif tool_name == "compare_locations":
                result = await self._compare_locations(arguments)
            elif tool_name == "get_neighborhood_info":
                result = await self._get_neighborhood_info(arguments)
            elif tool_name == "analyze_investment_opportunity":
                result = await self._analyze_investment_opportunity(arguments)
            elif tool_name == "compare_investment_strategies":
                result = await self._compare_investment_strategies(arguments)
            else:
                return self._create_error_response(request_id, -32602, f"Outil '{tool_name}' non implemente")
            
            # Formater la reponse selon le standard MCP
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_result_for_display(result, tool_name)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur execution outil {tool_name}: {e}")
            return self._create_error_response(request_id, -32603, f"Erreur execution: {str(e)}")

    async def _search_properties(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Recherche de biens immobiliers avec integration intelligente"""
        logger.info(f"Recherche de proprietes pour: {args}")
        
        # Utilisation du module principal si disponible
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
                logger.error(f"Erreur recherche reelle: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _get_property_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Genere un resume du marche immobilier pour une zone avec donnees dynamiques"""
        logger.info(f"Resume de marche pour: {args}")
        
        if self.mcp:
            try:
                # Utiliser les données de marché dynamiques
                market_data = await self.mcp.get_market_data_dynamic(
                    location=args['location'],
                    transaction_type='rent'  # Par défaut location
                )
                
                if 'error' not in market_data:
                    return {
                        "success": True,
                        "tool": "get_property_summary",
                        "analysis": market_data
                    }
            except Exception as e:
                logger.error(f"Erreur resume reelle: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _analyze_market(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du marche immobilier avec donnees dynamiques enrichies"""
        logger.info(f"Analyse de marche pour: {args}")
        
        if self.mcp:
            try:
                # Utiliser les données de marché dynamiques
                market_data = await self.mcp.get_market_data_dynamic(
                    location=args['location'],
                    transaction_type=args.get('transaction_type', 'rent')
                )
                
                if 'error' not in market_data:
                    return {
                        "success": True,
                        "tool": "analyze_market",
                        "analysis": market_data,
                        "insights": self._generate_market_insights(market_data)
                    }
            except Exception as e:
                logger.error(f"Erreur analyse reelle: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _compare_locations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Comparaison intelligente de plusieurs localisations"""
        logger.info(f"Comparaison de localisations: {args}")
        
        locations = args.get('locations', [])
        if len(locations) < 2:
            return {
                "success": False,
                "error": "Il faut au moins 2 localisations pour effectuer une comparaison"
            }
        
        if self.mcp:
            try:
                comparison = await self.mcp.compare_locations_dynamic(
                    locations=locations,
                    criteria=args.get('criteria', 'all')
                )
                
                if 'error' not in comparison:
                    return {
                        "success": True,
                        "tool": "compare_locations",
                        "comparison": comparison
                    }
            except Exception as e:
                logger.error(f"Erreur comparaison localisations: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _get_neighborhood_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Informations detaillees sur un quartier avec donnees dynamiques"""
        logger.info(f"Analyse de quartier: {args}")
        
        if self.mcp:
            try:
                # Utiliser le service de géocodage pour obtenir les informations du quartier
                if hasattr(self.mcp, 'aggregator') and hasattr(self.mcp.aggregator, 'geocoding_service'):
                    # D'abord géocoder l'adresse
                    coords = await self.mcp.aggregator.geocoding_service.geocode_address(args['location'])
                    if coords:
                        # Puis obtenir les informations du quartier
                        neighborhood_info = await self.mcp.aggregator.geocoding_service.get_neighborhood_info(coords)
                        return {
                            "success": True,
                            "tool": "get_neighborhood_info",
                            "analysis": neighborhood_info
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Impossible de localiser: {args['location']}"
                        }
                else:
                    # Fallback si le service de géocodage n'est pas disponible
                    return {
                        "success": False,
                        "error": "Service de géocodage non disponible"
                    }
            except Exception as e:
                logger.error(f"Erreur analyse quartier: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _analyze_investment_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse complete d'opportunites d'investissement immobilier"""
        logger.info(f"Analyse d'opportunite d'investissement pour: {args}")
        
        if self.mcp:
            try:
                analysis = await self.mcp.analyze_investment_opportunity_dynamic(
                    location=args['location'],
                    min_price=args.get('min_price'),
                    max_price=args.get('max_price'),
                    investment_profile=args.get('investment_profile', 'both'),
                    min_surface=args.get('min_surface'),
                    rooms=args.get('rooms')
                )
                
                if 'error' not in analysis:
                    return {
                        "success": True,
                        "tool": "analyze_investment_opportunity",
                        "analysis": analysis
                    }
            except Exception as e:
                logger.error(f"Erreur analyse opportunite: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    async def _compare_investment_strategies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les strategies d'investissement locatif vs marchand de biens"""
        logger.info(f"Comparaison de strategies d'investissement pour: {args}")
        
        if self.mcp:
            try:
                comparison = await self.mcp.compare_investment_strategies_dynamic(
                    location=args['location'],
                    property_data=args['property_data']
                )
                
                if 'error' not in comparison:
                    return {
                        "success": True,
                        "tool": "compare_investment_strategies",
                        "comparison": comparison
                    }
            except Exception as e:
                logger.error(f"Erreur comparaison strategies: {e}")
        
        return {
            "success": False,
            "error": "Aucune donnee reelle disponible - Service dynamique requis",
            "note": "Configurez DynamicRealEstateMCP pour des donnees temps reel"
        }

    # Méthodes de génération de données de test supprimées
    # Utilisation exclusive de données temps réel via DynamicRealEstateMCP

    # Méthode _generate_test_market_analysis supprimée

    # Toutes les méthodes de génération de données de test supprimées :
    # - _generate_test_comparison
    # - _generate_test_neighborhood_info  
    # - _generate_test_property_summary
    # - _generate_test_investment_opportunity
    # - _generate_test_investment_strategies
    # 
    # Utilisation exclusive de données temps réel via DynamicRealEstateMCP

    # Dernières méthodes de génération de données de test supprimées

    def _calculate_search_summary(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule un resume statistique des resultats de recherche"""
        if not properties:
            return {"message": "Aucune propriete trouvee"}
        
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

    def _generate_market_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Genere des insights intelligents bases sur l'analyse de marche"""
        insights = []
        
        price_stats = analysis.get('price_stats', {})
        avg_price = price_stats.get('avg', 0)
        total_listings = analysis.get('total_listings', 0)
        
        if avg_price > 0:
            if avg_price < 1200:
                insights.append("Zone abordable, excellente pour les primo-accedants")
            elif avg_price > 2500:
                insights.append("Marche haut de gamme, investissement de prestige")
            else:
                insights.append("Prix equilibres, marche stable")
        
        if total_listings > 100:
            insights.append("Marche dynamique avec beaucoup d'offres disponibles")
        elif total_listings < 20:
            insights.append("Marche restreint, agir rapidement sur les bonnes opportunites")
        
        return insights

    def _format_result_for_display(self, result: Dict[str, Any], tool_name: str) -> str:
        """
        Formate les resultats pour un affichage optimal dans Windsurf
        
        Cette fonction transforme nos donnees techniques en texte lisible
        sans utiliser de caracteres problematiques pour l'encodage
        """
        if not result.get("success", True):
            return f"[ERREUR {tool_name}] {result.get('error', 'Erreur inconnue')}"
        
        if tool_name == "search_properties":
            return self._format_search_display(result)
        elif tool_name == "get_property_summary":
            return self._format_property_summary_display(result)
        elif tool_name == "analyze_market":
            return self._format_market_display(result)
        elif tool_name == "compare_locations":
            return self._format_comparison_display(result)
        elif tool_name == "get_neighborhood_info":
            return self._format_neighborhood_display(result)
        elif tool_name == "analyze_investment_opportunity":
            return self._format_investment_opportunity_display(result)
        elif tool_name == "compare_investment_strategies":
            return self._format_investment_strategies_display(result)
        else:
            return json.dumps(result, indent=2, ensure_ascii=False)

    def _format_search_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage des resultats de recherche"""
        properties = result.get("properties", [])
        summary = result.get("summary", {})
        location = result.get("location", "")
        
        if not properties:
            return f"[RECHERCHE] Aucune annonce trouvee pour {location}\n\nEssayez d'elargir vos criteres de recherche."
        
        output = f"[RECHERCHE] {result['total_found']} annonces trouvees a {location}\n\n"
        
        # Resume des prix
        price_range = summary.get("price_range", {})
        if price_range.get("avg", 0) > 0:
            output += f"PRIX MOYEN: {price_range['avg']:.0f} euros\n"
            output += f"FOURCHETTE: {price_range['min']:.0f} - {price_range['max']:.0f} euros\n\n"
        
        # Top annonces
        output += "MEILLEURES ANNONCES:\n\n"
        
        for i, prop in enumerate(properties[:5], 1):
            output += f"{i}. {prop['title']}\n"
            output += f"   Prix: {prop['price']:,} euros"
            
            if prop.get('surface_area'):
                output += f" | Surface: {prop['surface_area']}m2"
                if 'price_per_sqm' in prop:
                    output += f" | Prix/m2: {prop['price_per_sqm']} euros/m2"
            
            output += f"\n   Localisation: {prop['location']}"
            
            if prop.get('rooms'):
                output += f" | Pieces: {prop['rooms']}"
            
            output += f"\n   Lien: {prop['url']}"
            output += f"\n   Source: {prop['source']}\n\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_market_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage de l'analyse de marche"""
        analysis = result.get("analysis", {})
        insights = result.get("insights", [])
        
        location = analysis.get("location", "Zone inconnue")
        total = analysis.get("total_listings", 0)
        
        output = f"[ANALYSE MARCHE] {location}\n\n"
        output += f"ANNONCES ANALYSEES: {total}\n\n"
        
        # Statistiques de prix
        price_stats = analysis.get("price_stats", {})
        if price_stats:
            output += "STATISTIQUES DE PRIX:\n"
            output += f"- Prix moyen: {price_stats['avg']:,.0f} euros\n"
            output += f"- Prix median: {price_stats['median']:,.0f} euros\n"
            output += f"- Fourchette: {price_stats['min']:,.0f} - {price_stats['max']:,.0f} euros\n\n"
        
        # Prix au m2
        price_per_sqm = analysis.get("price_per_sqm", {})
        if price_per_sqm:
            output += f"PRIX AU M2 MOYEN: {price_per_sqm['avg']} euros/m2\n"
            output += f"   (min: {price_per_sqm['min']} euros/m2, max: {price_per_sqm['max']} euros/m2)\n\n"
        
        # Insights
        if insights:
            output += "INSIGHTS DU MARCHE:\n"
            for insight in insights:
                output += f"- {insight}\n"
            output += "\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_comparison_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage de la comparaison"""
        locations = result.get("locations", [])
        comparison_data = result.get("comparison_data", {})
        winner = result.get("winner", {})
        
        output = f"[COMPARAISON] {' vs '.join(locations)}\n\n"
        
        # Tableau de comparaison simplifie
        output += "RESULTATS DE COMPARAISON:\n\n"
        
        for location in locations:
            data = comparison_data.get(location, {})
            output += f"{location}:\n"
            output += f"  - Prix moyen: {data.get('average_price', 0):,} euros\n"
            output += f"  - Annonces: {data.get('total_properties', 0)}\n"
            output += f"  - Prix/m2: {data.get('price_per_sqm', 0)} euros/m2\n\n"
        
        # Recommandations
        if winner:
            output += "RECOMMANDATIONS:\n"
            if winner.get("best_price"):
                output += f"- Meilleur prix: {winner['best_price']}\n"
            if winner.get("most_available"):
                output += f"- Plus de choix: {winner['most_available']}\n"
            output += "\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_neighborhood_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage de l'analyse de quartier"""
        analysis = result.get("analysis", {})
        location = result.get("location", "Quartier")
        
        output = f"[QUARTIER] {location}\n\n"
        
        # Scores
        if "transport_score" in analysis:
            output += f"TRANSPORTS: {analysis['transport_score']}/10\n"
        if "amenities_score" in analysis:
            output += f"COMMODITES: {analysis['amenities_score']}/10\n"
        if "safety_score" in analysis:
            output += f"SECURITE: {analysis['safety_score']}/10\n"
        if "overall_score" in analysis:
            output += f"SCORE GLOBAL: {analysis['overall_score']}/10\n\n"
        
        # Points forts
        highlights = analysis.get("highlights", [])
        if highlights:
            output += "POINTS FORTS:\n"
            for highlight in highlights:
                output += f"- {highlight}\n"
            output += "\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_property_summary_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage du resume de marche"""
        analysis = result.get("analysis", {})
        location = analysis.get("location", "Zone inconnue")
        
        output = f"[RESUME MARCHE] {location}\n\n"
        
        # Statistiques de prix
        price_stats = analysis.get("price_stats", {})
        if price_stats:
            output += "STATISTIQUES DE PRIX:\n"
            output += f"- Prix moyen: {price_stats['avg']:,.0f} euros\n"
            output += f"- Prix median: {price_stats['median']:,.0f} euros\n"
            output += f"- Fourchette: {price_stats['min']:,.0f} - {price_stats['max']:,.0f} euros\n\n"
        
        # Prix au m2
        price_per_sqm = analysis.get("price_per_sqm", {})
        if price_per_sqm:
            output += f"PRIX AU M2 MOYEN: {price_per_sqm['avg']} euros/m2\n"
            output += f"   (min: {price_per_sqm['min']} euros/m2, max: {price_per_sqm['max']} euros/m2)\n\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_investment_opportunity_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage de l'analyse d'opportunite d'investissement"""
        analysis = result.get("analysis", {})
        location = analysis.get("location", "Zone inconnue")
        
        output = f"[OPPORTUNITE D'INVESTISSEMENT] {location}\n\n"
        
        # Opportunites
        opportunities = analysis.get("opportunities", [])
        if opportunities:
            output += "OPPORTUNITES D'INVESTISSEMENT:\n\n"
            for opportunity in opportunities:
                output += f"- {opportunity['id']}: {opportunity['price']:,} euros\n"
                output += f"  - Surface: {opportunity['surface_area']}m2\n"
                output += f"  - Pieces: {opportunity['rooms']}\n"
                output += f"  - Type de bien: {opportunity['property_type']}\n"
                output += f"  - Rendement: {opportunity['yield']}%\n"
                output += f"  - Potentiel de croissance: {opportunity['growth_potential']}%\n\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _format_investment_strategies_display(self, result: Dict[str, Any]) -> str:
        """Formate l'affichage de la comparaison de strategies d'investissement"""
        comparison = result.get("comparison", {})
        location = result.get("location", "Zone inconnue")
        
        output = f"[COMPARAISON DE STRATEGIES D'INVESTISSEMENT] {location}\n\n"
        
        # Strategies
        rental_strategy = comparison.get("rental_strategy", {})
        sale_strategy = comparison.get("sale_strategy", {})
        
        output += "STRATEGIES D'INVESTISSEMENT:\n\n"
        output += f"- Strategie locative:\n"
        output += f"  - Rendement: {rental_strategy.get('yield', 0)}%\n"
        output += f"  - Potentiel de croissance: {rental_strategy.get('growth_potential', 0)}%\n"
        output += f"  - Risques: {', '.join(rental_strategy.get('risks', []))}\n\n"
        output += f"- Strategie de vente:\n"
        output += f"  - Rendement: {sale_strategy.get('yield', 0)}%\n"
        output += f"  - Potentiel de croissance: {sale_strategy.get('growth_potential', 0)}%\n"
        output += f"  - Risques: {', '.join(sale_strategy.get('risks', []))}\n\n"
        
        # Recommandation
        winner = result.get("winner", "")
        if winner:
            output += f"RECOMMANDATION: {winner}\n\n"
        
        if result.get("note"):
            output += f"INFO: {result['note']}"
        
        return output

    def _create_error_response(self, request_id: int, code: int, message: str) -> Dict[str, Any]:
        """Cree une reponse d'erreur standardisee MCP"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

async def main():
    """
    Point d'entree principal du serveur MCP
    
    Cette fonction gere la boucle principale de communication avec Windsurf
    en utilisant uniquement stdin/stdout pour eviter tout probleme d'encodage
    """
    logger.info("Demarrage du serveur MCP Immobilier")
    
    # Initialisation du serveur
    server = MCPRealEstateServer()
    
    # Initialisation du service dynamique
    await server.initialize_dynamic_service()
    
    try:
        # Boucle principale de traitement des requetes
        while True:
            try:
                # Lecture d'une ligne depuis stdin
                line = input()
                
                if not line.strip():
                    continue
                
                # Parse de la requete JSON
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur parsing JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response))
                    continue
                
                # Traitement de la requete
                response = await server.handle_request(request)
                
                # Envoi de la reponse vers stdout (communication avec Windsurf)
                print(json.dumps(response, ensure_ascii=False))
                
            except EOFError:
                # Fin de la communication
                logger.info("Communication terminee par le client")
                break
            except KeyboardInterrupt:
                # Arret manuel du serveur
                logger.info("Arret du serveur demande")
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
    finally:
        logger.info("Serveur MCP Immobilier arrete")

if __name__ == "__main__":
    # Lancement du serveur
    asyncio.run(main())