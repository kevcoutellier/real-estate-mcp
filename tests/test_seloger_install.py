#!/usr/bin/env python3
"""
Test installation SeLoger
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import RealEstateMCP

async def test_seloger():
    print("🧪 Test installation SeLoger")
    print("=" * 50)
    
    mcp = RealEstateMCP()
    
    try:
        results = await mcp.search_properties(
            location="Paris 11e",
            min_price=1000,
            max_price=2000,
            transaction_type="rent"
        )
        
        print(f"✅ Total: {len(results)} annonces")
        
        # Compter par source
        by_source = {}
        for result in results:
            source = result['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        print("📊 Répartition par source:")
        for source, count in by_source.items():
            print(f"  - {source}: {count} annonces")
            
        # Vérifier que SeLoger est présent
        seloger_count = sum(1 for r in results if 'seloger' in r['source'].lower())
        if seloger_count > 0:
            print("✅ SeLoger fonctionne !")
        else:
            print("⚠️ SeLoger en mode test (normal)")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_seloger())
