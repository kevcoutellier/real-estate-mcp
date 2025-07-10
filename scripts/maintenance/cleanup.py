#!/usr/bin/env python3
"""
Script de nettoyage automatique du projet MCP Real Estate
Supprime les fichiers temporaires, caches, et logs anciens
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_project():
    """Nettoie le projet des fichiers temporaires et obsolètes"""
    
    project_root = Path(__file__).parent.parent
    print(f"Nettoyage du projet : {project_root}")
    
    # 1. Supprimer les caches Python
    print("\n1. Suppression des caches Python...")
    pycache_dirs = list(project_root.rglob("__pycache__"))
    for cache_dir in pycache_dirs:
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            print(f"   ✓ Supprimé : {cache_dir}")
    
    # 2. Supprimer les fichiers .pyc
    print("\n2. Suppression des fichiers .pyc...")
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        pyc_file.unlink()
        print(f"   ✓ Supprimé : {pyc_file}")
    
    # 3. Supprimer les logs anciens (> 7 jours)
    print("\n3. Suppression des logs anciens...")
    log_files = list(project_root.glob("*.log"))
    cutoff_date = datetime.now() - timedelta(days=7)
    
    for log_file in log_files:
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            log_file.unlink()
            print(f"   ✓ Supprimé : {log_file}")
    
    # 4. Supprimer les fichiers de backup
    print("\n4. Suppression des fichiers de backup...")
    backup_patterns = ["*.backup_*", "*.bak", "*~"]
    for pattern in backup_patterns:
        backup_files = list(project_root.rglob(pattern))
        for backup_file in backup_files:
            backup_file.unlink()
            print(f"   ✓ Supprimé : {backup_file}")
    
    # 5. Nettoyer le dossier temporaire
    print("\n5. Nettoyage du dossier temporaire...")
    temp_dir = project_root / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"   ✓ Supprimé : {temp_dir}")
    
    # 6. Supprimer les fichiers de test temporaires
    print("\n6. Suppression des fichiers de test temporaires...")
    test_temp_files = list(project_root.rglob("test_*.tmp"))
    for temp_file in test_temp_files:
        temp_file.unlink()
        print(f"   ✓ Supprimé : {temp_file}")
    
    print("\n✅ Nettoyage terminé !")

def show_project_stats():
    """Affiche les statistiques du projet"""
    
    project_root = Path(__file__).parent.parent
    print(f"\n📊 Statistiques du projet : {project_root.name}")
    
    # Compter les fichiers par type
    file_counts = {}
    total_size = 0
    
    for file_path in project_root.rglob("*"):
        if file_path.is_file():
            extension = file_path.suffix.lower()
            if not extension:
                extension = "sans_extension"
            
            file_counts[extension] = file_counts.get(extension, 0) + 1
            total_size += file_path.stat().st_size
    
    # Afficher les statistiques
    print(f"\n📁 Répartition des fichiers :")
    for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {ext:15} : {count:3d} fichiers")
    
    print(f"\n💾 Taille totale : {total_size / (1024*1024):.1f} MB")
    print(f"📄 Total fichiers : {sum(file_counts.values())}")

def validate_structure():
    """Valide la structure du projet"""
    
    project_root = Path(__file__).parent.parent
    print(f"\n🔍 Validation de la structure : {project_root.name}")
    
    required_dirs = [
        "src",
        "config", 
        "examples",
        "scripts",
        "tests",
        "deprecated",
        "archive"
    ]
    
    required_files = [
        "README.md",
        "CHANGELOG.md", 
        "DEVELOPMENT.md",
        "requirements.txt",
        "mcp_server.py",
        "src/main.py"
    ]
    
    # Vérifier les dossiers
    print("\n📁 Dossiers requis :")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"   ✓ {dir_name}")
        else:
            print(f"   ✗ {dir_name} (manquant)")
    
    # Vérifier les fichiers
    print("\n📄 Fichiers requis :")
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"   ✓ {file_name}")
        else:
            print(f"   ✗ {file_name} (manquant)")

def main():
    """Fonction principale"""
    
    print("=== Script de Nettoyage MCP Real Estate ===")
    
    # Afficher les options
    print("\nOptions disponibles :")
    print("1. Nettoyer le projet")
    print("2. Afficher les statistiques")
    print("3. Valider la structure")
    print("4. Tout faire")
    
    choice = input("\nChoisissez une option (1-4) : ").strip()
    
    if choice == "1":
        cleanup_project()
    elif choice == "2":
        show_project_stats()
    elif choice == "3":
        validate_structure()
    elif choice == "4":
        cleanup_project()
        show_project_stats()
        validate_structure()
    else:
        print("Option invalide")

if __name__ == "__main__":
    main()
