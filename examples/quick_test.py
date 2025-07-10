#!/usr/bin/env python3
"""
Test rapide du MCP spécialisé
"""

import asyncio
import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def quick_test():
    """Test rapide des fonctionnalités"""
    print("🚀 Test rapide MCP spécialisé")
    
    try:
        from specialized_investment_mcp import SpecializedRealEstateMCP, InvestmentProfile
        print("✅ Import réussi")
        
        mcp = SpecializedRealEstateMCP()
        print("✅ Initialisation réussie")
        
        # Test simple
        test_property = {
            'price': 300000,
            'surface_area': 60,
            'location': 'Paris 11e',
            'description': 'Appartement à rénover',
            'property_type': 'Appartement'
        }
        
        print("🔄 Test comparaison...")
        result = await mcp.compare_investment_strategies("Paris 11e", test_property)
        
        if "error" not in result:
            print("✅ Test réussi !")
            rental = result['rental_analysis']
            dealer = result['dealer_analysis']
            print(f"📈 Rendement locatif: {rental['net_yield']:.1f}%")
            print(f"🔨 Marge marchand: {dealer['gross_margin_percent']:.1f}%")
            print(f"💡 Recommandation: {result['comparison']['recommendation']}")
        else:
            print(f"❌ Erreur: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())
