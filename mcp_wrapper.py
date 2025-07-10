#!/usr/bin/env python3
"""
Wrapper pour garantir l'utilisation de l'environnement virtuel
Ce script s'assure que le MCP fonctionne toujours avec les bonnes dépendances
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_venv_python():
    """Retourne le chemin vers Python dans l'environnement virtuel"""
    project_root = Path(__file__).parent
    
    if platform.system() == "Windows":
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / "venv" / "bin" / "python"
    
    return venv_python


def is_venv_active():
    """Vérifie si l'environnement virtuel est actif"""
    # Vérifier si on utilise le Python du venv
    current_python = Path(sys.executable)
    venv_python = get_venv_python()
    
    return current_python.resolve() == venv_python.resolve()


def activate_and_run():
    """Active l'environnement virtuel et lance le serveur MCP"""
    project_root = Path(__file__).parent
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print("❌ Environnement virtuel non trouvé !")
        print("🔧 Lancez 'python install.py' pour créer l'environnement")
        sys.exit(1)
    
    # Préparer l'environnement
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    
    # Lancer le serveur MCP avec le Python du venv
    server_script = project_root / "start_server.py"
    
    try:
        # Utiliser directement le Python du venv
        subprocess.run([str(venv_python), str(server_script)], 
                      cwd=str(project_root), 
                      env=env)
    except KeyboardInterrupt:
        print("\n🛑 Serveur MCP arrêté")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)


def main():
    """Point d'entrée principal"""
    if is_venv_active():
        # L'environnement virtuel est déjà actif, lancer directement
        from start_server import main as start_main
        import asyncio
        asyncio.run(start_main())
    else:
        # L'environnement virtuel n'est pas actif, le forcer
        activate_and_run()


if __name__ == "__main__":
    main()
