#!/usr/bin/env python3
"""
Correction rapide du problème MCP Real Estate
Fichier: quick_fix_mcp.py

PROBLÈME IDENTIFIÉ: Module 'httpx' manquant
SOLUTION: Installation automatique + redémarrage
"""

import sys
import subprocess
import os
from pathlib import Path

def install_httpx():
    """Installe le module httpx manquant"""
    print("🔧 CORRECTION DU PROBLÈME MCP")
    print("=" * 40)
    print("🎯 Problème identifié: Module 'httpx' manquant")
    print("💡 Solution: Installation automatique")
    print()
    
    try:
        print("📥 Installation de httpx...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'httpx'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ httpx installé avec succès")
            return True
        else:
            print(f"❌ Erreur installation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_imports():
    """Teste les imports après installation"""
    print("\n🧪 Test des imports...")
    
    try:
        import httpx
        print("✅ httpx importé")
        
        # Test du service dynamique
        project_root = Path(__file__).parent
        src_path = project_root / 'src'
        
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        
        from dynamic_data_service import DynamicDataService
        print("✅ dynamic_data_service importé")
        
        from main import DynamicRealEstateMCP
        print("✅ DynamicRealEstateMCP importé")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import échoué: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def clear_python_cache():
    """Nettoie le cache Python"""
    print("\n🧹 Nettoyage du cache...")
    
    cache_dirs = []
    for pycache in Path('.').rglob('__pycache__'):
        cache_dirs.append(pycache)
    
    for cache_dir in cache_dirs:
        try:
            import shutil
            shutil.rmtree(cache_dir)
            print(f"   ✅ Supprimé: {cache_dir}")
        except Exception as e:
            print(f"   ⚠️  Erreur: {cache_dir} - {e}")

def create_test_search():
    """Crée un test de recherche simple"""
    print("\n📝 Création d'un test de recherche...")
    
    test_content = '''#!/usr/bin/env python3
"""Test de recherche MCP après correction"""
import sys
import asyncio
from pathlib import Path

# Ajouter le chemin src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_search():
    """Test de recherche Antibes"""
    try:
        from main import DynamicRealEstateMCP
        
        print("🏠 Test de recherche MCP - Antibes")
        print("=" * 30)
        
        mcp = DynamicRealEstateMCP()
        print("✅ MCP initialisé")
        
        # Test recherche studios Antibes
        print("🔍 Recherche studios +30m² Antibes...")
        
        results = await mcp.search_properties_dynamic(
            location="Antibes",
            property_type="studio", 
            min_surface=30,
            transaction_type="sale"
        )
        
        if results and len(results) > 0:
            print(f"✅ Trouvé {len(results)} résultats:")
            for i, prop in enumerate(results[:3]):  # Afficher 3 premiers
                print(f"   {i+1}. {prop.get('title', 'Sans titre')}")
                print(f"      📍 {prop.get('location', 'N/A')}")
                print(f"      💰 {prop.get('price', 'N/A')} €")
                print(f"      📐 {prop.get('surface_area', 'N/A')} m²")
                print()
        else:
            print("⚠️  Aucun résultat trouvé")
            
        # Test données de marché
        print("📊 Test données de marché...")
        market_data = await mcp.get_market_data_dynamic("Antibes", "sale")
        
        if market_data:
            print(f"✅ Prix moyen: {market_data.get('avg_price_sqm', 'N/A')} €/m²")
            print(f"   Source: {market_data.get('source', 'N/A')}")
        else:
            print("⚠️  Données de marché non disponibles")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_search())
    if success:
        print("\\n🎉 Test réussi ! Le MCP fonctionne.")
    else:
        print("\\n❌ Test échoué. Vérifiez la configuration.")
'''

    try:
        with open('test_search_antibes.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("   ✅ Test créé: test_search_antibes.py")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    """Correction principale"""
    # Étape 1: Installer httpx
    if not install_httpx():
        print("\n❌ ÉCHEC: Impossible d'installer httpx")
        print("💡 Solution manuelle:")
        print("   pip install httpx")
        return 1
    
    # Étape 2: Nettoyer le cache
    clear_python_cache()
    
    # Étape 3: Tester les imports
    if not test_imports():
        print("\n❌ ÉCHEC: Imports toujours défaillants")
        return 1
    
    # Étape 4: Créer un test
    create_test_search()
    
    # Instructions finales
    print("\n" + "=" * 50)
    print("✅ CORRECTION TERMINÉE")
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("1. Redémarrer Windsurf complètement")
    print("2. Reconnecter le serveur MCP")
    print("3. Tester: python test_search_antibes.py")
    print("4. Essayer une recherche MCP dans Windsurf")
    print("\n💡 Le serveur MCP devrait maintenant fonctionner !")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())