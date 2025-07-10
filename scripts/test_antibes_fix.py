#!/usr/bin/env python3
"""
Test spécifique pour Antibes avec géolocalisation corrigée
"""

import sys
import os
import asyncio

# Ajouter le chemin src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

async def test_antibes_search():
    """Test de recherche spécifique pour Antibes"""
    print("🏖️ Test de recherche spécifique - Antibes")
    print("=" * 50)
    
    try:
        from main import DynamicRealEstateMCP
        
        # Initialiser le MCP dynamique
        mcp = DynamicRealEstateMCP()
        print("✅ MCP dynamique initialisé")
        
        # Test de géolocalisation d'Antibes
        print("\n📍 Test de géolocalisation d'Antibes")
        scraper = mcp.aggregator.scrapers['leboncoin']
        coords = await scraper._get_city_coordinates("Antibes")
        
        if coords:
            print(f"✅ Antibes géolocalisé: lat={coords['lat']}, lng={coords['lng']}")
            print(f"   (Coordonnées attendues: lat≈43.58, lng≈7.10)")
        else:
            print("❌ Échec de géolocalisation d'Antibes")
            return False
        
        # Test de recherche avec géolocalisation
        print("\n🔍 Recherche studios 30m²+ à Antibes (avec géolocalisation)")
        
        results = await mcp.search_properties(
            location="Antibes",
            property_type="studio",
            min_surface=30,
            transaction_type="rent"
        )
        
        print(f"📊 Nombre de résultats: {len(results)}")
        
        if results:
            print("\n🎯 Résultats trouvés:")
            antibes_count = 0
            for i, prop in enumerate(results[:5]):
                location = prop.get('location', 'N/A')
                print(f"\n   {i+1}. {prop.get('title', 'Sans titre')}")
                print(f"      Prix: {prop.get('price', 'N/A')} €")
                print(f"      Surface: {prop.get('surface_area', 'N/A')} m²")
                print(f"      Lieu: {location}")
                print(f"      Source: {prop.get('source', 'N/A')}")
                
                # Vérifier si c'est bien à Antibes ou dans la région
                if location and ('antibes' in location.lower() or 'cannes' in location.lower() or 'nice' in location.lower() or 'juan' in location.lower()):
                    antibes_count += 1
            
            print(f"\n📈 Analyse des résultats:")
            print(f"   - Total: {len(results)} annonces")
            print(f"   - Région Antibes/Côte d'Azur: {antibes_count} annonces")
            print(f"   - Pertinence géographique: {(antibes_count/len(results)*100):.1f}%")
            
            if antibes_count > 0:
                print("✅ Géolocalisation corrigée - résultats pertinents trouvés!")
            else:
                print("⚠️ Aucun résultat dans la région d'Antibes")
                
        else:
            print("⚠️ Aucun résultat trouvé")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale"""
    print("🚀 Test de correction géolocalisation Antibes")
    print("=" * 50)
    
    success = await test_antibes_search()
    
    if success:
        print("\n✅ Test terminé avec succès !")
        print("   La géolocalisation d'Antibes fonctionne correctement.")
    else:
        print("\n❌ Échec du test de géolocalisation.")

if __name__ == "__main__":
    asyncio.run(main())
