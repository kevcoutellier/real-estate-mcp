#!/usr/bin/env python3
"""
Diagnostic complet du système MCP immobilier
Ce script identifie précisément pourquoi le système utilise des données de démonstration
"""

import asyncio
import sys
import os
import importlib.util
import httpx
from datetime import datetime

# Ajouter le répertoire source au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class MCPDiagnostic:
    """Classe pour diagnostiquer les problèmes du système MCP"""
    
    def __init__(self):
        self.issues_found = []
        self.success_count = 0
        self.total_tests = 0
        
    async def run_complete_diagnosis(self):
        """Lance un diagnostic complet du système"""
        print("🔍 DIAGNOSTIC COMPLET DU SYSTÈME MCP IMMOBILIER")
        print("=" * 60)
        print("Ce diagnostic va identifier pourquoi vous obtenez des données de démonstration")
        print("au lieu de vraies annonces immobilières.\n")
        
        # Tests séquentiels avec explications détaillées
        await self._test_dependencies()
        await self._test_network_connectivity()
        await self._test_api_accessibility()
        await self._test_scraper_functionality()
        await self._test_ssl_configuration()
        await self._test_enrichment_services()
        
        # Rapport final avec recommandations
        await self._generate_final_report()
    
    async def _test_dependencies(self):
        """Teste la disponibilité de toutes les dépendances"""
        print("📦 TEST 1: Vérification des dépendances")
        print("-" * 40)
        
        dependencies = [
            ('httpx', 'Client HTTP pour les requêtes API'),
            ('beautifulsoup4', 'Parser HTML pour le scraping'),
            ('geopy', 'Service de géocodage'),
            ('playwright', 'Navigateur automatisé pour JavaScript'),
            ('ssl', 'Gestion des certificats SSL')
        ]
        
        for dep_name, description in dependencies:
            self.total_tests += 1
            try:
                if dep_name == 'beautifulsoup4':
                    import bs4
                    print(f"  ✅ BeautifulSoup4 - {description}")
                    self.success_count += 1
                elif dep_name == 'ssl':
                    import ssl
                    print(f"  ✅ SSL - {description}")
                    self.success_count += 1
                else:
                    importlib.import_module(dep_name)
                    print(f"  ✅ {dep_name} - {description}")
                    self.success_count += 1
            except ImportError as e:
                print(f"  ❌ {dep_name} - MANQUANT: {description}")
                self.issues_found.append(f"Dépendance manquante: {dep_name}")
                print(f"     💡 Solution: pip install {dep_name}")
        
        print()
    
    async def _test_network_connectivity(self):
        """Teste la connectivité réseau de base"""
        print("🌐 TEST 2: Connectivité réseau")
        print("-" * 40)
        
        test_urls = [
            ('https://httpbin.org/status/200', 'Test de connectivité HTTP générale'),
            ('https://api.leboncoin.fr', 'Accessibilité du domaine LeBonCoin'),
            ('https://www.seloger.com', 'Accessibilité du domaine SeLoger'),
            ('https://api-adresse.data.gouv.fr', 'API de géocodage française')
        ]
        
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            for url, description in test_urls:
                self.total_tests += 1
                try:
                    response = await client.get(url)
                    if response.status_code < 400:
                        print(f"  ✅ {description} - Accessible")
                        self.success_count += 1
                    else:
                        print(f"  ⚠️ {description} - Code {response.status_code}")
                        self.issues_found.append(f"Problème d'accès: {url}")
                except Exception as e:
                    print(f"  ❌ {description} - Erreur: {str(e)[:50]}...")
                    self.issues_found.append(f"Connectivité échouée: {url}")
        
        print()
    
    async def _test_api_accessibility(self):
        """Teste l'accessibilité des APIs spécifiques"""
        print("🔌 TEST 3: Accessibilité des APIs")
        print("-" * 40)
        
        # Test API LeBonCoin
        self.total_tests += 1
        try:
            async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
                payload = {
                    "filters": {
                        "category": {"id": "9"},
                        "enums": {"ad_type": ["offer"]},
                        "location": {"locations": [{"label": "Paris"}]},
                        "ranges": {}
                    },
                    "limit": 5
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                
                response = await client.post(
                    "https://api.leboncoin.fr/finder/search",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ads_count = len(data.get('ads', []))
                    print(f"  ✅ API LeBonCoin - Fonctionne ({ads_count} annonces trouvées)")
                    self.success_count += 1
                elif response.status_code == 403:
                    print(f"  🚫 API LeBonCoin - Bloquée (Code 403: Accès refusé)")
                    self.issues_found.append("LeBonCoin bloque les requêtes API")
                elif response.status_code == 429:
                    print(f"  ⏰ API LeBonCoin - Rate limit (Code 429: Trop de requêtes)")
                    self.issues_found.append("LeBonCoin applique un rate limiting")
                else:
                    print(f"  ❌ API LeBonCoin - Code {response.status_code}")
                    self.issues_found.append(f"LeBonCoin retourne le code {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ API LeBonCoin - Erreur: {str(e)[:60]}...")
            self.issues_found.append(f"Erreur API LeBonCoin: {str(e)[:100]}")
        
        # Test API géocodage
        self.total_tests += 1
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api-adresse.data.gouv.fr/search/",
                    params={'q': 'Paris 11e', 'limit': 1}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    features = data.get('features', [])
                    if features:
                        print(f"  ✅ API Géocodage - Fonctionne")
                        self.success_count += 1
                    else:
                        print(f"  ⚠️ API Géocodage - Aucun résultat")
                        self.issues_found.append("Géocodage ne retourne pas de résultats")
                else:
                    print(f"  ❌ API Géocodage - Code {response.status_code}")
                    self.issues_found.append("Problème API géocodage")
                    
        except Exception as e:
            print(f"  ❌ API Géocodage - Erreur: {str(e)[:50]}...")
            self.issues_found.append("Erreur géocodage")
        
        print()
    
    async def _test_scraper_functionality(self):
        """Teste le fonctionnement réel des scrapers"""
        print("🕷️ TEST 4: Fonctionnement des scrapers")
        print("-" * 40)
        
        try:
            # Import du système MCP
            from main import LeBonCoinScraper, SeLogerScraper
            
            # Test LeBonCoin Scraper
            self.total_tests += 1
            leboncoin = LeBonCoinScraper()
            search_params = {
                'location': 'Paris 11e',
                'min_price': 1000,
                'max_price': 2000,
                'transaction_type': 'rent'
            }
            
            print("  🔍 Test du scraper LeBonCoin...")
            results_lbc = await leboncoin.search(search_params)
            
            if results_lbc:
                # Vérifier si ce sont de vraies données ou des données de test
                real_data_count = sum(1 for r in results_lbc if 'test' not in r.source.lower())
                test_data_count = len(results_lbc) - real_data_count
                
                if real_data_count > 0:
                    print(f"    ✅ LeBonCoin - {real_data_count} vraies annonces + {test_data_count} tests")
                    self.success_count += 1
                else:
                    print(f"    ⚠️ LeBonCoin - Seulement {test_data_count} données de test")
                    self.issues_found.append("LeBonCoin utilise uniquement des données de test")
            else:
                print(f"    ❌ LeBonCoin - Aucun résultat")
                self.issues_found.append("LeBonCoin ne retourne aucun résultat")
            
            # Test SeLoger Scraper
            self.total_tests += 1
            try:
                seloger = SeLogerScraper()
                print("  🔍 Test du scraper SeLoger...")
                results_seloger = await seloger.search(search_params)
                
                if results_seloger:
                    real_data_seloger = sum(1 for r in results_seloger if 'test' not in r.source.lower())
                    if real_data_seloger > 0:
                        print(f"    ✅ SeLoger - {real_data_seloger} vraies annonces")
                        self.success_count += 1
                    else:
                        print(f"    ⚠️ SeLoger - Mode test uniquement")
                        self.issues_found.append("SeLoger utilise uniquement des données de test")
                else:
                    print(f"    ❌ SeLoger - Aucun résultat")
                    self.issues_found.append("SeLoger ne retourne aucun résultat")
                    
            except Exception as e:
                print(f"    ❌ SeLoger - Erreur: {str(e)[:50]}...")
                self.issues_found.append(f"Erreur SeLoger: {str(e)[:100]}")
            
        except ImportError as e:
            print(f"  ❌ Impossible d'importer les scrapers: {e}")
            self.issues_found.append("Problème d'import des scrapers")
        
        print()
    
    async def _test_ssl_configuration(self):
        """Teste la configuration SSL"""
        print("🔒 TEST 5: Configuration SSL")
        print("-" * 40)
        
        self.total_tests += 1
        try:
            import ssl
            
            # Test avec vérification SSL activée
            try:
                async with httpx.AsyncClient(timeout=10.0, verify=True) as client:
                    response = await client.get("https://httpbin.org/status/200")
                    print("  ✅ SSL avec vérification - Fonctionne")
                    self.success_count += 1
            except Exception as e:
                print(f"  ⚠️ SSL avec vérification - Problème: {str(e)[:50]}...")
                print("    💡 Votre système utilise verify=False pour contourner ce problème")
                self.issues_found.append("Problèmes de certificats SSL")
                
        except Exception as e:
            print(f"  ❌ Configuration SSL - Erreur: {e}")
            self.issues_found.append("Problème de configuration SSL")
        
        print()
    
    async def _test_enrichment_services(self):
        """Teste les services d'enrichissement géographique"""
        print("🗺️ TEST 6: Services d'enrichissement")
        print("-" * 40)
        
        try:
            from main import GeocodingService
            
            geocoding = GeocodingService()
            
            # Test géocodage
            self.total_tests += 1
            coords = await geocoding.geocode_address("Place de la République, Paris")
            
            if coords and 'lat' in coords and 'lon' in coords:
                print(f"  ✅ Géocodage - Fonctionne ({coords['lat']:.4f}, {coords['lon']:.4f})")
                self.success_count += 1
                
                # Test enrichissement quartier
                self.total_tests += 1
                try:
                    neighborhood = await geocoding.get_neighborhood_info(coords)
                    if neighborhood and neighborhood.get('score', 0) > 0:
                        print(f"  ✅ Enrichissement quartier - Score: {neighborhood.get('score', 'N/A')}")
                        self.success_count += 1
                    else:
                        print(f"  ⚠️ Enrichissement quartier - Données limitées")
                        self.issues_found.append("Enrichissement quartier incomplet")
                except Exception as e:
                    print(f"  ❌ Enrichissement quartier - Erreur: {str(e)[:50]}...")
                    self.issues_found.append("Erreur enrichissement quartier")
            else:
                print(f"  ❌ Géocodage - Échec")
                self.issues_found.append("Géocodage ne fonctionne pas")
                
        except ImportError as e:
            print(f"  ❌ Services d'enrichissement non disponibles: {e}")
            self.issues_found.append("Services d'enrichissement non importables")
        
        print()
    
    async def _generate_final_report(self):
        """Génère un rapport final avec des recommandations"""
        print("📊 RAPPORT FINAL DE DIAGNOSTIC")
        print("=" * 60)
        
        # Statistiques globales
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"Score global: {self.success_count}/{self.total_tests} tests réussis ({success_rate:.1f}%)")
        print()
        
        # Classification des problèmes
        if not self.issues_found:
            print("🎉 EXCELLENT ! Aucun problème détecté.")
            print("Votre système devrait fonctionner avec de vraies données.")
            print("Si vous obtenez encore des données de test, c'est probablement")
            print("un choix de configuration plutôt qu'un problème technique.")
        else:
            print("🔍 PROBLÈMES IDENTIFIÉS:")
            print()
            
            # Catégoriser les problèmes
            critical_issues = []
            warning_issues = []
            
            for issue in self.issues_found:
                if any(keyword in issue.lower() for keyword in ['manquant', 'bloquée', 'aucun résultat']):
                    critical_issues.append(issue)
                else:
                    warning_issues.append(issue)
            
            if critical_issues:
                print("❌ PROBLÈMES CRITIQUES (bloquent les vraies données):")
                for i, issue in enumerate(critical_issues, 1):
                    print(f"   {i}. {issue}")
                print()
            
            if warning_issues:
                print("⚠️ AVERTISSEMENTS (peuvent affecter les performances):")
                for i, issue in enumerate(warning_issues, 1):
                    print(f"   {i}. {issue}")
                print()
            
            # Recommandations spécifiques
            print("💡 RECOMMANDATIONS POUR ACTIVER LES VRAIES DONNÉES:")
            print()
            
            if any('manquant' in issue for issue in self.issues_found):
                print("1. INSTALLER LES DÉPENDANCES MANQUANTES:")
                print("   pip install httpx beautifulsoup4 geopy playwright")
                print("   playwright install chromium")
                print()
            
            if any('bloquée' in issue for issue in self.issues_found):
                print("2. CONTOURNER LES BLOCAGES D'API:")
                print("   - Utiliser des proxies rotatifs")
                print("   - Implémenter des délais entre requêtes")
                print("   - Utiliser Playwright avec des User-Agents variés")
                print("   - Considérer des solutions d'API payantes")
                print()
            
            if any('ssl' in issue.lower() for issue in self.issues_found):
                print("3. RÉSOUDRE LES PROBLÈMES SSL:")
                print("   - Votre système utilise déjà verify=False comme contournement")
                print("   - Pour la production, considérez configurer les certificats")
                print()
            
            print("4. ACTIVATION IMMÉDIATE MODE RÉEL:")
            print("   Si les APIs sont accessibles, modifiez votre code pour:")
            print("   - Réduire les timeouts pour détecter plus vite les échecs")
            print("   - Ajuster les User-Agents pour éviter la détection")
            print("   - Implémenter un retry intelligent")
        
        print()
        print("📈 PROCHAINES ÉTAPES RECOMMANDÉES:")
        
        if success_rate > 80:
            print("1. Votre système est en excellent état !")
            print("2. Ajustez les paramètres des scrapers pour forcer le mode réel")
            print("3. Implémentez des métriques pour monitorer le taux de succès")
        elif success_rate > 60:
            print("1. Résolvez les problèmes critiques identifiés")
            print("2. Testez individuellement chaque scraper")
            print("3. Implémentez un mode fallback gracieux")
        else:
            print("1. Priorité sur les dépendances et la connectivité")
            print("2. Considérez une approche alternative (scraping HTML)")
            print("3. Développez en mode test puis activez progressivement")
        
        print()
        print("🔄 Pour relancer ce diagnostic: python diagnostic_mcp.py")

# Point d'entrée
async def main():
    """Lance le diagnostic complet"""
    diagnostic = MCPDiagnostic()
    await diagnostic.run_complete_diagnosis()

if __name__ == "__main__":
    asyncio.run(main())