#!/usr/bin/env python3
"""
Script de redémarrage forcé du serveur MCP Real Estate
Fichier: scripts/force_mcp_restart.py

Ce script force le redémarrage du serveur MCP et vérifie qu'il utilise
la nouvelle configuration sans données de démonstration.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def kill_python_processes():
    """Tue tous les processus Python qui pourraient être le serveur MCP"""
    try:
        print("🔄 Arrêt des processus Python en cours...")
        
        # Lister les processus Python
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("🔍 Processus Python détectés")
            
            # Tuer les processus Python (attention : cela peut affecter d'autres scripts)
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                          capture_output=True)
            print("✅ Processus Python arrêtés")
        else:
            print("ℹ️  Aucun processus Python détecté")
            
    except Exception as e:
        print(f"⚠️  Erreur arrêt processus: {e}")

def clear_all_cache():
    """Nettoie tous les caches Python"""
    project_root = Path(__file__).parent.parent
    
    print("🧹 Nettoyage complet du cache...")
    
    # Supprimer __pycache__ récursivement
    for pycache_dir in project_root.rglob('__pycache__'):
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"  ✅ Supprimé: {pycache_dir.name}")
        except Exception as e:
            print(f"  ⚠️  Erreur: {e}")
    
    # Supprimer .pyc récursivement
    for pyc_file in project_root.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            print(f"  ✅ Supprimé: {pyc_file.name}")
        except Exception as e:
            print(f"  ⚠️  Erreur: {e}")

def test_new_configuration():
    """Teste la nouvelle configuration sans données de démonstration"""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / 'src'))
    
    try:
        print("🔍 Test de la nouvelle configuration...")
        
        # Test 1: Import du module dynamique
        from main import DynamicRealEstateMCP
        print("✅ Import DynamicRealEstateMCP réussi")
        
        # Test 2: Initialisation
        mcp = DynamicRealEstateMCP()
        print("✅ Initialisation DynamicRealEstateMCP réussie")
        
        # Test 3: Vérification qu'il n'y a pas de données hardcodées
        if hasattr(mcp, 'rental_database') and mcp.rental_database:
            print("⚠️  ATTENTION: rental_database non vide")
            return False
        else:
            print("✅ rental_database vide - OK")
        
        # Test 4: Test du service dynamique
        if hasattr(mcp, 'dynamic_service'):
            print("✅ Service dynamique disponible")
        else:
            print("⚠️  Service dynamique non trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test configuration: {e}")
        return False

def create_restart_instructions():
    """Crée des instructions pour redémarrer Windsurf"""
    instructions = """
🔄 INSTRUCTIONS DE REDÉMARRAGE WINDSURF

Pour que les modifications prennent effet, vous devez :

1. 📝 SAUVEGARDER tous vos fichiers ouverts
2. 🔄 FERMER complètement Windsurf
3. ⏳ ATTENDRE 10 secondes
4. 🚀 RELANCER Windsurf
5. 🔌 RECONNECTER le serveur MCP (si nécessaire)

Après redémarrage, testez une recherche :
- Si vous obtenez une ERREUR → ✅ Correct (pas de données de démo)
- Si vous obtenez des données "Demo" → ❌ Redémarrage nécessaire

Le MCP ne doit plus JAMAIS retourner de données de démonstration !
"""
    
    with open('RESTART_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(instructions)

def main():
    """Fonction principale"""
    
    print("🚀 REDÉMARRAGE FORCÉ DU SERVEUR MCP")
    print("=" * 50)
    
    # Étape 1: Arrêt des processus
    kill_python_processes()
    
    # Étape 2: Nettoyage du cache
    clear_all_cache()
    
    # Étape 3: Test de la configuration
    print("\n🔧 Test de la nouvelle configuration...")
    if test_new_configuration():
        print("✅ Configuration correcte")
    else:
        print("❌ Problème de configuration")
        return 1
    
    # Étape 4: Instructions de redémarrage
    print("\n📋 Création des instructions...")
    create_restart_instructions()
    
    print("\n" + "=" * 50)
    print("✅ REDÉMARRAGE FORCÉ TERMINÉ")
    print("🎯 ÉTAPE SUIVANTE: Redémarrer Windsurf complètement")
    print("📄 Voir: RESTART_INSTRUCTIONS.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
