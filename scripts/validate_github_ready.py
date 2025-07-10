#!/usr/bin/env python3
"""
Script de validation pour le déploiement GitHub
Vérifie que tous les fichiers nécessaires sont présents et corrects
"""

import os
import json
from pathlib import Path


def validate_github_readiness():
    """Valide que le projet est prêt pour GitHub"""
    
    project_root = Path(__file__).parent.parent
    print("🔍 Validation pour déploiement GitHub...")
    print(f"📁 Projet: {project_root}")
    
    errors = []
    warnings = []
    
    # Fichiers essentiels pour GitHub
    essential_files = {
        "README.md": "Documentation principale",
        "LICENSE": "Licence du projet", 
        "requirements.txt": "Dépendances Python",
        "install.py": "Script d'installation automatique",
        ".gitignore": "Fichiers à ignorer par Git",
        "start_server.py": "Point d'entrée principal"
    }
    
    print("\n📋 Vérification des fichiers essentiels...")
    
    for file_name, description in essential_files.items():
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} - {description}")
        else:
            errors.append(f"❌ Fichier manquant: {file_name} ({description})")
    
    # Vérification de la structure
    print("\n📁 Vérification de la structure...")
    
    required_dirs = ["src", "config", "scripts", "docs"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ Dossier: {dir_name}/")
        else:
            warnings.append(f"⚠️ Dossier manquant: {dir_name}/")
    
    # Vérification du .gitignore
    print("\n🚫 Vérification du .gitignore...")
    
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        required_patterns = ["venv/", "*.log", ".env", "__pycache__/"]
        for pattern in required_patterns:
            if pattern in gitignore_content:
                print(f"✅ Pattern ignoré: {pattern}")
            else:
                warnings.append(f"⚠️ Pattern manquant dans .gitignore: {pattern}")
    
    # Vérification du requirements.txt
    print("\n📦 Vérification des dépendances...")
    
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            requirements = f.read().strip().split('\n')
        
        essential_deps = ["httpx", "asyncio"]  # Dépendances critiques
        for dep in essential_deps:
            found = any(dep in req for req in requirements if req.strip())
            if found:
                print(f"✅ Dépendance: {dep}")
            else:
                warnings.append(f"⚠️ Dépendance manquante: {dep}")
    
    # Vérification de la configuration MCP
    print("\n⚙️ Vérification de la configuration MCP...")
    
    config_path = project_root / "config" / "mcp-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if config.get("main") == "start_server.py":
                print("✅ Configuration MCP: Point d'entrée correct")
            else:
                warnings.append("⚠️ Configuration MCP: Point d'entrée à vérifier")
                
        except json.JSONDecodeError:
            errors.append("❌ Configuration MCP: JSON invalide")
    
    # Vérification des fichiers sensibles
    print("\n🔒 Vérification des fichiers sensibles...")
    
    sensitive_files = [".env", "venv", "logs", "__pycache__"]
    for file_name in sensitive_files:
        file_path = project_root / file_name
        if file_path.exists():
            warnings.append(f"⚠️ Fichier sensible présent: {file_name} (doit être dans .gitignore)")
        else:
            print(f"✅ Fichier sensible absent: {file_name}")
    
    # Vérification du script d'installation
    print("\n🛠️ Test du script d'installation...")
    
    install_path = project_root / "install.py"
    if install_path.exists():
        try:
            # Test d'import basique
            import subprocess
            result = subprocess.run(
                ["python", "-c", "import install; print('Import OK')"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Script d'installation: Import réussi")
            else:
                warnings.append("⚠️ Script d'installation: Problème d'import")
        except Exception as e:
            warnings.append(f"⚠️ Script d'installation: {e}")
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE VALIDATION GITHUB")
    print("="*60)
    
    if not errors and not warnings:
        print("🎉 PARFAIT ! Projet prêt pour GitHub")
        print("✅ Tous les fichiers essentiels présents")
        print("✅ Structure correcte")
        print("✅ Configuration valide")
        print("✅ Aucun fichier sensible")
        
        print("\n🚀 Prochaines étapes:")
        print("1. git init (si pas déjà fait)")
        print("2. git add .")
        print("3. git commit -m 'Initial commit: MCP Real Estate for Claude Desktop'")
        print("4. Créer le repository sur GitHub")
        print("5. git remote add origin https://github.com/USERNAME/real-estate-mcp.git")
        print("6. git push -u origin main")
        
        return True
    
    if errors:
        print(f"❌ {len(errors)} ERREUR(S) CRITIQUE(S):")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"⚠️ {len(warnings)} AVERTISSEMENT(S):")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors:
        print("\n✅ Projet utilisable malgré les avertissements")
        print("🔧 Corrigez les avertissements pour une version optimale")
        return True
    else:
        print("\n❌ Corrections nécessaires avant déploiement")
        return False


def show_github_instructions():
    """Affiche les instructions pour GitHub"""
    print("\n" + "="*60)
    print("📖 INSTRUCTIONS GITHUB")
    print("="*60)
    
    print("\n🔗 Création du repository:")
    print("1. Aller sur https://github.com")
    print("2. Cliquer 'New repository'")
    print("3. Nom: real-estate-mcp")
    print("4. Description: MCP server for French real estate analysis")
    print("5. Public ou Private selon préférence")
    print("6. NE PAS initialiser avec README")
    
    print("\n💻 Commandes Git:")
    print("git init")
    print("git add .")
    print("git commit -m 'Initial commit: MCP Real Estate for Claude Desktop'")
    print("git branch -M main")
    print("git remote add origin https://github.com/USERNAME/real-estate-mcp.git")
    print("git push -u origin main")
    
    print("\n👥 Instructions utilisateurs:")
    print("git clone https://github.com/USERNAME/real-estate-mcp.git")
    print("cd real-estate-mcp")
    print("python install.py")
    
    print("\n🤖 Configuration Claude Desktop:")
    print("- Copier claude_desktop_config.json généré")
    print("- Ajouter à la configuration Claude Desktop")
    print("- Redémarrer Claude Desktop")


if __name__ == "__main__":
    success = validate_github_readiness()
    show_github_instructions()
    
    if success:
        print("\n🎯 Votre projet MCP Real Estate est prêt pour GitHub ! 🚀")
    else:
        print("\n⚠️ Veuillez corriger les erreurs avant le déploiement.")
