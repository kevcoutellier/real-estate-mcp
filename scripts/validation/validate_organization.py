#!/usr/bin/env python3
"""
Script de validation de l'organisation du projet MCP Real Estate
Vérifie que tous les composants sont correctement organisés
"""

import os
import sys
from pathlib import Path


def validate_organization():
    """Valide l'organisation du projet"""
    
    project_root = Path(__file__).parent.parent
    print("🔍 Validation de l'organisation du projet MCP Real Estate...")
    print(f"📁 Racine du projet: {project_root}")
    
    # Structure attendue
    expected_structure = {
        "src": {
            "type": "dir",
            "required": True,
            "files": ["__init__.py", "mcp_server.py", "main.py"]
        },
        "src/utils": {
            "type": "dir", 
            "required": True,
            "files": ["__init__.py", "logger.py"]
        },
        "src/models": {
            "type": "dir",
            "required": True,
            "files": ["__init__.py"]
        },
        "src/services": {
            "type": "dir",
            "required": True, 
            "files": ["__init__.py"]
        },
        "src/mcp": {
            "type": "dir",
            "required": True,
            "files": ["__init__.py"]
        },
        "config": {
            "type": "dir",
            "required": True,
            "files": ["mcp-config.json"]
        },
        "scripts": {
            "type": "dir",
            "required": True,
            "files": ["cleanup_project.py", "validate_organization.py"]
        },
        "docs": {
            "type": "dir", 
            "required": True,
            "files": ["PROJECT_ORGANIZATION.md"]
        },
        "logs": {
            "type": "dir",
            "required": True,
            "files": []
        },
        "start_server.py": {
            "type": "file",
            "required": True
        },
        "README.md": {
            "type": "file", 
            "required": True
        },
        "requirements.txt": {
            "type": "file",
            "required": True
        }
    }
    
    errors = []
    warnings = []
    
    print("\n📋 Vérification de la structure...")
    
    # Vérifier chaque élément
    for path_str, config in expected_structure.items():
        path = project_root / path_str
        
        if config["type"] == "dir":
            if not path.exists():
                if config["required"]:
                    errors.append(f"❌ Dossier manquant: {path_str}")
                else:
                    warnings.append(f"⚠️ Dossier optionnel manquant: {path_str}")
            else:
                print(f"✅ Dossier trouvé: {path_str}")
                
                # Vérifier les fichiers dans le dossier
                for file_name in config.get("files", []):
                    file_path = path / file_name
                    if not file_path.exists():
                        warnings.append(f"⚠️ Fichier manquant: {path_str}/{file_name}")
                    else:
                        print(f"  ✅ Fichier: {file_name}")
        
        elif config["type"] == "file":
            if not path.exists():
                if config["required"]:
                    errors.append(f"❌ Fichier manquant: {path_str}")
                else:
                    warnings.append(f"⚠️ Fichier optionnel manquant: {path_str}")
            else:
                print(f"✅ Fichier trouvé: {path_str}")
    
    # Vérifier les imports Python
    print("\n🐍 Vérification des imports Python...")
    
    try:
        sys.path.insert(0, str(project_root / "src"))
        
        # Test import du logger
        from utils.logger import setup_logger
        print("✅ Import utils.logger réussi")
        
        # Test import du serveur MCP
        from mcp_server import MCPRealEstateServer
        print("✅ Import mcp_server réussi")
        
        # Test du point d'entrée
        sys.path.insert(0, str(project_root))
        import start_server
        print("✅ Import start_server réussi")
        
    except ImportError as e:
        errors.append(f"❌ Erreur d'import: {e}")
    
    # Vérifier la configuration
    print("\n⚙️ Vérification de la configuration...")
    
    config_file = project_root / "config" / "mcp-config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if config_data.get("main") == "start_server.py":
                print("✅ Configuration MCP mise à jour")
            else:
                warnings.append("⚠️ Configuration MCP non mise à jour")
                
        except json.JSONDecodeError:
            errors.append("❌ Fichier de configuration JSON invalide")
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("="*60)
    
    if not errors and not warnings:
        print("🎉 PARFAIT ! L'organisation est complète et fonctionnelle.")
        print("✅ Tous les composants sont correctement organisés")
        print("✅ Tous les imports Python fonctionnent")
        print("✅ La configuration est à jour")
        return True
    
    if errors:
        print(f"❌ {len(errors)} ERREUR(S) CRITIQUE(S) :")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"⚠️ {len(warnings)} AVERTISSEMENT(S) :")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors:
        print("\n✅ Organisation fonctionnelle malgré les avertissements")
        return True
    else:
        print("\n❌ Organisation incomplète - corrections nécessaires")
        return False


def show_usage_instructions():
    """Affiche les instructions d'utilisation"""
    print("\n" + "="*60)
    print("📖 INSTRUCTIONS D'UTILISATION")
    print("="*60)
    
    print("\n🚀 Démarrage du serveur MCP :")
    print("  # Nouveau serveur (recommandé)")
    print("  python start_server.py")
    print()
    print("  # Serveur legacy (compatible)")
    print("  python mcp_real_estate_server.py")
    
    print("\n🛠️ Scripts utilitaires :")
    print("  # Nettoyage du projet")
    print("  python scripts/cleanup_project.py")
    print()
    print("  # Validation de l'organisation")
    print("  python scripts/validate_organization.py")
    print()
    print("  # Test du service dynamique")
    print("  python scripts/test_dynamic_service.py")
    
    print("\n📁 Structure des dossiers :")
    print("  src/          - Code source principal")
    print("  config/       - Configuration MCP")
    print("  scripts/      - Scripts utilitaires")
    print("  docs/         - Documentation")
    print("  logs/         - Fichiers de logs")
    print("  tests/        - Tests unitaires")
    
    print("\n📚 Documentation :")
    print("  README.md                      - Guide principal")
    print("  docs/PROJECT_ORGANIZATION.md   - Organisation détaillée")
    print("  docs/DEVELOPMENT.md            - Guide développeur")


if __name__ == "__main__":
    success = validate_organization()
    show_usage_instructions()
    
    if success:
        print("\n🎯 Le projet MCP Real Estate est parfaitement organisé !")
        sys.exit(0)
    else:
        print("\n⚠️ Des corrections sont nécessaires.")
        sys.exit(1)
