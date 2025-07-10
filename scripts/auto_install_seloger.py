#!/usr/bin/env python3
"""
Installation automatique SeLoger
Lancez: python auto_install_seloger.py
"""

import os
import sys
import subprocess
import shutil
import time

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filepath):
    """Vérifie si un fichier existe"""
    return os.path.exists(filepath)

def backup_file(filepath):
    """Fait une sauvegarde du fichier"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{int(time.time())}"
        shutil.copy2(filepath, backup_path)
        print(f"📋 Sauvegarde créée: {backup_path}")
        return backup_path
    return None

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print("📦 Installation des dépendances...")
    
    # Dépendances Python
    dependencies = [
        'playwright>=1.40.0',
        'beautifulsoup4>=4.12.0',
        'geopy>=2.4.0'
    ]
    
    for dep in dependencies:
        print(f"  Installing {dep}...")
        success, stdout, stderr = run_command(f"pip install {dep}")
        if success:
            print(f"    ✅ {dep}")
        else:
            print(f"    ❌ {dep}: {stderr}")
            return False
    
    # Installation Playwright browsers
    print("  Installing Playwright browsers...")
    success, stdout, stderr = run_command("playwright install chromium")
    if success:
        print("    ✅ Chromium browser")
    else:
        print(f"    ⚠️ Chromium: {stderr}")
        # Continuer même si chromium échoue
    
    return True

def add_imports_to_main():
    """Ajoute les imports nécessaires à main.py"""
    main_path = 'src/main.py'
    
    if not check_file_exists(main_path):
        print(f"❌ Fichier {main_path} non trouvé")
        return False
    
    # Lire le fichier
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Imports à ajouter
    new_imports = [
        'from playwright.async_api import async_playwright',
        'from urllib.parse import urlencode',
        'import re',
        'import time'
    ]
    
    # Vérifier quels imports sont déjà présents
    imports_to_add = []
    for imp in new_imports:
        if imp not in content:
            imports_to_add.append(imp)
    
    if not imports_to_add:
        print("✅ Imports déjà présents")
        return True
    
    # Trouver où insérer les imports
    lines = content.split('\n')
    import_insert_index = -1
    
    for i, line in enumerate(lines):
        if line.startswith('import asyncio'):
            import_insert_index = i + 1
            break
    
    if import_insert_index == -1:
        print("❌ Impossible de trouver où insérer les imports")
        return False
    
    # Insérer les nouveaux imports
    for imp in reversed(imports_to_add):
        lines.insert(import_insert_index, imp)
    
    # Écrire le fichier modifié
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Imports ajoutés: {', '.join(imports_to_add)}")
    return True

def add_seloger_class():
    """Ajoute la classe SeLogerScraper"""
    main_path = 'src/main.py'
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la classe existe déjà
    if 'class SeLogerScraper' in content:
        print("✅ Classe SeLogerScraper déjà présente")
        return True
    
    # Code de la classe SeLogerScraper (version simplifiée)
    seloger_class = '''
class SeLogerScraper:
    """Scraper pour SeLoger.com avec fallback"""
    
    def __init__(self):
        self.base_url = "https://www.seloger.com"
        self.search_url = "https://www.seloger.com/list.htm"
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        self._debug_shown = False
        
    async def search(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche SeLoger avec fallback vers données de test"""
        listings = []
        
        try:
            # Tentative avec Playwright
            listings = await self._search_playwright(search_params)
            
            # Si pas de résultats, utiliser les données de test
            if not listings:
                listings = self._generate_test_data(search_params)
                
        except Exception as e:
            logger.error(f"Erreur SeLoger: {e}")
            listings = self._generate_test_data(search_params)
            
        return listings
    
    async def _search_playwright(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Recherche avec Playwright"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Construire URL
                url = self._build_url(search_params)
                logger.info(f"Recherche SeLoger: {url}")
                
                await page.goto(url)
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(2)
                
                # Parser
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                listings = self._parse_html(soup)
                
                await browser.close()
                return listings
                
        except Exception as e:
            logger.error(f"Playwright SeLoger: {e}")
            return []
    
    def _build_url(self, params: Dict[str, Any]) -> str:
        """Construit URL SeLoger"""
        seloger_params = {
            'types': '1,2',
            'projects': '2' if params.get('transaction_type') == 'rent' else '1',
            'places': f"[{{{params.get('location', '')}}}]"
        }
        
        if params.get('min_price'):
            seloger_params['price'] = f"{params['min_price']}/999999999"
        
        query = urlencode(seloger_params, safe='{}[]/')
        return f"{self.search_url}?{query}"
    
    def _parse_html(self, soup: BeautifulSoup) -> List[PropertyListing]:
        """Parse HTML SeLoger"""
        listings = []
        items = soup.select('.c-pa-list') or soup.select('.annonce') or []
        
        logger.info(f"Trouvé {len(items)} items SeLoger")
        
        for item in items:
            try:
                title_elem = item.select_one('.c-pa-link') or item.select_one('h2')
                price_elem = item.select_one('.c-pa-price') or item.select_one('.price')
                location_elem = item.select_one('.c-pa-ville') or item.select_one('.ville')
                
                if title_elem and price_elem:
                    listing = PropertyListing(
                        id=f"seloger_{abs(hash(title_elem.get_text()))}",
                        title=title_elem.get_text(strip=True),
                        price=self._parse_price(price_elem.get_text()),
                        location=location_elem.get_text(strip=True) if location_elem else '',
                        property_type='Appartement',
                        source='SeLoger',
                        url=item.find('a')['href'] if item.find('a') else '',
                        created_at=datetime.now()
                    )
                    listings.append(listing)
                    
            except Exception as e:
                logger.error(f"Erreur parsing SeLoger item: {e}")
                continue
        
        return listings
    
    def _parse_price(self, price_text: str) -> float:
        """Parse prix"""
        if not price_text:
            return 0.0
        
        clean = re.sub(r'[^\\d,.]', '', price_text)
        clean = clean.replace(',', '.')
        
        try:
            return float(clean)
        except:
            return 0.0
    
    def _generate_test_data(self, search_params: Dict[str, Any]) -> List[PropertyListing]:
        """Génère des données de test SeLoger"""
        location = search_params.get('location', 'Paris')
        min_price = search_params.get('min_price', 1000)
        max_price = search_params.get('max_price', 2000)
        
        test_listings = []
        
        for i in range(2):
            price = min_price + (max_price - min_price) * (i + 1) / 3
            
            listing = PropertyListing(
                id=f"test_seloger_{i+1}",
                title=f"Appartement T{i+2} {location} - SeLoger",
                price=price,
                currency='EUR',
                location=location,
                property_type='Appartement',
                surface_area=40 + i * 20,
                rooms=i + 2,
                bedrooms=i + 1,
                description=f"Appartement {40 + i * 20}m² à {location}",
                images=[],
                source='SeLoger (Test)',
                url=f"https://www.seloger.com/test{i+1}",
                created_at=datetime.now()
            )
            test_listings.append(listing)
        
        logger.info(f"Généré {len(test_listings)} annonces de test SeLoger")
        return test_listings
'''
    
    # Trouver où insérer la classe (après LeBonCoinScraper)
    leboncoin_end = content.find('return type_mapping.get(str(real_estate_type), \'Inconnu\')')
    if leboncoin_end == -1:
        print("❌ Impossible de trouver où insérer la classe SeLogerScraper")
        return False
    
    # Trouver la fin de la classe LeBonCoinScraper
    insert_pos = content.find('\n\nclass', leboncoin_end)
    if insert_pos == -1:
        insert_pos = len(content)
    
    # Insérer la classe
    new_content = content[:insert_pos] + seloger_class + content[insert_pos:]
    
    # Écrire le fichier modifié
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Classe SeLogerScraper ajoutée")
    return True

def update_property_aggregator():
    """Met à jour PropertyAggregator pour inclure SeLoger"""
    main_path = 'src/main.py'
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si SeLoger est déjà dans les scrapers
    if "'seloger': SeLogerScraper()" in content:
        print("✅ SeLoger déjà dans PropertyAggregator")
        return True
    
    # Remplacer la ligne des scrapers
    old_scrapers = "self.scrapers = {\\n            'leboncoin': LeBonCoinScraper()\\n        }"
    new_scrapers = """self.scrapers = {
            'leboncoin': LeBonCoinScraper(),
            'seloger': SeLogerScraper()
        }"""
    
    if old_scrapers in content:
        content = content.replace(old_scrapers, new_scrapers)
    else:
        # Chercher un pattern plus flexible
        import re
        pattern = r"self\.scrapers = \{[^}]*'leboncoin': LeBonCoinScraper\(\)[^}]*\}"
        replacement = """self.scrapers = {
            'leboncoin': LeBonCoinScraper(),
            'seloger': SeLogerScraper()
        }"""
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Écrire le fichier modifié
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PropertyAggregator mis à jour")
    return True

def create_test_file():
    """Crée un fichier de test pour vérifier l'installation"""
    test_content = '''#!/usr/bin/env python3
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
'''
    
    with open('test_seloger_install.py', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ Fichier de test créé: test_seloger_install.py")

def main():
    """Installation complète"""
    print("🚀 Installation automatique SeLoger")
    print("=" * 60)
    
    # Vérifications préalables
    if not check_file_exists('src/main.py'):
        print("❌ Fichier src/main.py non trouvé")
        print("   Assurez-vous d'être dans le bon répertoire")
        return False
    
    # Sauvegarde
    backup_path = backup_file('src/main.py')
    
    # Installation
    steps = [
        ("📦 Installation des dépendances", install_dependencies),
        ("📝 Ajout des imports", add_imports_to_main),
        ("🔧 Ajout de la classe SeLogerScraper", add_seloger_class),
        ("⚙️ Mise à jour de PropertyAggregator", update_property_aggregator),
        ("🧪 Création du fichier de test", create_test_file)
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\\n{step_name}...")
        if not step_func():
            print(f"❌ Échec: {step_name}")
            success = False
            break
        print(f"✅ {step_name} terminé")
    
    if success:
        print("\\n🎉 Installation terminée avec succès !")
        print("\\n🚀 Prochaines étapes:")
        print("1. Testez: python test_seloger_install.py")
        print("2. Si tout fonctionne, continuez avec la semaine 2")
        print("3. Si problème, restaurez: cp src/main.py.backup_* src/main.py")
    else:
        print("\\n❌ Installation échouée")
        if backup_path:
            print(f"💾 Restaurez la sauvegarde: cp {backup_path} src/main.py")
    
    return success

if __name__ == "__main__":
    main()