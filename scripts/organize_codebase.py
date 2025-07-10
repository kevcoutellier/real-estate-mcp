#!/usr/bin/env python3
"""
Script d'organisation finale de la codebase MCP Real Estate
Nettoie et optimise la structure du projet selon les bonnes pratiques
"""

import os
import shutil
import sys
from pathlib import Path

def get_project_root():
    """Trouve la racine du projet"""
    current = Path(__file__).parent.parent
    return current

def organize_root_files():
    """Organise les fichiers à la racine du projet"""
    root = get_project_root()
    
    # Fichiers à déplacer vers des dossiers appropriés
    moves = {
        # Tests à déplacer
        'test_mcp_complete.py': 'tests/',
        'test_mcp_quick.py': 'tests/',
        'test_mcp_tools.py': 'tests/',
        
        # Logs à nettoyer
        'mcp_server.log': 'logs/',
        
        # Scripts de démarrage à organiser
        'start_mcp.bat': 'scripts/start/',
        'start_mcp.sh': 'scripts/start/',
        'run_with_venv.bat': 'scripts/start/',
        'run_with_venv.sh': 'scripts/start/',
        
        # Configuration à centraliser
        'claude_desktop_config.json': 'config/',
        'claude_desktop_config_portable.json': 'config/',
    }
    
    # Créer les dossiers nécessaires
    for target_dir in set(os.path.dirname(target) for target in moves.values()):
        target_path = root / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
    
    # Effectuer les déplacements
    moved_files = []
    for source, target in moves.items():
        source_path = root / source
        target_path = root / target / source
        
        if source_path.exists() and not target_path.exists():
            try:
                shutil.move(str(source_path), str(target_path))
                moved_files.append(f"{source} → {target}")
            except Exception as e:
                print(f"Erreur lors du déplacement de {source}: {e}")
    
    return moved_files

def clean_pycache():
    """Nettoie tous les dossiers __pycache__"""
    root = get_project_root()
    cleaned = []
    
    for pycache_dir in root.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
                cleaned.append(str(pycache_dir.relative_to(root)))
            except Exception as e:
                print(f"Erreur lors du nettoyage de {pycache_dir}: {e}")
    
    return cleaned

def organize_scripts():
    """Organise les scripts par catégorie"""
    root = get_project_root()
    scripts_dir = root / "scripts"
    
    # Catégories de scripts
    categories = {
        'validation': [
            'validate_github_ready.py',
            'validate_hardcoded_removal.py',
            'validate_no_demo_data.py',
            'validate_organization.py',
            'validate_real_data.py'
        ],
        'testing': [
            'test_antibes_fix.py',
            'test_antibes_search.py',
            'test_dynamic_service.py',
            'test_dynamic_vs_static.py'
        ],
        'maintenance': [
            'cleanup.py',
            'cleanup_project.py',
            'force_mcp_restart.py',
            'restart_mcp_dynamic.py',
            'restart_mcp_server.py'
        ],
        'development': [
            'diagnostic_mcp.py',
            'ai_conversation_simulator.py',
            'entreprise_friendly_activator.py'
        ],
        'installation': [
            'auto_install_seloger.py',
            'activate_dynamic.py'
        ]
    }
    
    # Créer les sous-dossiers
    organized = []
    for category in categories.keys():
        category_dir = scripts_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Déplacer les scripts
        for script in categories[category]:
            source = scripts_dir / script
            target = category_dir / script
            
            if source.exists() and not target.exists():
                try:
                    shutil.move(str(source), str(target))
                    organized.append(f"{script} → scripts/{category}/")
                except Exception as e:
                    print(f"Erreur lors du déplacement de {script}: {e}")
    
    return organized

def create_missing_init_files():
    """Crée les fichiers __init__.py manquants"""
    root = get_project_root()
    created = []
    
    # Dossiers qui doivent avoir un __init__.py
    python_dirs = [
        'src',
        'src/models',
        'src/services',
        'src/utils',
        'src/mcp',
        'src/scrapers',
        'tests'
    ]
    
    for dir_path in python_dirs:
        full_path = root / dir_path
        init_file = full_path / "__init__.py"
        
        if full_path.exists() and not init_file.exists():
            init_file.write_text('"""Package initialization file."""\n')
            created.append(str(init_file.relative_to(root)))
    
    return created

def update_gitignore():
    """Met à jour le .gitignore avec les patterns appropriés"""
    root = get_project_root()
    gitignore_path = root / ".gitignore"
    
    additional_patterns = [
        "",
        "# Organisation patterns",
        "logs/*.log",
        "*.tmp",
        "*.bak",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# IDE files",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "",
        "# Cache directories",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        "",
        "# Temporary files",
        "temp/",
        "tmp/",
        "*.temp"
    ]
    
    if gitignore_path.exists():
        current_content = gitignore_path.read_text()
        
        # Ajouter les nouveaux patterns s'ils n'existent pas
        new_patterns = []
        for pattern in additional_patterns:
            if pattern and pattern not in current_content:
                new_patterns.append(pattern)
        
        if new_patterns:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n'.join(new_patterns))
            return len(new_patterns)
    
    return 0

def create_organization_summary():
    """Crée un résumé de l'organisation finale"""
    root = get_project_root()
    summary_path = root / "CODEBASE_ORGANIZATION.md"
    
    content = """# Organisation de la Codebase MCP Real Estate

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
"""
    
    summary_path.write_text(content, encoding='utf-8')
    return str(summary_path.relative_to(root))

def main():
    """Fonction principale d'organisation"""
    print("🔧 Organisation de la codebase MCP Real Estate...")
    print("=" * 50)
    
    # 1. Nettoyer les caches
    print("\n1. Nettoyage des caches...")
    cleaned_cache = clean_pycache()
    if cleaned_cache:
        print(f"   ✅ {len(cleaned_cache)} dossiers __pycache__ nettoyés")
    else:
        print("   ✅ Aucun cache à nettoyer")
    
    # 2. Organiser les fichiers racine
    print("\n2. Organisation des fichiers racine...")
    moved_files = organize_root_files()
    if moved_files:
        for move in moved_files:
            print(f"   ✅ {move}")
    else:
        print("   ✅ Fichiers racine déjà organisés")
    
    # 3. Organiser les scripts
    print("\n3. Organisation des scripts...")
    organized_scripts = organize_scripts()
    if organized_scripts:
        for script in organized_scripts:
            print(f"   ✅ {script}")
    else:
        print("   ✅ Scripts déjà organisés")
    
    # 4. Créer les fichiers __init__.py
    print("\n4. Création des fichiers __init__.py...")
    created_init = create_missing_init_files()
    if created_init:
        for init_file in created_init:
            print(f"   ✅ {init_file}")
    else:
        print("   ✅ Tous les fichiers __init__.py existent")
    
    # 5. Mettre à jour .gitignore
    print("\n5. Mise à jour du .gitignore...")
    new_patterns = update_gitignore()
    if new_patterns > 0:
        print(f"   ✅ {new_patterns} nouveaux patterns ajoutés")
    else:
        print("   ✅ .gitignore déjà à jour")
    
    # 6. Créer le résumé d'organisation
    print("\n6. Création du résumé d'organisation...")
    summary_file = create_organization_summary()
    print(f"   ✅ {summary_file} créé")
    
    print("\n" + "=" * 50)
    print("🎉 Organisation terminée avec succès !")
    print("\n📋 Résumé des actions :")
    print(f"   • Caches nettoyés : {len(cleaned_cache)}")
    print(f"   • Fichiers déplacés : {len(moved_files)}")
    print(f"   • Scripts organisés : {len(organized_scripts)}")
    print(f"   • Fichiers __init__.py créés : {len(created_init)}")
    print(f"   • Patterns .gitignore ajoutés : {new_patterns}")
    print(f"   • Documentation créée : {summary_file}")
    
    print("\n🚀 La codebase est maintenant parfaitement organisée !")

if __name__ == "__main__":
    main()
