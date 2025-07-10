#!/usr/bin/env python3
"""
Démonstration pratique du MCP spécialisé investissement
Exemples d'utilisation avec le MCP real estate
"""

import asyncio
import sys
import os
import json

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specialized_investment_mcp import SpecializedRealEstateMCP, InvestmentProfile

async def demo_investment_analysis():
    """Démonstration complète des analyses d'investissement"""
    
    print("🏠 DÉMONSTRATION MCP SPÉCIALISÉ INVESTISSEMENT")
    print("=" * 60)
    
    # Initialisation
    mcp = SpecializedRealEstateMCP()
    
    # 1. Analyse d'opportunités locatives Paris 11e
    print("\n🎯 1. ANALYSE INVESTISSEMENT LOCATIF - Paris 11e")
    print("-" * 50)
    
    try:
        rental_analysis = await mcp.analyze_investment_opportunity(
            location="Paris 11e",
            min_price=250000,
            max_price=450000,
            investment_profile=InvestmentProfile.RENTAL_INVESTOR,
            min_surface=40
        )
        
        if "error" not in rental_analysis:
            print(f"✅ {rental_analysis['total_opportunities']} opportunités analysées")
            
            # Résumé du marché
            market = rental_analysis.get('market_summary', {}).get('rental_market', {})
            if market:
                print(f"\n📊 RÉSUMÉ MARCHÉ LOCATIF:")
                print(f"   • Rendement net moyen: {market.get('average_net_yield', 0):.1f}%")
                print(f"   • Score moyen: {market.get('average_investment_score', 0):.1f}/100")
                print(f"   • Bonnes opportunités: {market.get('opportunities_count', 0)}")
            
            # Top 3 opportunités
            top_ops = rental_analysis.get('top_opportunities', [])[:3]
            if top_ops:
                print(f"\n🏆 TOP 3 OPPORTUNITÉS LOCATIVES:")
                for i, opp in enumerate(top_ops, 1):
                    prop = opp['property']
                    rental = opp['analyses'].get('rental', {})
                    if 'error' not in rental:
                        print(f"\n   {i}. {prop.get('title', 'N/A')[:50]}...")
                        print(f"      💰 Prix: {prop.get('price', 0):,.0f}€ | Surface: {prop.get('surface_area', 0)}m²")
                        print(f"      📈 Rendement net: {rental.get('net_yield', 0):.1f}%")
                        print(f"      💸 Cash-flow: {rental.get('cash_flow', 0):+.0f}€/mois")
                        print(f"      🎯 Score: {rental.get('investment_score', 0):.0f}/100")
        else:
            print(f"❌ Erreur: {rental_analysis['error']}")
            
    except Exception as e:
        print(f"❌ Erreur analyse locative: {e}")
    
    # 2. Analyse marchand de biens Lyon
    print("\n\n🔨 2. ANALYSE MARCHAND DE BIENS - Lyon")
    print("-" * 50)
    
    try:
        dealer_analysis = await mcp.analyze_investment_opportunity(
            location="Lyon",
            min_price=150000,
            max_price=350000,
            investment_profile=InvestmentProfile.PROPERTY_DEALER
        )
        
        if "error" not in dealer_analysis:
            print(f"✅ {dealer_analysis['total_opportunities']} opportunités analysées")
            
            # Résumé du marché
            market = dealer_analysis.get('market_summary', {}).get('dealer_market', {})
            if market:
                print(f"\n📊 RÉSUMÉ MARCHÉ MARCHAND DE BIENS:")
                print(f"   • Marge brute moyenne: {market.get('average_gross_margin', 0):.1f}%")
                print(f"   • Score moyen: {market.get('average_dealer_score', 0):.1f}/100")
                print(f"   • Bonnes opportunités: {market.get('opportunities_count', 0)}")
            
            # Top 3 opportunités
            top_ops = dealer_analysis.get('top_opportunities', [])[:3]
            if top_ops:
                print(f"\n🏆 TOP 3 OPPORTUNITÉS MARCHAND DE BIENS:")
                for i, opp in enumerate(top_ops, 1):
                    prop = opp['property']
                    dealer = opp['analyses'].get('dealer', {})
                    if 'error' not in dealer:
                        print(f"\n   {i}. {prop.get('title', 'N/A')[:50]}...")
                        print(f"      💰 Prix: {prop.get('price', 0):,.0f}€ | Surface: {prop.get('surface_area', 0)}m²")
                        print(f"      🔨 Travaux: {dealer.get('renovation_cost', 0):,.0f}€ ({dealer.get('renovation_duration', 0)} sem)")
                        print(f"      📈 Marge: {dealer.get('gross_margin_percent', 0):.1f}%")
                        print(f"      💸 Gain net: {dealer.get('net_margin', 0):,.0f}€")
                        print(f"      🎯 Score: {dealer.get('dealer_score', 0):.0f}/100")
        else:
            print(f"❌ Erreur: {dealer_analysis['error']}")
            
    except Exception as e:
        print(f"❌ Erreur analyse marchand: {e}")
    
    # 3. Comparaison de stratégies sur un bien spécifique
    print("\n\n⚖️ 3. COMPARAISON STRATÉGIES - Bien spécifique")
    print("-" * 50)
    
    # Bien d'exemple
    test_property = {
        'id': 'demo_123',
        'title': 'Appartement 3P à rénover - Potentiel exceptionnel',
        'price': 320000,
        'location': 'Paris 20e',
        'surface_area': 65,
        'rooms': 3,
        'description': 'Appartement lumineux à rénover entièrement, proche métro, quartier en pleine mutation',
        'property_type': 'Appartement'
    }
    
    print(f"🏠 BIEN ANALYSÉ:")
    print(f"   📍 {test_property['location']}")
    print(f"   💰 Prix: {test_property['price']:,}€")
    print(f"   📐 Surface: {test_property['surface_area']}m² ({test_property['rooms']} pièces)")
    print(f"   📝 {test_property['description'][:60]}...")
    
    try:
        comparison = await mcp.compare_investment_strategies(
            test_property['location'],
            test_property
        )
        
        if "error" not in comparison:
            rental = comparison['rental_analysis']
            dealer = comparison['dealer_analysis']
            comp = comparison['comparison']
            
            print(f"\n📈 ANALYSE LOCATIVE:")
            print(f"   💰 Loyer estimé: {rental['estimated_rent']:.0f}€/mois ({rental['rent_per_sqm']:.1f}€/m²)")
            print(f"   📊 Rendement brut: {rental['gross_yield']:.1f}% | Net: {rental['net_yield']:.1f}%")
            print(f"   💸 Cash-flow: {rental['cash_flow']:+.0f}€/mois")
            print(f"   📈 Plus-value 10 ans: {rental['capital_appreciation']:.1f}%")
            print(f"   🎯 Score investissement: {rental['investment_score']:.0f}/100")
            print(f"   ✅ Points forts: {', '.join(rental['pros'][:2])}")
            if rental['cons']:
                print(f"   ⚠️ Points faibles: {', '.join(rental['cons'][:2])}")
            
            print(f"\n🔨 ANALYSE MARCHAND DE BIENS:")
            print(f"   🏗️ Travaux: {dealer['renovation_cost']:,.0f}€ ({dealer['renovation_duration']} semaines)")
            print(f"   📊 Valeur actuelle: {dealer['market_value_current']:,.0f}€")
            print(f"   📈 Valeur rénovée: {dealer['market_value_renovated']:,.0f}€")
            print(f"   💰 Marge brute: {dealer['gross_margin_percent']:.1f}% ({dealer['gross_margin']:,.0f}€)")
            print(f"   💸 Gain net: {dealer['net_margin']:,.0f}€")
            print(f"   ⏱️ Durée projet: {dealer['renovation_duration']} sem + {dealer['estimated_sale_duration']} mois vente")
            print(f"   🎯 Score dealer: {dealer['dealer_score']:.0f}/100")
            print(f"   🎪 Opportunité: {dealer['opportunity_level']}")
            
            print(f"\n💡 COMPARAISON ET RECOMMANDATION:")
            print(f"   🏠 Rendement locatif annuel: {comp['rental_annual_return']:.1f}%")
            print(f"   🔨 Rendement marchand annuel: {comp['dealer_annual_return']:.1f}%")
            print(f"   🎯 RECOMMANDATION: {comp['recommendation']}")
            
            # Analyse des risques
            risk_comp = comp['risk_comparison']
            print(f"\n⚠️ ANALYSE DES RISQUES:")
            print(f"   🏠 Locatif - Marché: {risk_comp['rental']['market_risk']} | Liquidité: {risk_comp['rental']['liquidity_risk']} | Gestion: {risk_comp['rental']['management_complexity']}")
            print(f"   🔨 Marchand - Marché: {risk_comp['dealer']['market_risk']} | Liquidité: {risk_comp['dealer']['liquidity_risk']} | Gestion: {risk_comp['dealer']['management_complexity']}")
            
        else:
            print(f"❌ Erreur: {comparison['error']}")
            
    except Exception as e:
        print(f"❌ Erreur comparaison: {e}")
    
    # 4. Analyse de marché rapide
    print("\n\n📊 4. ANALYSE DE MARCHÉ - Marseille")
    print("-" * 50)
    
    try:
        # Utilisation du serveur pour l'analyse de marché
        from specialized_mcp_server import SpecializedMCPServer
        server = SpecializedMCPServer()
        
        market_result = await server.handle_get_market_analysis({"location": "Marseille"})
        
        if "error" not in market_result:
            print(f"✅ Analyse de marché réussie pour {market_result['location']}")
            
            market_summary = market_result.get('market_summary', {})
            
            if 'rental_market' in market_summary:
                rental = market_summary['rental_market']
                print(f"\n🏠 MARCHÉ LOCATIF:")
                print(f"   📊 Rendement net moyen: {rental.get('average_net_yield', 0):.1f}%")
                print(f"   🎯 Score moyen: {rental.get('average_investment_score', 0):.1f}/100")
                print(f"   ✅ Bonnes opportunités: {rental.get('opportunities_count', 0)}")
            
            if 'dealer_market' in market_summary:
                dealer = market_summary['dealer_market']
                print(f"\n🔨 MARCHÉ MARCHAND DE BIENS:")
                print(f"   📊 Marge brute moyenne: {dealer.get('average_gross_margin', 0):.1f}%")
                print(f"   🎯 Score moyen: {dealer.get('average_dealer_score', 0):.1f}/100")
                print(f"   ✅ Bonnes opportunités: {dealer.get('opportunities_count', 0)}")
        else:
            print(f"❌ Erreur: {market_result['error']}")
            
    except Exception as e:
        print(f"❌ Erreur analyse marché: {e}")
    
    print("\n\n🎉 DÉMONSTRATION TERMINÉE")
    print("=" * 60)
    print("🚀 Votre MCP spécialisé est opérationnel pour l'analyse d'investissement immobilier !")
    print("\n📋 Fonctionnalités disponibles:")
    print("   • Analyse investissement locatif avec calculs de rentabilité")
    print("   • Analyse marchand de biens avec estimation travaux et marges")
    print("   • Comparaison des stratégies d'investissement")
    print("   • Analyses de marché par zone géographique")
    print("   • Scores et recommandations personnalisés")
    print("   • Gestion des risques et projections")

if __name__ == "__main__":
    asyncio.run(demo_investment_analysis())
