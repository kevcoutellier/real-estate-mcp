#!/bin/bash
# Script Unix/Linux/Mac pour lancer le MCP avec environnement virtuel actif
# Utilisé par Claude Desktop sur Unix

# Se placer dans le dossier du script
cd "$(dirname "$0")"

# Vérifier que l'environnement virtuel existe
if [ ! -f "venv/bin/python" ]; then
    echo "❌ Environnement virtuel non trouvé !"
    echo "🔧 Lancez 'python install.py' pour créer l'environnement"
    exit 1
fi

# Activer l'environnement virtuel et lancer le serveur
source venv/bin/activate
export PYTHONPATH="$(pwd)/src"
python mcp_wrapper.py
