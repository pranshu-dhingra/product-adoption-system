"""
Demo script for Product Adoption & Expansion Intelligence Copilot.
Demonstrates the system with example customer analyses.
"""
from src.agent.core import AdoptionCopilotAgent
from src.main import format_intelligence


def run_demo():
    """Run demonstration of the copilot system."""
    print("\n" + "=" * 80)
    print("Product Adoption & Expansion Intelligence Copilot - Demo")
    print("=" * 80 + "\n")
    
    agent = AdoptionCopilotAgent()
    
    # Demo 1: Healthy customer
    print("\n" + "=" * 80)
    print("DEMO 1: Healthy Customer (cust_001 - Acme Corporation)")
    print("=" * 80)
    intelligence1 = agent.analyze_customer("cust_001")
    print(format_intelligence(intelligence1))
    
    # Demo 2: At-risk customer
    print("\n\n" + "=" * 80)
    print("DEMO 2: At-Risk Customer (cust_003 - Legacy Systems Co)")
    print("=" * 80)
    intelligence2 = agent.analyze_customer("cust_003")
    print(format_intelligence(intelligence2))
    
    # Demo 3: Question answering
    print("\n\n" + "=" * 80)
    print("DEMO 3: Question Answering (cust_002 - TechStart Inc)")
    print("=" * 80)
    print("\nQuestion: What is the churn risk?")
    answer1 = agent.answer_question("cust_002", "What is the churn risk?")
    print(answer1)
    
    print("\n\nQuestion: What features should they adopt?")
    answer2 = agent.answer_question("cust_002", "What features should they adopt?")
    print(answer2)
    
    print("\n\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_demo()

