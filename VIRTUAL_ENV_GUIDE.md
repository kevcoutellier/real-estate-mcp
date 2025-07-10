# 🐍 Guide Environnement Virtuel - MCP Real Estate

## ❓ Pourquoi l'Environnement Virtuel est Essentiel

Pour Claude Desktop, l'environnement virtuel doit être **actif en permanence** car :

1. **Claude Desktop lance le serveur MCP en arrière-plan**
2. **Les dépendances doivent être disponibles 24/7**
3. **Isolation des packages Python nécessaire**
4. **Évite les conflits avec d'autres projets Python**

## 🔧 Solutions Implémentées

### 1. Configuration Automatique

Le script `install.py` configure automatiquement Claude Desktop pour utiliser le Python de l'environnement virtuel :

```json
{
  "mcpServers": {
    "real-estate-mcp": {
      "command": "/chemin/vers/venv/Scripts/python.exe",
      "args": ["mcp_wrapper.py"],
      "env": {
        "PYTHONPATH": "/chemin/vers/src",
        "VIRTUAL_ENV": "/chemin/vers/venv"
      }
    }
  }
}
```

### 2. Wrapper de Sécurité (`mcp_wrapper.py`)

Le wrapper garantit que l'environnement virtuel est utilisé :

- ✅ **Détection automatique** si le venv est actif
- ✅ **Activation forcée** si nécessaire
- ✅ **Vérification des dépendances**
- ✅ **Gestion d'erreurs robuste**

### 3. Scripts de Démarrage

#### Windows : `run_with_venv.bat`
```batch
call venv\Scripts\activate.bat
python mcp_wrapper.py
```

#### Unix/Linux/Mac : `run_with_venv.sh`
```bash
source venv/bin/activate
python mcp_wrapper.py
```

## 🚀 Installation et Configuration

### Étape 1 : Installation Automatique
```bash
git clone https://github.com/USERNAME/real-estate-mcp.git
cd real-estate-mcp
python install.py
```

### Étape 2 : Configuration Claude Desktop

Le fichier `claude_desktop_config.json` est généré automatiquement :

#### Windows
```json
{
  "mcpServers": {
    "real-estate-mcp": {
      "command": "C:\\chemin\\vers\\projet\\venv\\Scripts\\python.exe",
      "args": ["C:\\chemin\\vers\\projet\\mcp_wrapper.py"],
      "cwd": "C:\\chemin\\vers\\projet"
    }
  }
}
```

#### Unix/Linux/Mac
```json
{
  "mcpServers": {
    "real-estate-mcp": {
      "command": "/chemin/vers/projet/venv/bin/python",
      "args": ["/chemin/vers/projet/mcp_wrapper.py"],
      "cwd": "/chemin/vers/projet"
    }
  }
}
```

### Étape 3 : Copier dans Claude Desktop

1. **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`
2. **macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
3. **Linux** : `~/.config/Claude/claude_desktop_config.json`

## 🔍 Vérification du Fonctionnement

### Test Manuel
```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Tester le wrapper
python mcp_wrapper.py
```

### Test avec Claude Desktop
1. Redémarrer Claude Desktop
2. Vérifier que "real-estate-mcp" apparaît dans les outils
3. Tester une recherche : "Trouve des studios à Antibes"

## 🛠️ Dépannage

### Problème : "Module not found"
```bash
# Vérifier l'environnement virtuel
python -c "import sys; print(sys.executable)"

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problème : "Environnement virtuel non trouvé"
```bash
# Recréer l'environnement virtuel
python -m venv venv

# Réinstaller
python install.py
```

### Problème : Claude Desktop ne trouve pas le MCP
1. Vérifier les chemins dans `claude_desktop_config.json`
2. S'assurer que les chemins sont absolus
3. Redémarrer Claude Desktop
4. Vérifier les logs de Claude Desktop

## 📊 Avantages de cette Approche

### ✅ Fiabilité
- L'environnement virtuel est **toujours** utilisé
- Pas de dépendance sur l'activation manuelle
- Détection automatique des problèmes

### ✅ Simplicité
- Installation en une commande
- Configuration automatique
- Pas de manipulation manuelle

### ✅ Robustesse
- Gestion d'erreurs complète
- Scripts de fallback
- Validation automatique

### ✅ Compatibilité
- Fonctionne sur Windows, macOS, Linux
- Compatible avec toutes les versions de Claude Desktop
- Indépendant de l'environnement système

## 🎯 Résultat Final

Avec cette configuration :

1. **Claude Desktop utilise automatiquement l'environnement virtuel**
2. **Toutes les dépendances sont disponibles 24/7**
3. **Aucune intervention manuelle nécessaire**
4. **Le MCP fonctionne de manière fiable et permanente**

**L'environnement virtuel est maintenant actif 100% du temps ! 🚀**
