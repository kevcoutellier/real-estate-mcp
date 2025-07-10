#!/usr/bin/env python3
"""
Test de l'installation actuelle
Créez ce fichier: test_current_install.py
"""
import asyncio
import sys
import os

# Correction du path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_imports():
    """Test des imports"""
    print("📦 Test des imports")
    print("=" * 50)
    
    imports_status = {}
    
    # Test imports de base
    try:
        import httpx
        imports_status['httpx'] = "✅"
    except ImportError:
        imports_status['httpx'] = "❌ pip install httpx"
    
    try:
        from bs4 import BeautifulSoup
        imports_status['beautifulsoup4'] = "✅"
    except ImportError:
        imports_status['beautifulsoup4'] = "❌ pip install beautifulsoup4"
    
    try:
        import geopy
        imports_status['geopy'] = "✅"
    except ImportError:
        imports_status['geopy'] = "❌ pip install geopy"
    
    try:
        from playwright.async_api import async_playwright
        imports_status['playwright'] = "✅"
    except ImportError:
        imports_status['playwright'] = "❌ pip install playwright"
    
    # Affichage
    for lib, status in imports_status.items():
        print(f"  {status} {lib}")
    
    return all("✅" in status for status in imports_status.values())

async def test_main_imports():
    """Test des imports du main.py"""
    print("\n🔧 Test imports main.py")
    print("=" * 50)
    
    try:
        from main import PropertyListing
        print("  ✅ PropertyListing")
    except ImportError as e:
        print(f"  ❌ PropertyListing: {e}")
        return False
    
    try:
        from main import LeBonCoinScraper
        print("  ✅ LeBonCoinScraper")
    except ImportError as e:
        print(f"  ❌ LeBonCoinScraper: {e}")
        return False
    
    try:
        from main import PropertyAggregator
        print("  ✅ PropertyAggregator")
    except ImportError as e:
        print(f"  ❌ PropertyAggregator: {e}")
        return False
    
    try:
        from main import GeocodingService
        print("  ✅ GeocodingService")
    except ImportError as e:
        print(f"  ❌ GeocodingService: {e}")
        return False
    
    try:
        from main import EnrichedRealEstateMCP
        print("  ✅ EnrichedRealEstateMCP")
    except ImportError as e:
        print(f"  ❌ EnrichedRealEstateMCP: {e}")
        print("  💡 Ajoutez la classe RealEstateMCP de base")
        return False
    
    return True

async def test_basic_mcp():
    """Test MCP de base"""
    print("\n🏠 Test MCP de base")
    print("=" * 50)
    
    try:
        from main import RealEstateMCP
        
        mcp = RealEstateMCP()
        print("  ✅ MCP instancié")
        
        # Test recherche simple
        results = await mcp.search_properties(
            location="Paris 11e",
            min_price=1000,
            max_price=2000,
            transaction_type="rent"
        )
        
        print(f"  ✅ Recherche: {len(results)} annonces")
        
        # Vérifier structure
        if results:
            example = results[0]
            required_fields = ['title', 'price', 'location', 'source']
            
            for field in required_fields:
                if field in example:
                    print(f"    ✅ {field}: {example[field]}")
                else:
                    print(f"    ❌ {field}: manquant")
        
        return True
        
    except ImportError:
        print("  ❌ RealEstateMCP non trouvé")
        print("  💡 Ajoutez la classe RealEstateMCP de base")
        return False
    except Exception as e:
        print(f"  ❌ Erreur MCP: {e}")
        return False

async def test_enriched_mcp():
    """Test MCP enrichi"""
    print("\n🗺️ Test MCP enrichi")
    print("=" * 50)
    
    try:
        from main import EnrichedRealEstateMCP
        
        mcp = EnrichedRealEstateMCP()
        print("  ✅ MCP enrichi instancié")
        
        # Test géocodage simple
        geocoding = mcp.aggregator.geocoding_service
        coords = await geocoding.geocode_address("Paris 11e")
        
        if coords:
            print(f"  ✅ Géocodage: {coords['lat']:.4f}, {coords['lon']:.4f}")
        else:
            print("  ⚠️ Géocodage échoué (réseau?)")
        
        # Test recherche enrichie
        results = await mcp.search_properties(
            location="Paris 11e",
            min_price=1000,
            max_price=2000,
            transaction_type="rent"
        )
        
        print(f"  ✅ Recherche enrichie: {len(results)} annonces")
        
        # Vérifier enrichissement
        with_coords = sum(1 for r in results if r.get('coordinates'))
        print(f"  📍 Avec coordonnées: {with_coords}/{len(results)}")
        
        with_neighborhood = sum(1 for r in results if r.get('neighborhood_info'))
        print(f"  🏘️ Avec info quartier: {with_neighborhood}/{len(results)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur MCP enrichi: {e}")
        print("  💡 Mode dégradé possible avec MCP de base")
        return False

async def test_scrapers():
    """Test des scrapers individuels"""
    print("\n🔍 Test des scrapers")
    print("=" * 50)
    
    # Test LeBonCoin
    try:
        from main import LeBonCoinScraper
        
        scraper = LeBonCoinScraper()
        results = await scraper.search({
            'location': 'Paris 11e',
            'min_price': 1000,
            'max_price': 2000,
            'transaction_type': 'rent'
        })
        
        print(f"  ✅ LeBonCoin: {len(results)} annonces")
        
        # Vérifier si ce sont des vraies données ou test
        if results:
            real_data = any('test' not in r.source.lower() for r in results)
            if real_data:
                print("    📡 Données réelles")
            else:
                print("    🧪 Données de test")
        
    except Exception as e:
        print(f"  ❌ LeBonCoin: {e}")
    
    # Test SeLoger (si disponible)
    try:
        from main import SeLogerScraper
        
        scraper = SeLogerScraper()
        results = await scraper.search({
            'location': 'Paris 11e',
            'min_price': 1000,
            'max_price': 2000,
            'transaction_type': 'rent'
        })
        
        print(f"  ✅ SeLoger: {len(results)} annonces")
        
    except ImportError:
        print("  ⚠️ SeLoger: Non disponible")
    except Exception as e:
        print(f"  ❌ SeLoger: {e}")

async def main():
    """Test complet de l'installation"""
    print("🚀 Test Installation MCP Immobilier")
    print("=" * 70)
    
    # Tests séquentiels
    tests = [
        ("📦 Imports système", test_imports),
        ("🔧 Imports main.py", test_main_imports),
        ("🏠 MCP de base", test_basic_mcp),
        ("🗺️ MCP enrichi", test_enriched_mcp),
        ("🔍 Scrapers", test_scrapers)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 50)
        
        try:
            success = await test_func()
            results[test_name] = "✅" if success else "❌"
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results[test_name] = "❌"
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 Résumé des tests")
    print("=" * 70)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    # Diagnostic et recommandations
    success_count = sum(1 for r in results.values() if r == "✅")
    total_tests = len(results)
    
    print(f"\n🎯 Score: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("\n🎉 Installation parfaite !")
        print("✅ Votre MCP est prêt à utiliser")
        print("\n🚀 Commandes de test:")
        print("  python test_current_install.py")
        print("  python -c 'import asyncio; from src.main import EnrichedRealEstateMCP; asyncio.run(EnrichedRealEstateMCP().search_properties(\"Paris 11e\", min_price=1000, max_price=2000))'")
        
    elif success_count >= 3:
        print("\n✅ Installation fonctionnelle !")
        print("⚠️ Quelques fonctionnalités manquent")
        print("\n🔧 Actions recommandées:")
        
        if results.get("🏠 MCP de base") == "❌":
            print("1. Ajoutez la classe RealEstateMCP de base")
        if results.get("🗺️ MCP enrichi") == "❌":
            print("2. Vérifiez les imports geopy/playwright")
        
        print("\n💡 Vous pouvez utiliser le MCP en mode basique")
        
    else:
        print("\n❌ Installation incomplète")
        print("\n🔧 Actions nécessaires:")
        
        if results.get("📦 Imports système") == "❌":
            print("1. Installez les dépendances manquantes")
        if results.get("🔧 Imports main.py") == "❌":
            print("2. Vérifiez la structure de main.py")
            
        print("\n📖 Consultez le guide d'installation")

if __name__ == "__main__":
    asyncio.run(main())
    