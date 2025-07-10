# Guide de Développement - MCP Real Estate

## 🏗️ Architecture

### Structure du Code Principal

```
src/
├── main.py                 # MCP principal avec analyses intégrées
├── rental_analyzer.py      # Logique d'investissement locatif
├── dealer_analyzer.py      # Logique marchand de biens
└── scrapers/              # Modules de scraping par site
```

### Classes Principales

#### `EnrichedRealEstateMCP`
- **Hérite de** : `RealEstateMCP`
- **Fonctionnalités** : Recherche + enrichissement géographique + analyses d'investissement
- **Méthodes clés** :
  - `search_properties()` : Recherche multi-sources
  - `analyze_investment_opportunity()` : Analyse d'opportunités
  - `compare_investment_strategies()` : Comparaison de stratégies

#### `RentalMarketAnalyzer`
- **Responsabilité** : Analyses d'investissement locatif
- **Données** : Base de loyers, fiscalité, rendements
- **Méthodes** : `analyze_rental_investment()`, `estimate_rental_income()`

#### `PropertyDealerAnalyzer`
- **Responsabilité** : Analyses marchand de biens
- **Données** : Coûts rénovation, marges, timing
- **Méthodes** : `analyze_dealer_opportunity()`, `estimate_renovation_costs()`

## 🔧 Ajout de Nouvelles Fonctionnalités

### 1. Nouveau Scraper

```python
# Dans src/scrapers/nouveau_site.py
class NouveauSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__("nouveau_site")
    
    async def search_properties(self, params: SearchParams) -> List[PropertyListing]:
        # Implémentation du scraping
        pass
```

### 2. Nouvelle Métrique d'Investissement

```python
# Dans rental_analyzer.py ou dealer_analyzer.py
def calculate_nouvelle_metrique(self, listing: PropertyListing) -> float:
    """Calcule une nouvelle métrique d'investissement"""
    # Logique de calcul
    return metrique_value
```

### 3. Nouveau Profil d'Investissement

```python
# Dans main.py
class InvestmentProfile(Enum):
    RENTAL_INVESTOR = "rental_investor"
    PROPERTY_DEALER = "property_dealer"
    NOUVEAU_PROFIL = "nouveau_profil"  # Ajouter ici
    BOTH = "both"
```

## 🧪 Tests et Validation

### Tests Unitaires
```bash
# Tests des analyseurs
python -m pytest tests/test_analyzers.py

# Tests d'intégration
python examples/test_integrated_mcp.py
```

### Tests de Performance
```python
# Mesurer les temps de réponse
import time
start = time.time()
results = await mcp.analyze_investment_opportunity(...)
print(f"Temps d'exécution: {time.time() - start:.2f}s")
```

## 📊 Données et Configuration

### Base de Données Locative
```python
# Structure dans main.py
rental_database = {
    "ville": {
        "studio": {"min": 400, "max": 600, "avg": 500},
        "T2": {"min": 600, "max": 900, "avg": 750},
        # ...
    }
}
```

### Coûts de Rénovation
```python
# Structure dans main.py
renovation_costs = {
    "peinture": {"min": 15, "max": 25, "unit": "m²"},
    "electricite": {"min": 80, "max": 120, "unit": "m²"},
    # ...
}
```

## 🔍 Debugging et Logs

### Configuration des Logs
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Points de Debug Importants
- Recherche de propriétés : vérifier les paramètres de recherche
- Analyses d'investissement : valider les calculs financiers
- Scraping : surveiller les erreurs SSL et timeouts

### Scripts de Diagnostic
```bash
# Diagnostic complet
python scripts/diagnostic_mcp.py

# Test de connectivité
python scripts/test_scrapers.py
```

## 🚀 Déploiement

### Variables d'Environnement
```bash
# .env
REAL_ESTATE_API_KEY=your_api_key
LOG_LEVEL=INFO
SCRAPING_DELAY=1
```

### Configuration MCP
```json
{
  "mcpServers": {
    "real-estate": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/real-estate-MCP"
    }
  }
}
```

## 🔄 Maintenance

### Mise à Jour des Données
- **Loyers** : Mettre à jour `rental_database` trimestriellement
- **Coûts rénovation** : Réviser `renovation_costs` annuellement
- **Scrapers** : Surveiller les changements de sites web

### Monitoring
- Surveiller les logs pour les erreurs de scraping
- Vérifier les temps de réponse des analyses
- Contrôler la qualité des données retournées

## 📈 Optimisations

### Performance
- Mise en cache des résultats de recherche
- Parallélisation des analyses d'investissement
- Optimisation des requêtes de scraping

### Qualité des Données
- Validation des prix et surfaces
- Filtrage des doublons
- Enrichissement automatique manquant

## 🤝 Contribution

### Standards de Code
- PEP 8 pour le style Python
- Type hints obligatoires
- Docstrings pour toutes les méthodes publiques
- Tests unitaires pour les nouvelles fonctionnalités

### Workflow Git
1. Créer une branche feature/nom-fonctionnalité
2. Développer avec tests
3. Valider avec les exemples
4. Pull request avec description détaillée

---

**Dernière mise à jour** : Janvier 2025
