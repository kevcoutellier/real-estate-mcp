# 🏠 MCP Real Estate - Serveur MCP pour l'Immobilier Français

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Serveur MCP (Model Context Protocol) pour l'analyse et la recherche d'opportunités immobilières françaises, compatible avec Claude Desktop et Windsurf.

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Git

### Installation Manuelle

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/real-estate-mcp.git
cd real-estate-mcp

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt
```

## 🤖 Configuration MCP

### Pour Claude Desktop

Ajoutez cette configuration à votre fichier `claude_desktop_config.json` :

**Windows** : `%APPDATA%\Claude\claude_desktop_config.json`
**macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux** : `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "real-estate-mcp": {
      "command": "C:\\chemin\\vers\\votre\\projet\\venv\\Scripts\\python.exe",
      "args": ["C:\\chemin\\vers\\votre\\projet\\mcp_real_estate_server.py"],
      "cwd": "C:\\chemin\\vers\\votre\\projet"
    }
  }
}
```

### Pour Windsurf

Le serveur est directement compatible avec Windsurf via le système MCP intégré.

### Test de l'Installation

```bash
# Tester le serveur MCP
python mcp_real_estate_server.py

# Ou utiliser le script de démarrage
python start_server.py
```

## 🛠️ Fonctionnalités

### 7 Outils MCP Disponibles

1. **🔍 search_properties** - Recherche de biens immobiliers avec filtres avancés
2. **📊 analyze_market** - Analyse complète du marché par zone géographique
3. **🏘️ get_neighborhood_info** - Informations détaillées sur un quartier (transports, commodités)
4. **⚖️ compare_locations** - Comparaison multi-critères de plusieurs zones
5. **📋 get_property_summary** - Résumé synthétique du marché immobilier
6. **💰 analyze_investment_opportunity** - Analyse d'opportunités d'investissement locatif/marchand de biens
7. **📈 compare_investment_strategies** - Comparaison de stratégies d'investissement

### Sources de Données

- **APIs Immobilières** - Données d'annonces en temps réel
- **Données Géographiques** - Géocodage et informations de localisation
- **Analyses de Marché** - Statistiques et tendances immobilières
- **Calculs d'Investissement** - Rentabilité locative et plus-values potentielles

## 📖 Exemples d'Utilisation

### Recherche de Studios à Antibes

```text
Trouve-moi des studios de plus de 30m² à louer à Antibes
```

### Analyse de Marché

```text
Analyse le marché immobilier locatif à Lyon
```

### Comparaison d'Investissement

```text
Compare les stratégies d'investissement locatif vs marchand de biens pour un appartement 3 pièces à 250 000€ à Marseille
```

## 🧪 Tests et Validation

```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Mac

# Tester le serveur MCP
python mcp_real_estate_server.py

# Tester avec le script de démarrage
python start_server.py
```

## 🔧 Développement

### Structure des Modules

- **`mcp_real_estate_server.py`** - Serveur MCP principal
- **`src/main.py`** - Logique métier et analyses
- **`src/mcp_server.py`** - Interface MCP
- **`src/dynamic_data_service.py`** - Service de données dynamiques
- **`src/rental_analyzer.py`** - Analyseur d'investissement locatif
- **`src/dealer_analyzer.py`** - Analyseur marchand de biens

## 📁 Structure du Projet

```text
real-estate-mcp/
├── 📂 src/                           # Code source principal
│   ├── 🐍 main.py                    # Logique métier et analyses
│   ├── 🐍 mcp_server.py              # Interface MCP
│   ├── 🐍 dynamic_data_service.py    # Service de données
│   ├── 🐍 rental_analyzer.py         # Analyse investissement locatif
│   ├── 🐍 dealer_analyzer.py         # Analyse marchand de biens
│   └── 🐍 __init__.py               # Module Python
├── 📂 config/                        # Configuration
├── 📂 data/                          # Données locales
├── 🐍 mcp_real_estate_server.py      # Serveur MCP principal
├── 🐍 start_server.py               # Script de démarrage
├── 📄 requirements.txt              # Dépendances Python
├── 📄 .env                          # Variables d'environnement
└── 📄 README.md                     # Documentation
```

## 🐛 Dépannage

### Problème d'Import ou de Modules
```bash
# Vérifier l'environnement virtuel
python -c "import sys; print(sys.executable)"

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier les imports
python -c "from src.main import DynamicRealEstateMCP; print('Import OK')"
```

### Problème de Configuration MCP

1. Vérifiez que les chemins dans la configuration sont corrects (utilisez des chemins absolus)
2. Redémarrez Claude Desktop ou Windsurf après modification
3. Vérifiez les logs du serveur MCP (`mcp_server.log`)

### Problème d'Encodage (Windows)

```bash
# Le serveur gère automatiquement l'encodage UTF-8
# Vérifiez les logs pour les erreurs d'encodage
type mcp_server.log
```

### Test de Connectivité

```bash
# Tester la communication MCP
python mcp_real_estate_server.py
# Le serveur doit démarrer sans erreur
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- 🐛 Signaler un bug via les issues GitHub
- 💡 Demander une fonctionnalité via les issues GitHub
- 📧 Contact direct pour le support technique

## ⭐ Remerciements

- [Model Context Protocol](https://modelcontextprotocol.io/) pour le standard MCP
- [Claude Desktop](https://claude.ai/) et [Windsurf](https://codeium.com/windsurf) pour l'intégration IA
- Communauté open source pour les outils et bibliothèques utilisés

---

## Prêt à analyser le marché immobilier français avec l'IA ! 🏠✨
