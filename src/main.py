"""
Main entry point for Product Adoption & Expansion Intelligence Copilot.
Provides CLI interface for customer intelligence analysis.
"""
import json
import sys
import os
from typing import Optional

# Handle imports for both package and script execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.core import AdoptionCopilotAgent
from src.data.models import CustomerIntelligence


def format_intelligence(intelligence: CustomerIntelligence, format: str = "text") -> str:
    """
    Format customer intelligence for display.
    
    Args:
        intelligence: Customer intelligence data
        format: "text" or "json"
    """
    if format == "json":
        return json.dumps({
            "customer_id": intelligence.customer_id,
            "customer_name": intelligence.customer_name,
            "generated_at": intelligence.generated_at.isoformat(),
            "adoption_recommendations": [
                {
                    "feature_id": r.feature_id,
                    "feature_name": r.feature_name,
                    "priority": r.priority,
                    "reason": r.reason,
                    "suggested_action": r.suggested_action,
                    "expected_impact": r.expected_impact,
                    "confidence": r.confidence
                }
                for r in intelligence.adoption_recommendations
            ],
            "onboarding_playbook": [
                {
                    "step_number": s.step_number,
                    "title": s.title,
                    "description": s.description,
                    "feature_id": s.feature_id,
                    "estimated_time_minutes": s.estimated_time_minutes
                }
                for s in intelligence.onboarding_playbook
            ],
            "churn_risk": {
                "risk_level": intelligence.churn_risk.risk_level.value,
                "risk_score": intelligence.churn_risk.risk_score,
                "signals": intelligence.churn_risk.signals,
                "recommended_intervention": intelligence.churn_risk.recommended_intervention,
                "urgency_days": intelligence.churn_risk.urgency_days
            }
        }, indent=2)
    
    # Text format
    output = []
    output.append("=" * 80)
    output.append(f"Product Adoption & Expansion Intelligence Copilot")
    output.append("=" * 80)
    output.append("")
    output.append(f"Customer: {intelligence.customer_name} ({intelligence.customer_id})")
    output.append(f"Generated: {intelligence.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Churn Risk
    output.append("-" * 80)
    output.append("CHURN RISK ASSESSMENT")
    output.append("-" * 80)
    output.append(f"Risk Level: {intelligence.churn_risk.risk_level.value.upper()}")
    output.append(f"Risk Score: {intelligence.churn_risk.risk_score:.2f}")
    output.append("")
    output.append("Risk Signals:")
    for signal in intelligence.churn_risk.signals:
        output.append(f"  • {signal}")
    output.append("")
    output.append(f"Recommended Intervention:")
    output.append(f"  {intelligence.churn_risk.recommended_intervention}")
    output.append(f"  Urgency: {intelligence.churn_risk.urgency_days} days")
    output.append("")
    
    # Adoption Recommendations
    output.append("-" * 80)
    output.append("ADOPTION RECOMMENDATIONS")
    output.append("-" * 80)
    for i, rec in enumerate(intelligence.adoption_recommendations, 1):
        output.append(f"\n{i}. {rec.feature_name} (Priority: {rec.priority})")
        output.append(f"   Confidence: {rec.confidence:.0%}")
        output.append(f"   Reason: {rec.reason}")
        output.append(f"   Suggested Action: {rec.suggested_action}")
        output.append(f"   Expected Impact: {rec.expected_impact}")
    output.append("")
    
    # Onboarding Playbook
    output.append("-" * 80)
    output.append("ONBOARDING PLAYBOOK")
    output.append("-" * 80)
    for step in intelligence.onboarding_playbook:
        output.append(f"\nStep {step.step_number}: {step.title}")
        output.append(f"  {step.description}")
        if step.feature_id:
            output.append(f"  Feature: {step.feature_id}")
        output.append(f"  Estimated Time: {step.estimated_time_minutes} minutes")
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)


def main():
    """Main CLI entry point."""
    agent = AdoptionCopilotAgent()
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <customer_id> [format] [question]")
        print("\nExamples:")
        print("  python -m src.main cust_001")
        print("  python -m src.main cust_001 json")
        print("  python -m src.main cust_001 text 'What is the churn risk?'")
        print("\nAvailable customers:")
        data_access = agent.data_access
        for cust_id in data_access.list_customers():
            customer = data_access.get_customer(cust_id)
            print(f"  {cust_id}: {customer.name}")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "text"
    question = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        if question:
            # Answer specific question
            answer = agent.answer_question(customer_id, question)
            print(answer)
        else:
            # Full intelligence analysis
            intelligence = agent.analyze_customer(customer_id)
            print(format_intelligence(intelligence, format=output_format))
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

