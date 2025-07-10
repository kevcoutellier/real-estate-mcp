#!/usr/bin/env python3
"""
Script d'installation automatique pour MCP Real Estate
Configure l'environnement virtuel et les dépendances pour Claude Desktop
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, cwd=None, shell=True):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def create_virtual_environment(project_root):
    """Crée l'environnement virtuel"""
    print("🐍 Création de l'environnement virtuel...")
    
    venv_path = project_root / "venv"
    
    if venv_path.exists():
        print("✅ Environnement virtuel déjà existant")
        return True
    
    # Créer l'environnement virtuel
    success, stdout, stderr = run_command([sys.executable, "-m", "venv", "venv"], cwd=project_root)
    
    if success:
        print("✅ Environnement virtuel créé avec succès")
        return True
    else:
        print(f"❌ Erreur lors de la création de l'environnement virtuel: {stderr}")
        return False


def install_dependencies(project_root):
    """Installe les dépendances dans l'environnement virtuel"""
    print("📦 Installation des dépendances...")
    
    # Déterminer le chemin vers pip dans l'environnement virtuel
    if platform.system() == "Windows":
        pip_path = project_root / "venv" / "Scripts" / "pip.exe"
        python_path = project_root / "venv" / "Scripts" / "python.exe"
    else:
        pip_path = project_root / "venv" / "bin" / "pip"
        python_path = project_root / "venv" / "bin" / "python"
    
    if not pip_path.exists():
        print(f"❌ pip introuvable: {pip_path}")
        return False
    
    # Mettre à jour pip
    success, stdout, stderr = run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], cwd=project_root)
    if not success:
        print(f"⚠️ Avertissement lors de la mise à jour de pip: {stderr}")
    
    # Installer les dépendances
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        success, stdout, stderr = run_command([str(pip_path), "install", "-r", "requirements.txt"], cwd=project_root)
        if success:
            print("✅ Dépendances installées avec succès")
            return True
        else:
            print(f"❌ Erreur lors de l'installation des dépendances: {stderr}")
            return False
    else:
        print("⚠️ Fichier requirements.txt introuvable")
        return False


def create_claude_config(project_root):
    """Crée la configuration pour Claude Desktop"""
    print("🤖 Configuration pour Claude Desktop...")
    
    # Déterminer le chemin vers python dans l'environnement virtuel
    if platform.system() == "Windows":
        python_path = project_root / "venv" / "Scripts" / "python.exe"
    else:
        python_path = project_root / "venv" / "bin" / "python"
    
    # Configuration MCP pour Claude Desktop avec environnement virtuel garanti
    claude_config = {
        "mcpServers": {
            "real-estate-mcp": {
                "command": str(python_path),
                "args": [str(project_root / "mcp_wrapper.py")],
                "cwd": str(project_root),
                "env": {
                    "PYTHONPATH": str(project_root / "src"),
                    "VIRTUAL_ENV": str(project_root / "venv")
                }
            }
        }
    }
    
    # Sauvegarder la configuration
    config_file = project_root / "claude_desktop_config.json"
    
    import json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(claude_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration Claude Desktop créée: {config_file}")
    return True


def create_startup_scripts(project_root):
    """Crée les scripts de démarrage pour différents OS"""
    print("📜 Création des scripts de démarrage...")
    
    # Script Windows
    if platform.system() == "Windows":
        bat_content = f"""@echo off
cd /d "{project_root}"
call venv\\Scripts\\activate.bat
python start_server.py
pause
"""
        with open(project_root / "start_mcp.bat", 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print("✅ Script Windows créé: start_mcp.bat")
    
    # Script Unix/Linux/Mac
    sh_content = f"""#!/bin/bash
cd "{project_root}"
source venv/bin/activate
python start_server.py
"""
    with open(project_root / "start_mcp.sh", 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # Rendre le script exécutable sur Unix
    if platform.system() != "Windows":
        os.chmod(project_root / "start_mcp.sh", 0o755)
        print("✅ Script Unix créé: start_mcp.sh")
    
    return True


def test_installation(project_root):
    """Teste l'installation"""
    print("🧪 Test de l'installation...")
    
    # Déterminer le chemin vers python dans l'environnement virtuel
    if platform.system() == "Windows":
        python_path = project_root / "venv" / "Scripts" / "python.exe"
    else:
        python_path = project_root / "venv" / "bin" / "python"
    
    # Test d'import
    test_command = [
        str(python_path), "-c",
        "import sys; sys.path.insert(0, 'src'); from mcp_server import MCPRealEstateServer; print('✅ Import réussi')"
    ]
    
    success, stdout, stderr = run_command(test_command, cwd=project_root)
    
    if success:
        print("✅ Test d'installation réussi")
        return True
    else:
        print(f"❌ Test d'installation échoué: {stderr}")
        return False


def main():
    """Fonction principale d'installation"""
    print("🚀 INSTALLATION MCP REAL ESTATE POUR CLAUDE DESKTOP")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    print(f"📁 Dossier du projet: {project_root}")
    
    steps = [
        ("Environnement virtuel", lambda: create_virtual_environment(project_root)),
        ("Dépendances", lambda: install_dependencies(project_root)),
        ("Configuration Claude", lambda: create_claude_config(project_root)),
        ("Scripts de démarrage", lambda: create_startup_scripts(project_root)),
        ("Test installation", lambda: test_installation(project_root))
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\n📋 Étape: {step_name}")
        print("-" * 30)
        
        if step_func():
            success_count += 1
        else:
            print(f"❌ Échec de l'étape: {step_name}")
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE L'INSTALLATION")
    print("=" * 60)
    
    if success_count == len(steps):
        print("🎉 INSTALLATION RÉUSSIE !")
        print("\n📖 Instructions pour Claude Desktop:")
        print(f"1. Copiez le contenu de 'claude_desktop_config.json'")
        print(f"2. Ajoutez-le à votre configuration Claude Desktop")
        print(f"3. Redémarrez Claude Desktop")
        print(f"4. Le MCP 'real-estate-mcp' sera disponible")
        
        print("\n🚀 Test manuel:")
        if platform.system() == "Windows":
            print(f"   Double-cliquez sur 'start_mcp.bat'")
        else:
            print(f"   Exécutez './start_mcp.sh'")
        
        print("\n🔗 Configuration GitHub:")
        print("   Le projet est prêt pour être poussé sur GitHub")
        print("   Les utilisateurs pourront cloner et installer avec 'python install.py'")
        
    else:
        print(f"⚠️ Installation partielle: {success_count}/{len(steps)} étapes réussies")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez l'installation")
    
    return success_count == len(steps)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
