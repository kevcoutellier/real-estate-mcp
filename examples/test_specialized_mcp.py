#!/usr/bin/env python3
"""
Test du MCP spécialisé pour investissement locatif et marchand de biens
"""

import asyncio
import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specialized_investment_mcp import SpecializedRealEstateMCP, InvestmentProfile

async def test_specialized_mcp():
    """Test du MCP spécialisé"""
    print("🎯 Test MCP Spécialisé - Investissement & Marchand de Biens")
    print("=" * 70)
    
    # Initialisation
    try:
        mcp = SpecializedRealEstateMCP()
        print("✅ MCP spécialisé initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return
    
    # Test analyse d'opportunités locatives
    print("\n🏠 Test analyse investissement locatif...")
    try:
        rental_results = await mcp.analyze_investment_opportunity(
            location="Paris 11e",
            min_price=200000,
            max_price=400000,
            investment_profile=InvestmentProfile.RENTAL_INVESTOR
        )
        
        if "error" not in rental_results:
            print(f"✅ {rental_results['total_opportunities']} opportunités locatives analysées")
            
            # Affichage du résumé marché
            market = rental_results.get('market_summary', {}).get('rental_market', {})
            if market:
                print(f"   📊 Rendement net moyen: {market.get('average_net_yield', 0)}%")
                print(f"   🎯 Bonnes opportunités: {market.get('opportunities_count', 0)}")
            
            # Meilleure opportunité
            top_opportunity = rental_results.get('top_opportunities', [])
            if top_opportunity:
                top = top_opportunity[0]
                rental_analysis = top['analyses'].get('rental', {})
                if rental_analysis and 'error' not in rental_analysis:
                    print(f"   🏆 Meilleur rendement: {rental_analysis.get('net_yield', 0)}%")
                    print(f"   💰 Cash-flow: {rental_analysis.get('cash_flow', 0)}€/mois")
                    print(f"   📈 Score investissement: {rental_analysis.get('investment_score', 0)}/100")
        else:
            print(f"⚠️ {rental_results['error']}")
        
    except Exception as e:
        print(f"❌ Erreur test locatif: {e}")
    
    # Test analyse marchand de biens
    print("\n🔨 Test analyse marchand de biens...")
    try:
        dealer_results = await mcp.analyze_investment_opportunity(
            location="Paris 11e",
            min_price=150000,
            max_price=350000,
            investment_profile=InvestmentProfile.PROPERTY_DEALER
        )
        
        if "error" not in dealer_results:
            print(f"✅ {dealer_results['total_opportunities']} opportunités marchand analysées")
            
            # Affichage du résumé marché
            market = dealer_results.get('market_summary', {}).get('dealer_market', {})
            if market:
                print(f"   📊 Marge brute moyenne: {market.get('average_gross_margin', 0)}%")
                print(f"   🎯 Bonnes opportunités: {market.get('opportunities_count', 0)}")
            
            # Meilleure opportunité
            top_opportunity = dealer_results.get('top_opportunities', [])
            if top_opportunity:
                top = top_opportunity[0]
                dealer_analysis = top['analyses'].get('dealer', {})
                if dealer_analysis and 'error' not in dealer_analysis:
                    print(f"   🏆 Meilleure marge: {dealer_analysis.get('gross_margin_percent', 0)}%")
                    print(f"   💰 Gain net: {dealer_analysis.get('net_margin', 0):,.0f}€")
                    print(f"   ⏱️ Durée projet: {dealer_analysis.get('renovation_duration', 0)} semaines + {dealer_analysis.get('estimated_sale_duration', 0)} mois")
                    print(f"   🎯 Score dealer: {dealer_analysis.get('dealer_score', 0)}/100")
        else:
            print(f"⚠️ {dealer_results['error']}")
            
    except Exception as e:
        print(f"❌ Erreur test marchand: {e}")
    
    # Test comparaison des stratégies
    print("\n⚖️ Test comparaison des stratégies...")
    try:
        # Simuler un bien pour la comparaison
        test_property = {
            'id': 'test_123',
            'title': 'Appartement 3 pièces à rénover',
            'price': 280000,
            'location': 'Paris 11e',
            'surface_area': 65,
            'rooms': 3,
            'description': 'Appartement à rénover avec potentiel',
            'property_type': 'Appartement'
        }
        
        comparison = await mcp.compare_investment_strategies("Paris 11e", test_property)
        
        if "error" not in comparison:
            print("✅ Comparaison des stratégies réalisée")
            
            comp_data = comparison.get('comparison', {})
            print(f"   🏠 Rendement locatif annuel: {comp_data.get('rental_annual_return', 0):.1f}%")
            print(f"   🔨 Rendement marchand annuel: {comp_data.get('dealer_annual_return', 0):.1f}%")
            print(f"   💡 Recommandation: {comp_data.get('recommendation', 'Non disponible')}")
        else:
            print(f"⚠️ Erreur comparaison: {comparison.get('error', 'Inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur test comparaison: {e}")
    
    print("\n🎯 Tests terminés !")
    print("\n🚀 Fonctionnalités disponibles:")
    print("   • Analyse d'investissement locatif avec calculs de rentabilité")
    print("   • Analyse d'opportunités marchand de biens avec estimation travaux")
    print("   • Comparaison des stratégies d'investissement")
    print("   • Scores et recommandations personnalisés")
    print("   • Résumés de marché par zone géographique")

async def demo_detailed_analysis():
    """Démonstration d'une analyse détaillée"""
    print("\n" + "="*70)
    print("📊 DÉMONSTRATION - Analyse détaillée d'un bien")
    print("="*70)
    
    # Bien d'exemple
    demo_property = {
        'id': 'demo_456',
        'title': 'Appartement 2 pièces - Bon potentiel locatif',
        'price': 320000,
        'location': 'Paris 20e',
        'surface_area': 45,
        'rooms': 2,
        'description': 'Appartement lumineux à rafraîchir, proche métro',
        'property_type': 'Appartement'
    }
    
    print(f"🏠 Bien analysé:")
    print(f"   📍 {demo_property['location']}")
    print(f"   💰 Prix: {demo_property['price']:,}€")
    print(f"   📐 Surface: {demo_property['surface_area']}m²")
    print(f"   🏠 Type: {demo_property['rooms']} pièces")
    
    try:
        mcp = SpecializedRealEstateMCP()
        
        # Analyse complète
        comparison = await mcp.compare_investment_strategies(
            demo_property['location'], 
            demo_property
        )
        
        if "error" not in comparison:
            rental = comparison['rental_analysis']
            dealer = comparison['dealer_analysis']
            
            print(f"\n📈 ANALYSE LOCATIVE:")
            print(f"   💰 Loyer estimé: {rental['estimated_rent']:.0f}€/mois")
            print(f"   📊 Rendement brut: {rental['gross_yield']:.1f}%")
            print(f"   📉 Rendement net: {rental['net_yield']:.1f}%")
            print(f"   💸 Cash-flow: {rental['cash_flow']:.0f}€/mois")
            print(f"   🎯 Score: {rental['investment_score']:.0f}/100")
            
            print(f"\n🔨 ANALYSE MARCHAND DE BIENS:")
            print(f"   🏗️ Coût travaux: {dealer['renovation_cost']:,.0f}€")
            print(f"   ⏱️ Durée travaux: {dealer['renovation_duration']} semaines")
            print(f"   💰 Marge brute: {dealer['gross_margin_percent']:.1f}%")
            print(f"   💸 Gain net: {dealer['net_margin']:,.0f}€")
            print(f"   🎯 Score: {dealer['dealer_score']:.0f}/100")
            
            print(f"\n💡 RECOMMANDATION:")
            print(f"   {comparison['comparison']['recommendation']}")
            
        else:
            print(f"❌ Erreur: {comparison['error']}")
            
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")

if __name__ == "__main__":
    asyncio.run(test_specialized_mcp())
    asyncio.run(demo_detailed_analysis())
