#!/usr/bin/env python3
"""
Simulateur de conversation IA pour tester l'interface
Créez ce fichier: ai_conversation_simulator.py
"""

import asyncio
import json
import sys
import os
import re
from typing import Dict, List, Any

# Ajouter le chemin vers le serveur MCP
sys.path.insert(0, '.')

class AIConversationSimulator:
    """Simulateur d'IA conversationnelle pour tester le MCP"""
    
    def __init__(self):
        # Import dynamique pour éviter les erreurs
        try:
            from mcp_server import MCPServer
            self.mcp_server = MCPServer()
            self.available = True
        except Exception as e:
            print(f"⚠️ Erreur chargement MCP Server: {e}")
            self.available = False
    
    def parse_user_intent(self, user_message: str) -> Dict[str, Any]:
        """Parse l'intention de l'utilisateur et les paramètres"""
        
        intent = {
            "action": "unknown",
            "parameters": {},
            "confidence": 0.0
        }
        
        message_lower = user_message.lower()
        
        # Patterns de recherche
        search_patterns = [
            r"trouve.* (appartement|maison|logement|t\d|studio)",
            r"cherche.* (appartement|maison|logement|t\d|studio)",
            r"recherche.* (appartement|maison|logement|t\d|studio)",
            r"(appartement|maison|logement|t\d|studio).* à louer",
            r"(appartement|maison|logement|t\d|studio).* à vendre"
        ]
        
        # Patterns d'analyse
        analysis_patterns = [
            r"analyse.* marché",
            r"marché.* (immobilier|de)",
            r"statistiques.* (immobilier|prix)",
            r"tendances.* (immobilier|prix)"
        ]
        
        # Patterns de comparaison
        comparison_patterns = [
            r"compare.* (avec|vs|versus|et)",
            r"différence.* entre",
            r"meilleur.* entre",
            r"(vs|versus)"
        ]
        
        # Détection de l'action principale
        if any(re.search(pattern, message_lower) for pattern in search_patterns):
            intent["action"] = "search_properties"
            intent["confidence"] = 0.8
        elif any(re.search(pattern, message_lower) for pattern in analysis_patterns):
            intent["action"] = "analyze_market"
            intent["confidence"] = 0.9
        elif any(re.search(pattern, message_lower) for pattern in comparison_patterns):
            intent["action"] = "compare_locations"
            intent["confidence"] = 0.85
        
        # Extraction des paramètres
        
        # Localisation
        location_patterns = [
            r"à ([A-Za-z\s\d°]+?)(?:\s|,|$|\.)",
            r"dans (?:le |la |les )?([A-Za-z\s\d°]+?)(?:\s|,|$|\.)",
            r"paris (\d+)e?",
            r"(\d+)(?:e|ème) arrondissement",
            r"(lyon|marseille|toulouse|nice|nantes|strasbourg|bordeaux|lille|rennes|montpellier)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).strip()
                if location:
                    # Nettoyage et standardisation
                    if re.match(r'^\d+$', location):
                        intent["parameters"]["location"] = f"Paris {location}e"
                    else:
                        intent["parameters"]["location"] = location.title()
                    break
        
        # Prix
        price_patterns = [
            r"budget (\d+)(?:\s?€)?",
            r"max (\d+)(?:\s?€)?",
            r"maximum (\d+)(?:\s?€)?",
            r"jusqu'à (\d+)(?:\s?€)?",
            r"entre (\d+)(?:\s?€)? et (\d+)(?:\s?€)?",
            r"(\d+)(?:\s?€)? à (\d+)(?:\s?€)?"
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if "entre" in pattern or "à" in pattern:
                    intent["parameters"]["min_price"] = int(match.group(1))
                    intent["parameters"]["max_price"] = int(match.group(2))
                else:
                    intent["parameters"]["max_price"] = int(match.group(1))
                break
        
        # Type de bien
        if re.search(r"t\d", message_lower):
            rooms_match = re.search(r"t(\d)", message_lower)
            if rooms_match:
                intent["parameters"]["rooms"] = int(rooms_match.group(1))
                intent["parameters"]["property_type"] = "appartement"
        elif "studio" in message_lower:
            intent["parameters"]["rooms"] = 1
            intent["parameters"]["property_type"] = "appartement"
        elif "appartement" in message_lower:
            intent["parameters"]["property_type"] = "appartement"
        elif "maison" in message_lower:
            intent["parameters"]["property_type"] = "maison"
        
        # Surface
        surface_match = re.search(r"(\d+)\s*m²?", message_lower)
        if surface_match:
            intent["parameters"]["min_surface"] = int(surface_match.group(1))
        
        # Transaction type
        if any(word in message_lower for word in ["louer", "location", "locatif"]):
            intent["parameters"]["transaction_type"] = "rent"
        elif any(word in message_lower for word in ["acheter", "achat", "vente", "investissement"]):
            intent["parameters"]["transaction_type"] = "sale"
        
        # Gestion spéciale pour les comparaisons
        if intent["action"] == "compare_locations":
            # Extraire les localisations multiples
            locations = []
            compare_patterns = [
                r"compare ([A-Za-z\s\d°]+?) (?:avec|vs|versus|et) ([A-Za-z\s\d°]+)",
                r"([A-Za-z\s\d°]+?) (?:vs|versus) ([A-Za-z\s\d°]+)",
                r"entre ([A-Za-z\s\d°]+?) et ([A-Za-z\s\d°]+)"
            ]
            
            for pattern in compare_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    locations = [match.group(1).strip().title(), match.group(2).strip().title()]
                    break
            
            if locations:
                intent["parameters"]["locations"] = locations
        
        return intent
    
    async def process_user_message(self, user_message: str) -> str:
        """Traite un message utilisateur et retourne une réponse IA"""
        
        if not self.available:
            return "❌ Serveur MCP non disponible. Vérifiez l'installation."
        
        # Parse l'intention
        intent = self.parse_user_intent(user_message)
        
        if intent["confidence"] < 0.5:
            return f"""Je ne suis pas sûr de comprendre votre demande. Voici ce que je peux faire :

🔍 **Rechercher des biens** : "Trouve-moi un T2 à Paris 11e sous 1500€"
📊 **Analyser le marché** : "Analyse le marché immobilier de Lyon"  
🔄 **Comparer des quartiers** : "Compare Paris 11e vs Paris 16e"
🏘️ **Analyser un quartier** : "Analyse du quartier République"

Pouvez-vous reformuler votre demande ?"""
        
        # Exécuter l'action correspondante
        try:
            result = await self.mcp_server.handle_request(intent["action"], intent["parameters"])
            
            if "error" in result:
                return f"❌ Erreur : {result['error']}"
            
            # Générer une réponse naturelle
            return self.generate_natural_response(intent["action"], result, user_message)
            
        except Exception as e:
            return f"❌ Erreur lors du traitement : {str(e)}"
    
    def generate_natural_response(self, action: str, result: Dict[str, Any], original_message: str) -> str:
        """Génère une réponse naturelle à partir des résultats"""
        
        if action == "search_properties":
            return self.format_search_response(result)
        elif action == "analyze_market":
            return self.format_market_analysis(result)
        elif action == "compare_locations":
            return self.format_comparison_response(result)
        else:
            return f"Résultat obtenu :\n{json.dumps(result, indent=2, ensure_ascii=False)}"
    
    def format_search_response(self, result: Dict[str, Any]) -> str:
        """Formate la réponse de recherche"""
        
        count = result.get("count", 0)
        properties = result.get("properties", [])
        summary = result.get("summary", {})
        
        if count == 0:
            return "😔 Aucun bien trouvé avec ces critères. Essayez d'élargir votre recherche !"
        
        response = f"🏠 **J'ai trouvé {count} biens qui correspondent à vos critères !**\n\n"
        
        # Résumé
        avg_price = summary.get("avg_price", 0)
        price_range = summary.get("price_range", {})
        
        if avg_price > 0:
            response += f"💰 **Prix moyen** : {avg_price:.0f}€\n"
            response += f"📊 **Fourchette** : {price_range.get('min', 0):.0f}€ - {price_range.get('max', 0):.0f}€\n\n"
        
        # Top 3 des biens
        response += "🏆 **Mes 3 meilleures suggestions :**\n\n"
        
        for i, prop in enumerate(properties[:3], 1):
            title = prop.get("title", "Sans titre")[:60]
            price = prop.get("price", 0)
            location = prop.get("location", "Localisation inconnue")
            surface = prop.get("surface_area")
            source = prop.get("source", "")
            
            response += f"**{i}. {title}{'...' if len(prop.get('title', '')) > 60 else ''}**\n"
            response += f"   💰 {price}€"
            
            if surface:
                response += f" | 📐 {surface}m²"
                if price > 0 and surface > 0:
                    price_per_sqm = price / surface
                    response += f" | 💎 {price_per_sqm:.0f}€/m²"
            
            response += f"\n   📍 {location} | 🏢 {source}\n\n"
        
        if count > 3:
            response += f"... et {count - 3} autres biens disponibles !\n\n"
        
        # Conseil personnalisé
        if avg_price > 2000:
            response += "💡 **Conseil** : Ce quartier est plutôt haut de gamme. Vous pourriez trouver de meilleures affaires dans les arrondissements voisins."
        elif avg_price < 1000:
            response += "💡 **Conseil** : Excellentes opportunités dans cette zone ! Vérifiez bien l'état des biens à ces prix."
        
        return response
    
    def format_market_analysis(self, result: Dict[str, Any]) -> str:
        """Formate l'analyse de marché"""
        
        location = result.get("location", "Zone inconnue")
        total = result.get("total_properties", 0)
        market_stats = result.get("market_stats", {})
        
        response = f"📊 **Analyse du marché immobilier - {location}**\n\n"
        
        if total == 0:
            return f"{response}😔 Aucune donnée disponible pour cette zone."
        
        # Statistiques principales
        avg_price = market_stats.get("average_price", 0)
        median_price = market_stats.get("median_price", 0)
        price_range = market_stats.get("price_range", {})
        
        response += f"🏠 **{total} annonces** analysées\n\n"
        
        response += "💰 **Analyse des prix :**\n"
        response += f"   • Prix moyen : {avg_price:.0f}€\n"
        response += f"   • Prix médian : {median_price:.0f}€\n"
        response += f"   • Fourchette : {price_range.get('min', 0):.0f}€ - {price_range.get('max', 0):.0f}€\n\n"
        
        # Prix au m² si disponible
        price_per_sqm = result.get("price_per_sqm")
        if price_per_sqm:
            response += "📐 **Prix au m² :**\n"
            response += f"   • Moyen : {price_per_sqm.get('average', 0):.0f}€/m²\n"
            response += f"   • Min-Max : {price_per_sqm.get('min', 0):.0f}€ - {price_per_sqm.get('max', 0):.0f}€/m²\n\n"
        
        # Répartition par source
        sources = result.get("sources_breakdown", {})
        if sources:
            response += "📱 **Sources des annonces :**\n"
            for source, count in sources.items():
                percentage = (count / total) * 100
                response += f"   • {source} : {count} annonces ({percentage:.1f}%)\n"
            response += "\n"
        
        # Types de biens
        prop_types = result.get("property_types", {})
        if prop_types:
            response += "🏘️ **Types de biens :**\n"
            for prop_type, count in prop_types.items():
                percentage = (count / total) * 100
                response += f"   • {prop_type} : {count} ({percentage:.1f}%)\n"
            response += "\n"
        
        # Insights et recommandations
        response += "💡 **Insights :**\n"
        
        if avg_price > 0:
            if avg_price < 1200:
                response += "   • 🟢 Zone abordable, bonne opportunité pour primo-accédants\n"
            elif avg_price > 2500:
                response += "   • 🟡 Zone premium, marché haut de gamme\n"
            else:
                response += "   • 🔵 Zone équilibrée, prix dans la moyenne du marché\n"
        
        if total > 50:
            response += "   • 📈 Marché dynamique avec beaucoup d'offres\n"
        elif total < 10:
            response += "   • 📉 Marché restreint, peu d'offres disponibles\n"
        
        return response
    
    def format_comparison_response(self, result: Dict[str, Any]) -> str:
        """Formate la réponse de comparaison"""
        
        locations = result.get("locations_compared", [])
        comparison_data = result.get("comparison_data", {})
        recommendations = result.get("recommendations", [])
        
        if len(locations) < 2:
            return "❌ Impossible de comparer moins de 2 localisations."
        
        response = f"🔄 **Comparaison : {' vs '.join(locations)}**\n\n"
        
        # Tableau de comparaison
        response += "| Critère | " + " | ".join(locations) + " |\n"
        response += "|---------|" + "|".join(["-" * (len(loc) + 2) for loc in locations]) + "|\n"
        
        # Nombre d'annonces
        counts = [str(comparison_data.get(loc, {}).get("total_properties", 0)) for loc in locations]
        response += "| 🏠 Annonces | " + " | ".join(counts) + " |\n"
        
        # Prix moyens
        prices = [f"{comparison_data.get(loc, {}).get('average_price', 0):.0f}€" for loc in locations]
        response += "| 💰 Prix moyen | " + " | ".join(prices) + " |\n"
        
        # Prix au m² si disponible
        price_per_sqm = [f"{comparison_data.get(loc, {}).get('price_per_sqm', 0):.0f}€/m²" for loc in locations]
        if any(float(p.replace('€/m²', '')) > 0 for p in price_per_sqm):
            response += "| 📐 Prix/m² | " + " | ".join(price_per_sqm) + " |\n"
        
        response += "\n"
        
        # Recommandations
        if recommendations:
            response += "🏆 **Mes recommandations :**\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                rec_type = rec.get("type", "")
                location = rec.get("location", "")
                reason = rec.get("reason", "")
                
                if rec_type == "most_affordable":
                    emoji = "💰"
                    title = "Meilleur prix"
                elif rec_type == "best_value_per_sqm":
                    emoji = "💎"
                    title = "Meilleur rapport qualité-prix"
                elif rec_type == "most_options":
                    emoji = "📈"
                    title = "Plus grand choix"
                else:
                    emoji = "🎯"
                    title = "Recommandation"
                
                response += f"**{emoji} {title} : {location}**\n"
                response += f"   {reason}\n\n"
        
        # Conseil final
        response += "💡 **Conseil** : La comparaison dépend de vos priorités (budget, surface, choix d'annonces). "
        response += "N'hésitez pas à me demander une analyse plus détaillée d'un quartier spécifique !"
        
        return response

# Interface de test conversationnel
async def test_conversation():
    """Test interactif de la conversation IA"""
    
    simulator = AIConversationSimulator()
    
    if not simulator.available:
        print("❌ Simulateur non disponible")
        return
    
    print("🤖 Simulateur de conversation IA - MCP Immobilier")
    print("=" * 60)
    print("Tapez vos questions comme si vous parliez à Claude !")
    print("Exemples :")
    print("- 'Trouve-moi un T2 à Paris 11e sous 1500€'")
    print("- 'Analyse le marché immobilier de Lyon'")
    print("- 'Compare Paris 11e vs Paris 16e'")
    print("\nTapez 'quit' pour quitter\n")
    
    while True:
        try:
            user_input = input("🗣️  Vous : ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir !")
                break
            
            if not user_input:
                continue
            
            print("🤖 Claude : Analyse de votre demande...")
            response = await simulator.process_user_message(user_input)
            print(f"🤖 Claude : {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur : {e}")

# Tests automatisés
async def run_automated_tests():
    """Tests automatisés des requêtes conversationnelles"""
    
    simulator = AIConversationSimulator()
    
    test_queries = [
        "Trouve-moi un appartement à Paris 11e entre 1000€ et 1800€",
        "Analyse le marché immobilier de Paris 11e", 
        "Compare Paris 11e vs Paris 16e",
        "Je cherche un T2 sous 1500€ à Lyon",
        "Quel est le prix moyen des appartements à Marseille ?"
    ]
    
    print("🧪 Tests automatisés des requêtes conversationnelles")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        response = await simulator.process_user_message(query)
        print(f"🤖 Réponse: {response[:200]}{'...' if len(response) > 200 else ''}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(run_automated_tests())
    else:
        asyncio.run(test_conversation())