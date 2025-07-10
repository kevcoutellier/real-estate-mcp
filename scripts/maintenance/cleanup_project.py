#!/usr/bin/env python3
"""
Script de nettoyage et organisation du projet MCP Real Estate
Déplace les fichiers obsolètes vers le dossier archive
"""

import os
import shutil
from pathlib import Path


def cleanup_project():
    """Nettoie et organise la structure du projet"""
    
    project_root = Path(__file__).parent.parent
    archive_dir = project_root / "archive"
    
    # Créer le dossier archive s'il n'existe pas
    archive_dir.mkdir(exist_ok=True)
    
    # Fichiers à archiver (obsolètes ou dupliqués)
    files_to_archive = [
        "mcp_server.py",  # Ancien serveur, remplacé par src/mcp_server.py
        "RESTART_INSTRUCTIONS.txt",  # Instructions obsolètes
    ]
    
    print("🧹 Nettoyage du projet MCP Real Estate...")
    
    # Archiver les fichiers obsolètes
    for file_name in files_to_archive:
        file_path = project_root / file_name
        if file_path.exists():
            archive_path = archive_dir / file_name
            shutil.move(str(file_path), str(archive_path))
            print(f"✅ Archivé: {file_name}")
    
    # Vérifier la structure des dossiers
    required_dirs = [
        "src/models",
        "src/services", 
        "src/mcp",
        "src/utils",
        "logs",
        "docs",
        "scripts",
        "config"
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Créé: {dir_path}")
    
    # Créer les fichiers __init__.py manquants
    python_dirs = [
        "src",
        "src/models",
        "src/services",
        "src/mcp", 
        "src/utils"
    ]
    
    for dir_path in python_dirs:
        init_file = project_root / dir_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"🐍 Créé: {dir_path}/__init__.py")
    
    print("\n✨ Nettoyage terminé !")
    print("\n📊 Structure finale:")
    print_directory_tree(project_root, max_depth=2)


def print_directory_tree(path: Path, prefix: str = "", max_depth: int = 2, current_depth: int = 0):
    """Affiche l'arborescence du projet"""
    if current_depth >= max_depth:
        return
    
    items = sorted([p for p in path.iterdir() if not p.name.startswith('.') and p.name != '__pycache__'])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_tree(item, next_prefix, max_depth, current_depth + 1)


if __name__ == "__main__":
    cleanup_project()
