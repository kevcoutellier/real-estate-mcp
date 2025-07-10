# MCP Real Estate - Plateforme d'Analyse Immobilière

> **Plateforme MCP complète pour la recherche, l'analyse et l'investissement immobilier en France**

## 🏠 Vue d'ensemble

Le MCP Real Estate est une plateforme unifiée qui combine :
- **Recherche de biens** : Agrégation multi-sources (SeLoger, LeBonCoin, etc.)
- **Enrichissement géographique** : Données de quartier, transports, commodités
- **Analyses d'investissement** : Calculs de rentabilité locative et marchand de biens
- **Recommandations intelligentes** : Scoring et conseils personnalisés

## 🚀 Fonctionnalités Principales

### 📊 **Recherche et Analyse de Base**
- Recherche multi-critères (prix, surface, localisation, type)
- Enrichissement automatique avec données géographiques
- Résumés de marché par zone
- Analyse de quartier (transports, commerces, écoles)

### 💰 **Analyses d'Investissement Avancées**
- **Investissement Locatif** :
  - Calcul de rendement net et brut
  - Estimation des loyers de marché
  - Analyse cash-flow et fiscalité
  - Score de rentabilité

- **Marchand de Biens** :
  - Estimation des coûts de rénovation
  - Calcul des marges et ROI
  - Analyse des délais de revente
  - Évaluation des risques

### 🎯 **Outils MCP Disponibles**

| Outil | Description |
|-------|-------------|
| `search_properties` | Recherche de biens selon critères |
| `analyze_investment_opportunity` | Analyse complète d'opportunités d'investissement |
| `compare_investment_strategies` | Comparaison locatif vs marchand de biens |
| `get_property_summary` | Résumé de marché pour une zone |

## 📁 Structure du Projet

```
real-estate-MCP/
├── src/                     # Code source principal
│   ├── mcp_server.py       # Serveur MCP principal
│   ├── main.py             # Logique métier MCP
│   ├── models/             # Modèles de données
│   ├── services/           # Services métier
│   ├── mcp/                # Implémentation MCP
│   └── utils/              # Utilitaires
├── config/                  # Configuration
│   └── mcp-config.json     # Configuration MCP
├── scripts/                 # Scripts utilitaires
├── tests/                   # Tests
├── examples/               # Exemples d'utilisation
├── docs/                   # Documentation
├── logs/                   # Fichiers de logs
├── start_server.py         # Point d'entrée principal
└── mcp_real_estate_server.py  # Serveur compatible (legacy)
```

## 🛠️ Installation et Configuration

### Prérequis
```bash
Python 3.8+
pip install -r requirements.txt
```

### Configuration MCP
1. Copier `config/mcp-config.json` vers votre répertoire MCP
2. Ajuster les chemins selon votre environnement
3. Configurer les variables d'environnement dans `.env`

### Démarrage du serveur
```bash
python mcp_server.py
```

## 📈 Exemples d'Utilisation

### Recherche de base
```python
from src.main import EnrichedRealEstateMCP

mcp = EnrichedRealEstateMCP()
results = await mcp.search_properties(
    location="Paris 11e",
    min_price=300000,
    max_price=500000,
    transaction_type="sale"
)
```

### Analyse d'investissement
```python
# Analyse d'opportunités d'investissement
analysis = await mcp.analyze_investment_opportunity(
    location="Lyon",
    min_price=200000,
    max_price=400000,
    investment_profile="both"  # locatif + marchand
)

# Comparaison de stratégies
comparison = await mcp.compare_investment_strategies(
    location="Marseille",
    property_data=property_info
)
```

## 🎯 Profils d'Investissement

- **`rental_investor`** : Focus sur la rentabilité locative
- **`property_dealer`** : Focus sur la revente après rénovation  
- **`both`** : Analyse des deux stratégies

## 📊 Métriques et Scoring

### Investissement Locatif
- Rendement net et brut
- Cash-flow mensuel
- Ratio d'endettement
- Score de rentabilité (0-100)

### Marchand de Biens
- Marge brute estimée
- Coûts de rénovation
- Délai de revente
- Score d'opportunité (0-100)

## 🔧 Développement

### Tests
```bash
# Test du MCP intégré
python examples/test_integrated_mcp.py

# Démonstration complète
python examples/demo_investment_analysis.py
```

### Structure des données
- Base de données locative intégrée (50+ villes)
- Coûts de rénovation par catégorie
- Données de marché temps réel

## 📝 Logs et Monitoring

Les logs sont configurés au niveau INFO et incluent :
- Requêtes de recherche
- Analyses d'investissement
- Erreurs de scraping
- Performance des API

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Consulter les exemples dans `/examples`
- Vérifier les logs dans `mcp_server.log`
- Utiliser les scripts de diagnostic dans `/scripts`

---

**Version actuelle** : 2.0 (MCP Intégré)  
**Dernière mise à jour** : Janvier 2025
