"""
Démonstration de l'architecture flexible et adaptative.
Montre comment les nouvelles capacités résolvent les problèmes de rigidité.
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Ajout du chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.flexible_models import FlexibleProperty, ContextualMarketAnalyzer
from core.dynamic_responses import ContextualResponseSystem
from core.adaptive_engine import AdaptiveEngine, AdaptationContext
from services.flexible_analysis import FlexibleAnalysisService


async def demo_flexible_property():
    """Démontre la flexibilité des modèles de propriété."""
    print("=== DÉMONSTRATION: Modèles Flexibles ===\n")
    
    # Création d'une propriété avec données minimales
    prop1 = FlexibleProperty(
        id="demo_1",
        price=250000,
        location="Paris 11e"
    )
    
    print("1. Propriété avec données minimales:")
    print(f"   Titre généré: {prop1.get('display_title')}")
    print(f"   Segment de marché: {prop1.get('market_segment')}")
    print(f"   Hiérarchie location: {prop1.get('location_hierarchy')}")
    
    # Enrichissement progressif
    prop1.update(
        surface_area=65,
        rooms=3,
        elevator=True,
        parking=True
    )
    
    print("\n2. Après enrichissement:")
    print(f"   Prix au m²: {prop1.get('price_per_sqm')}€")
    print(f"   Valeur estimée: {prop1.get('estimated_value')}€")
    print(f"   Nouveau segment: {prop1.get('market_segment')}")
    
    # Enrichissement externe
    prop1.enrich_with('transport_api', {
        'metro_distance': 200,
        'transport_score': 9.2
    })
    
    print("\n3. Après enrichissement externe:")
    print(f"   Enrichissements: {[e['enricher'] for e in prop1._metadata['enrichments']]}")
    print(f"   Données complètes: {len(prop1.to_dict())} champs")


async def demo_contextual_analysis():
    """Démontre l'analyse contextuelle adaptative."""
    print("\n=== DÉMONSTRATION: Analyse Contextuelle ===\n")
    
    # Création de propriétés de test
    properties = [
        FlexibleProperty(
            id=f"test_{i}",
            price=200000 + i * 50000,
            location="Lyon",
            surface_area=50 + i * 15,
            rooms=2 + (i % 3),
            property_type="appartement"
        )
        for i in range(10)
    ]
    
    analyzer = ContextualMarketAnalyzer()
    
    # Analyse pour différents contextes
    contexts = [
        {'market_type': 'luxury'},
        {'market_type': 'budget'},
        {'market_type': 'family'},
        {'market_type': 'investment'}
    ]
    
    for context in contexts:
        print(f"Analyse pour contexte: {context['market_type']}")
        
        analysis = await analyzer.analyze(properties, context)
        insights = analyzer.get_insights(analysis)
        
        print(f"   Type d'analyse: {analysis.get('market_type', 'general')}")
        print(f"   Insights générés: {len(insights)}")
        if insights:
            print(f"   Premier insight: {insights[0]}")
        print()


async def demo_dynamic_responses():
    """Démontre le système de réponses dynamiques."""
    print("=== DÉMONSTRATION: Réponses Dynamiques ===\n")
    
    # Données d'analyse simulées
    analysis_data = {
        'total_properties': 25,
        'price_analysis': {
            'mean': 320000,
            'median': 295000,
            'min': 180000,
            'max': 580000,
            'outliers': [580000]
        },
        'insights': [
            'Marché équilibré avec une légère tendance haussière',
            'Forte demande pour les appartements 3 pièces',
            'Prix au m² supérieur à la moyenne régionale'
        ]
    }
    
    response_system = ContextualResponseSystem()
    
    # Différents formats de réponse
    formats = [
        {'format': 'conversational', 'tone': 'casual'},
        {'format': 'technical', 'tone': 'expert'},
        {'format': 'summary', 'tone': 'professional'},
        {'format': 'investment', 'tone': 'expert'}
    ]
    
    for context in formats:
        print(f"Format: {context['format']} | Ton: {context['tone']}")
        
        response = response_system.generate_response(analysis_data, context)
        
        print(f"   Type de réponse: {response.get('type')}")
        
        if 'message' in response:
            print(f"   Message: {response['message'][:100]}...")
        elif 'summary' in response:
            print(f"   Résumé: {response['summary'][:100]}...")
        
        print(f"   Confiance: {response.get('context', {}).get('confidence_level', 'N/A')}")
        print()


async def demo_adaptive_engine():
    """Démontre le moteur d'adaptation."""
    print("=== DÉMONSTRATION: Moteur Adaptatif ===\n")
    
    engine = AdaptiveEngine()
    
    # Contextes utilisateur différents
    contexts = [
        AdaptationContext(
            user_expertise_level='beginner',
            user_preferences={'max_budget': 300000}
        ),
        AdaptationContext(
            user_expertise_level='expert',
            market_conditions={'segment': 'luxury', 'volatility': 'high'},
            temporal_factors={'urgency': 'high'}
        ),
        AdaptationContext(
            geographic_context={'focus_areas': ['Paris 11e', 'Paris 20e']},
            user_preferences={'investment_profile': 'rental_investor'}
        )
    ]
    
    base_data = {
        'properties': [{'id': 'test', 'price': 250000, 'location': 'Paris'}],
        'total_properties': 1,
        'insights': ['Marché stable']
    }
    
    for i, context in enumerate(contexts, 1):
        print(f"Adaptation {i}:")
        print(f"   Expertise: {context.user_expertise_level}")
        print(f"   Préférences: {bool(context.user_preferences)}")
        print(f"   Conditions marché: {bool(context.market_conditions)}")
        
        adapted_data = await engine.adapt_analysis(base_data.copy(), context)
        
        metadata = adapted_data.get('adaptation_metadata', {})
        print(f"   Stratégie utilisée: {metadata.get('strategy_used')}")
        print(f"   Règles appliquées: {len(metadata.get('rules_applied', []))}")
        print()
    
    # Statistiques du moteur
    stats = engine.get_adaptation_stats()
    print(f"Statistiques du moteur:")
    print(f"   Règles actives: {stats['active_rules']}/{stats['total_rules']}")
    print(f"   Historique: {stats['context_history_size']} contextes")


async def demo_complete_workflow():
    """Démontre un workflow complet avec l'architecture flexible."""
    print("=== DÉMONSTRATION: Workflow Complet ===\n")
    
    # Simulation d'une recherche utilisateur
    user_request = {
        'location': 'Lyon',
        'max_price': 400000,
        'min_surface': 60,
        'rooms': 3,
        'user_profile': 'family_buyer',
        'expertise_level': 'intermediate'
    }
    
    print(f"Requête utilisateur: {user_request['location']}, budget {user_request['max_price']}€")
    
    # Simulation de propriétés trouvées
    mock_properties = [
        FlexibleProperty(
            id=f"lyon_{i}",
            price=300000 + i * 25000,
            location="Lyon",
            surface_area=65 + i * 10,
            rooms=3,
            property_type="appartement",
            elevator=i % 2 == 0,
            parking=i % 3 == 0
        )
        for i in range(8)
    ]
    
    # Service d'analyse flexible
    flexible_service = FlexibleAnalysisService()
    
    # Conversion des propriétés (simulation)
    from models.property import PropertyListing
    
    property_listings = []
    for fp in mock_properties:
        listing = PropertyListing(
            id=fp.get('id'),
            title=fp.get('display_title'),
            price=fp.get('price'),
            location=fp.get('location'),
            property_type=fp.get('property_type'),
            surface_area=fp.get('surface_area'),
            rooms=fp.get('rooms'),
            description="",
            source="demo"
        )
        property_listings.append(listing)
    
    # Analyse flexible complète
    context = {
        'user_preferences': {
            'max_budget': user_request['max_price'],
            'focus': 'family'
        },
        'expertise_level': user_request['expertise_level']
    }
    
    result = await flexible_service.analyze_market_flexible(
        property_listings,
        user_request['location'],
        context
    )
    
    print(f"\nRésultats de l'analyse flexible:")
    print(f"   Type de réponse: {result.get('type')}")
    print(f"   Propriétés analysées: {result.get('total_properties', 0)}")
    
    if 'message' in result:
        print(f"   Message: {result['message']}")
    
    if 'key_points' in result:
        print(f"   Points clés: {len(result['key_points'])}")
        for point in result['key_points'][:2]:
            print(f"     - {point}")
    
    if 'context' in result:
        confidence = result['context'].get('confidence_level', 0)
        print(f"   Niveau de confiance: {confidence:.2f}")


async def main():
    """Fonction principale de démonstration."""
    print("🏠 DÉMONSTRATION DE L'ARCHITECTURE FLEXIBLE")
    print("=" * 50)
    print("Résolution des problèmes de rigidité identifiés:\n")
    print("✅ Structures flexibles remplacent les classes rigides")
    print("✅ Logique adaptative remplace les calculs mécaniques") 
    print("✅ Réponses dynamiques remplacent les formats fixes")
    print("✅ Adaptation contextuelle remplace les données hardcodées")
    print("\n" + "=" * 50 + "\n")
    
    try:
        await demo_flexible_property()
        await demo_contextual_analysis()
        await demo_dynamic_responses()
        await demo_adaptive_engine()
        await demo_complete_workflow()
        
        print("\n" + "=" * 50)
        print("✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
        print("L'architecture flexible résout tous les problèmes identifiés!")
        
    except Exception as e:
        print(f"\n❌ Erreur durant la démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
