"""
Analysis tools for feature adoption, expansion, and churn risk.
Implements business logic and heuristics for recommendations.
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from ..data.models import (
    Customer, Feature, FeatureUsage, Recommendation,
    FeatureCategory, ChurnRiskLevel, ChurnRiskAssessment
)
from .data_access import DataAccessTool


class AnalysisTool:
    """
    Tool for analyzing customer usage patterns and generating insights.
    Implements explainable business logic for recommendations.
    """
    
    def __init__(self, data_access: DataAccessTool):
        """Initialize with data access dependency."""
        self.data_access = data_access
    
    def analyze_feature_adoption(
        self, 
        customer: Customer
    ) -> List[Recommendation]:
        """
        Analyze which features customer should adopt next.
        Returns prioritized recommendations with explanations.
        """
        recommendations = []
        feature_catalog = self.data_access.get_all_features()
        adopted_features = customer.get_adopted_features(feature_catalog)
        active_features = customer.get_active_features()
        
        # Core features that should be adopted
        core_features = [
            feat for feat in feature_catalog.values()
            if feat.category == FeatureCategory.CORE
        ]
        
        # Premium features available on their plan
        available_premium = [
            feat for feat in feature_catalog.values()
            if feat.is_premium and customer.plan_tier in ["professional", "enterprise"]
        ]
        
        # Analyze core feature gaps
        for feature in core_features:
            if feature.id not in adopted_features:
                usage = customer.features.get(feature.id)
                priority = 1 if feature.id not in active_features else 2
                
                reason = self._generate_adoption_reason(
                    feature, customer, usage, "core"
                )
                
                recommendations.append(Recommendation(
                    feature_id=feature.id,
                    feature_name=feature.name,
                    priority=priority,
                    reason=reason,
                    suggested_action=self._suggest_action(feature, customer, usage),
                    expected_impact=f"Increase core product engagement and reduce churn risk",
                    confidence=0.85 if priority == 1 else 0.65
                ))
        
        # Analyze premium feature opportunities
        for feature in available_premium:
            if feature.id not in adopted_features:
                usage = customer.features.get(feature.id)
                
                # Check if customer has foundational features adopted
                has_foundation = len(adopted_features) >= 3
                
                if has_foundation:
                    reason = self._generate_adoption_reason(
                        feature, customer, usage, "expansion"
                    )
                    
                    recommendations.append(Recommendation(
                        feature_id=feature.id,
                        feature_name=feature.name,
                        priority=3,
                        reason=reason,
                        suggested_action=self._suggest_action(feature, customer, usage),
                        expected_impact=f"Potential expansion revenue: ${customer.mrr * 0.15:.0f}/month",
                        confidence=0.6
                    ))
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)
        return recommendations[:5]  # Top 5
    
    def _generate_adoption_reason(
        self,
        feature: Feature,
        customer: Customer,
        usage: FeatureUsage,
        context: str
    ) -> str:
        """Generate explainable reason for adoption recommendation."""
        days_since_start = (datetime.now() - customer.subscription_start).days
        
        if context == "core":
            if not usage or usage.total_actions == 0:
                return (
                    f"Core feature '{feature.name}' has never been used. "
                    f"Customer has been subscribed for {days_since_start} days. "
                    f"This is essential for basic product value."
                )
            elif usage.usage_frequency < feature.usage_frequency_target:
                return (
                    f"Core feature '{feature.name}' is underutilized. "
                    f"Usage frequency ({usage.usage_frequency:.1%}) is below target "
                    f"({feature.usage_frequency_target:.1%}). "
                    f"Last used {self._days_ago_str(usage.last_used)}."
                )
        
        elif context == "expansion":
            if not usage or usage.total_actions == 0:
                return (
                    f"Premium feature '{feature.name}' is available on {customer.plan_tier} plan "
                    f"but unused. Customer has adopted {len(customer.get_adopted_features(self.data_access.get_all_features()))} features, "
                    f"suggesting readiness for advanced capabilities."
                )
            else:
                return (
                    f"Premium feature '{feature.name}' shows early interest "
                    f"({usage.total_actions} actions) but not fully adopted. "
                    f"Accelerating adoption could drive expansion."
                )
        
        return f"Feature '{feature.name}' aligns with customer's usage patterns."
    
    def _suggest_action(
        self,
        feature: Feature,
        customer: Customer,
        usage: FeatureUsage
    ) -> str:
        """Suggest concrete action for feature adoption."""
        if not usage or usage.total_actions == 0:
            return (
                f"Schedule 30-min onboarding session with {customer.account_manager} "
                f"to demonstrate {feature.name} and set up initial workflow."
            )
        else:
            days_since_last = (datetime.now() - usage.last_used).days if usage.last_used else 999
            if days_since_last > 30:
                return (
                    f"Send re-engagement email with use case examples for {feature.name}. "
                    f"Follow up with quick check-in call to address barriers."
                )
            else:
                return (
                    f"Provide advanced tips and best practices for {feature.name} "
                    f"via in-app guidance or documentation link."
                )
    
    def assess_churn_risk(self, customer: Customer) -> ChurnRiskAssessment:
        """
        Assess churn risk with explainable signals.
        Returns risk level, score, and intervention recommendations.
        """
        signals = []
        risk_score = 0.0
        
        feature_catalog = self.data_access.get_all_features()
        adopted_features = customer.get_adopted_features(feature_catalog)
        days_since_start = (datetime.now() - customer.subscription_start).days
        
        # Signal 1: Low feature adoption
        core_features = [
            f for f in feature_catalog.values()
            if f.category == FeatureCategory.CORE
        ]
        adopted_core = [f for f in core_features if f.id in adopted_features]
        adoption_rate = len(adopted_core) / len(core_features) if core_features else 0
        
        if adoption_rate < 0.5:
            signals.append(
                f"Low core feature adoption ({len(adopted_core)}/{len(core_features)} core features adopted)"
            )
            risk_score += 0.3
        
        # Signal 2: Declining usage
        recent_usage = 0
        stale_features = 0
        for feat_id, usage in customer.features.items():
            if usage.last_used:
                days_since_last = (datetime.now() - usage.last_used).days
                if days_since_last <= 30:
                    recent_usage += 1
                elif days_since_last > 60:
                    stale_features += 1
        
        if recent_usage < 2:
            signals.append(f"Low recent activity ({recent_usage} features used in last 30 days)")
            risk_score += 0.25
        
        if stale_features > 3:
            signals.append(f"Multiple features unused for 60+ days ({stale_features} features)")
            risk_score += 0.2
        
        # Signal 3: Plan-value mismatch
        if customer.plan_tier in ["professional", "enterprise"]:
            premium_features = [
                f for f in feature_catalog.values()
                if f.is_premium and f.id in adopted_features
            ]
            if len(premium_features) == 0:
                signals.append(
                    f"Premium plan ({customer.plan_tier}) but no premium features adopted"
                )
                risk_score += 0.15
        
        # Signal 4: Time-based risk (new customers)
        if days_since_start < 90 and adoption_rate < 0.3:
            signals.append(
                f"New customer ({days_since_start} days) with low early adoption"
            )
            risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.6:
            risk_level = ChurnRiskLevel.HIGH
            urgency_days = 7
            intervention = (
                f"Immediate intervention required. Schedule executive business review "
                f"with {customer.account_manager} within {urgency_days} days. "
                f"Focus on core feature adoption and value realization."
            )
        elif risk_score >= 0.35:
            risk_level = ChurnRiskLevel.MEDIUM
            urgency_days = 30
            intervention = (
                f"Proactive engagement recommended. Schedule quarterly business review "
                f"and create adoption playbook for top 3 core features. "
                f"Monitor usage trends weekly."
            )
        else:
            risk_level = ChurnRiskLevel.LOW
            urgency_days = 90
            intervention = (
                f"Maintain regular check-ins. Continue expansion conversations "
                f"around premium features and advanced use cases."
            )
        
        if not signals:
            signals.append("No significant risk signals detected")
        
        return ChurnRiskAssessment(
            risk_level=risk_level,
            risk_score=min(1.0, risk_score),
            signals=signals,
            recommended_intervention=intervention,
            urgency_days=urgency_days
        )
    
    def _days_ago_str(self, date: datetime) -> str:
        """Format days ago string."""
        if not date:
            return "never"
        days = (datetime.now() - date).days
        if days == 0:
            return "today"
        elif days == 1:
            return "1 day ago"
        else:
            return f"{days} days ago"

