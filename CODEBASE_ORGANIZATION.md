# Organisation de la Codebase MCP Real Estate

## 📁 Structure Finale

### Dossiers Principaux
```
real-estate-MCP/
├── src/                    # Code source principal
│   ├── main.py            # MCP unifié principal
│   ├── mcp_server.py      # Serveur MCP moderne
│   ├── models/            # Modèles de données
│   ├── services/          # Services métier
│   ├── utils/             # Utilitaires
│   └── scrapers/          # Scrapers de données
├── config/                # Configuration
├── scripts/               # Scripts utilitaires organisés
│   ├── validation/        # Scripts de validation
│   ├── testing/          # Scripts de test
│   ├── maintenance/      # Scripts de maintenance
│   ├── development/      # Scripts de développement
│   └── start/            # Scripts de démarrage
├── tests/                 # Tests unitaires
├── docs/                  # Documentation
├── examples/              # Exemples d'utilisation
├── logs/                  # Fichiers de logs
├── data/                  # Données de référence
├── deprecated/            # Code obsolète
└── archive/               # Anciennes versions
```

### Points d'Entrée
- **mcp_real_estate_server.py** : Serveur MCP principal (production)
- **start_server.py** : Démarrage simplifié
- **install.py** : Installation automatique

### Scripts Organisés
- **validation/** : Validation de la codebase
- **testing/** : Tests spécialisés
- **maintenance/** : Nettoyage et maintenance
- **development/** : Outils de développement
- **start/** : Scripts de démarrage

## 🎯 Avantages de cette Organisation

### Clarté
- Structure modulaire claire
- Séparation des responsabilités
- Navigation intuitive

### Maintenabilité
- Code organisé par fonction
- Documentation centralisée
- Scripts catégorisés

### Évolutivité
- Architecture extensible
- Ajout facile de nouveaux modules
- Compatibilité préservée

## 🚀 Utilisation

### Démarrage Rapide
```bash
python mcp_real_estate_server.py
```

### Développement
```bash
python src/mcp_server.py
```

### Tests
```bash
python -m pytest tests/
```

### Maintenance
```bash
python scripts/maintenance/cleanup.py
```

Cette organisation garantit une codebase professionnelle, maintenable et évolutive.
