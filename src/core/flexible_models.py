"""
Modèles flexibles et adaptatifs pour l'immobilier.

Cette architecture remplace les structures rigides par des modèles dynamiques
qui s'adaptent au contexte et aux données disponibles.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Type
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class FlexibleProperty:
    """
    Propriété immobilière flexible qui s'adapte aux données disponibles.
    Remplace les dataclasses rigides par une structure dynamique.
    """
    
    def __init__(self, **kwargs):
        self._data = {}
        self._metadata = {
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'confidence_scores': {},
            'data_sources': {},
            'enrichments': []
        }
        
        # Champs essentiels avec validation flexible
        self._essential_fields = {
            'id', 'price', 'location'
        }
        
        # Champs optionnels avec types suggérés
        self._optional_fields = {
            'title': str,
            'surface_area': (int, float),
            'rooms': int,
            'property_type': str,
            'description': str,
            'coordinates': dict,
            'images': list,
            'amenities': list,
            'energy_rating': str,
            'year_built': int,
            'floor': int,
            'elevator': bool,
            'parking': bool,
            'garden': bool,
            'balcony': bool,
            'furnished': bool
        }
        
        self.update(**kwargs)
    
    def update(self, **kwargs):
        """Met à jour les données avec validation flexible."""
        for key, value in kwargs.items():
            if value is not None:
                # Validation et conversion automatique
                validated_value = self._validate_and_convert(key, value)
                self._data[key] = validated_value
                self._metadata['updated_at'] = datetime.now()
    
    def _validate_and_convert(self, key: str, value: Any) -> Any:
        """Valide et convertit une valeur selon le contexte."""
        if key in self._optional_fields:
            expected_type = self._optional_fields[key]
            if isinstance(expected_type, tuple):
                # Plusieurs types acceptés
                for t in expected_type:
                    try:
                        return t(value) if not isinstance(value, t) else value
                    except (ValueError, TypeError):
                        continue
            else:
                try:
                    return expected_type(value) if not isinstance(value, expected_type) else value
                except (ValueError, TypeError):
                    logger.warning(f"Impossible de convertir {key}={value} en {expected_type}")
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur avec fallback intelligent."""
        if key in self._data:
            return self._data[key]
        
        # Fallbacks intelligents
        fallbacks = {
            'price_per_sqm': lambda: self._calculate_price_per_sqm(),
            'display_title': lambda: self._generate_display_title(),
            'location_hierarchy': lambda: self._parse_location_hierarchy(),
            'estimated_value': lambda: self._estimate_value(),
            'market_segment': lambda: self._determine_market_segment()
        }
        
        if key in fallbacks:
            try:
                computed_value = fallbacks[key]()
                if computed_value is not None:
                    return computed_value
            except Exception as e:
                logger.debug(f"Erreur calcul fallback {key}: {e}")
        
        return default
    
    def _calculate_price_per_sqm(self) -> Optional[float]:
        """Calcule le prix au m² si possible."""
        price = self._data.get('price')
        surface = self._data.get('surface_area')
        if price and surface and surface > 0:
            return round(price / surface, 2)
        return None
    
    def _generate_display_title(self) -> str:
        """Génère un titre d'affichage intelligent."""
        parts = []
        
        if 'property_type' in self._data:
            parts.append(self._data['property_type'].title())
        
        if 'rooms' in self._data:
            parts.append(f"{self._data['rooms']} pièces")
        
        if 'surface_area' in self._data:
            parts.append(f"{self._data['surface_area']}m²")
        
        if 'location' in self._data:
            parts.append(self._data['location'])
        
        return ' - '.join(parts) if parts else 'Propriété'
    
    def _parse_location_hierarchy(self) -> Dict[str, str]:
        """Parse la localisation en hiérarchie."""
        location = self._data.get('location', '')
        hierarchy = {}
        
        # Patterns courants français
        if ',' in location:
            parts = [p.strip() for p in location.split(',')]
            if len(parts) >= 2:
                hierarchy['city'] = parts[0]
                hierarchy['region'] = parts[-1]
                if len(parts) > 2:
                    hierarchy['district'] = parts[1]
        
        # Détection arrondissements parisiens
        if 'Paris' in location and ('e' in location or 'er' in location):
            import re
            match = re.search(r'Paris\s*(\d+)', location)
            if match:
                hierarchy['city'] = 'Paris'
                hierarchy['arrondissement'] = f"{match.group(1)}e"
        
        return hierarchy
    
    def _estimate_value(self) -> Optional[float]:
        """Estime la valeur basée sur les données disponibles."""
        # Logique d'estimation flexible selon les données
        price = self._data.get('price')
        if not price:
            return None
        
        # Facteurs d'ajustement selon les caractéristiques
        multiplier = 1.0
        
        if self._data.get('elevator'):
            multiplier *= 1.05
        if self._data.get('parking'):
            multiplier *= 1.1
        if self._data.get('garden'):
            multiplier *= 1.15
        
        return round(price * multiplier, 2)
    
    def _determine_market_segment(self) -> str:
        """Détermine le segment de marché."""
        price = self._data.get('price', 0)
        surface = self._data.get('surface_area', 0)
        
        if price == 0:
            return 'unknown'
        
        price_per_sqm = price / surface if surface > 0 else price / 50  # Estimation
        
        if price_per_sqm > 15000:
            return 'luxury'
        elif price_per_sqm > 8000:
            return 'premium'
        elif price_per_sqm > 4000:
            return 'standard'
        else:
            return 'budget'
    
    def enrich_with(self, enricher_name: str, data: Dict[str, Any]):
        """Enrichit la propriété avec des données externes."""
        self._data.update(data)
        self._metadata['enrichments'].append({
            'enricher': enricher_name,
            'timestamp': datetime.now(),
            'fields_added': list(data.keys())
        })
    
    def set_confidence(self, field: str, score: float):
        """Définit un score de confiance pour un champ."""
        self._metadata['confidence_scores'][field] = max(0.0, min(1.0, score))
    
    def get_confidence(self, field: str) -> float:
        """Récupère le score de confiance d'un champ."""
        return self._metadata['confidence_scores'].get(field, 0.5)
    
    def to_dict(self, include_metadata: bool = False) -> Dict[str, Any]:
        """Convertit en dictionnaire avec options."""
        result = dict(self._data)
        
        # Ajout des champs calculés populaires
        computed_fields = ['price_per_sqm', 'display_title', 'market_segment']
        for field in computed_fields:
            value = self.get(field)
            if value is not None:
                result[field] = value
        
        if include_metadata:
            result['_metadata'] = self._metadata
        
        return result
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        self.update(**{key: value})
    
    def __contains__(self, key: str) -> bool:
        return key in self._data or key in ['price_per_sqm', 'display_title', 'market_segment']
    
    def __repr__(self) -> str:
        return f"FlexibleProperty({self.get('display_title', 'Unknown')})"


class AdaptiveAnalyzer(ABC):
    """Interface pour les analyseurs adaptatifs."""
    
    @abstractmethod
    async def analyze(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse adaptative basée sur le contexte."""
        pass
    
    @abstractmethod
    def get_insights(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Génère des insights contextuels."""
        pass


class ContextualMarketAnalyzer(AdaptiveAnalyzer):
    """Analyseur de marché contextuel et adaptatif."""
    
    def __init__(self):
        self.analysis_strategies = {
            'luxury': self._analyze_luxury_market,
            'budget': self._analyze_budget_market,
            'rental': self._analyze_rental_market,
            'investment': self._analyze_investment_market,
            'family': self._analyze_family_market
        }
    
    async def analyze(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse adaptative selon le contexte."""
        if not properties:
            return {'error': 'Aucune propriété à analyser'}
        
        # Détection automatique du contexte si non fourni
        if not context.get('market_type'):
            context['market_type'] = self._detect_market_type(properties)
        
        # Sélection de la stratégie d'analyse
        strategy = self.analysis_strategies.get(
            context['market_type'], 
            self._analyze_general_market
        )
        
        base_analysis = await self._base_analysis(properties)
        contextual_analysis = await strategy(properties, context)
        
        return {
            **base_analysis,
            **contextual_analysis,
            'context': context,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _base_analysis(self, properties: List[FlexibleProperty]) -> Dict[str, Any]:
        """Analyse de base adaptative."""
        prices = [p.get('price') for p in properties if p.get('price')]
        surfaces = [p.get('surface_area') for p in properties if p.get('surface_area')]
        
        analysis = {
            'total_properties': len(properties),
            'price_analysis': self._flexible_price_analysis(prices),
            'surface_analysis': self._flexible_surface_analysis(surfaces),
            'location_distribution': self._analyze_locations(properties),
            'property_types': self._analyze_property_types(properties)
        }
        
        return analysis
    
    def _flexible_price_analysis(self, prices: List[float]) -> Dict[str, Any]:
        """Analyse flexible des prix."""
        if not prices:
            return {'status': 'no_data'}
        
        analysis = {
            'count': len(prices),
            'min': min(prices),
            'max': max(prices),
            'mean': statistics.mean(prices),
            'median': statistics.median(prices)
        }
        
        if len(prices) > 1:
            analysis['std_dev'] = statistics.stdev(prices)
            analysis['coefficient_variation'] = analysis['std_dev'] / analysis['mean']
            
            # Détection d'outliers
            q1 = statistics.quantiles(prices, n=4)[0]
            q3 = statistics.quantiles(prices, n=4)[2]
            iqr = q3 - q1
            analysis['outliers'] = [
                p for p in prices 
                if p < q1 - 1.5 * iqr or p > q3 + 1.5 * iqr
            ]
        
        return analysis
    
    def _flexible_surface_analysis(self, surfaces: List[float]) -> Dict[str, Any]:
        """Analyse flexible des surfaces."""
        if not surfaces:
            return {'status': 'no_data'}
        
        return {
            'count': len(surfaces),
            'min': min(surfaces),
            'max': max(surfaces),
            'mean': statistics.mean(surfaces),
            'median': statistics.median(surfaces),
            'distribution': self._categorize_surfaces(surfaces)
        }
    
    def _categorize_surfaces(self, surfaces: List[float]) -> Dict[str, int]:
        """Catégorise les surfaces de manière flexible."""
        categories = defaultdict(int)
        
        for surface in surfaces:
            if surface < 30:
                categories['studio_small'] += 1
            elif surface < 60:
                categories['medium'] += 1
            elif surface < 100:
                categories['large'] += 1
            else:
                categories['very_large'] += 1
        
        return dict(categories)
    
    def _analyze_locations(self, properties: List[FlexibleProperty]) -> Dict[str, Any]:
        """Analyse flexible des localisations."""
        locations = defaultdict(int)
        hierarchies = defaultdict(lambda: defaultdict(int))
        
        for prop in properties:
            location = prop.get('location', 'Unknown')
            locations[location] += 1
            
            hierarchy = prop.get('location_hierarchy', {})
            for level, value in hierarchy.items():
                hierarchies[level][value] += 1
        
        return {
            'raw_locations': dict(locations),
            'hierarchy': {k: dict(v) for k, v in hierarchies.items()},
            'unique_locations': len(locations)
        }
    
    def _analyze_property_types(self, properties: List[FlexibleProperty]) -> Dict[str, int]:
        """Analyse flexible des types de propriétés."""
        types = defaultdict(int)
        
        for prop in properties:
            prop_type = prop.get('property_type', 'unknown')
            types[prop_type.lower()] += 1
        
        return dict(types)
    
    def _detect_market_type(self, properties: List[FlexibleProperty]) -> str:
        """Détecte automatiquement le type de marché."""
        prices = [p.get('price', 0) for p in properties]
        avg_price = statistics.mean(prices) if prices else 0
        
        luxury_indicators = sum(1 for p in properties if p.get('elevator') or p.get('parking'))
        family_indicators = sum(1 for p in properties if p.get('rooms', 0) >= 3)
        
        if avg_price > 500000:
            return 'luxury'
        elif family_indicators > len(properties) * 0.6:
            return 'family'
        elif avg_price < 200000:
            return 'budget'
        else:
            return 'general'
    
    async def _analyze_luxury_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse spécialisée pour le marché du luxe."""
        luxury_features = ['elevator', 'parking', 'garden', 'balcony']
        feature_analysis = {}
        
        for feature in luxury_features:
            count = sum(1 for p in properties if p.get(feature))
            feature_analysis[feature] = {
                'count': count,
                'percentage': count / len(properties) * 100
            }
        
        return {
            'market_type': 'luxury',
            'luxury_features': feature_analysis,
            'premium_ratio': len([p for p in properties if p.get('market_segment') == 'luxury']) / len(properties)
        }
    
    async def _analyze_budget_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse spécialisée pour le marché économique."""
        return {
            'market_type': 'budget',
            'affordability_index': self._calculate_affordability(properties),
            'value_opportunities': self._find_value_opportunities(properties)
        }
    
    async def _analyze_rental_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse spécialisée pour le marché locatif."""
        return {
            'market_type': 'rental',
            'rental_yield_estimates': self._estimate_rental_yields(properties),
            'tenant_preferences': self._analyze_tenant_preferences(properties)
        }
    
    async def _analyze_investment_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse spécialisée pour l'investissement."""
        return {
            'market_type': 'investment',
            'investment_scores': self._calculate_investment_scores(properties),
            'roi_projections': self._project_roi(properties)
        }
    
    async def _analyze_family_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse spécialisée pour les familles."""
        return {
            'market_type': 'family',
            'family_suitability': self._assess_family_suitability(properties),
            'school_proximity': context.get('school_data', 'not_available')
        }
    
    async def _analyze_general_market(self, properties: List[FlexibleProperty], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse générale adaptative."""
        return {
            'market_type': 'general',
            'market_balance': self._assess_market_balance(properties),
            'growth_indicators': self._identify_growth_indicators(properties)
        }
    
    def _calculate_affordability(self, properties: List[FlexibleProperty]) -> float:
        """Calcule un indice d'accessibilité."""
        prices = [p.get('price', 0) for p in properties if p.get('price')]
        if not prices:
            return 0.0
        
        median_price = statistics.median(prices)
        # Supposons un revenu médian de référence
        median_income = 35000  # À adapter selon la région
        return median_income / (median_price / 100) if median_price > 0 else 0.0
    
    def _find_value_opportunities(self, properties: List[FlexibleProperty]) -> List[Dict[str, Any]]:
        """Identifie les opportunités de valeur."""
        opportunities = []
        
        for prop in properties:
            price_per_sqm = prop.get('price_per_sqm')
            if price_per_sqm and price_per_sqm < 3000:  # Seuil adaptatif
                opportunities.append({
                    'property_id': prop.get('id'),
                    'reason': 'low_price_per_sqm',
                    'value': price_per_sqm
                })
        
        return opportunities
    
    def _estimate_rental_yields(self, properties: List[FlexibleProperty]) -> Dict[str, float]:
        """Estime les rendements locatifs."""
        # Logique d'estimation adaptative
        yields = {}
        
        for prop in properties:
            price = prop.get('price', 0)
            surface = prop.get('surface_area', 0)
            
            if price > 0 and surface > 0:
                # Estimation basée sur des ratios de marché
                estimated_rent = surface * 15  # €/m²/mois (adaptatif)
                annual_rent = estimated_rent * 12
                yield_pct = (annual_rent / price) * 100
                yields[prop.get('id', 'unknown')] = round(yield_pct, 2)
        
        return yields
    
    def _analyze_tenant_preferences(self, properties: List[FlexibleProperty]) -> Dict[str, Any]:
        """Analyse les préférences des locataires."""
        preferences = {
            'furnished': sum(1 for p in properties if p.get('furnished')),
            'with_parking': sum(1 for p in properties if p.get('parking')),
            'with_elevator': sum(1 for p in properties if p.get('elevator')),
            'with_balcony': sum(1 for p in properties if p.get('balcony'))
        }
        
        total = len(properties)
        return {k: {'count': v, 'percentage': v/total*100} for k, v in preferences.items()}
    
    def _calculate_investment_scores(self, properties: List[FlexibleProperty]) -> Dict[str, float]:
        """Calcule des scores d'investissement."""
        scores = {}
        
        for prop in properties:
            score = 0.0
            
            # Facteurs de score adaptatifs
            if prop.get('parking'):
                score += 0.2
            if prop.get('elevator'):
                score += 0.15
            if prop.get('garden'):
                score += 0.25
            
            price_per_sqm = prop.get('price_per_sqm', 0)
            if price_per_sqm < 5000:  # Bon rapport qualité-prix
                score += 0.3
            
            scores[prop.get('id', 'unknown')] = min(1.0, score)
        
        return scores
    
    def _project_roi(self, properties: List[FlexibleProperty]) -> Dict[str, Dict[str, float]]:
        """Projette le retour sur investissement."""
        projections = {}
        
        for prop in properties:
            price = prop.get('price', 0)
            if price > 0:
                # Projections adaptatives
                projections[prop.get('id', 'unknown')] = {
                    '1_year': price * 0.03,  # 3% appreciation
                    '5_years': price * 0.18,  # 18% total
                    '10_years': price * 0.40   # 40% total
                }
        
        return projections
    
    def _assess_family_suitability(self, properties: List[FlexibleProperty]) -> Dict[str, Any]:
        """Évalue l'adéquation pour les familles."""
        suitable_count = 0
        
        for prop in properties:
            rooms = prop.get('rooms', 0)
            surface = prop.get('surface_area', 0)
            
            if rooms >= 3 and surface >= 70:
                suitable_count += 1
        
        return {
            'suitable_properties': suitable_count,
            'suitability_rate': suitable_count / len(properties) * 100,
            'criteria': 'rooms >= 3 AND surface >= 70m²'
        }
    
    def _assess_market_balance(self, properties: List[FlexibleProperty]) -> Dict[str, Any]:
        """Évalue l'équilibre du marché."""
        segments = defaultdict(int)
        
        for prop in properties:
            segment = prop.get('market_segment', 'unknown')
            segments[segment] += 1
        
        total = len(properties)
        balance = {k: v/total for k, v in segments.items()}
        
        return {
            'segment_distribution': dict(segments),
            'balance_ratios': balance,
            'diversity_index': len(segments)
        }
    
    def _identify_growth_indicators(self, properties: List[FlexibleProperty]) -> List[str]:
        """Identifie les indicateurs de croissance."""
        indicators = []
        
        # Analyse des prix
        prices = [p.get('price', 0) for p in properties if p.get('price')]
        if prices:
            avg_price = statistics.mean(prices)
            if avg_price > 300000:
                indicators.append("Prix moyens élevés indiquant une demande forte")
        
        # Analyse des caractéristiques premium
        premium_count = sum(1 for p in properties if p.get('elevator') or p.get('parking'))
        if premium_count > len(properties) * 0.5:
            indicators.append("Forte proportion de biens avec équipements premium")
        
        return indicators
    
    def get_insights(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Génère des insights contextuels et adaptatifs."""
        insights = []
        
        market_type = analysis_result.get('context', {}).get('market_type', 'general')
        
        # Insights adaptatifs selon le type de marché
        if market_type == 'luxury':
            insights.extend(self._luxury_insights(analysis_result))
        elif market_type == 'budget':
            insights.extend(self._budget_insights(analysis_result))
        elif market_type == 'rental':
            insights.extend(self._rental_insights(analysis_result))
        elif market_type == 'investment':
            insights.extend(self._investment_insights(analysis_result))
        elif market_type == 'family':
            insights.extend(self._family_insights(analysis_result))
        
        # Insights généraux adaptatifs
        insights.extend(self._general_insights(analysis_result))
        
        return insights
    
    def _luxury_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights spécialisés pour le marché du luxe."""
        insights = []
        
        luxury_features = analysis.get('luxury_features', {})
        for feature, data in luxury_features.items():
            if data['percentage'] > 80:
                insights.append(f"Marché haut de gamme: {data['percentage']:.1f}% des biens ont {feature}")
        
        return insights
    
    def _budget_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights pour le marché économique."""
        insights = []
        
        affordability = analysis.get('affordability_index', 0)
        if affordability > 0.1:
            insights.append(f"Marché accessible avec un indice d'accessibilité de {affordability:.2f}")
        
        opportunities = analysis.get('value_opportunities', [])
        if opportunities:
            insights.append(f"{len(opportunities)} opportunités de valeur identifiées")
        
        return insights
    
    def _rental_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights pour le marché locatif."""
        insights = []
        
        yields = analysis.get('rental_yield_estimates', {})
        if yields:
            avg_yield = statistics.mean(yields.values())
            insights.append(f"Rendement locatif moyen estimé: {avg_yield:.2f}%")
        
        return insights
    
    def _investment_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights pour l'investissement."""
        insights = []
        
        scores = analysis.get('investment_scores', {})
        if scores:
            high_score_count = sum(1 for score in scores.values() if score > 0.7)
            insights.append(f"{high_score_count} biens avec un score d'investissement élevé")
        
        return insights
    
    def _family_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights pour les familles."""
        insights = []
        
        suitability = analysis.get('family_suitability', {})
        rate = suitability.get('suitability_rate', 0)
        insights.append(f"{rate:.1f}% des biens sont adaptés aux familles")
        
        return insights
    
    def _general_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Insights généraux adaptatifs."""
        insights = []
        
        total = analysis.get('total_properties', 0)
        if total > 0:
            insights.append(f"Analyse basée sur {total} propriétés")
        
        price_analysis = analysis.get('price_analysis', {})
        if 'outliers' in price_analysis and price_analysis['outliers']:
            insights.append(f"{len(price_analysis['outliers'])} biens avec des prix atypiques détectés")
        
        return insights
