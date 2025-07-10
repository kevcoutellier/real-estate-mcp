#!/usr/bin/env python3
"""
Script de démarrage du serveur MCP Real Estate
Point d'entrée principal pour lancer le serveur
"""

import sys
import os

# Ajouter le dossier src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Lancer le serveur
if __name__ == "__main__":
    from mcp_server import main
    import asyncio
    
    print("Démarrage du serveur MCP Real Estate...")
    asyncio.run(main())
