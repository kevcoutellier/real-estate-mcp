#!/usr/bin/env python3
"""
Point d'entrée principal pour le MCP Real Estate restructuré
"""

import logging
from .mcp.dynamic_mcp import DynamicRealEstateMCP
from .dynamic_data_service import get_dynamic_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Outils MCP pour la version dynamique
MCP_TOOLS_DYNAMIC = [
    {
        "name": "search_properties",
        "description": "Recherche des propriétés selon les critères spécifiés",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou arrondissement"},
                "min_price": {"type": "number", "description": "Prix minimum en euros"},
                "max_price": {"type": "number", "description": "Prix maximum en euros"},
                "property_type": {"type": "string", "description": "Type de bien"},
                "min_surface": {"type": "number", "description": "Surface minimale en m²"},
                "max_surface": {"type": "number", "description": "Surface maximale en m²"},
                "rooms": {"type": "integer", "description": "Nombre de pièces"},
                "transaction_type": {"type": "string", "enum": ["rent", "sale"], "default": "rent"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_property_summary",
        "description": "Génère un résumé du marché immobilier pour une zone",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou arrondissement"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_neighborhood_info",
        "description": "Analyse détaillée d'un quartier avec informations sur les transports, commodités et qualité de vie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Quartier ou adresse à analyser"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "analyze_market",
        "description": "Analyse complète du marché immobilier d'une zone avec statistiques détaillées",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Zone à analyser"},
                "transaction_type": {"type": "string", "enum": ["rent", "sale"], "default": "rent"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "analyze_investment_opportunity",
        "description": "Analyse complète d'opportunités d'investissement immobilier",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou arrondissement"},
                "min_price": {"type": "number", "description": "Prix minimum en euros"},
                "max_price": {"type": "number", "description": "Prix maximum en euros"},
                "investment_profile": {"type": "string", "enum": ["rental_investor", "property_dealer", "both"], "default": "both"},
                "min_surface": {"type": "number", "description": "Surface minimale en m²"},
                "rooms": {"type": "integer", "description": "Nombre de pièces souhaité"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "compare_investment_strategies",
        "description": "Compare les stratégies d'investissement locatif vs marchand de biens pour un bien spécifique",
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
                    },
                    "required": ["price", "surface"]
                }
            },
            "required": ["location", "property_data"]
        }
    },
    {
        "name": "compare_locations",
        "description": "Compare plusieurs quartiers ou villes selon différents critères immobiliers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "locations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "description": "Liste des localisations à comparer"
                },
                "criteria": {"type": "string", "enum": ["price", "availability", "quality", "all"], "default": "all"}
            },
            "required": ["locations"]
        }
    }
]


# Instance principale du MCP
_mcp_instance = None


async def get_mcp_instance():
    """Récupère l'instance MCP singleton"""
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = DynamicRealEstateMCP()
        logger.info("Instance MCP dynamique créée")
    return _mcp_instance


# Fonctions d'interface pour les outils MCP
async def search_properties(**kwargs):
    """Interface pour la recherche de propriétés"""
    mcp = await get_mcp_instance()
    return await mcp.search_properties(**kwargs)


async def get_property_summary(**kwargs):
    """Interface pour le résumé de marché"""
    mcp = await get_mcp_instance()
    return await mcp.get_property_summary(**kwargs)


async def get_neighborhood_info(**kwargs):
    """Interface pour l'analyse de quartier"""
    mcp = await get_mcp_instance()
    return await mcp.get_neighborhood_analysis(**kwargs)


async def analyze_market(**kwargs):
    """Interface pour l'analyse de marché"""
    mcp = await get_mcp_instance()
    location = kwargs.get('location')
    transaction_type = kwargs.get('transaction_type', 'rent')
    return await mcp.get_market_data_dynamic(location, transaction_type)


async def analyze_investment_opportunity(**kwargs):
    """Interface pour l'analyse d'opportunité d'investissement"""
    mcp = await get_mcp_instance()
    return await mcp.analyze_investment_opportunity_dynamic(**kwargs)


async def compare_investment_strategies(**kwargs):
    """Interface pour la comparaison de stratégies d'investissement"""
    mcp = await get_mcp_instance()
    return await mcp.compare_investment_strategies_dynamic(**kwargs)


async def compare_locations(**kwargs):
    """Interface pour la comparaison de localisations"""
    mcp = await get_mcp_instance()
    return await mcp.compare_locations_dynamic(**kwargs)


# Mapping des outils vers leurs fonctions
TOOL_FUNCTIONS = {
    "search_properties": search_properties,
    "get_property_summary": get_property_summary,
    "get_neighborhood_info": get_neighborhood_info,
    "analyze_market": analyze_market,
    "analyze_investment_opportunity": analyze_investment_opportunity,
    "compare_investment_strategies": compare_investment_strategies,
    "compare_locations": compare_locations
}


def get_available_tools():
    """Retourne la liste des outils disponibles"""
    return MCP_TOOLS_DYNAMIC


async def execute_tool(tool_name: str, **kwargs):
    """Exécute un outil MCP"""
    if tool_name not in TOOL_FUNCTIONS:
        raise ValueError(f"Outil inconnu: {tool_name}")
    
    function = TOOL_FUNCTIONS[tool_name]
    return await function(**kwargs)


if __name__ == "__main__":
    import asyncio
    
    async def test_main():
        """Test de base du système restructuré"""
        logger.info("Test du système MCP restructuré")
        
        # Test de recherche
        try:
            results = await search_properties(location="Paris 11e", max_price=2000)
            logger.info(f"Recherche réussie: {len(results)} résultats")
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
        
        # Test d'analyse de marché
        try:
            market_data = await analyze_market(location="Paris")
            logger.info(f"Analyse de marché réussie: {market_data.get('location', 'N/A')}")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de marché: {e}")
    
    asyncio.run(test_main())
