"""
Agent core with reasoning engine.
Orchestrates tools and memory to generate customer intelligence.
"""
from typing import Optional
from datetime import datetime
from ..data.models import (
    Customer, CustomerIntelligence, Recommendation,
    OnboardingStep, ChurnRiskAssessment
)
from ..tools.data_access import DataAccessTool
from ..tools.analysis import AnalysisTool
from ..memory.context import MemoryStore


class AdoptionCopilotAgent:
    """
    Core agent for product adoption and expansion intelligence.
    
    Architecture:
    - Reasoning: Orchestrates analysis tools to answer business questions
    - Tools: Data access and analysis capabilities
    - Memory: Context and historical patterns
    - Explainability: Every output includes clear rationale
    """
    
    def __init__(
        self,
        data_access: Optional[DataAccessTool] = None,
        analysis_tool: Optional[AnalysisTool] = None,
        memory: Optional[MemoryStore] = None
    ):
        """
        Initialize agent with dependencies.
        Allows injection for testing or production use.
        """
        self.data_access = data_access or DataAccessTool()
        self.analysis = analysis_tool or AnalysisTool(self.data_access)
        self.memory = memory or MemoryStore()
    
    def analyze_customer(
        self,
        customer_id: str
    ) -> CustomerIntelligence:
        """
        Main entry point: Generate complete intelligence for a customer.
        
        Reasoning flow:
        1. Retrieve customer data
        2. Analyze feature adoption opportunities
        3. Assess churn risk
        4. Generate onboarding playbook
        5. Store context in memory
        6. Return structured intelligence
        """
        # Step 1: Retrieve customer
        customer = self.data_access.get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Step 2: Store context
        self.memory.store_customer_context(customer_id, {
            "plan_tier": customer.plan_tier,
            "mrr": customer.mrr,
            "industry": customer.industry,
            "company_size": customer.company_size,
            "account_manager": customer.account_manager
        })
        
        # Step 3: Analyze adoption opportunities
        recommendations = self.analysis.analyze_feature_adoption(customer)
        self.memory.store_recommendations(customer_id, recommendations)
        
        # Step 4: Assess churn risk
        churn_risk = self.analysis.assess_churn_risk(customer)
        self.memory.store_churn_assessment(customer_id, churn_risk)
        
        # Step 5: Generate onboarding playbook
        onboarding_playbook = self._generate_onboarding_playbook(
            customer, recommendations
        )
        
        # Step 6: Return complete intelligence
        return CustomerIntelligence(
            customer_id=customer.id,
            customer_name=customer.name,
            adoption_recommendations=recommendations[:3],  # Top 3
            onboarding_playbook=onboarding_playbook,
            churn_risk=churn_risk,
            generated_at=datetime.now()
        )
    
    def _generate_onboarding_playbook(
        self,
        customer: Customer,
        recommendations: list[Recommendation]
    ) -> list[OnboardingStep]:
        """
        Generate personalized onboarding playbook from recommendations.
        Focuses on highest-priority features.
        """
        playbook = []
        
        if not recommendations:
            # Default onboarding if no specific recommendations
            playbook.append(OnboardingStep(
                step_number=1,
                title="Explore Core Dashboard",
                description="Get familiar with the main analytics dashboard and key metrics",
                feature_id="feat_core_dashboard",
                estimated_time_minutes=15
            ))
            return playbook
        
        # Build playbook from top recommendations
        top_recommendation = recommendations[0]
        feature = self.data_access.get_feature(top_recommendation.feature_id)
        
        if feature:
            playbook.append(OnboardingStep(
                step_number=1,
                title=f"Set up {feature.name}",
                description=top_recommendation.suggested_action,
                feature_id=feature.id,
                estimated_time_minutes=30
            ))
        
        # Add second step if available
        if len(recommendations) > 1:
            second_rec = recommendations[1]
            second_feature = self.data_access.get_feature(second_rec.feature_id)
            if second_feature:
                playbook.append(OnboardingStep(
                    step_number=2,
                    title=f"Explore {second_feature.name}",
                    description=second_rec.suggested_action,
                    feature_id=second_feature.id,
                    estimated_time_minutes=20
                ))
        
        # Add general enablement step
        playbook.append(OnboardingStep(
            step_number=len(playbook) + 1,
            title="Schedule Success Review",
            description=(
                f"Book a 30-minute call with {customer.account_manager} "
                f"to review progress and discuss next steps"
            ),
            estimated_time_minutes=30
        ))
        
        return playbook
    
    def answer_question(
        self,
        customer_id: str,
        question: str
    ) -> str:
        """
        Answer specific questions about a customer.
        Demonstrates agentic reasoning with tool use.
        """
        customer = self.data_access.get_customer(customer_id)
        if not customer:
            return f"Customer {customer_id} not found."
        
        question_lower = question.lower()
        
        # Route to appropriate analysis
        if "churn" in question_lower or "risk" in question_lower:
            assessment = self.analysis.assess_churn_risk(customer)
            trend = self.memory.get_risk_trend(customer_id)
            trend_str = f" (trend: {trend})" if trend else ""
            return (
                f"Churn Risk: {assessment.risk_level.value.upper()} "
                f"(score: {assessment.risk_score:.2f}){trend_str}\n\n"
                f"Signals:\n" + "\n".join(f"  - {s}" for s in assessment.signals) + "\n\n"
                f"Intervention: {assessment.recommended_intervention}"
            )
        
        elif "adopt" in question_lower or "feature" in question_lower:
            recommendations = self.analysis.analyze_feature_adoption(customer)
            if not recommendations:
                return "No adoption recommendations at this time."
            
            result = "Top Adoption Recommendations:\n\n"
            for i, rec in enumerate(recommendations[:3], 1):
                result += (
                    f"{i}. {rec.feature_name} (Priority: {rec.priority})\n"
                    f"   Reason: {rec.reason}\n"
                    f"   Action: {rec.suggested_action}\n\n"
                )
            return result
        
        elif "using" in question_lower or "usage" in question_lower:
            adopted = customer.get_adopted_features(self.data_access.get_all_features())
            active = customer.get_active_features()
            return (
                f"Customer has {len(adopted)} adopted features and {len(active)} active features.\n"
                f"Adopted: {', '.join(adopted[:5])}{'...' if len(adopted) > 5 else ''}"
            )
        
        else:
            # General intelligence summary
            intelligence = self.analyze_customer(customer_id)
            return self._format_intelligence_summary(intelligence)
    
    def _format_intelligence_summary(self, intelligence: CustomerIntelligence) -> str:
        """Format intelligence as readable summary."""
        return (
            f"Customer Intelligence for {intelligence.customer_name}:\n\n"
            f"Churn Risk: {intelligence.churn_risk.risk_level.value.upper()}\n"
            f"Top Recommendations: {len(intelligence.adoption_recommendations)}\n"
            f"Onboarding Steps: {len(intelligence.onboarding_playbook)}\n"
            f"Generated: {intelligence.generated_at.strftime('%Y-%m-%d %H:%M')}"
        )

