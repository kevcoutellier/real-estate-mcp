# MCP Real Estate Spécialisé - Extension Investissement

## 🎯 Vue d'ensemble

Extension spécialisée du MCP Real Estate pour l'**investissement locatif** et le **marchand de biens** avec analyses métier avancées, calculs de rentabilité et recommandations personnalisées.

## 🚀 Fonctionnalités

### 📈 Investissement Locatif
- **Calculs de rentabilité** : Rendement brut/net, cash-flow mensuel
- **Estimation loyers** : Prix au m², fourchettes de marché
- **Analyse charges** : Copropriété, taxes, assurance, gestion
- **Étude quartier** : Demande locative, profil locataires, risque vacance
- **Projections** : Plus-value sur 10 ans, rendement total
- **Score d'investissement** : Note sur 100 avec recommandations

### 🔨 Marchand de Biens
- **Estimation travaux** : Coûts détaillés par poste, durée chantier
- **Analyse marché** : Valeur actuelle vs rénovée, ventes comparables
- **Calcul rentabilité** : Marge brute/nette, investissement total
- **Gestion timing** : Durée revente, liquidité marché, facteurs saisonniers
- **Évaluation risques** : Risque chantier, marché, liquidité
- **Score opportunité** : Note sur 100 avec plan d'action

### ⚖️ Comparaison Stratégies
- **Analyse comparative** : Locatif vs Marchand de biens
- **Recommandations** : Stratégie optimale selon le bien
- **Gestion risques** : Comparaison des profils de risque

## 🛠️ Installation

### Prérequis
```bash
pip install httpx beautifulsoup4 geopy playwright
```

### Structure des fichiers
```
src/
├── specialized_investment_mcp.py    # MCP principal
├── rental_analyzer.py              # Analyseur locatif
├── dealer_analyzer.py              # Analyseur marchand de biens
└── main.py                         # MCP de base

specialized_mcp_server.py            # Serveur MCP
test_specialized_mcp.py             # Tests
mcp-specialized-config.json         # Configuration MCP
```

## 📊 Utilisation

### 1. Analyse d'opportunités d'investissement

```python
from specialized_investment_mcp import SpecializedRealEstateMCP, InvestmentProfile

mcp = SpecializedRealEstateMCP()

# Analyse locative
result = await mcp.analyze_investment_opportunity(
    location="Paris 11e",
    min_price=200000,
    max_price=400000,
    investment_profile=InvestmentProfile.RENTAL_INVESTOR
)

# Analyse marchand de biens
result = await mcp.analyze_investment_opportunity(
    location="Lyon",
    min_price=150000,
    max_price=300000,
    investment_profile=InvestmentProfile.PROPERTY_DEALER
)

# Analyse combinée
result = await mcp.analyze_investment_opportunity(
    location="Marseille",
    investment_profile=InvestmentProfile.BOTH
)
```

### 2. Comparaison de stratégies

```python
property_data = {
    "price": 280000,
    "surface_area": 55,
    "location": "Paris 20e",
    "description": "Appartement à rénover",
    "property_type": "Appartement",
    "rooms": 3
}

comparison = await mcp.compare_investment_strategies(
    location="Paris 20e",
    property_data=property_data
)
```

### 3. Test du système

```bash
python test_specialized_mcp.py
```

## 📋 Outils MCP Disponibles

### `analyze_investment_opportunity`
Analyse complète d'opportunités d'investissement

**Paramètres :**
- `location` (requis) : Localisation de recherche
- `min_price` : Prix minimum en euros
- `max_price` : Prix maximum en euros  
- `investment_profile` : "rental_investor", "property_dealer", ou "both"
- `surface_area` : Surface minimale en m²
- `rooms` : Nombre de pièces
- `property_type` : Type de bien

**Retour :**
```json
{
  "location": "Paris 11e",
  "investment_profile": "rental_investor",
  "total_opportunities": 10,
  "market_summary": {
    "rental_market": {
      "average_net_yield": 4.2,
      "average_investment_score": 75.3,
      "opportunities_count": 6
    }
  },
  "top_opportunities": [...]
}
```

### `compare_investment_strategies`
Compare locatif vs marchand de biens pour un bien

**Paramètres :**
- `location` (requis) : Localisation du bien
- `property_data` (requis) : Données du bien

**Retour :**
```json
{
  "rental_analysis": {...},
  "dealer_analysis": {...},
  "comparison": {
    "rental_annual_return": 8.5,
    "dealer_annual_return": 66.9,
    "recommendation": "Opportunité marchand de biens intéressante"
  }
}
```

### `get_market_analysis`
Analyse rapide du marché d'une zone

**Paramètres :**
- `location` (requis) : Zone à analyser

## 🎯 Exemples de Résultats

### Analyse Locative
```json
{
  "gross_yield": 5.2,
  "net_yield": 3.8,
  "cash_flow": 150,
  "estimated_rent": 1200,
  "investment_score": 78.5,
  "pros": [
    "Excellent rendement net de 3.8%",
    "Cash-flow positif de 150€/mois",
    "Forte demande locative dans le quartier"
  ],
  "recommendations": [
    "Vérifier les travaux nécessaires avant achat",
    "Étudier l'évolution du quartier"
  ]
}
```

### Analyse Marchand de Biens
```json
{
  "renovation_cost": 45000,
  "renovation_duration": 8,
  "gross_margin_percent": 22.5,
  "net_margin": 58000,
  "dealer_score": 85.2,
  "opportunity_level": "Excellente",
  "action_plan": [
    "Négocier rapidement le prix d'achat",
    "Planifier les travaux avec 2-3 entreprises"
  ]
}
```

## 🔧 Configuration

### Base de données des loyers
Modifiez `rental_analyzer.py` pour ajouter vos données locales :

```python
self.rental_database = {
    "votre_ville": {
        "avg_rent_sqm": 25.0,
        "range_min": 22.0,
        "range_max": 28.0,
        "demand": "Forte",
        "tenant_profile": "Jeunes actifs",
        "vacancy_rate": 3.0
    }
}
```

### Coûts de rénovation
Ajustez `dealer_analyzer.py` selon vos coûts locaux :

```python
self.renovation_costs = {
    "renovation_complete": {
        "cost_per_sqm": 800,  # Ajustez selon votre marché
        "duration_weeks": 8
    }
}
```

## 📈 Métriques Calculées

### Investissement Locatif
- **Rendement brut** : (Loyer annuel / Prix d'achat) × 100
- **Rendement net** : (Revenus nets annuels / Prix d'achat) × 100
- **Cash-flow** : Loyer - Charges - Taxes - Gestion
- **Score investissement** : Algorithme pondéré (rendement 40%, demande 25%, plus-value 20%, risques 15%)

### Marchand de Biens
- **Marge brute** : Valeur rénovée - Investissement total
- **Marge nette** : Marge brute - Frais de vente (8%)
- **Score dealer** : Algorithme pondéré (marge 50%, risques 30%, liquidité 20%)

## 🚨 Limitations

- **Données simulées** : Les prix et loyers sont basés sur des estimations
- **Enrichissement géographique** : Erreurs SSL normales pour les APIs externes
- **Marché local** : Adaptez les coefficients à votre zone géographique

## 🔄 Évolutions Futures

- [ ] Intégration APIs immobilières réelles
- [ ] Base de données persistante
- [ ] Interface web de visualisation
- [ ] Alertes automatiques sur nouvelles opportunités
- [ ] Calculs fiscaux avancés (LMNP, SCI, etc.)
- [ ] Simulation de financement

## 🤝 Support

Pour toute question ou amélioration, consultez les logs d'exécution ou modifiez les paramètres dans les analyseurs spécialisés.

---

**🎯 Votre MCP spécialisé est maintenant opérationnel pour analyser les opportunités d'investissement immobilier !**
