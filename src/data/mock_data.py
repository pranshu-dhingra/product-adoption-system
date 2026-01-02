"""
Mock data generator for product adoption analysis.
Creates realistic customer usage patterns for demonstration.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, List
from .models import (
    Customer, Feature, FeatureUsage, FeatureCategory,
    ChurnRiskLevel
)


# Feature catalog - represents available product features
FEATURE_CATALOG = {
    "feat_core_dashboard": Feature(
        id="feat_core_dashboard",
        name="Core Dashboard",
        category=FeatureCategory.CORE,
        description="Main analytics dashboard with key metrics",
        is_premium=False,
        adoption_threshold_days=7,
        usage_frequency_target=0.7
    ),
    "feat_core_reports": Feature(
        id="feat_core_reports",
        name="Custom Reports",
        category=FeatureCategory.CORE,
        description="Create and export custom reports",
        is_premium=False,
        adoption_threshold_days=14,
        usage_frequency_target=0.4
    ),
    "feat_collab_teams": Feature(
        id="feat_collab_teams",
        name="Team Collaboration",
        category=FeatureCategory.COLLABORATION,
        description="Share insights and collaborate with team members",
        is_premium=False,
        adoption_threshold_days=21,
        usage_frequency_target=0.5
    ),
    "feat_collab_comments": Feature(
        id="feat_collab_comments",
        name="Comments & Annotations",
        category=FeatureCategory.COLLABORATION,
        description="Add comments and annotations to reports",
        is_premium=True,
        adoption_threshold_days=30,
        usage_frequency_target=0.3
    ),
    "feat_analytics_advanced": Feature(
        id="feat_analytics_advanced",
        name="Advanced Analytics",
        category=FeatureCategory.ANALYTICS,
        description="Advanced statistical analysis and forecasting",
        is_premium=True,
        adoption_threshold_days=45,
        usage_frequency_target=0.2
    ),
    "feat_analytics_ai": Feature(
        id="feat_analytics_ai",
        name="AI-Powered Insights",
        category=FeatureCategory.ANALYTICS,
        description="Automated insights and anomaly detection",
        is_premium=True,
        adoption_threshold_days=60,
        usage_frequency_target=0.15
    ),
    "feat_integration_api": Feature(
        id="feat_integration_api",
        name="API Integration",
        category=FeatureCategory.INTEGRATION,
        description="REST API for data integration",
        is_premium=False,
        adoption_threshold_days=30,
        usage_frequency_target=0.3
    ),
    "feat_integration_webhook": Feature(
        id="feat_integration_webhook",
        name="Webhook Integration",
        category=FeatureCategory.INTEGRATION,
        description="Real-time webhook notifications",
        is_premium=True,
        adoption_threshold_days=45,
        usage_frequency_target=0.25
    ),
    "feat_admin_audit": Feature(
        id="feat_admin_audit",
        name="Audit Logs",
        category=FeatureCategory.ADMIN,
        description="Comprehensive audit logging",
        is_premium=True,
        adoption_threshold_days=30,
        usage_frequency_target=0.1
    ),
    "feat_admin_sso": Feature(
        id="feat_admin_sso",
        name="SSO Authentication",
        category=FeatureCategory.ADMIN,
        description="Single Sign-On integration",
        is_premium=True,
        adoption_threshold_days=60,
        usage_frequency_target=0.1
    ),
}


def generate_feature_usage(
    customer_id: str,
    feature_id: str,
    days_since_start: int,
    adoption_probability: float = 0.6,
    usage_intensity: str = "normal"
) -> FeatureUsage:
    """
    Generate realistic feature usage data.
    
    Args:
        customer_id: Customer identifier
        feature_id: Feature identifier
        days_since_start: Days since customer subscription started
        adoption_probability: Probability that customer has used this feature
        usage_intensity: "low", "normal", "high"
    """
    if random.random() > adoption_probability:
        # Feature not used
        return FeatureUsage(
            feature_id=feature_id,
            customer_id=customer_id,
            first_used=None,
            last_used=None,
            total_sessions=0,
            total_actions=0,
            days_active=0,
            usage_frequency=0.0
        )
    
    # Feature has been used
    first_used_days_ago = random.randint(0, min(days_since_start, 90))
    first_used = datetime.now() - timedelta(days=first_used_days_ago)
    
    # Determine usage intensity
    intensity_multipliers = {
        "low": (0.3, 0.2),
        "normal": (1.0, 0.5),
        "high": (2.5, 0.8)
    }
    session_mult, freq_mult = intensity_multipliers.get(usage_intensity, (1.0, 0.5))
    
    days_active = max(1, int((days_since_start - first_used_days_ago) * freq_mult))
    total_sessions = max(1, int(days_active * session_mult * random.uniform(0.5, 1.5)))
    total_actions = total_sessions * random.randint(3, 15)
    
    # Usage frequency: active days / total days since first use
    days_since_first = max(1, (datetime.now() - first_used).days)
    usage_frequency = min(1.0, days_active / days_since_first)
    
    last_used = first_used + timedelta(days=random.randint(0, days_since_first))
    
    return FeatureUsage(
        feature_id=feature_id,
        customer_id=customer_id,
        first_used=first_used,
        last_used=last_used,
        total_sessions=total_sessions,
        total_actions=total_actions,
        days_active=days_active,
        usage_frequency=usage_frequency
    )


def generate_customer(
    customer_id: str,
    name: str,
    plan_tier: str,
    subscription_start: datetime,
    mrr: float,
    industry: str,
    company_size: str,
    account_manager: str,
    usage_profile: str = "normal"
) -> Customer:
    """
    Generate a customer with realistic usage patterns.
    
    Args:
        usage_profile: "healthy", "normal", "at_risk", "champion"
    """
    days_since_start = (datetime.now() - subscription_start).days
    
    # Define usage patterns by profile
    profile_configs = {
        "healthy": {
            "core_adoption": 0.9,
            "premium_adoption": 0.4,
            "intensity": "normal"
        },
        "normal": {
            "core_adoption": 0.7,
            "premium_adoption": 0.2,
            "intensity": "normal"
        },
        "at_risk": {
            "core_adoption": 0.4,
            "premium_adoption": 0.05,
            "intensity": "low"
        },
        "champion": {
            "core_adoption": 0.95,
            "premium_adoption": 0.7,
            "intensity": "high"
        }
    }
    
    config = profile_configs.get(usage_profile, profile_configs["normal"])
    
    # Generate feature usage
    features = {}
    for feat_id, feature in FEATURE_CATALOG.items():
        adoption_prob = config["core_adoption"] if not feature.is_premium else config["premium_adoption"]
        features[feat_id] = generate_feature_usage(
            customer_id=customer_id,
            feature_id=feat_id,
            days_since_start=days_since_start,
            adoption_probability=adoption_prob,
            usage_intensity=config["intensity"]
        )
    
    return Customer(
        id=customer_id,
        name=name,
        plan_tier=plan_tier,
        subscription_start=subscription_start,
        mrr=mrr,
        industry=industry,
        company_size=company_size,
        account_manager=account_manager,
        features=features
    )


def generate_mock_customers() -> Dict[str, Customer]:
    """Generate a set of mock customers with varied profiles."""
    customers = {}
    
    # Healthy customer
    customers["cust_001"] = generate_customer(
        customer_id="cust_001",
        name="Acme Corporation",
        plan_tier="enterprise",
        subscription_start=datetime.now() - timedelta(days=180),
        mrr=5000.0,
        industry="Technology",
        company_size="500-1000",
        account_manager="Sarah Johnson",
        usage_profile="healthy"
    )
    
    # Normal customer
    customers["cust_002"] = generate_customer(
        customer_id="cust_002",
        name="TechStart Inc",
        plan_tier="professional",
        subscription_start=datetime.now() - timedelta(days=120),
        mrr=1500.0,
        industry="SaaS",
        company_size="50-200",
        account_manager="Mike Chen",
        usage_profile="normal"
    )
    
    # At-risk customer
    customers["cust_003"] = generate_customer(
        customer_id="cust_003",
        name="Legacy Systems Co",
        plan_tier="professional",
        subscription_start=datetime.now() - timedelta(days=200),
        mrr=2000.0,
        industry="Manufacturing",
        company_size="200-500",
        account_manager="Sarah Johnson",
        usage_profile="at_risk"
    )
    
    # Champion customer
    customers["cust_004"] = generate_customer(
        customer_id="cust_004",
        name="Innovation Labs",
        plan_tier="enterprise",
        subscription_start=datetime.now() - timedelta(days=365),
        mrr=8000.0,
        industry="Technology",
        company_size="1000+",
        account_manager="Mike Chen",
        usage_profile="champion"
    )
    
    # New customer (low adoption expected)
    customers["cust_005"] = generate_customer(
        customer_id="cust_005",
        name="Fresh Startup",
        plan_tier="basic",
        subscription_start=datetime.now() - timedelta(days=30),
        mrr=500.0,
        industry="E-commerce",
        company_size="10-50",
        account_manager="Sarah Johnson",
        usage_profile="normal"
    )
    
    return customers


def get_feature_catalog() -> Dict[str, Feature]:
    """Get the feature catalog."""
    return FEATURE_CATALOG.copy()

