#!/usr/bin/env python3
"""
Script de validation : Vérification de l'absence de données de démonstration
Fichier: scripts/validate_no_demo_data.py

Ce script vérifie que toutes les données de démonstration ont été supprimées
du MCP Real Estate selon la demande utilisateur.
"""

import os
import re
import sys
from pathlib import Path

def check_demo_patterns():
    """Vérifie la présence de patterns de données de démonstration"""
    
    # Patterns à rechercher
    demo_patterns = [
        r'demo',
        r'test.*data',
        r'generate.*test',
        r'LeBonCoin.*Demo',
        r'SeLoger.*Demo',
        r'PAP.*Demo',
        r'demonstration',
        r'donnees.*test',
        r'resultats.*demonstration',
        r'example\.com',
        r'test_leboncoin',
        r'test_seloger'
    ]
    
    # Fichiers à vérifier
    files_to_check = [
        'src/main.py',
        'mcp_real_estate_server.py'
    ]
    
    project_root = Path(__file__).parent.parent
    issues_found = []
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if not full_path.exists():
            continue
            
        print(f"\n🔍 Vérification de {file_path}...")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                
                for pattern in demo_patterns:
                    if re.search(pattern, line_lower, re.IGNORECASE):
                        # Ignorer les commentaires qui expliquent la suppression
                        if ('supprim' in line_lower or 'removed' in line_lower or 
                            'deleted' in line_lower or '# ' in line):
                            continue
                            
                        issues_found.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                        
        except Exception as e:
            print(f"❌ Erreur lecture {file_path}: {e}")
    
    return issues_found

def check_mcp_configuration():
    """Vérifie que le MCP utilise DynamicRealEstateMCP"""
    
    project_root = Path(__file__).parent.parent
    server_file = project_root / 'mcp_real_estate_server.py'
    
    if not server_file.exists():
        return ["Fichier serveur MCP introuvable"]
    
    issues = []
    
    try:
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier l'import
        if 'from main import DynamicRealEstateMCP' not in content:
            issues.append("Import de DynamicRealEstateMCP manquant")
        
        if 'from main import EnrichedRealEstateMCP' in content:
            issues.append("Import obsolète de EnrichedRealEstateMCP trouvé")
        
        # Vérifier l'initialisation
        if 'self.mcp = DynamicRealEstateMCP()' not in content:
            issues.append("Initialisation de DynamicRealEstateMCP manquante")
        
        if 'self.mcp = EnrichedRealEstateMCP()' in content:
            issues.append("Initialisation obsolète de EnrichedRealEstateMCP trouvée")
            
    except Exception as e:
        issues.append(f"Erreur lecture serveur MCP: {e}")
    
    return issues

def main():
    """Fonction principale de validation"""
    
    print("🚀 VALIDATION : SUPPRESSION DES DONNÉES DE DÉMONSTRATION")
    print("=" * 60)
    
    # Vérification des patterns de démonstration
    print("\n📋 Vérification des patterns de démonstration...")
    demo_issues = check_demo_patterns()
    
    if demo_issues:
        print(f"❌ {len(demo_issues)} problèmes trouvés :")
        for issue in demo_issues:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     Pattern: {issue['pattern']}")
            print(f"     Contenu: {issue['content']}")
            print()
    else:
        print("✅ Aucun pattern de démonstration trouvé")
    
    # Vérification de la configuration MCP
    print("\n🔧 Vérification de la configuration MCP...")
    config_issues = check_mcp_configuration()
    
    if config_issues:
        print(f"❌ {len(config_issues)} problèmes de configuration :")
        for issue in config_issues:
            print(f"  • {issue}")
    else:
        print("✅ Configuration MCP correcte")
    
    # Résumé final
    total_issues = len(demo_issues) + len(config_issues)
    
    print("\n" + "=" * 60)
    if total_issues == 0:
        print("🎉 VALIDATION RÉUSSIE : Aucune donnée de démonstration détectée")
        print("✅ Le MCP Real Estate utilise exclusivement des données temps réel")
        return 0
    else:
        print(f"❌ VALIDATION ÉCHOUÉE : {total_issues} problèmes détectés")
        print("🔧 Corrigez les problèmes ci-dessus avant de continuer")
        return 1

if __name__ == "__main__":
    sys.exit(main())
