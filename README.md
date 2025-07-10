# 🏠 MCP Real Estate - Serveur MCP pour Claude Desktop

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Serveur MCP (Model Context Protocol) pour l'agrégation et l'analyse d'annonces immobilières françaises, compatible avec Claude Desktop.

## 🚀 Installation Rapide

### Prérequis
- Python 3.8 ou supérieur
- Git

### Installation Automatique

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/real-estate-mcp.git
cd real-estate-mcp

# 2. Lancer l'installation automatique
python install.py
```

L'installation automatique va :
- ✅ Créer l'environnement virtuel
- ✅ Installer toutes les dépendances
- ✅ Générer la configuration pour Claude Desktop
- ✅ Créer les scripts de démarrage
- ✅ Tester l'installation

## 🤖 Configuration Claude Desktop

### ⚡ Environnement Virtuel Automatique

Ce projet utilise un **wrapper intelligent** qui garantit que l'environnement virtuel est **actif 100% du temps** pour Claude Desktop.

### Configuration Automatique

Après l'installation, copiez le contenu de `claude_desktop_config.json` dans votre configuration Claude Desktop :

### Windows
Fichier de configuration : `%APPDATA%\Claude\claude_desktop_config.json`

### macOS
Fichier de configuration : `~/Library/Application Support/Claude/claude_desktop_config.json`

### Linux
Fichier de configuration : `~/.config/Claude/claude_desktop_config.json`

Exemple de configuration générée :
```json
{
  "mcpServers": {
    "real-estate-mcp": {
      "command": "/chemin/vers/votre/projet/venv/Scripts/python.exe",
      "args": ["/chemin/vers/votre/projet/mcp_wrapper.py"],
      "cwd": "/chemin/vers/votre/projet",
      "env": {
        "PYTHONPATH": "/chemin/vers/votre/projet/src",
        "VIRTUAL_ENV": "/chemin/vers/votre/projet/venv"
      }
    }
  }
}
```

### 🔧 Fonctionnement du Wrapper

- ✅ **Détection automatique** de l'environnement virtuel
- ✅ **Activation forcée** si nécessaire
- ✅ **Vérification des dépendances**
- ✅ **Gestion d'erreurs robuste**

**Résultat** : L'environnement virtuel est actif en permanence, sans intervention manuelle !

## 🛠️ Fonctionnalités

### 7 Outils MCP Disponibles

1. **🔍 search_properties** - Recherche de biens immobiliers
2. **📊 analyze_market** - Analyse de marché par zone
3. **🏘️ get_neighborhood_info** - Informations détaillées sur un quartier
4. **⚖️ compare_locations** - Comparaison de plusieurs zones
5. **📋 get_property_summary** - Résumé du marché immobilier
6. **💰 analyze_investment_opportunity** - Analyse d'opportunités d'investissement
7. **📈 compare_investment_strategies** - Comparaison de stratégies d'investissement

### Sources de Données
- **LeBonCoin API** - Annonces en temps réel
- **API DVF** - Données de valeurs foncières officielles
- **API INSEE** - Statistiques démographiques
- **API Adresse française** - Géocodage et normalisation

## 📖 Exemples d'Utilisation

### Recherche de Studios à Antibes
```
Trouve-moi des studios de plus de 30m² à louer à Antibes
```

### Analyse de Marché
```
Analyse le marché immobilier locatif à Lyon
```

### Comparaison d'Investissement
```
Compare les stratégies d'investissement locatif vs marchand de biens pour un appartement 3 pièces à 250 000€ à Marseille
```

## 🔧 Installation Manuelle

Si l'installation automatique échoue :

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Tester l'installation
python start_server.py
```

## 🧪 Tests

```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Mac

# Tester la recherche Antibes
python scripts/test_antibes_search.py

# Valider l'organisation
python scripts/validate_organization.py
```

## 📁 Structure du Projet

```
real-estate-mcp/
├── 📂 src/                      # Code source principal
│   ├── 🐍 mcp_server.py         # Serveur MCP
│   ├── 🐍 main.py               # Logique métier
│   └── 📂 utils/                # Utilitaires
├── 📂 config/                   # Configuration
├── 📂 scripts/                  # Scripts utilitaires
├── 📂 docs/                     # Documentation
├── 🐍 install.py                # Installation automatique
├── 🐍 start_server.py           # Point d'entrée
└── 📄 requirements.txt          # Dépendances
```

## 🐛 Dépannage

### Problème d'Import
```bash
# Vérifier l'environnement virtuel
python -c "import sys; print(sys.executable)"

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problème de Permissions (Unix/Mac)
```bash
chmod +x start_mcp.sh
```

### Problème Claude Desktop
1. Vérifiez que les chemins dans `claude_desktop_config.json` sont corrects
2. Redémarrez Claude Desktop après modification
3. Vérifiez les logs de Claude Desktop

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- 📖 [Documentation complète](docs/)
- 🐛 [Signaler un bug](https://github.com/votre-username/real-estate-mcp/issues)
- 💡 [Demander une fonctionnalité](https://github.com/votre-username/real-estate-mcp/issues)

## ⭐ Remerciements

- [Model Context Protocol](https://modelcontextprotocol.io/) pour le standard MCP
- [Claude Desktop](https://claude.ai/) pour l'intégration IA
- APIs officielles françaises pour les données immobilières

---

**Prêt à analyser le marché immobilier français avec Claude ! 🏠✨**
