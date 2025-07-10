# 🏠 MCP Immobilier

Agrégateur d'annonces immobilières françaises via Model Context Protocol (MCP).

## 🚀 Installation rapide

\`\`\`bash
# Cloner et installer
git clone <your-repo>
cd real-estate-mcp
make install

# Activer l'environnement
source venv/bin/activate

# Tester
make test
\`\`\`

## 📋 Fonctionnalités

### ✅ Semaine 1 (Actuel)
- [x] Scraping LeBonCoin
- [x] Recherche par critères
- [x] Résumé de marché
- [x] Cache simple
- [x] Déduplication de base

### 🔄 Semaine 2 (Prochaine)
- [ ] Scraping SeLoger
- [ ] Géocodage automatique
- [ ] Enrichissement quartier
- [ ] Amélioration déduplication

## 🔧 Utilisation

### Recherche simple
\`\`\`python
from src.main import RealEstateMCP

mcp = RealEstateMCP()
results = await mcp.search_properties(
    location="Paris 11e",
    min_price=1000,
    max_price=2000,
    transaction_type="rent"
)
\`\`\`

### Résumé de marché
\`\`\`python
summary = await mcp.get_property_summary("Lyon")
print(f"Prix moyen: {summary['price_stats']['avg']}€")
\`\`\`

## 🛠️ Développement

\`\`\`bash
# Tests
make test

# Lancement en dev
make run

# Nettoyage
make clean
\`\`\`

## 📊 Performances cibles

- **Résultats**: 50+ annonces par recherche
- **Vitesse**: <5s par requête
- **Sources**: 3+ sites immobiliers
- **Précision**: 90%+ géocodage

## 🔮 Roadmap

1. **Semaine 1**: Base + LeBonCoin ✅
2. **Semaine 2**: Multi-sources + géocodage
3. **Semaine 3**: Analyse + intelligence
4. **Semaine 4**: Production-ready

## 📞 Support

- Issues: [GitHub Issues](link)
- Docs: [Documentation](link)
- Contact: your-email@example.com
EOF

echo "✅ Configuration terminée !"
echo ""
echo "🚀 Prochaines étapes:"
echo "1. cd real-estate-mcp"
echo "2. source venv/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. python test_mcp.py"
echo ""
echo "📝 Ensuite, copiez le code principal dans src/main.py"