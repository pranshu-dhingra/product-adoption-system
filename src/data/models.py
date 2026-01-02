"""
Data models for customer, feature usage, and product context.
Designed to support enterprise-level analysis with clear business semantics.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class FeatureCategory(Enum):
    """Feature categories for grouping and analysis."""
    CORE = "core"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    ADMIN = "admin"
    PREMIUM = "premium"


class ChurnRiskLevel(Enum):
    """Churn risk classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Feature:
    """Represents a product feature."""
    id: str
    name: str
    category: FeatureCategory
    description: str
    is_premium: bool = False
    adoption_threshold_days: int = 30  # Days to consider "adopted"
    usage_frequency_target: float = 0.5  # Target usage frequency (0-1)


@dataclass
class FeatureUsage:
    """Usage metrics for a specific feature by a customer."""
    feature_id: str
    customer_id: str
    first_used: Optional[datetime]
    last_used: Optional[datetime]
    total_sessions: int = 0
    total_actions: int = 0
    days_active: int = 0
    usage_frequency: float = 0.0  # 0-1 scale
    
    def is_adopted(self, feature: Feature) -> bool:
        """Check if feature meets adoption criteria."""
        if not self.first_used:
            return False
        days_since_first = (datetime.now() - self.first_used).days
        return (days_since_first >= feature.adoption_threshold_days and 
                self.usage_frequency >= feature.usage_frequency_target)


@dataclass
class Customer:
    """Customer profile with subscription and usage context."""
    id: str
    name: str
    plan_tier: str  # e.g., "basic", "professional", "enterprise"
    subscription_start: datetime
    mrr: float  # Monthly Recurring Revenue
    industry: str
    company_size: str
    account_manager: str
    features: Dict[str, FeatureUsage] = field(default_factory=dict)
    
    def get_active_features(self) -> List[str]:
        """Get list of feature IDs with any usage."""
        return [fid for fid, usage in self.features.items() 
                if usage.total_actions > 0]
    
    def get_adopted_features(self, feature_catalog: Dict[str, Feature]) -> List[str]:
        """Get list of adopted feature IDs."""
        return [fid for fid, usage in self.features.items()
                if fid in feature_catalog and usage.is_adopted(feature_catalog[fid])]


@dataclass
class Recommendation:
    """A structured recommendation for feature adoption or action."""
    feature_id: str
    feature_name: str
    priority: int  # 1 = highest
    reason: str  # Explainable rationale
    suggested_action: str
    expected_impact: str  # Business impact description
    confidence: float = 0.0  # 0-1 scale


@dataclass
class OnboardingStep:
    """A step in the onboarding playbook."""
    step_number: int
    title: str
    description: str
    feature_id: Optional[str] = None
    estimated_time_minutes: int = 15


@dataclass
class ChurnRiskAssessment:
    """Churn risk analysis with explainable signals."""
    risk_level: ChurnRiskLevel
    risk_score: float  # 0-1 scale
    signals: List[str]  # Explainable risk indicators
    recommended_intervention: str
    urgency_days: int  # Days until intervention needed


@dataclass
class CustomerIntelligence:
    """Complete intelligence output for a customer."""
    customer_id: str
    customer_name: str
    adoption_recommendations: List[Recommendation]
    onboarding_playbook: List[OnboardingStep]
    churn_risk: ChurnRiskAssessment
    generated_at: datetime = field(default_factory=datetime.now)

