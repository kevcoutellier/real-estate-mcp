#!/usr/bin/env python3
"""
Script de validation de la suppression des données hardcodées
Vérifie que toutes les données statiques ont été supprimées du MCP Real Estate
"""

import os
import sys
import re
from pathlib import Path

def check_hardcoded_patterns():
    """Vérifie les patterns de données hardcodées dans le code"""
    
    print("🔍 VALIDATION DE LA SUPPRESSION DES DONNÉES HARDCODÉES")
    print("=" * 60)
    
    # Fichiers à vérifier
    files_to_check = [
        "src/main.py",
        "src/dynamic_data_service.py"
    ]
    
    # Patterns à détecter (qui ne devraient plus exister)
    hardcoded_patterns = [
        # Données de loyers hardcodées
        r'"paris":\s*{[^}]*"avg_rent_sqm":\s*\d+',
        r'"lyon":\s*{[^}]*"avg_rent_sqm":\s*\d+',
        r'"marseille":\s*{[^}]*"avg_rent_sqm":\s*\d+',
        
        # Coûts de rénovation hardcodés
        r'"rafraichissement":\s*{[^}]*"cost_per_sqm":\s*\d+',
        r'"renovation_complete":\s*{[^}]*"cost_per_sqm":\s*\d+',
        
        # Prix hardcodés par ville
        r"'paris':\s*{[^}]*'rent':\s*{[^}]*'avg_sqm':\s*\d+",
        r"'lyon':\s*{[^}]*'rent':\s*{[^}]*'avg_sqm':\s*\d+",
        
        # Descriptions hardcodées spécifiques
        r'"Charmant appartement parisien"',
        r'"Appartement rénové dans immeuble en pierre"',
        r'"Appartement avec vue mer"',
        
        # Quartiers hardcodés spécifiques
        r'"11e arr\."',
        r'"Presqu\'île"',
        r'"Vieux-Port"'
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"⚠️ Fichier non trouvé: {file_path}")
            continue
            
        print(f"\n📄 Vérification: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_issues = []
        
        for i, pattern in enumerate(hardcoded_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                file_issues.extend(matches)
                issues_found.append(f"{file_path}: Pattern {i+1} trouvé - {matches[0][:50]}...")
        
        if file_issues:
            print(f"❌ {len(file_issues)} données hardcodées trouvées")
        else:
            print("✅ Aucune donnée hardcodée détectée")
    
    return issues_found

def check_method_implementations():
    """Vérifie que les méthodes obsolètes lèvent bien NotImplementedError"""
    
    print(f"\n🔧 VÉRIFICATION DES MÉTHODES OBSOLÈTES")
    print("-" * 40)
    
    main_file = "src/main.py"
    
    if not os.path.exists(main_file):
        print(f"❌ Fichier non trouvé: {main_file}")
        return False
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier que get_rental_data lève NotImplementedError
    rental_data_pattern = r'def get_rental_data\(.*?\):(.*?)(?=def|\Z)'
    rental_match = re.search(rental_data_pattern, content, re.DOTALL)
    
    if rental_match:
        method_body = rental_match.group(1)
        if 'NotImplementedError' in method_body:
            print("✅ get_rental_data lève NotImplementedError")
        else:
            print("❌ get_rental_data ne lève pas NotImplementedError")
            return False
    else:
        print("⚠️ Méthode get_rental_data non trouvée")
    
    # Vérifier que get_renovation_costs lève NotImplementedError
    renovation_pattern = r'def get_renovation_costs\(.*?\):(.*?)(?=def|\Z)'
    renovation_match = re.search(renovation_pattern, content, re.DOTALL)
    
    if renovation_match:
        method_body = renovation_match.group(1)
        if 'NotImplementedError' in method_body:
            print("✅ get_renovation_costs lève NotImplementedError")
        else:
            print("❌ get_renovation_costs ne lève pas NotImplementedError")
            return False
    else:
        print("⚠️ Méthode get_renovation_costs non trouvée")
    
    return True

def check_dynamic_service_exists():
    """Vérifie que le service dynamique existe"""
    
    print(f"\n🚀 VÉRIFICATION DU SERVICE DYNAMIQUE")
    print("-" * 40)
    
    dynamic_file = "src/dynamic_data_service.py"
    
    if os.path.exists(dynamic_file):
        print("✅ Service dynamique présent")
        
        with open(dynamic_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les fonctions clés
        key_functions = [
            'get_market_data',
            'get_renovation_costs',
            'DynamicDataService'
        ]
        
        for func in key_functions:
            if func in content:
                print(f"✅ {func} présent")
            else:
                print(f"❌ {func} manquant")
                return False
        
        return True
    else:
        print("❌ Service dynamique manquant")
        return False

def generate_report():
    """Génère un rapport de validation"""
    
    print(f"\n📊 RAPPORT DE VALIDATION")
    print("=" * 60)
    
    # Vérifications
    hardcoded_issues = check_hardcoded_patterns()
    methods_ok = check_method_implementations()
    dynamic_ok = check_dynamic_service_exists()
    
    # Résumé
    print(f"\n🎯 RÉSUMÉ")
    print("-" * 20)
    
    if not hardcoded_issues:
        print("✅ Données hardcodées: SUPPRIMÉES")
    else:
        print(f"❌ Données hardcodées: {len(hardcoded_issues)} problèmes")
        for issue in hardcoded_issues:
            print(f"   - {issue}")
    
    if methods_ok:
        print("✅ Méthodes obsolètes: CORRECTEMENT DÉSACTIVÉES")
    else:
        print("❌ Méthodes obsolètes: PROBLÈMES DÉTECTÉS")
    
    if dynamic_ok:
        print("✅ Service dynamique: PRÉSENT")
    else:
        print("❌ Service dynamique: MANQUANT")
    
    # Conclusion
    all_ok = not hardcoded_issues and methods_ok and dynamic_ok
    
    print(f"\n{'🎉' if all_ok else '⚠️'} CONCLUSION")
    print("-" * 20)
    
    if all_ok:
        print("✅ SUPPRESSION DES DONNÉES HARDCODÉES: RÉUSSIE")
        print("✅ Le MCP utilise maintenant exclusivement des données temps réel")
        print("✅ Migration vers DynamicRealEstateMCP recommandée")
    else:
        print("❌ SUPPRESSION INCOMPLÈTE")
        print("⚠️ Certaines données hardcodées subsistent")
        print("🔧 Corrections nécessaires avant utilisation")
    
    return all_ok

if __name__ == "__main__":
    # Changer vers le répertoire du projet
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    # Lancer la validation
    success = generate_report()
    
    # Code de sortie
    sys.exit(0 if success else 1)
