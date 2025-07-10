#!/usr/bin/env python3
"""
Test de l'intégration des fonctionnalités d'investissement dans le MCP principal
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import EnrichedRealEstateMCP, InvestmentProfile

async def test_integrated_mcp():
    """Test complet du MCP intégré avec analyses d'investissement"""
    
    print("=== Test du MCP Real Estate Intégré ===\n")
    
    # Initialisation du MCP
    mcp = EnrichedRealEstateMCP()
    
    # Test 1: Recherche de base
    print("1. Test de recherche de base...")
    try:
        results = await mcp.search_properties(
            location="Paris 11e",
            min_price=200000,
            max_price=500000,
            transaction_type="sale"
        )
        print(f"   ✓ Trouvé {len(results)} biens")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # Test 2: Analyse d'opportunités d'investissement
    print("\n2. Test d'analyse d'opportunités d'investissement...")
    try:
        investment_analysis = await mcp.analyze_investment_opportunity(
            location="Paris 11e",
            min_price=250000,
            max_price=400000,
            investment_profile=InvestmentProfile.BOTH
        )
        
        if "error" in investment_analysis:
            print(f"   ⚠ Aucun bien trouvé: {investment_analysis['error']}")
        else:
            print(f"   ✓ Analysé {investment_analysis['total_opportunities']} opportunités")
            print(f"   ✓ Profil: {investment_analysis['investment_profile']}")
            
            # Afficher le résumé du marché
            market_summary = investment_analysis.get('market_summary', {})
            print(f"   ✓ Prix moyen: {market_summary.get('average_price', 0):,.0f}€")
            
            # Afficher les meilleures opportunités
            top_opportunities = investment_analysis.get('top_opportunities', [])
            if top_opportunities:
                print(f"   ✓ Meilleure opportunité: {top_opportunities[0]['property'].get('title', 'N/A')}")
    
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # Test 3: Comparaison de stratégies (avec bien fictif)
    print("\n3. Test de comparaison de stratégies...")
    try:
        # Bien fictif pour le test
        sample_property = {
            "id": "test-001",
            "title": "Appartement 3 pièces - Test",
            "price": 350000,
            "location": "Paris 11e",
            "surface_area": 65,
            "description": "Appartement à rénover, proche métro",
            "url": "https://example.com/test",
            "coordinates": {"lat": 48.8566, "lng": 2.3522}
        }
        
        comparison = await mcp.compare_investment_strategies(
            location="Paris 11e",
            property_data=sample_property
        )
        
        print(f"   ✓ Analyse locative - Score: {comparison['rental_analysis'].get('rental_score', 0)}")
        print(f"   ✓ Analyse marchand - Score: {comparison['dealer_analysis'].get('dealer_score', 0)}")
        print(f"   ✓ Recommandation: {comparison['comparison']['recommendation']}")
        
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # Test 4: Résumé de marché
    print("\n4. Test de résumé de marché...")
    try:
        summary = await mcp.get_property_summary("Paris 11e")
        print(f"   ✓ Résumé généré pour {summary.get('location', 'N/A')}")
        if 'market_analysis' in summary:
            print(f"   ✓ Analyse de marché incluse")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    print("\n=== Tests terminés ===")

async def test_analyzers_initialization():
    """Test de l'initialisation des analyseurs"""
    
    print("\n=== Test d'initialisation des analyseurs ===")
    
    mcp = EnrichedRealEstateMCP()
    
    # Forcer l'initialisation
    await mcp._ensure_analyzers_initialized()
    
    # Vérifier que les analyseurs sont bien initialisés
    if hasattr(mcp, 'rental_analyzer') and mcp.rental_analyzer:
        print("   ✓ RentalAnalyzer initialisé")
    else:
        print("   ✗ RentalAnalyzer non initialisé")
    
    if hasattr(mcp, 'dealer_analyzer') and mcp.dealer_analyzer:
        print("   ✓ DealerAnalyzer initialisé")
    else:
        print("   ✗ DealerAnalyzer non initialisé")
    
    # Test des données intégrées
    if hasattr(mcp, 'rental_database') and mcp.rental_database:
        print(f"   ✓ Base de données locative: {len(mcp.rental_database)} villes")
    
    if hasattr(mcp, 'renovation_costs') and mcp.renovation_costs:
        print(f"   ✓ Coûts de rénovation: {len(mcp.renovation_costs)} catégories")

def test_data_structures():
    """Test des structures de données intégrées"""
    
    print("\n=== Test des structures de données ===")
    
    mcp = EnrichedRealEstateMCP()
    
    # Test des profils d'investissement
    profiles = list(InvestmentProfile)
    print(f"   ✓ Profils d'investissement: {[p.value for p in profiles]}")
    
    # Test des données de base
    print(f"   ✓ Base de données locative: {len(mcp.rental_database)} entrées")
    print(f"   ✓ Coûts de rénovation: {len(mcp.renovation_costs)} catégories")
    
    # Afficher quelques exemples
    if mcp.rental_database:
        first_city = list(mcp.rental_database.keys())[0]
        print(f"   ✓ Exemple ville: {first_city}")
    
    if mcp.renovation_costs:
        first_category = list(mcp.renovation_costs.keys())[0]
        print(f"   ✓ Exemple rénovation: {first_category}")

async def main():
    """Fonction principale de test"""
    
    print("Démarrage des tests du MCP Real Estate intégré...\n")
    
    # Tests des structures de données
    test_data_structures()
    
    # Tests d'initialisation
    await test_analyzers_initialization()
    
    # Tests fonctionnels
    await test_integrated_mcp()
    
    print("\n✅ Tous les tests sont terminés!")

if __name__ == "__main__":
    asyncio.run(main())
