# Changelog - MCP Real Estate

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [2.0.0] - 2025-01-10

### 🎉 **Intégration Majeure - MCP Unifié**

#### ✨ Ajouté
- **Analyses d'investissement intégrées** dans le MCP principal
- **Profils d'investissement** : locatif, marchand de biens, mixte
- **Nouveaux outils MCP** :
  - `analyze_investment_opportunity` : analyse complète d'opportunités
  - `compare_investment_strategies` : comparaison de stratégies
- **Base de données locative** intégrée (50+ villes françaises)
- **Coûts de rénovation** par catégorie et région
- **Scoring intelligent** pour les opportunités d'investissement
- **Calculs financiers avancés** : rendement, cash-flow, marges, ROI

#### 🔧 Modifié
- **Architecture unifiée** : tout dans `src/main.py`
- **Initialisation lazy loading** des analyseurs pour éviter les imports circulaires
- **Enrichissement géographique** amélioré avec données d'investissement
- **Structure des données** optimisée pour les analyses

#### 📁 Organisé
- **Dossiers créés** : `archive/`, `deprecated/`, `examples/`, `scripts/`, `config/`
- **Fichiers obsolètes** déplacés vers `deprecated/`
- **Scripts utilitaires** organisés dans `scripts/`
- **Exemples et tests** regroupés dans `examples/`

#### 🗑️ Supprimé
- Serveur MCP spécialisé séparé (intégré dans le principal)
- Fichiers de configuration redondants
- Anciens fichiers de backup

---

## [1.5.0] - 2025-01-09

### 🏗️ **Développement des Analyses Spécialisées**

#### ✨ Ajouté
- **RentalMarketAnalyzer** : analyse complète d'investissement locatif
- **PropertyDealerAnalyzer** : analyse marchand de biens
- **Structures de données** : `RentalAnalysis`, `DealerAnalysis`
- **Serveur MCP spécialisé** pour les analyses d'investissement
- **Scripts de test** et démonstration

#### 🔧 Modifié
- **Enrichissement des données** de propriétés
- **Calculs financiers** détaillés et précis
- **Système de scoring** pour les opportunités

---

## [1.0.0] - 2025-01-08

### 🎯 **Version Initiale - MCP Real Estate de Base**

#### ✨ Ajouté
- **Scraping multi-sources** : SeLoger, LeBonCoin
- **Agrégation de données** immobilières
- **Enrichissement géographique** avec coordonnées
- **API de géocodage** et informations de quartier
- **Serveur MCP** de base avec outils de recherche
- **Configuration** et déploiement

#### 🛠️ Infrastructure
- **Structure de projet** Python avec modules
- **Gestion des dépendances** avec requirements.txt
- **Logging** et gestion d'erreurs
- **Tests** de base et validation

---

## 📋 Types de Changements

- ✨ **Ajouté** : nouvelles fonctionnalités
- 🔧 **Modifié** : changements de fonctionnalités existantes
- 🗑️ **Supprimé** : fonctionnalités supprimées
- 🐛 **Corrigé** : corrections de bugs
- 🔒 **Sécurité** : corrections de vulnérabilités
- 📁 **Organisé** : restructuration de fichiers
- 🛠️ **Infrastructure** : changements techniques

---

## 🔮 Roadmap Future

### Version 2.1.0 (Prévue)
- [ ] **Analyses prédictives** avec machine learning
- [ ] **API REST** pour intégration externe
- [ ] **Dashboard web** pour visualisation
- [ ] **Alertes automatiques** sur les opportunités

### Version 2.2.0 (Prévue)
- [ ] **Nouveaux scrapers** : PAP, Orpi, Century21
- [ ] **Analyses de marché** avancées par secteur
- [ ] **Simulation de financement** avec banques
- [ ] **Export PDF** des analyses

### Version 3.0.0 (Vision)
- [ ] **Intelligence artificielle** pour recommandations
- [ ] **Intégration notariale** pour données officielles
- [ ] **Plateforme collaborative** multi-utilisateurs
- [ ] **Mobile app** native

---

**Format basé sur** [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)  
**Versioning** : [Semantic Versioning](https://semver.org/lang/fr/)
