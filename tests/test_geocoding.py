#!/usr/bin/env python3
"""
Test du géocodage - Jour 3-4
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_geocoding_simple():
    """Test simple du géocodage"""
    print("🗺️ Test géocodage simple")
    print("=" * 50)
    
    # Test avec geopy directement
    try:
        from geopy.geocoders import Nominatim
        
        geolocator = Nominatim(user_agent="test-mcp")
        
        # Test avec République
        print("📍 Test: Place de la République, Paris")
        location = geolocator.geocode("Place de la République, Paris")
        
        if location:
            print(f"  ✅ Trouvé: {location.latitude}, {location.longitude}")
            print(f"  📍 Adresse: {location.address}")
        else:
            print("  ❌ Pas trouvé")
            
        # Test avec Paris 11e
        print("\n📍 Test: Paris 11e")
        location = geolocator.geocode("Paris 11e")
        
        if location:
            print(f"  ✅ Trouvé: {location.latitude}, {location.longitude}")
        else:
            print("  ❌ Pas trouvé")
            
    except Exception as e:
        print(f"❌ Erreur géocodage: {e}")
        print("💡 Installez geopy: pip install geopy")
        return False
    
    return True

async def test_api_adresse():
    """Test de l'API Adresse française"""
    print("\n🇫🇷 Test API Adresse française")
    print("=" * 50)
    
    try:
        import httpx
        
        client = httpx.AsyncClient(timeout=10.0)
        
        # Test avec Paris 11e
        print("📍 Test: Paris 11e")
        response = await client.get(
            "https://api-adresse.data.gouv.fr/search/",
            params={'q': 'Paris 11e', 'limit': 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])
            
            if features:
                coords = features[0]['geometry']['coordinates']
                print(f"  ✅ Coordonnées: {coords[1]}, {coords[0]}")
                print(f"  📍 Adresse: {features[0]['properties']['label']}")
            else:
                print("  ❌ Pas de résultat")
        else:
            print(f"  ❌ Erreur API: {response.status_code}")
            
        await client.aclose()
        
    except Exception as e:
        print(f"❌ Erreur API Adresse: {e}")
        return False
    
    return True

async def test_overpass_api():
    """Test de l'API Overpass (OpenStreetMap)"""
    print("\n🗺️ Test API Overpass (transports)")
    print("=" * 50)
    
    try:
        import httpx
        
        client = httpx.AsyncClient(timeout=15.0)
        
        # Coordonnées de République
        lat, lon = 48.8676, 2.3631
        
        # Chercher les stations de métro
        query = f"""
        [out:json][timeout:10];
        (
            node["public_transport"="station"]["station"="subway"](around:500,{lat},{lon});
        );
        out geom;
        """
        
        print("🚇 Recherche stations métro près de République...")
        response = await client.post(
            "https://overpass-api.de/api/interpreter",
            data=query
        )
        
        if response.status_code == 200:
            data = response.json()
            stations = data.get('elements', [])
            
            print(f"  ✅ Trouvé {len(stations)} stations")
            
            for station in stations[:3]:
                name = station.get('tags', {}).get('name', 'Station inconnue')
                print(f"    - {name}")
        else:
            print(f"  ❌ Erreur Overpass: {response.status_code}")
            
        await client.aclose()
        
    except Exception as e:
        print(f"❌ Erreur Overpass: {e}")
        return False
    
    return True

async def test_full_enrichment():
    """Test complet avec l'enrichissement"""
    print("\n🏠 Test avec annonces enrichies")
    print("=" * 50)
    
    try:
        from main import RealEstateMCP
        
        # Test MCP classique
        mcp = RealEstateMCP()
        results = await mcp.search_properties(
            location="Paris 11e",
            min_price=1000,
            max_price=2000,
            transaction_type="rent"
        )
        
        print(f"✅ Annonces trouvées: {len(results)}")
        
        # Vérifier si des coordonnées sont présentes
        with_coords = sum(1 for r in results if r.get('coordinates'))
        print(f"📍 Avec coordonnées: {with_coords}/{len(results)}")
        
        # Exemple d'annonce
        if results:
            example = results[0]
            print(f"\n📋 Exemple d'annonce:")
            print(f"  Titre: {example['title'][:50]}...")
            print(f"  Prix: {example['price']}€")
            print(f"  Localisation: {example['location']}")
            print(f"  Source: {example['source']}")
            
            if example.get('coordinates'):
                coords = example['coordinates']
                print(f"  Coordonnées: {coords['lat']:.4f}, {coords['lon']:.4f}")
            else:
                print("  Coordonnées: Non disponibles")
        
    except Exception as e:
        print(f"❌ Erreur test MCP: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Tests complets géocodage"""
    print("🚀 Tests Géocodage - Jour 3-4")
    print("=" * 60)
    
    tests = [
        ("📍 Géocodage simple", test_geocoding_simple),
        ("🇫🇷 API Adresse française", test_api_adresse),
        ("🗺️ API Overpass", test_overpass_api),
        ("🏠 Enrichissement complet", test_full_enrichment)
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
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 Résumé des tests")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    # Recommandations
    print("\n💡 Recommandations:")
    
    if results.get("📍 Géocodage simple") == "✅":
        print("✅ Géocodage de base fonctionnel")
    else:
        print("❌ Installer geopy: pip install geopy")
    
    if results.get("🇫🇷 API Adresse française") == "✅":
        print("✅ API Adresse française accessible")
    else:
        print("⚠️ API Adresse française inaccessible (vérifiez la connexion)")
    
    if results.get("🗺️ API Overpass") == "✅":
        print("✅ API Overpass fonctionnelle")
    else:
        print("⚠️ API Overpass lente ou inaccessible")
    
    print("\n🚀 Prochaines étapes:")
    print("1. Si tous les tests passent → Intégrer l'enrichissement")
    print("2. Si certains échouent → Utiliser seulement géocodage de base")
    print("3. Passer au jour 5-6 → Déduplication intelligente")

if __name__ == "__main__":
    asyncio.run(main())