# 🚀 Guide de Déploiement MCP Real Estate

## ❌ Pourquoi copier juste le config.json ne suffit pas

Votre configuration actuelle utilise des **chemins absolus Windows** :
```json
"command": "C:\\Users\\kcoutellier\\Documents\\MCP\\real-estate-MCP\\venv\\Scripts\\python.exe"
```

Cela ne fonctionnera pas sur d'autres machines car :
- Les chemins sont spécifiques à votre système
- L'environnement virtuel n'existe pas ailleurs
- Les dépendances ne sont pas installées

## ✅ Solution : Déploiement Complet

### 1. Préparer le repository GitHub

```bash
# Créer un .gitignore approprié
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "logs/" >> .gitignore
echo "cache/" >> .gitignore
echo "claude_desktop_config.json" >> .gitignore
```

### 2. Créer un requirements.txt

Assurez-vous d'avoir un fichier `requirements.txt` avec toutes les dépendances :
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0
mcp>=1.0.0
```

### 3. Instructions pour l'utilisateur final

L'utilisateur qui clone votre repo doit :

#### Étape 1 : Cloner le repository
```bash
git clone https://github.com/votre-username/real-estate-MCP.git
cd real-estate-MCP
```

#### Étape 2 : Exécuter l'installation automatique
```bash
python install.py
```

#### Étape 3 : Copier la configuration générée
Le script `install.py` génère automatiquement `claude_desktop_config.json` avec les bons chemins.

L'utilisateur doit copier le contenu de ce fichier dans sa configuration Claude Desktop :
- **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac** : `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux** : `~/.config/claude/claude_desktop_config.json`

#### Étape 4 : Redémarrer Claude Desktop

## 🛠️ Fichiers à inclure dans le repository

### Fichiers essentiels :
- ✅ `install.py` (script d'installation automatique)
- ✅ `requirements.txt` (dépendances Python)
- ✅ `README.md` (documentation utilisateur)
- ✅ `src/` (code source)
- ✅ `mcp_wrapper.py` (wrapper MCP)
- ✅ `start_server.py` (serveur principal)

### Fichiers à exclure (.gitignore) :
- ❌ `venv/` (environnement virtuel)
- ❌ `claude_desktop_config.json` (configuration locale)
- ❌ `__pycache__/` (cache Python)
- ❌ `logs/` (fichiers de log)

## 📋 Checklist de déploiement

- [ ] Repository GitHub créé
- [ ] .gitignore configuré
- [ ] requirements.txt à jour
- [ ] README.md avec instructions claires
- [ ] Script install.py testé
- [ ] Configuration locale supprimée du repo
- [ ] Tests de déploiement effectués

## 🎯 Résultat attendu

Après déploiement, n'importe qui peut :
1. Cloner votre repository
2. Exécuter `python install.py`
3. Copier la configuration générée dans Claude Desktop
4. Utiliser votre MCP immédiatement

## ⚠️ Notes importantes

- Le script `install.py` détecte automatiquement l'OS (Windows/Mac/Linux)
- Les chemins sont générés dynamiquement selon l'environnement
- L'environnement virtuel est créé localement sur chaque machine
- Les dépendances sont installées automatiquement
