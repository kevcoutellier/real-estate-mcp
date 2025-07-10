import asyncio
import sys
import os
from typing import Dict, Any, Optional

# Ajout du répertoire source au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_enriched() -> None:
    """
    Teste le fonctionnement du MCP enrichi pour la recherche immobilière.
    Vérifie le géocodage et la recherche de propriétés avec enrichissement des données.
    """
    try:
        from main import EnrichedRealEstateMCP
        print('✅ MCP enrichi importé avec succès')
        
        # Initialisation du MCP
        mcp = EnrichedRealEstateMCP()
        print('✅ MCP enrichi correctement instancié')
        
        # Test de géocodage
        test_address = 'Paris 11e'
        print(f'\n🔍 Test de géocodage pour l\'adresse: {test_address}')
        
        geocoding = mcp.aggregator.geocoding_service
        coords = await geocoding.geocode_address(test_address)
        
        if coords and 'lat' in coords and 'lon' in coords:
            print(f'✅ Géocodage réussi: {coords["lat"]:.4f}, {coords["lon"]:.4f}')
        else:
            print('❌ Échec du géocodage: coordonnées non trouvées')
            return
        
        # Test de recherche enrichie
        print('\n🔍 Test de recherche de propriétés...')
        
        search_params = {
            'location': test_address,
            'min_price': 1000,
            'max_price': 2000,
            'transaction_type': 'rent'
        }
        
        results = await mcp.search_properties(**search_params)
        
        if not results:
            print('⚠️ Aucun résultat trouvé pour la recherche')
            return
            
        print(f'✅ {len(results)} annonces trouvées et enrichies')
        
        # Vérification de l'enrichissement
        with_coords = sum(1 for r in results if r.get('coordinates'))
        coord_ratio = (with_coords / len(results)) * 100 if results else 0
        print(f'📍 Taux d\'enrichissement des coordonnées: {with_coords}/{len(results)} ({coord_ratio:.1f}%)')
        
    except ImportError as e:
        print(f'❌ Erreur d\'importation: {e}')
    except Exception as e:
        print(f'❌ Erreur inattendue lors du test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_enriched())