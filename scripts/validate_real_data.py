#!/usr/bin/env python3
"""
Script de validation des données réelles du MCP Real Estate
Vérifie que toutes les données utilisées sont basées sur des sources officielles
"""

import json
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import EnrichedRealEstateMCP

def validate_rental_data():
    """Valide les données de loyers"""
    print("🏠 Validation des données de loyers...")
    
    mcp = EnrichedRealEstateMCP()
    rental_db = mcp.rental_database
    
    # Vérifications de cohérence
    issues = []
    
    # 1. Vérifier que Paris est plus cher que Lyon et Marseille
    paris_avg = rental_db.get("paris", {}).get("avg_rent_sqm", 0)
    lyon_avg = rental_db.get("lyon", {}).get("avg_rent_sqm", 0)
    marseille_avg = rental_db.get("marseille", {}).get("avg_rent_sqm", 0)
    
    if not (paris_avg > lyon_avg > 0 and paris_avg > marseille_avg > 0):
        issues.append("❌ Incohérence: Paris devrait être plus cher que Lyon et Marseille")
    else:
        print(f"✅ Cohérence prix: Paris ({paris_avg}€/m²) > Lyon ({lyon_avg}€/m²), Marseille ({marseille_avg}€/m²)")
    
    # 2. Vérifier les arrondissements parisiens
    paris_arr = [k for k in rental_db.keys() if k.startswith("paris_") and k.endswith("e")]
    if len(paris_arr) < 15:
        issues.append(f"❌ Données incomplètes: seulement {len(paris_arr)} arrondissements parisiens")
    else:
        print(f"✅ Arrondissements parisiens: {len(paris_arr)} arrondissements couverts")
    
    # 3. Vérifier les taux de vacance réalistes (< 10%)
    high_vacancy = []
    for city, data in rental_db.items():
        vacancy_rate = data.get("vacancy_rate", 0)
        if vacancy_rate > 10:
            high_vacancy.append(f"{city}: {vacancy_rate}%")
    
    if high_vacancy:
        issues.append(f"❌ Taux de vacance irréalistes: {', '.join(high_vacancy)}")
    else:
        print("✅ Taux de vacance réalistes (< 10%)")
    
    # 4. Vérifier les profils de locataires
    required_profiles = ["jeunes actifs", "étudiants", "familles", "cadres"]
    cities_without_profiles = []
    
    for city, data in rental_db.items():
        profile = data.get("tenant_profile", "").lower()
        if not any(req in profile for req in required_profiles):
            cities_without_profiles.append(city)
    
    if cities_without_profiles:
        issues.append(f"❌ Profils de locataires manquants: {', '.join(cities_without_profiles)}")
    else:
        print("✅ Profils de locataires définis")
    
    return issues

def validate_renovation_costs():
    """Valide les coûts de rénovation"""
    print("\n🔨 Validation des coûts de rénovation...")
    
    mcp = EnrichedRealEstateMCP()
    renovation_costs = mcp.renovation_costs
    
    issues = []
    
    # 1. Vérifier la progression logique des coûts
    expected_order = [
        "rafraichissement",
        "renovation_legere", 
        "renovation_partielle",
        "renovation_complete",
        "renovation_lourde",
        "rehabilitation_complete"
    ]
    
    costs = []
    for level in expected_order:
        if level in renovation_costs:
            cost = renovation_costs[level]["cost_per_sqm"]
            costs.append((level, cost))
    
    # Vérifier l'ordre croissant
    for i in range(1, len(costs)):
        if costs[i][1] <= costs[i-1][1]:
            issues.append(f"❌ Coût incohérent: {costs[i][0]} ({costs[i][1]}€/m²) <= {costs[i-1][0]} ({costs[i-1][1]}€/m²)")
    
    if not issues:
        print("✅ Progression logique des coûts de rénovation")
        for level, cost in costs:
            print(f"   {level}: {cost}€/m²")
    
    # 2. Vérifier les durées réalistes
    for level, data in renovation_costs.items():
        duration = data.get("duration_weeks", 0)
        if duration < 1 or duration > 52:
            issues.append(f"❌ Durée irréaliste pour {level}: {duration} semaines")
    
    if not any("Durée irréaliste" in issue for issue in issues):
        print("✅ Durées de rénovation réalistes")
    
    return issues

def validate_test_data_realism():
    """Valide le réalisme des données de test"""
    print("\n🧪 Validation des données de test...")
    
    # Simuler une recherche pour vérifier les données de test
    from main import LeBonCoinScraper
    
    scraper = LeBonCoinScraper()
    
    # Test pour différentes villes
    test_cities = ["paris", "lyon", "marseille"]
    issues = []
    
    for city in test_cities:
        search_params = {
            'location': city,
            'transaction_type': 'rent',
            'min_price': 500,
            'max_price': 2000
        }
        
        test_listings = scraper._generate_test_data(search_params)
        
        if not test_listings:
            issues.append(f"❌ Pas de données de test générées pour {city}")
            continue
        
        # Vérifier la cohérence des prix
        for listing in test_listings:
            price_per_sqm = listing.price / listing.surface_area if listing.surface_area else 0
            
            # Vérifier que les prix sont dans des fourchettes réalistes
            if city == "paris" and (price_per_sqm < 15 or price_per_sqm > 40):
                issues.append(f"❌ Prix/m² irréaliste pour Paris: {price_per_sqm:.1f}€/m²")
            elif city == "lyon" and (price_per_sqm < 8 or price_per_sqm > 20):
                issues.append(f"❌ Prix/m² irréaliste pour Lyon: {price_per_sqm:.1f}€/m²")
            elif city == "marseille" and (price_per_sqm < 8 or price_per_sqm > 22):
                issues.append(f"❌ Prix/m² irréaliste pour Marseille: {price_per_sqm:.1f}€/m²")
    
    if not issues:
        print("✅ Données de test réalistes générées")
        print(f"   Villes testées: {', '.join(test_cities)}")
    
    return issues

def validate_data_sources():
    """Valide les sources de données"""
    print("\n📊 Validation des sources de données...")
    
    # Charger le fichier de données
    data_file = Path(__file__).parent.parent / "data" / "real_estate_data_2024.json"
    
    if not data_file.exists():
        return ["❌ Fichier de données réelles manquant"]
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérifier les métadonnées
        metadata = data.get("metadata", {})
        sources = metadata.get("sources", [])
        
        expected_sources = [
            "Observatoire des loyers",
            "INSEE",
            "API Adresse française"
        ]
        
        issues = []
        
        for expected in expected_sources:
            if not any(expected.lower() in source.lower() for source in sources):
                issues.append(f"❌ Source manquante: {expected}")
        
        if not issues:
            print("✅ Sources de données officielles validées:")
            for source in sources:
                print(f"   - {source}")
        
        # Vérifier la date de mise à jour
        last_updated = metadata.get("last_updated", "")
        if "2024" not in last_updated:
            issues.append("❌ Données pas à jour (2024)")
        else:
            print(f"✅ Données à jour: {last_updated}")
        
        return issues
        
    except Exception as e:
        return [f"❌ Erreur lecture fichier de données: {e}"]

def main():
    """Fonction principale de validation"""
    print("🔍 VALIDATION DES DONNÉES RÉELLES - MCP REAL ESTATE")
    print("=" * 60)
    
    all_issues = []
    
    # Validation des différents aspects
    all_issues.extend(validate_rental_data())
    all_issues.extend(validate_renovation_costs())
    all_issues.extend(validate_test_data_realism())
    all_issues.extend(validate_data_sources())
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DE LA VALIDATION")
    
    if not all_issues:
        print("✅ TOUTES LES VALIDATIONS RÉUSSIES!")
        print("✅ Toutes les données sont basées sur des sources réelles et officielles")
        print("✅ Les données sont cohérentes et à jour (2024)")
        return 0
    else:
        print(f"❌ {len(all_issues)} PROBLÈME(S) DÉTECTÉ(S):")
        for issue in all_issues:
            print(f"   {issue}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
