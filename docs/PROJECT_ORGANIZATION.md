# Organisation du Projet MCP Real Estate

## 📁 Structure Organisée

Le projet MCP Real Estate a été réorganisé pour une meilleure maintenabilité et une structure plus claire.

### Structure des Dossiers

```
real-estate-MCP/
├── 📂 src/                      # Code source principal
│   ├── 🐍 mcp_server.py         # Serveur MCP principal (nouveau)
│   ├── 🐍 main.py               # Logique métier MCP
│   ├── 📂 models/               # Modèles de données
│   ├── 📂 services/             # Services métier
│   ├── 📂 mcp/                  # Implémentation MCP
│   └── 📂 utils/                # Utilitaires (logger, helpers)
│
├── 📂 config/                   # Configuration
│   └── 📄 mcp-config.json       # Configuration MCP
│
├── 📂 scripts/                  # Scripts utilitaires
│   ├── 🐍 cleanup_project.py    # Nettoyage du projet
│   ├── 🐍 restart_mcp_dynamic.py # Redémarrage avec données dynamiques
│   └── 🐍 test_*.py             # Scripts de test
│
├── 📂 tests/                    # Tests unitaires et d'intégration
│   ├── 🐍 test_mcp.py           # Tests du MCP
│   └── 🐍 test_*.py             # Autres tests
│
├── 📂 examples/                 # Exemples d'utilisation
│   ├── 🐍 demo_investment_analysis.py
│   └── 🐍 test_integrated_mcp.py
│
├── 📂 docs/                     # Documentation
│   ├── 📂 api/                  # Documentation API
│   ├── 📂 guides/               # Guides utilisateur
│   ├── 📄 CHANGELOG.md          # Historique des versions
│   ├── 📄 DEVELOPMENT.md        # Guide développeur
│   └── 📄 *.md                  # Autres documentations
│
├── 📂 logs/                     # Fichiers de logs
│   └── 📄 mcp_server.log        # Logs du serveur
│
├── 📂 archive/                  # Fichiers archivés
│   └── 📄 mcp_server.py         # Ancien serveur (archivé)
│
├── 📂 deprecated/               # Fichiers obsolètes
│   └── 🐍 specialized_*.py      # Anciens MCP spécialisés
│
├── 🐍 start_server.py           # Point d'entrée principal (nouveau)
├── 🐍 mcp_real_estate_server.py # Serveur compatible (legacy)
├── 📄 README.md                 # Documentation principale
└── 📄 requirements.txt          # Dépendances Python
```

## 🚀 Points d'Entrée

### Nouveau Serveur (Recommandé)
```bash
python start_server.py
```
- Structure modulaire organisée
- Logs centralisés dans `logs/`
- Configuration via `src/utils/logger.py`

### Serveur Compatible (Legacy)
```bash
python mcp_real_estate_server.py
```
- Maintenu pour compatibilité
- Fonctionnalités identiques
- Transition en douceur

## 🔧 Modules Principaux

### `src/mcp_server.py`
- Serveur MCP principal
- Gestion des requêtes et réponses
- Architecture modulaire

### `src/main.py`
- Logique métier du MCP
- Classes `DynamicRealEstateMCP`
- Analyseurs d'investissement

### `src/utils/logger.py`
- Configuration centralisée des logs
- Logs rotatifs par date
- Support UTF-8 complet

## 📊 Avantages de la Nouvelle Structure

### ✅ Organisation
- Code source séparé par responsabilité
- Documentation centralisée
- Scripts utilitaires regroupés

### ✅ Maintenabilité
- Imports Python propres
- Modules réutilisables
- Tests organisés

### ✅ Évolutivité
- Structure extensible
- Ajout facile de nouveaux services
- Séparation claire des préoccupations

### ✅ Compatibilité
- Ancien serveur maintenu
- Migration progressive possible
- Aucune rupture de fonctionnalité

## 🛠️ Scripts Utilitaires

### Nettoyage du Projet
```bash
python scripts/cleanup_project.py
```
- Archive les fichiers obsolètes
- Crée la structure de dossiers
- Affiche l'arborescence finale

### Redémarrage Dynamique
```bash
python scripts/restart_mcp_dynamic.py
```
- Redémarre avec données temps réel
- Nettoie le cache
- Valide la configuration

### Tests de Validation
```bash
python scripts/test_dynamic_service.py
python scripts/validate_real_data.py
```

## 📝 Migration

### Pour les Développeurs
1. Utiliser `start_server.py` comme nouveau point d'entrée
2. Importer depuis `src.utils.logger` pour les logs
3. Placer nouveaux modules dans `src/services/` ou `src/models/`

### Pour les Utilisateurs
- Aucun changement nécessaire
- Les deux serveurs fonctionnent identiquement
- Migration transparente

## 🔮 Prochaines Étapes

1. **Modularisation** : Déplacer plus de code vers `src/services/`
2. **Tests** : Étendre la couverture de tests
3. **Documentation** : Compléter la documentation API
4. **CI/CD** : Mettre en place l'intégration continue

Cette organisation garantit une base solide pour le développement futur du MCP Real Estate.
