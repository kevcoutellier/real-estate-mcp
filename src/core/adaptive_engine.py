"""
Moteur d'adaptation contextuelle pour l'analyse immobilière.
Remplace la logique déterministe par des algorithmes adaptatifs.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextualRule:
    """Règle contextuelle adaptative."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    priority: int = 1
    active: bool = True
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class AdaptationContext:
    """Contexte d'adaptation avec historique."""
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_history: List[Dict[str, Any]] = field(default_factory=list)
    market_conditions: Dict[str, Any] = field(default_factory=dict)
    temporal_factors: Dict[str, Any] = field(default_factory=dict)
    geographic_context: Dict[str, Any] = field(default_factory=dict)
    user_expertise_level: str = "intermediate"
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)


class AdaptiveEngine:
    """Moteur d'adaptation contextuelle principal."""
    
    def __init__(self):
        self.rules = []
        self.context_history = deque(maxlen=100)
        self.adaptation_strategies = {
            'market_based': self._market_based_adaptation,
            'user_based': self._user_based_adaptation,
            'temporal_based': self._temporal_adaptation,
            'geographic_based': self._geographic_adaptation,
            'hybrid': self._hybrid_adaptation
        }
        
        self.learning_enabled = True
        self.adaptation_weights = {
            'user_preferences': 0.3,
            'market_conditions': 0.25,
            'temporal_factors': 0.2,
            'geographic_context': 0.15,
            'interaction_patterns': 0.1
        }
        
        self._initialize_base_rules()
    
    def _initialize_base_rules(self):
        """Initialise les règles de base adaptatives."""
        
        # Règle d'adaptation des prix selon le marché
        self.add_rule(ContextualRule(
            name="price_adaptation_luxury",
            condition=lambda ctx: ctx.get('market_conditions', {}).get('segment') == 'luxury',
            action=lambda data: self._adapt_for_luxury_market(data),
            priority=2
        ))
        
        # Règle d'adaptation pour débutants
        self.add_rule(ContextualRule(
            name="beginner_simplification",
            condition=lambda ctx: ctx.get('user_expertise_level') == 'beginner',
            action=lambda data: self._simplify_for_beginners(data),
            priority=3
        ))
        
        # Règle d'adaptation temporelle
        self.add_rule(ContextualRule(
            name="seasonal_adaptation",
            condition=lambda ctx: self._is_peak_season(ctx),
            action=lambda data: self._adapt_for_season(data),
            priority=1
        ))
        
        # Règle d'adaptation géographique
        self.add_rule(ContextualRule(
            name="geographic_focus",
            condition=lambda ctx: len(ctx.get('geographic_context', {}).get('focus_areas', [])) > 0,
            action=lambda data: self._adapt_for_geography(data),
            priority=2
        ))
    
    def add_rule(self, rule: ContextualRule):
        """Ajoute une règle d'adaptation."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    async def adapt_analysis(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adapte l'analyse selon le contexte."""
        logger.info(f"Adaptation contextuelle en cours pour {len(data.get('properties', []))} propriétés")
        
        # Sauvegarde du contexte pour l'apprentissage
        self.context_history.append({
            'timestamp': datetime.now(),
            'context': context,
            'data_size': len(data.get('properties', []))
        })
        
        # Application des règles contextuelles
        adapted_data = data.copy()
        applied_rules = []
        
        for rule in self.rules:
            if rule.active and rule.condition(context.__dict__):
                try:
                    adapted_data = rule.action(adapted_data)
                    applied_rules.append(rule.name)
                    rule.usage_count += 1
                    logger.debug(f"Règle appliquée: {rule.name}")
                except Exception as e:
                    logger.error(f"Erreur application règle {rule.name}: {e}")
        
        # Sélection de la stratégie d'adaptation
        strategy = self._select_adaptation_strategy(context)
        adapted_data = await self.adaptation_strategies[strategy](adapted_data, context)
        
        # Enrichissement avec métadonnées d'adaptation
        adapted_data['adaptation_metadata'] = {
            'strategy_used': strategy,
            'rules_applied': applied_rules,
            'adaptation_timestamp': datetime.now().isoformat(),
            'context_factors': self._extract_context_factors(context)
        }
        
        return adapted_data
    
    def _select_adaptation_strategy(self, context: AdaptationContext) -> str:
        """Sélectionne la stratégie d'adaptation optimale."""
        scores = {}
        
        # Score basé sur les préférences utilisateur
        if context.user_preferences:
            scores['user_based'] = len(context.user_preferences) * 0.3
        
        # Score basé sur les conditions de marché
        if context.market_conditions:
            scores['market_based'] = len(context.market_conditions) * 0.25
        
        # Score basé sur les facteurs temporels
        if context.temporal_factors:
            scores['temporal_based'] = len(context.temporal_factors) * 0.2
        
        # Score basé sur le contexte géographique
        if context.geographic_context:
            scores['geographic_based'] = len(context.geographic_context) * 0.15
        
        # Stratégie hybride si plusieurs facteurs
        if len([s for s in scores.values() if s > 0.1]) > 2:
            return 'hybrid'
        
        # Sélection de la stratégie avec le score le plus élevé
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'market_based'
    
    async def _market_based_adaptation(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adaptation basée sur les conditions de marché."""
        market_conditions = context.market_conditions
        
        if market_conditions.get('volatility') == 'high':
            # Ajout d'alertes de volatilité
            data['market_alerts'] = data.get('market_alerts', [])
            data['market_alerts'].append({
                'type': 'volatility_warning',
                'message': 'Marché volatil détecté - prudence recommandée',
                'severity': 'medium'
            })
        
        if market_conditions.get('trend') == 'bullish':
            # Ajustement des recommandations pour marché haussier
            data['investment_recommendations'] = data.get('investment_recommendations', [])
            data['investment_recommendations'].append(
                'Marché haussier: considérez l\'achat rapide des bonnes opportunités'
            )
        
        return data
    
    async def _user_based_adaptation(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adaptation basée sur les préférences utilisateur."""
        preferences = context.user_preferences
        
        # Filtrage selon les préférences de prix
        if 'max_budget' in preferences:
            max_budget = preferences['max_budget']
            if 'properties' in data:
                data['properties'] = [
                    p for p in data['properties'] 
                    if p.get('price', 0) <= max_budget
                ]
        
        # Adaptation des insights selon les intérêts
        if preferences.get('focus') == 'investment':
            data['priority_insights'] = [
                insight for insight in data.get('insights', [])
                if any(keyword in insight.lower() for keyword in ['rendement', 'roi', 'investissement'])
            ]
        
        return data
    
    async def _temporal_adaptation(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adaptation basée sur les facteurs temporels."""
        temporal_factors = context.temporal_factors
        
        current_month = datetime.now().month
        
        # Adaptation saisonnière
        if current_month in [6, 7, 8]:  # Été
            data['seasonal_note'] = 'Période estivale: marché généralement plus actif'
        elif current_month in [11, 12, 1]:  # Hiver
            data['seasonal_note'] = 'Période hivernale: négociations souvent plus favorables'
        
        # Adaptation selon l'urgence
        if temporal_factors.get('urgency') == 'high':
            data['quick_recommendations'] = self._generate_quick_recommendations(data)
        
        return data
    
    async def _geographic_adaptation(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adaptation basée sur le contexte géographique."""
        geo_context = context.geographic_context
        
        focus_areas = geo_context.get('focus_areas', [])
        if focus_areas:
            # Priorisation des propriétés dans les zones d'intérêt
            if 'properties' in data:
                prioritized = []
                others = []
                
                for prop in data['properties']:
                    location = prop.get('location', '').lower()
                    if any(area.lower() in location for area in focus_areas):
                        prioritized.append(prop)
                    else:
                        others.append(prop)
                
                data['properties'] = prioritized + others
                data['geographic_prioritization'] = f"{len(prioritized)} propriétés prioritaires dans les zones d'intérêt"
        
        return data
    
    async def _hybrid_adaptation(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Adaptation hybride combinant plusieurs stratégies."""
        # Application séquentielle des stratégies avec pondération
        strategies = ['market_based', 'user_based', 'temporal_based', 'geographic_based']
        
        for strategy in strategies:
            if strategy in self.adaptation_strategies:
                data = await self.adaptation_strategies[strategy](data, context)
        
        # Synthèse des adaptations
        data['hybrid_adaptation_summary'] = {
            'strategies_applied': strategies,
            'adaptation_confidence': self._calculate_adaptation_confidence(context)
        }
        
        return data
    
    def _adapt_for_luxury_market(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation spécifique pour le marché du luxe."""
        # Mise en avant des caractéristiques premium
        if 'insights' in data:
            luxury_insights = []
            for insight in data['insights']:
                if any(keyword in insight.lower() for keyword in ['premium', 'luxe', 'haut de gamme']):
                    luxury_insights.append(f"🏆 {insight}")
                else:
                    luxury_insights.append(insight)
            data['insights'] = luxury_insights
        
        # Ajout de métriques spécifiques au luxe
        data['luxury_metrics'] = {
            'premium_features_analysis': 'Analyse des équipements haut de gamme',
            'exclusivity_index': 'Indice d\'exclusivité du marché'
        }
        
        return data
    
    def _simplify_for_beginners(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplifie l'analyse pour les débutants."""
        # Simplification des insights
        if 'insights' in data:
            simplified_insights = []
            for insight in data['insights'][:3]:  # Limite à 3 insights
                # Simplification du langage
                simplified = insight.replace('coefficient de variation', 'variabilité des prix')
                simplified = simplified.replace('médian', 'prix du milieu')
                simplified_insights.append(f"ℹ️ {simplified}")
            data['insights'] = simplified_insights
        
        # Ajout d'explications
        data['beginner_explanations'] = {
            'price_analysis': 'Analyse des prix pour comprendre le marché',
            'market_trends': 'Tendances qui influencent les prix',
            'investment_basics': 'Notions de base pour investir'
        }
        
        return data
    
    def _is_peak_season(self, context: Dict[str, Any]) -> bool:
        """Détermine si c'est la haute saison immobilière."""
        current_month = datetime.now().month
        return current_month in [4, 5, 6, 9, 10]  # Printemps et début automne
    
    def _adapt_for_season(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation saisonnière."""
        current_month = datetime.now().month
        
        if current_month in [4, 5, 6]:  # Printemps
            data['seasonal_advice'] = 'Printemps: période idéale pour visiter et acheter'
        elif current_month in [9, 10]:  # Automne
            data['seasonal_advice'] = 'Automne: bon moment pour négocier avant l\'hiver'
        
        return data
    
    def _adapt_for_geography(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation géographique."""
        # Cette méthode serait enrichie avec des données géographiques réelles
        data['geographic_insights'] = [
            'Analyse adaptée à votre zone géographique d\'intérêt'
        ]
        return data
    
    def _generate_quick_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Génère des recommandations rapides."""
        recommendations = []
        
        if data.get('total_properties', 0) > 0:
            recommendations.append('Concentrez-vous sur les 3 premières propriétés')
            recommendations.append('Contactez rapidement les agents pour les biens intéressants')
        
        return recommendations
    
    def _extract_context_factors(self, context: AdaptationContext) -> Dict[str, Any]:
        """Extrait les facteurs de contexte pertinents."""
        return {
            'user_expertise': context.user_expertise_level,
            'preferences_count': len(context.user_preferences),
            'session_length': len(context.session_history),
            'geographic_focus': bool(context.geographic_context.get('focus_areas'))
        }
    
    def _calculate_adaptation_confidence(self, context: AdaptationContext) -> float:
        """Calcule la confiance dans l'adaptation."""
        confidence = 0.5  # Base
        
        # Facteurs qui augmentent la confiance
        if context.user_preferences:
            confidence += 0.2
        if context.session_history:
            confidence += 0.1
        if context.market_conditions:
            confidence += 0.15
        
        return min(1.0, confidence)
    
    def learn_from_feedback(self, rule_name: str, success: bool):
        """Apprentissage basé sur les retours."""
        if not self.learning_enabled:
            return
        
        for rule in self.rules:
            if rule.name == rule_name:
                # Mise à jour du taux de succès
                total_uses = rule.usage_count
                if total_uses > 0:
                    current_success_rate = rule.success_rate
                    new_success_rate = (current_success_rate * (total_uses - 1) + (1.0 if success else 0.0)) / total_uses
                    rule.success_rate = new_success_rate
                
                # Désactivation des règles peu performantes
                if rule.usage_count > 10 and rule.success_rate < 0.3:
                    rule.active = False
                    logger.info(f"Règle {rule_name} désactivée pour faible performance")
                
                break
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'adaptation."""
        active_rules = [r for r in self.rules if r.active]
        
        return {
            'total_rules': len(self.rules),
            'active_rules': len(active_rules),
            'context_history_size': len(self.context_history),
            'learning_enabled': self.learning_enabled,
            'rule_performance': {
                rule.name: {
                    'usage_count': rule.usage_count,
                    'success_rate': rule.success_rate,
                    'active': rule.active
                }
                for rule in self.rules
            }
        }


class ContextualDataEnricher:
    """Enrichisseur de données contextuel."""
    
    def __init__(self):
        self.enrichment_strategies = {
            'market_data': self._enrich_with_market_data,
            'geographic_data': self._enrich_with_geographic_data,
            'temporal_data': self._enrich_with_temporal_data,
            'user_context': self._enrich_with_user_context
        }
    
    async def enrich_data(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Enrichit les données selon le contexte."""
        enriched_data = data.copy()
        
        for strategy_name, strategy_func in self.enrichment_strategies.items():
            try:
                enriched_data = await strategy_func(enriched_data, context)
            except Exception as e:
                logger.error(f"Erreur enrichissement {strategy_name}: {e}")
        
        return enriched_data
    
    async def _enrich_with_market_data(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Enrichit avec des données de marché."""
        # Simulation d'enrichissement avec données de marché
        market_conditions = context.market_conditions
        
        if market_conditions:
            data['market_context'] = {
                'current_trend': market_conditions.get('trend', 'stable'),
                'volatility_level': market_conditions.get('volatility', 'medium'),
                'market_temperature': market_conditions.get('temperature', 'neutral')
            }
        
        return data
    
    async def _enrich_with_geographic_data(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Enrichit avec des données géographiques."""
        # Simulation d'enrichissement géographique
        if 'properties' in data:
            for prop in data['properties']:
                location = prop.get('location', '')
                # Enrichissement simulé
                prop['geographic_enrichment'] = {
                    'transport_score': 7.5,  # Score simulé
                    'amenities_score': 8.0,
                    'safety_score': 7.8
                }
        
        return data
    
    async def _enrich_with_temporal_data(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Enrichit avec des données temporelles."""
        current_time = datetime.now()
        
        data['temporal_context'] = {
            'analysis_timestamp': current_time.isoformat(),
            'market_cycle_phase': self._determine_market_cycle_phase(current_time),
            'seasonal_factor': self._calculate_seasonal_factor(current_time)
        }
        
        return data
    
    async def _enrich_with_user_context(self, data: Dict[str, Any], context: AdaptationContext) -> Dict[str, Any]:
        """Enrichit avec le contexte utilisateur."""
        data['user_context'] = {
            'expertise_level': context.user_expertise_level,
            'session_duration': len(context.session_history),
            'preferences_defined': bool(context.user_preferences)
        }
        
        return data
    
    def _determine_market_cycle_phase(self, timestamp: datetime) -> str:
        """Détermine la phase du cycle de marché."""
        # Logique simplifiée basée sur la période de l'année
        month = timestamp.month
        if month in [1, 2, 3]:
            return 'recovery'
        elif month in [4, 5, 6]:
            return 'growth'
        elif month in [7, 8, 9]:
            return 'peak'
        else:
            return 'correction'
    
    def _calculate_seasonal_factor(self, timestamp: datetime) -> float:
        """Calcule un facteur saisonnier."""
        month = timestamp.month
        # Facteur plus élevé au printemps et en automne
        seasonal_factors = {
            1: 0.8, 2: 0.7, 3: 0.9, 4: 1.2, 5: 1.3, 6: 1.1,
            7: 0.9, 8: 0.8, 9: 1.2, 10: 1.3, 11: 0.9, 12: 0.7
        }
        return seasonal_factors.get(month, 1.0)
