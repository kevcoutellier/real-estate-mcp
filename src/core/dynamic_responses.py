"""
Système de réponses dynamiques et contextuelles.
Remplace les formats de sortie rigides par des réponses adaptatives.
"""

import json
import random
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter(ABC):
    """Interface pour les formateurs de réponse adaptatifs."""
    
    @abstractmethod
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les données selon le contexte."""
        pass


class ContextualResponseSystem:
    """Système de réponses contextuelles et dynamiques."""
    
    def __init__(self):
        self.formatters = {
            'detailed': DetailedFormatter(),
            'summary': SummaryFormatter(),
            'conversational': ConversationalFormatter(),
            'technical': TechnicalFormatter(),
            'investment': InvestmentFormatter(),
            'family': FamilyFormatter()
        }
        
        self.tone_adapters = {
            'professional': self._professional_tone,
            'casual': self._casual_tone,
            'expert': self._expert_tone,
            'beginner': self._beginner_tone
        }
    
    def generate_response(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Génère une réponse adaptée au contexte."""
        if context is None:
            context = self._infer_context(data)
        
        # Sélection du formateur
        formatter_type = context.get('format', 'conversational')
        formatter = self.formatters.get(formatter_type, self.formatters['conversational'])
        
        # Formatage initial
        response = formatter.format(data, context)
        
        # Adaptation du ton
        tone = context.get('tone', 'professional')
        if tone in self.tone_adapters:
            response = self.tone_adapters[tone](response, context)
        
        # Enrichissement contextuel
        response = self._enrich_response(response, context)
        
        return response
    
    def _infer_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Infère le contexte à partir des données."""
        context = {
            'timestamp': datetime.now().isoformat(),
            'format': 'conversational',
            'tone': 'professional'
        }
        
        # Inférence basée sur les données
        if 'investment_scores' in data:
            context['format'] = 'investment'
        elif 'family_suitability' in data:
            context['format'] = 'family'
        elif data.get('total_properties', 0) > 50:
            context['format'] = 'summary'
        
        return context
    
    def _professional_tone(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Applique un ton professionnel."""
        if 'summary' in response:
            response['summary'] = f"Analyse professionnelle: {response['summary']}"
        return response
    
    def _casual_tone(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Applique un ton décontracté."""
        casual_phrases = [
            "Voici ce qu'on a trouvé:",
            "Alors, regardons ça de plus près:",
            "Intéressant! Voici les points clés:"
        ]
        
        if 'summary' in response:
            intro = random.choice(casual_phrases)
            response['summary'] = f"{intro} {response['summary']}"
        
        return response
    
    def _expert_tone(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Applique un ton d'expert."""
        if 'insights' in response:
            response['expert_analysis'] = response.pop('insights')
        return response
    
    def _beginner_tone(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapte pour les débutants."""
        if 'technical_details' in response:
            response['explanations'] = response.pop('technical_details')
        return response
    
    def _enrich_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit la réponse avec des éléments contextuels."""
        # Ajout de métadonnées contextuelles
        response['context'] = {
            'analysis_type': context.get('format', 'general'),
            'confidence_level': self._calculate_confidence(response),
            'recommendations': self._generate_recommendations(response, context)
        }
        
        return response
    
    def _calculate_confidence(self, response: Dict[str, Any]) -> float:
        """Calcule un niveau de confiance pour la réponse."""
        confidence = 0.5  # Base
        
        if response.get('total_properties', 0) > 10:
            confidence += 0.2
        if 'price_analysis' in response and response['price_analysis'].get('count', 0) > 5:
            confidence += 0.2
        if len(response.get('insights', [])) > 3:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_recommendations(self, response: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Génère des recommandations contextuelles."""
        recommendations = []
        
        format_type = context.get('format', 'general')
        
        if format_type == 'investment':
            recommendations.append("Considérez la diversification géographique")
            recommendations.append("Analysez les tendances de marché à long terme")
        elif format_type == 'family':
            recommendations.append("Vérifiez la proximité des écoles")
            recommendations.append("Considérez les espaces verts à proximité")
        
        return recommendations


class DetailedFormatter(ResponseFormatter):
    """Formateur détaillé avec toutes les informations."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'detailed_analysis',
            'summary': self._create_detailed_summary(data),
            'statistics': data.get('price_analysis', {}),
            'insights': data.get('insights', []),
            'raw_data': data,
            'analysis_depth': 'comprehensive'
        }
    
    def _create_detailed_summary(self, data: Dict[str, Any]) -> str:
        total = data.get('total_properties', 0)
        price_stats = data.get('price_analysis', {})
        
        summary_parts = [f"Analyse détaillée de {total} propriétés."]
        
        if price_stats.get('mean'):
            summary_parts.append(f"Prix moyen: {price_stats['mean']:,.0f}€")
        if price_stats.get('median'):
            summary_parts.append(f"Prix médian: {price_stats['median']:,.0f}€")
        
        return " ".join(summary_parts)


class SummaryFormatter(ResponseFormatter):
    """Formateur résumé pour les grandes quantités de données."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'market_summary',
            'key_metrics': self._extract_key_metrics(data),
            'highlights': self._create_highlights(data),
            'quick_insights': data.get('insights', [])[:3]  # Top 3
        }
    
    def _extract_key_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        metrics = {}
        
        if 'price_analysis' in data:
            price_data = data['price_analysis']
            metrics['price_range'] = f"{price_data.get('min', 0):,.0f}€ - {price_data.get('max', 0):,.0f}€"
            metrics['average_price'] = f"{price_data.get('mean', 0):,.0f}€"
        
        metrics['total_properties'] = data.get('total_properties', 0)
        
        return metrics
    
    def _create_highlights(self, data: Dict[str, Any]) -> List[str]:
        highlights = []
        
        total = data.get('total_properties', 0)
        if total > 100:
            highlights.append(f"Large échantillon de {total} propriétés")
        
        price_analysis = data.get('price_analysis', {})
        if price_analysis.get('outliers'):
            highlights.append(f"{len(price_analysis['outliers'])} prix atypiques détectés")
        
        return highlights


class ConversationalFormatter(ResponseFormatter):
    """Formateur conversationnel et naturel."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'conversational_response',
            'message': self._create_conversational_message(data),
            'key_points': self._extract_conversation_points(data),
            'follow_up_suggestions': self._suggest_follow_ups(data)
        }
    
    def _create_conversational_message(self, data: Dict[str, Any]) -> str:
        total = data.get('total_properties', 0)
        
        if total == 0:
            return "Je n'ai pas trouvé de propriétés correspondant à vos critères."
        
        price_stats = data.get('price_analysis', {})
        
        message_parts = [
            f"J'ai analysé {total} propriétés pour vous.",
        ]
        
        if price_stats.get('mean'):
            avg_price = price_stats['mean']
            if avg_price > 500000:
                message_parts.append("On est sur un marché plutôt haut de gamme.")
            elif avg_price < 200000:
                message_parts.append("Les prix sont plutôt accessibles.")
            else:
                message_parts.append("Les prix sont dans la moyenne du marché.")
        
        return " ".join(message_parts)
    
    def _extract_conversation_points(self, data: Dict[str, Any]) -> List[str]:
        points = []
        
        insights = data.get('insights', [])
        for insight in insights[:3]:  # Top 3 insights
            points.append(f"💡 {insight}")
        
        return points
    
    def _suggest_follow_ups(self, data: Dict[str, Any]) -> List[str]:
        suggestions = [
            "Voulez-vous que je me concentre sur une zone particulière?",
            "Souhaitez-vous une analyse plus détaillée des prix?",
            "Puis-je vous aider à identifier les meilleures opportunités?"
        ]
        
        return suggestions[:2]  # Limite à 2 suggestions


class TechnicalFormatter(ResponseFormatter):
    """Formateur technique avec métriques avancées."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'technical_analysis',
            'statistical_summary': self._create_statistical_summary(data),
            'metrics': self._calculate_advanced_metrics(data),
            'data_quality': self._assess_data_quality(data),
            'methodology': self._describe_methodology(data)
        }
    
    def _create_statistical_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        price_stats = data.get('price_analysis', {})
        
        return {
            'sample_size': data.get('total_properties', 0),
            'price_distribution': {
                'mean': price_stats.get('mean'),
                'median': price_stats.get('median'),
                'std_deviation': price_stats.get('std_dev'),
                'coefficient_variation': price_stats.get('coefficient_variation')
            },
            'outlier_detection': {
                'count': len(price_stats.get('outliers', [])),
                'values': price_stats.get('outliers', [])
            }
        }
    
    def _calculate_advanced_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'market_concentration': self._calculate_concentration(data),
            'price_volatility': self._calculate_volatility(data),
            'diversity_index': self._calculate_diversity(data)
        }
    
    def _calculate_concentration(self, data: Dict[str, Any]) -> float:
        """Calcule l'indice de concentration du marché."""
        locations = data.get('location_distribution', {}).get('raw_locations', {})
        if not locations:
            return 0.0
        
        total = sum(locations.values())
        hhi = sum((count/total)**2 for count in locations.values())
        return round(hhi, 3)
    
    def _calculate_volatility(self, data: Dict[str, Any]) -> float:
        """Calcule la volatilité des prix."""
        price_stats = data.get('price_analysis', {})
        mean = price_stats.get('mean', 0)
        std_dev = price_stats.get('std_dev', 0)
        
        return round(std_dev / mean, 3) if mean > 0 else 0.0
    
    def _calculate_diversity(self, data: Dict[str, Any]) -> float:
        """Calcule l'indice de diversité des types de propriétés."""
        prop_types = data.get('property_types', {})
        if not prop_types:
            return 0.0
        
        total = sum(prop_types.values())
        shannon_index = -sum((count/total) * math.log(count/total) for count in prop_types.values() if count > 0)
        return round(shannon_index, 3)
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la qualité des données."""
        total = data.get('total_properties', 0)
        
        return {
            'completeness': 'high' if total > 20 else 'medium' if total > 5 else 'low',
            'sample_size': total,
            'data_freshness': 'current',  # À adapter selon les timestamps
            'reliability_score': min(1.0, total / 50)
        }
    
    def _describe_methodology(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Décrit la méthodologie d'analyse."""
        return {
            'analysis_type': 'statistical_market_analysis',
            'price_calculation': 'mean_median_with_outlier_detection',
            'trend_identification': 'comparative_analysis',
            'confidence_interval': '95%'
        }


class InvestmentFormatter(ResponseFormatter):
    """Formateur spécialisé pour l'investissement."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'investment_analysis',
            'investment_summary': self._create_investment_summary(data),
            'opportunities': self._identify_opportunities(data),
            'risk_assessment': self._assess_risks(data),
            'recommendations': self._generate_investment_recommendations(data)
        }
    
    def _create_investment_summary(self, data: Dict[str, Any]) -> str:
        roi_data = data.get('roi_projections', {})
        scores = data.get('investment_scores', {})
        
        if not roi_data and not scores:
            return "Analyse d'investissement en cours..."
        
        high_score_count = sum(1 for score in scores.values() if score > 0.7) if scores else 0
        
        return f"Potentiel d'investissement identifié sur {high_score_count} propriétés avec scores élevés."
    
    def _identify_opportunities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'investissement."""
        opportunities = []
        
        value_opps = data.get('value_opportunities', [])
        for opp in value_opps[:5]:  # Top 5
            opportunities.append({
                'type': 'value_opportunity',
                'description': f"Prix attractif: {opp.get('value', 0):.0f}€/m²",
                'property_id': opp.get('property_id')
            })
        
        return opportunities
    
    def _assess_risks(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Évalue les risques d'investissement."""
        price_stats = data.get('price_analysis', {})
        volatility = price_stats.get('coefficient_variation', 0)
        
        risk_level = 'low'
        if volatility > 0.3:
            risk_level = 'high'
        elif volatility > 0.15:
            risk_level = 'medium'
        
        return {
            'market_volatility': risk_level,
            'liquidity_risk': 'medium',  # À calculer selon les données de marché
            'overall_assessment': risk_level
        }
    
    def _generate_investment_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'investissement."""
        recommendations = []
        
        market_type = data.get('context', {}).get('market_type', 'general')
        
        if market_type == 'luxury':
            recommendations.append("Marché de luxe: privilégiez la qualité et l'emplacement")
        elif market_type == 'budget':
            recommendations.append("Marché accessible: opportunités de plus-value à long terme")
        
        recommendations.append("Diversifiez vos investissements géographiquement")
        recommendations.append("Considérez les tendances démographiques locales")
        
        return recommendations


class FamilyFormatter(ResponseFormatter):
    """Formateur spécialisé pour les familles."""
    
    def format(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'family_analysis',
            'family_summary': self._create_family_summary(data),
            'suitable_properties': self._count_suitable_properties(data),
            'family_criteria': self._analyze_family_criteria(data),
            'neighborhood_factors': self._assess_neighborhood_factors(data)
        }
    
    def _create_family_summary(self, data: Dict[str, Any]) -> str:
        suitability = data.get('family_suitability', {})
        rate = suitability.get('suitability_rate', 0)
        
        if rate > 70:
            return f"Excellent choix pour les familles: {rate:.0f}% des biens sont adaptés."
        elif rate > 40:
            return f"Bon potentiel familial: {rate:.0f}% des biens conviennent aux familles."
        else:
            return f"Options limitées pour les familles: seulement {rate:.0f}% des biens sont adaptés."
    
    def _count_suitable_properties(self, data: Dict[str, Any]) -> int:
        suitability = data.get('family_suitability', {})
        return suitability.get('suitable_properties', 0)
    
    def _analyze_family_criteria(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les critères importants pour les familles."""
        surface_analysis = data.get('surface_analysis', {})
        
        return {
            'space_adequacy': 'good' if surface_analysis.get('mean', 0) > 70 else 'limited',
            'room_distribution': data.get('location_distribution', {}),
            'family_friendly_features': self._count_family_features(data)
        }
    
    def _count_family_features(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Compte les caractéristiques importantes pour les familles."""
        # Cette logique serait enrichie avec des données réelles
        return {
            'gardens': 0,  # À calculer depuis les propriétés
            'parking_spaces': 0,
            'elevators': 0,
            'balconies': 0
        }
    
    def _assess_neighborhood_factors(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Évalue les facteurs de quartier pour les familles."""
        return {
            'school_proximity': 'unknown',  # À enrichir avec des données externes
            'safety_rating': 'unknown',
            'green_spaces': 'unknown',
            'public_transport': 'unknown'
        }


# Utilitaire pour importer math si nécessaire
try:
    import math
except ImportError:
    # Fallback simple si math n'est pas disponible
    class math:
        @staticmethod
        def log(x):
            return 0.0  # Fallback simple
