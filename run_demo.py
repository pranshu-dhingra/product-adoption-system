"""
Interactive command-line interface for Product Adoption & Expansion Intelligence Copilot.

Sample interaction:
  > cust_005
  Customer Summary: Fresh Startup | Plan: basic | MRR: $500 | Age: 30 days | 
  Core Adoption: Low (1/2) | Risk: LOW | Recent Usage: 2 features (last 7d)
  
  Menu:
  1) View Adoption Snapshot
  2) View Churn Risk Summary
  3) View Top Recommendations
  4) View Onboarding Playbook
  5) Show Raw Usage Data
  6) Ask Free-Form Question
  7) Expand All
  8) Back / Exit
  
  > 1
  Adoption Snapshot — Core Dashboard
  Key Claim: Core feature 'Core Dashboard' has never been used.
  Evidence:
    • Customer subscribed for 30 days
    • 0 total actions recorded
    • Feature adoption threshold: 7 days
  Confidence: 85%
  Suggested Action:
    1. Schedule 30-min onboarding session with Sarah Johnson (30 min)
    2. Demonstrate Core Dashboard workflow (15 min)

Run: python run_demo.py
"""
import sys
import os
import csv
import textwrap
from datetime import datetime
from typing import Optional, List, Dict

# Add current directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.core import AdoptionCopilotAgent
from src.data.models import Customer


# Logging setup
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "interaction_log.csv")


def wrap_text(text: str, width: int = 80, indent: int = 0, subsequent_indent: int = None) -> List[str]:
    """
    Wrap text at word boundaries with proper indentation.
    
    Args:
        text: Text to wrap
        width: Maximum line width (default 80)
        indent: Initial line indentation (default 0)
        subsequent_indent: Subsequent lines indentation (defaults to indent)
    
    Returns:
        List of wrapped lines
    """
    if subsequent_indent is None:
        subsequent_indent = indent
    
    # Calculate effective width (accounting for indentation)
    effective_width = width - indent
    
    # Wrap the text
    wrapper = textwrap.TextWrapper(
        width=effective_width,
        initial_indent=' ' * indent,
        subsequent_indent=' ' * subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False
    )
    
    return wrapper.wrap(text)


def format_wrapped_text(text: str, prefix: str = "", width: int = 80) -> List[str]:
    """
    Format text with a prefix, wrapping at word boundaries.
    Preserves prefix on first line, indents subsequent lines.
    
    Args:
        text: Text to format
        prefix: Prefix string (e.g., "WHY:", "WHAT:", "ACTION:")
        width: Maximum line width (default 80)
    
    Returns:
        List of formatted lines
    """
    if not text:
        return [prefix] if prefix else []
    
    # Calculate indentation based on prefix length
    prefix_len = len(prefix)
    
    # If prefix exists, combine with text
    if prefix:
        # Add space after prefix if not already present
        if prefix and not prefix.endswith(' '):
            full_text = f"{prefix} {text}"
        else:
            full_text = f"{prefix}{text}"
        # Subsequent lines should align with text after prefix
        subsequent_indent = prefix_len + 1  # prefix + space
    else:
        full_text = text
        subsequent_indent = 0
    
    # Calculate effective width for wrapping
    effective_width = width
    
    # Wrap the text
    wrapper = textwrap.TextWrapper(
        width=effective_width,
        initial_indent='',
        subsequent_indent=' ' * subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False
    )
    
    return wrapper.wrap(full_text)


def ensure_logs_dir():
    """Create logs directory if it doesn't exist."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)


def log_interaction(
    customer_id: str,
    action: str,
    query: str = "",
    result_key: str = ""
):
    """
    Log user interaction to CSV file.
    
    Columns: timestamp, user, customer_id, action, summary_of_query, result_key
    """
    ensure_logs_dir()
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if new file
        if not file_exists:
            writer.writerow([
                'timestamp', 'user', 'customer_id', 'action', 
                'summary_of_query', 'result_key'
            ])
        
        # Write interaction record
        writer.writerow([
            datetime.now().isoformat(),
            'cli_user',  # Could be enhanced with actual user identification
            customer_id,
            action,
            query[:200] if query else '',  # Truncate long queries
            result_key
        ])


def print_welcome():
    """Display welcome message."""
    print("\n" + "=" * 80)
    print("Product Adoption & Expansion Intelligence Copilot")
    print("=" * 80)
    print("\nAnalyze customer adoption, expansion opportunities, and churn risk.")
    print("\nCommands:")
    print("  <customer_id>  - Analyze a specific customer (e.g., cust_001)")
    print("  list           - Show all available customers")
    print("  help           - Display help message")
    print("  quit / exit    - Exit the application")
    print()


def list_customers(agent, limit: Optional[int] = None):
    """
    Display available customers, optionally limited to top N by MRR.
    Default shows all if dataset is small (< 20 customers).
    """
    data_access = agent.data_access
    customer_ids = data_access.list_customers()
    
    if not customer_ids:
        print("\n[INFO] No customers found in dataset.")
        return
    
    # Show all if dataset is small, otherwise respect limit
    if limit is None and len(customer_ids) > 20:
        limit = 20
    elif limit is None:
        limit = len(customer_ids)
    
    customers = []
    for cust_id in customer_ids:
        customer = data_access.get_customer(cust_id)
        if customer:
            customers.append((customer, cust_id))
    
    # Sort by MRR descending
    customers.sort(key=lambda x: x[0].mrr, reverse=True)
    
    display_count = min(limit, len(customers))
    print(f"\nAvailable Customers ({display_count} of {len(customers)} shown):")
    print("-" * 80)
    
    for customer, cust_id in customers[:display_count]:
        print(f"  {cust_id:12} - {customer.name:30} | "
              f"Plan: {customer.plan_tier:12} | MRR: ${customer.mrr:>8,.0f}")
    
    if len(customers) > display_count:
        print(f"\n  ... and {len(customers) - display_count} more. Use 'list N' to see more.")
    print()


def generate_customer_summary(agent, customer: Customer) -> Dict[str, str]:
    """
    Generate concise customer summary with 4-6 top-level signals.
    Returns dict of signal labels and values for display.
    """
    from datetime import datetime
    
    days_since_start = (datetime.now() - customer.subscription_start).days
    
    # Calculate core feature adoption
    feature_catalog = agent.data_access.get_all_features()
    core_features = [f for f in feature_catalog.values() 
                     if f.category.value == "core"]
    adopted_core = customer.get_adopted_features(feature_catalog)
    adopted_core_count = len([f for f in core_features if f.id in adopted_core])
    core_adoption_status = "High" if adopted_core_count >= len(core_features) * 0.8 else \
                          "OK" if adopted_core_count >= len(core_features) * 0.5 else "Low"
    
    # Calculate recent usage (last 30 days)
    recent_features = 0
    for usage in customer.features.values():
        if usage.last_used:
            days_since = (datetime.now() - usage.last_used).days
            if days_since <= 30:
                recent_features += 1
    
    # Get churn risk (quick assessment)
    churn_risk = agent.analysis.assess_churn_risk(customer)
    risk_label = churn_risk.risk_level.value.upper()
    
    # Check for usage trend (simplified: compare last 30d vs 60d)
    usage_trend = "+" if recent_features >= 2 else "-" if recent_features == 0 else "~"
    
    return {
        "org": customer.name,
        "plan": customer.plan_tier,
        "mrr": f"${customer.mrr:,.0f}",
        "age_days": str(days_since_start),
        "core_adoption": f"{core_adoption_status} ({adopted_core_count}/{len(core_features)})",
        "risk": risk_label,
        "recent_usage": f"{recent_features} features (last 30d)",
        "usage_trend": usage_trend
    }


def print_customer_summary(agent, customer: Customer):
    """Display concise customer summary in one-line format."""
    summary = generate_customer_summary(agent, customer)
    
    print("\n" + "=" * 80)
    print(f"Customer Summary: {summary['org']} | "
          f"Plan: {summary['plan']} | "
          f"MRR: {summary['mrr']} | "
          f"Age: {summary['age_days']} days")
    print(f"Core Adoption: {summary['core_adoption']} | "
          f"Risk: {summary['risk']} | "
          f"Recent Usage: {summary['recent_usage']} | "
          f"Trend: {summary['usage_trend']}")
    print("=" * 80)


def print_menu():
    """Display the selective reasoning menu."""
    print("\nMenu:")
    print("  1) View Adoption Snapshot")
    print("  2) View Churn Risk Summary")
    print("  3) View Top Recommendations")
    print("  4) View Onboarding Playbook")
    print("  5) Show Raw Usage Data")
    print("  6) Ask Free-Form Question")
    print("  7) Expand All")
    print("  8) Back / Exit")
    print()


def format_adoption_snapshot(agent, customer: Customer) -> str:
    """
    Format concise adoption snapshot using ACTION/DECISION structure.
    Menu-driven output uses WHY → WHAT → ACTION for prescriptive guidance.
    Reuses existing analysis logic but presents in CSM-friendly format.
    """
    recommendations = agent.analysis.analyze_feature_adoption(customer)
    
    if not recommendations:
        return "No adoption recommendations available."
    
    top_rec = recommendations[0]
    feature = agent.data_access.get_feature(top_rec.feature_id)
    usage = customer.features.get(top_rec.feature_id)
    
    # Gather concrete evidence from data
    evidence = []
    if usage:
        if usage.total_actions == 0:
            evidence.append(f"• 0 total actions recorded")
        else:
            evidence.append(f"• {usage.total_actions} total actions")
            if usage.last_used:
                days_ago = (datetime.now() - usage.last_used).days
                evidence.append(f"• Last used {days_ago} days ago")
            evidence.append(f"• Usage frequency: {usage.usage_frequency:.1%}")
    else:
        evidence.append(f"• Feature never used")
    
    days_since_start = (datetime.now() - customer.subscription_start).days
    evidence.append(f"• Customer subscribed for {days_since_start} days")
    
    if feature:
        evidence.append(f"• Adoption threshold: {feature.adoption_threshold_days} days")
    
    # Format confidence
    confidence_pct = int(top_rec.confidence * 100)
    confidence_label = "High" if confidence_pct >= 70 else "Medium" if confidence_pct >= 40 else "Low"
    
    # Format action steps
    action_steps = top_rec.suggested_action.split('. ')
    if len(action_steps) > 1:
        action_steps = [s.strip() for s in action_steps if s.strip()]
    else:
        action_steps = [top_rec.suggested_action]
    
    output = []
    output.append(f"\nAdoption Snapshot — {top_rec.feature_name}")
    output.append("-" * 80)
    
    # WHY → WHAT → ACTION structure
    # WHY: Brief factual cause (1-2 lines max)
    output.append("WHY:")
    if usage and usage.total_actions == 0:
        output.append(f"  Feature never used after {days_since_start} days")
    elif usage and usage.last_used:
        days_ago = (datetime.now() - usage.last_used).days
        output.append(f"  Feature underutilized (last used {days_ago} days ago)")
    else:
        output.append(f"  Core feature adoption gap identified")

    # WHAT: Current state or gap (1 short line)
    output.append("")
    output.extend(format_wrapped_text(top_rec.reason, prefix="WHAT:", width=80))

    # ACTION: Concrete next step (who + what + timeframe)
    output.append("\nACTION:")
    for i, step in enumerate(action_steps[:3], 1):  # Max 3 steps
        time_est = "15 min" if i == 1 else "20 min"
        step_text = f"{step} ({time_est})"
        output.extend(format_wrapped_text(step_text, prefix=f"  {i}.", width=80))
    
    output.append("")
    
    return "\n".join(output)


def format_churn_risk_summary(agent, customer: Customer) -> str:
    """
    Format churn risk summary using DIAGNOSTIC structure.
    Menu-driven output always includes WHY layer for CSM decision-making.
    """
    assessment = agent.analysis.assess_churn_risk(customer)
    
    # Get trend if available
    trend = agent.memory.get_risk_trend(customer.id)
    trend_str = f" (trend: {trend})" if trend else ""
    
    # Format risk score as percentage
    risk_pct = int(assessment.risk_score * 100)
    
    output = []
    output.append(f"\nChurn Risk Summary")
    output.append("-" * 80)
    output.append(f"Risk Level: {assessment.risk_level.value.upper()} "
                  f"(score: {risk_pct}%){trend_str}")
    
    # WHY structure: Signals → Interpretation → Implication
    output.append("\nObserved Signals:")
    for signal in assessment.signals[:5]:  # Top 5 signals
        output.extend(format_wrapped_text(signal, prefix="  •", width=80))
    
    # Interpretation layer
    if assessment.risk_level.value == 'high':
        output.append("\nInterpretation: Multiple risk indicators suggest elevated churn probability.")
    elif assessment.risk_level.value == 'medium':
        output.append("\nInterpretation: Some risk signals present, but not yet critical.")
    else:
        output.append("\nInterpretation: No significant risk patterns detected.")
    
    # Business implication
    output.append(f"\nBusiness Implication:")
    output.extend(format_wrapped_text(assessment.recommended_intervention, prefix="  ", width=80))
    output.append(f"  Urgency: {assessment.urgency_days} days")
    output.append("")
    
    return "\n".join(output)


def format_top_recommendations(agent, customer: Customer) -> str:
    """
    Format top recommendations using ACTION/DECISION structure.
    Menu-driven output uses WHY → WHAT → ACTION for prescriptive guidance.
    """
    recommendations = agent.analysis.analyze_feature_adoption(customer)
    
    if not recommendations:
        return "\nNo recommendations available.\n"
    
    output = []
    output.append("\nTop Recommendations")
    output.append("-" * 80)
    
    for i, rec in enumerate(recommendations[:3], 1):  # Top 3
        confidence_pct = int(rec.confidence * 100)
        output.append(f"\n{i}. {rec.feature_name} (Priority {rec.priority}, {confidence_pct}% confidence)")
        
        # WHY → WHAT → ACTION structure
        # WHY: Brief factual cause (1-2 lines max)
        output.extend(format_wrapped_text(rec.reason, prefix="   WHY:", width=80))
        # WHAT: Current state or gap (1 short line)
        feature = agent.data_access.get_feature(rec.feature_id)
        usage = customer.features.get(rec.feature_id)
        if usage and usage.total_actions == 0:
            what_state = "Feature not adopted"
        elif usage:
            what_state = f"Feature underutilized ({usage.usage_frequency:.0%} frequency)"
        else:
            what_state = "Feature adoption gap"
        output.append(f"   WHAT: {what_state}")
        # ACTION: Concrete next step (who + what + timeframe)
        output.extend(format_wrapped_text(rec.suggested_action, prefix="   ACTION:", width=80))
    
    output.append("")
    return "\n".join(output)


def format_onboarding_playbook(agent, customer: Customer) -> str:
    """
    Format onboarding playbook using ACTION/DECISION structure.
    Menu-driven output uses WHY → WHAT → ACTION for prescriptive guidance.
    """
    recommendations = agent.analysis.analyze_feature_adoption(customer)
    playbook = agent._generate_onboarding_playbook(customer, recommendations)
    
    if not playbook:
        return "\nNo onboarding steps available.\n"
    
    output = []
    output.append("\nOnboarding Playbook")
    output.append("-" * 80)
    
    # WHY: Brief factual cause (1-2 lines max)
    if recommendations:
        top_rec = recommendations[0]
        output.append("")
        output.extend(format_wrapped_text(top_rec.reason, prefix="WHY:", width=80))

    # WHAT: Current state or gap (1 short line)
    feature_catalog = agent.data_access.get_all_features()
    adopted = customer.get_adopted_features(feature_catalog)
    core_features = [f for f in feature_catalog.values() if f.category.value == "core"]
    adopted_core = len([f.id for f in core_features if f.id in adopted])
    output.append(f"\nWHAT: {adopted_core}/{len(core_features)} core features adopted")

    # ACTION: Concrete next steps (who + what + timeframe)
    output.append("\nACTION:")
    for step in playbook:
        output.append(f"  {step.step_number}. {step.title}")
        output.append(f"     {step.description}")
        output.append(f"     Time: {step.estimated_time_minutes} minutes")
    
    output.append("")
    return "\n".join(output)


def format_raw_usage_data(agent, customer: Customer, limit: int = 10) -> str:
    """Format raw usage data as a simple table."""
    output = []
    output.append("\nRaw Usage Data (Top Features)")
    output.append("-" * 80)
    output.append(f"{'Feature ID':<25} {'Actions':<10} {'Sessions':<10} {'Last Used':<15} {'Frequency':<10}")
    output.append("-" * 80)
    
    # Sort by total_actions descending
    usage_items = sorted(
        customer.features.items(),
        key=lambda x: x[1].total_actions,
        reverse=True
    )
    
    for feat_id, usage in usage_items[:limit]:
        last_used_str = "Never" if not usage.last_used else \
                       f"{(datetime.now() - usage.last_used).days}d ago"
        freq_str = f"{usage.usage_frequency:.1%}"
        
        output.append(f"{feat_id:<25} {usage.total_actions:<10} "
                     f"{usage.total_sessions:<10} {last_used_str:<15} {freq_str:<10}")
    
    output.append("")
    return "\n".join(output)


def classify_question_intent_type(question: str, intent: str) -> str:
    """
    Classify question into one of three answer composition types:
    - FACT/STATUS: Informational questions (just facts, no causal reasoning)
    - DIAGNOSTIC: Explanatory questions (include WHY: signals → interpretation → implication)
    - ACTION/DECISION: Prescriptive questions (WHY → WHAT → ACTION structure)
    
    Determines how answer should be structured, not what data to retrieve.
    """
    question_lower = question.lower()
    
    # ACTION/DECISION: Questions asking what to do, what actions to take
    # Detected via: "should", "what to do", "recommend", "next steps", "pitch", "focus"
    action_keywords = ['should', 'what to do', 'recommend', 'next step', 'action', 
                      'pitch', 'focus on', 'prioritize', 'do this week', 'suggest']
    if any(kw in question_lower for kw in action_keywords):
        return 'ACTION_DECISION'
    
    # DIAGNOSTIC: Questions asking why, how engaged, what's wrong, explain
    # Detected via: "why", "how engaged", "explain", "what's wrong", "reason"
    diagnostic_keywords = ['why', 'how engaged', 'explain', "what's wrong", 'reason',
                          'cause', 'because', 'low', 'high', 'problem', 'issue']
    if any(kw in question_lower for kw in diagnostic_keywords):
        return 'DIAGNOSTIC'
    
    # Intent-based classification: some intents are inherently diagnostic or action-oriented
    if intent in ['recommendations', 'onboarding']:
        return 'ACTION_DECISION'
    
    if intent in ['churn_risk']:
        # Churn risk can be FACT (what is risk) or DIAGNOSTIC (why is risk high)
        if any(kw in question_lower for kw in diagnostic_keywords):
            return 'DIAGNOSTIC'
        return 'FACT_STATUS'
    
    # FACT/STATUS: Default for informational questions
    # "what is", "how many", "show me", "tell me about" (without why/how engaged)
    return 'FACT_STATUS'


def classify_question_intent(question: str) -> str:
    """
    Classify question intent using keyword matching.
    
    Intent categories:
    - overview: General customer info, summary, status
    - adoption: Feature adoption, what features used, adoption rate
    - recommendations: What should they do next, best actions, priorities
    - onboarding: Enablement steps, how to onboard, getting started
    - churn_risk: Churn risk, retention, at risk, leaving
    - usage_trends: Usage patterns, recent changes, activity trends
    - usage_data: Specific usage metrics, feature usage counts
    
    Returns intent category string.
    
    Example classifications:
    - "What is the churn risk?" → churn_risk
    - "What features should they adopt?" → recommendations
    - "How many features are they using?" → adoption
    - "What are the onboarding steps?" → onboarding
    - "Show me usage trends" → usage_trends
    - "What's the usage data?" → usage_data
    - "Tell me about this customer" → overview
    """
    question_lower = question.lower()
    
    # Churn risk keywords (highest priority to avoid false matches)
    churn_keywords = ['churn', 'risk', 'retention', 'leaving', 'cancel', 
                     'at risk', 'likely to leave', 'retention risk']
    if any(kw in question_lower for kw in churn_keywords):
        return 'churn_risk'
    
    # Recommendations keywords
    rec_keywords = ['recommend', 'should', 'next', 'best action', 'priority',
                   'what to do', 'suggest', 'advice', 'focus on']
    if any(kw in question_lower for kw in rec_keywords):
        return 'recommendations'
    
    # Onboarding keywords
    onboarding_keywords = ['onboard', 'enablement', 'getting started', 
                          'how to start', 'first steps', 'setup', 'initial']
    if any(kw in question_lower for kw in onboarding_keywords):
        return 'onboarding'
    
    # Adoption keywords
    adoption_keywords = ['adopt', 'adoption', 'using', 'features used',
                        'what features', 'feature usage', 'adopted']
    if any(kw in question_lower for kw in adoption_keywords):
        return 'adoption'
    
    # Usage trends keywords
    trend_keywords = ['trend', 'recent', 'change', 'activity', 'pattern',
                     'increasing', 'decreasing', 'last', 'recently']
    if any(kw in question_lower for kw in trend_keywords):
        return 'usage_trends'
    
    # Usage data keywords
    data_keywords = ['usage data', 'metrics', 'count', 'how many', 
                    'usage stats', 'statistics', 'numbers']
    if any(kw in question_lower for kw in data_keywords):
        return 'usage_data'
    
    # Overview keywords (catch-all for general questions)
    overview_keywords = ['overview', 'summary', 'status', 'info', 'tell me about',
                         'what about', 'how is', 'customer', 'account']
    if any(kw in question_lower for kw in overview_keywords):
        return 'overview'
    
    # Default to overview if no clear intent
    return 'overview'


def answer_question_by_intent(agent, customer: Customer, question: str, intent: str) -> str:
    """
    Route question to appropriate reasoning function based on intent.
    Returns targeted answer with selective causal explanations based on intent type.
    
    Answer composition follows three-tier structure:
    - FACT/STATUS: Concise facts only
    - DIAGNOSTIC: Signals → Interpretation → Business Implication
    - ACTION/DECISION: WHY (brief cause) → WHAT (current state) → ACTION (next step)
    """
    from datetime import datetime
    
    # Determine answer composition type
    intent_type = classify_question_intent_type(question, intent)
    
    if intent == 'churn_risk':
        assessment = agent.analysis.assess_churn_risk(customer)
        trend = agent.memory.get_risk_trend(customer.id)
        
        if intent_type == 'FACT_STATUS':
            # Just the facts: risk level and score
            output = []
            output.append(f"Churn Risk: {assessment.risk_level.value.upper()} "
                         f"(score: {assessment.risk_score:.1%})")
            if trend:
                output.append(f"Trend: {trend}")
            return "\n".join(output)
        
        elif intent_type == 'DIAGNOSTIC':
            # WHY structure: Signals → Interpretation → Implication
            output = []
            output.append(f"Churn Risk: {assessment.risk_level.value.upper()} "
                         f"(score: {assessment.risk_score:.1%})")
            if trend:
                output.append(f"Trend: {trend}")
            
            output.append("\nObserved Signals:")
            for signal in assessment.signals:
                output.extend(format_wrapped_text(signal, prefix="  •", width=80))
            
            # Interpretation layer
            if assessment.risk_level.value == 'high':
                output.append("\nInterpretation: Multiple risk indicators suggest elevated churn probability.")
            elif assessment.risk_level.value == 'medium':
                output.append("\nInterpretation: Some risk signals present, but not yet critical.")
            else:
                output.append("\nInterpretation: No significant risk patterns detected.")
            
            # Business implication
            output.append("\nBusiness Implication:")
            output.extend(format_wrapped_text(assessment.recommended_intervention, prefix="  ", width=80))
            return "\n".join(output)
        
        else:  # ACTION_DECISION
            # WHY → WHAT → ACTION structure
            output = []
            # WHY: Brief factual cause (1-2 lines max)
            output.append("WHY:")
            if assessment.signals:
                output.append(f"  {assessment.signals[0]}")
            else:
                output.append(f"  Risk score: {assessment.risk_score:.1%}")
            
            # WHAT: Current state or gap (1 short line)
            output.append(f"\nWHAT: Churn risk is {assessment.risk_level.value.upper()}")
            
            # ACTION: Concrete next step (who + what + timeframe)
            output.append("")
            output.extend(format_wrapped_text(assessment.recommended_intervention, prefix="ACTION:", width=80))
            
            return "\n".join(output)
    
    elif intent == 'recommendations':
        recommendations = agent.analysis.analyze_feature_adoption(customer)
        
        if not recommendations:
            return ("No specific recommendations at this time. "
                   "Customer shows healthy adoption patterns.")
        
        # Recommendations are always ACTION/DECISION type
        output = []
        output.append("Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            confidence_pct = int(rec.confidence * 100)
            output.append(f"\n{i}. {rec.feature_name} ({confidence_pct}% confidence)")
            
            # WHY: Brief factual cause (1-2 lines max)
            output.extend(format_wrapped_text(rec.reason, prefix="   WHY:", width=80))
            
            # WHAT: Current state or gap (1 short line)
            usage = customer.features.get(rec.feature_id)
            if usage and usage.total_actions == 0:
                what_state = "Feature not adopted"
            elif usage:
                what_state = f"Feature underutilized"
            else:
                what_state = "Feature adoption gap"
            output.append(f"   WHAT: {what_state}")
            
            # ACTION: Concrete next step (who + what + timeframe)
            output.extend(format_wrapped_text(rec.suggested_action, prefix="   ACTION:", width=80))
        
        return "\n".join(output)
    
    elif intent == 'onboarding':
        recommendations = agent.analysis.analyze_feature_adoption(customer)
        playbook = agent._generate_onboarding_playbook(customer, recommendations)
        
        if not playbook:
            return "No specific onboarding steps available."
        
        # Onboarding is ACTION/DECISION type
        output = []
        output.append("Onboarding Playbook:")
        
        # WHY: Brief factual cause (1-2 lines max)
        if recommendations:
            top_rec = recommendations[0]
            output.append("")
            output.extend(format_wrapped_text(top_rec.reason, prefix="WHY:", width=80))
        
        # WHAT: Current state or gap (1 short line)
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        output.append(f"\nWHAT: {len(adopted)} features currently adopted")
        
        # ACTION: Concrete next steps (who + what + timeframe)
        output.append("\nACTION:")
        for step in playbook:
            output.append(f"  {step.step_number}. {step.title}")
            output.append(f"     {step.description}")
            output.append(f"     Time: {step.estimated_time_minutes} minutes")
        
        return "\n".join(output)
    
    elif intent == 'adoption':
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        active = customer.get_active_features()
        
        # Calculate core adoption
        core_features = [f for f in feature_catalog.values() 
                        if f.category.value == "core"]
        adopted_core = [f.id for f in core_features if f.id in adopted]
        
        if intent_type == 'FACT_STATUS':
            # Just the facts
            output = []
            output.append(f"Adoption Status:")
            output.append(f"  • Total adopted: {len(adopted)}")
            output.append(f"  • Active features: {len(active)}")
            output.append(f"  • Core adoption: {len(adopted_core)}/{len(core_features)}")
            if adopted:
                output.append(f"\nAdopted Features:")
                for feat_id in adopted[:5]:
                    feature = feature_catalog.get(feat_id)
                    if feature:
                        output.append(f"  • {feature.name}")
                if len(adopted) > 5:
                    output.append(f"  ... and {len(adopted) - 5} more")
            return "\n".join(output)
        
        else:  # DIAGNOSTIC
            # WHY structure: Signals → Interpretation → Implication
            output = []
            output.append("Adoption Analysis:")
            
            # Observed signals
            output.append("\nObserved Signals:")
            output.append(f"  • Total adopted features: {len(adopted)}")
            output.append(f"  • Active features: {len(active)}")
            output.append(f"  • Core features adopted: {len(adopted_core)}/{len(core_features)}")
            
            # Interpretation
            adoption_rate = len(adopted_core) / len(core_features) if core_features else 0
            if adoption_rate >= 0.8:
                output.append("\nInterpretation: Strong core feature adoption indicates healthy engagement.")
            elif adoption_rate >= 0.5:
                output.append("\nInterpretation: Moderate adoption suggests room for improvement.")
            else:
                output.append("\nInterpretation: Low core adoption may indicate value realization gaps.")
            
            # Business implication
            if adoption_rate < 0.5:
                output.append("\nBusiness Implication: Focus on core feature enablement to reduce churn risk.")
            else:
                output.append("\nBusiness Implication: Consider expansion opportunities with premium features.")
            
            return "\n".join(output)
    
    elif intent == 'usage_trends':
        # Analyze recent usage patterns
        recent_30d = 0
        recent_7d = 0
        stale_features = 0
        
        for usage in customer.features.values():
            if usage.last_used:
                days_since = (datetime.now() - usage.last_used).days
                if days_since <= 7:
                    recent_7d += 1
                if days_since <= 30:
                    recent_30d += 1
                elif days_since > 60:
                    stale_features += 1
        
        days_since_start = (datetime.now() - customer.subscription_start).days
        
        if intent_type == 'FACT_STATUS':
            # Just the facts
            output = []
            output.append("Usage Trends:")
            output.append(f"  • Last 7 days: {recent_7d} features")
            output.append(f"  • Last 30 days: {recent_30d} features")
            output.append(f"  • Stale (60+ days): {stale_features} features")
            output.append(f"  • Customer age: {days_since_start} days")
            return "\n".join(output)
        
        else:  # DIAGNOSTIC
            # WHY structure
            output = []
            output.append("Usage Trend Analysis:")
            
            # Observed signals
            output.append("\nObserved Signals:")
            output.append(f"  • Features used in last 7 days: {recent_7d}")
            output.append(f"  • Features used in last 30 days: {recent_30d}")
            output.append(f"  • Stale features (60+ days): {stale_features}")
            output.append(f"  • Customer age: {days_since_start} days")
            
            # Interpretation
            if recent_30d < 2:
                output.append("\nInterpretation: Low recent activity suggests declining engagement.")
            elif recent_7d >= 3:
                output.append("\nInterpretation: Healthy recent usage indicates active product adoption.")
            else:
                output.append("\nInterpretation: Moderate activity levels, monitor for trends.")
            
            # Business implication
            if recent_30d < 2:
                output.append("\nBusiness Implication: Re-engagement needed to prevent churn risk.")
            elif stale_features > 3:
                output.append("\nBusiness Implication: Multiple unused features may indicate confusion or lack of value.")
            else:
                output.append("\nBusiness Implication: Current usage patterns support retention.")
            
            return "\n".join(output)
    
    elif intent == 'usage_data':
        # Usage data is always FACT/STATUS (just metrics)
        output = []
        output.append("Usage Data (Top Features by Activity):")
        output.append(f"{'Feature':<30} {'Actions':<10} {'Sessions':<10} {'Last Used':<15}")
        output.append("-" * 70)
        
        usage_items = sorted(
            customer.features.items(),
            key=lambda x: x[1].total_actions,
            reverse=True
        )
        
        for feat_id, usage in usage_items[:8]:
            feature = agent.data_access.get_feature(feat_id)
            name = feature.name if feature else feat_id[:28]
            last_used_str = "Never" if not usage.last_used else \
                           f"{(datetime.now() - usage.last_used).days}d ago"
            
            output.append(f"{name:<30} {usage.total_actions:<10} "
                         f"{usage.total_sessions:<10} {last_used_str:<15}")
        
        return "\n".join(output)
    
    elif intent == 'overview':
        # Overview is always FACT/STATUS (concise facts only)
        summary = generate_customer_summary(agent, customer)
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        assessment = agent.analysis.assess_churn_risk(customer)
        
        output = []
        output.append(f"Customer Overview: {customer.name}")
        output.append(f"  • Plan: {summary['plan']} | MRR: {summary['mrr']}")
        output.append(f"  • Age: {summary['age_days']} days")
        output.append(f"  • Core Adoption: {summary['core_adoption']}")
        output.append(f"  • Churn Risk: {assessment.risk_level.value.upper()}")
        output.append(f"  • Adopted Features: {len(adopted)}")
        output.append(f"  • Recent Usage: {summary['recent_usage']}")
        
        return "\n".join(output)
    
    else:
        return ("I don't have enough evidence in the current data to answer that confidently. "
               "Could you rephrase your question or ask about adoption, recommendations, "
               "churn risk, or usage patterns?")


def classify_response_intent(question: str) -> tuple:
    """
    Classify question into WHY/WHAT/ACTION response intent.
    
    Returns:
        (intent, reason) tuple where intent is 'WHY', 'WHAT', or 'ACTION'
        and reason is a one-line explanation
    """
    question_lower = question.lower()
    
    # WHY: Questions asking for explanation, cause, reason
    why_keywords = ['why', 'how come', 'reason', 'cause', 'because', 'explain',
                   'what\'s wrong', 'what\'s the problem', 'how engaged',
                   'why is', 'why are', 'why do', 'why does']
    why_synonyms = ['indicating', 'suggesting', 'meaning', 'implication']
    
    if any(kw in question_lower for kw in why_keywords):
        return ('WHY', "question asks 'why' or seeks explanation")
    
    # ACTION: Questions asking what to do, recommendations, next steps
    action_keywords = ['should', 'what to do', 'recommend', 'next step', 'action',
                      'pitch', 'focus on', 'prioritize', 'do this week', 'suggest',
                      'how to', 'what should', 'what can', 'steps', 'playbook']
    
    if any(kw in question_lower for kw in action_keywords):
        return ('ACTION', "question asks for recommendations or actions")
    
    # WHAT: Questions asking for facts, status, information
    what_keywords = ['what is', 'what are', 'what\'s', 'how many', 'how much',
                    'show me', 'tell me', 'list', 'status', 'current', 'is',
                    'are', 'has', 'have', 'using', 'used']
    
    if any(kw in question_lower for kw in what_keywords):
        return ('WHAT', "question asks for factual information")
    
    # Default: prefer WHY > ACTION > WHAT
    if any(syn in question_lower for syn in why_synonyms):
        return ('WHY', "question contains interpretive language")
    
    # If ambiguous, default to WHY
    return ('WHY', "ambiguous question, defaulting to explanatory response")


def compose_why_response(agent, customer: Customer, question: str, intent: str) -> tuple:
    """
    Compose WHY response: WHY (causal) → WHAT (factual) → ACTION (optional).
    Returns (output_lines, confidence_score).
    """
    from datetime import datetime
    
    output = []
    
    # Determine what the question is about
    question_lower = question.lower()
    
    if 'churn' in question_lower or 'risk' in question_lower:
        assessment = agent.analysis.assess_churn_risk(customer)
        
        # WHY: Causal explanation
        if assessment.risk_level.value == 'high':
            why_text = ("Multiple risk signals present, indicating elevated churn "
                       "probability because core features remain unadopted and usage "
                       "has declined.")
        elif assessment.risk_level.value == 'medium':
            why_text = ("Some risk indicators detected, suggesting potential retention "
                       "issues if adoption patterns don't improve.")
        else:
            why_text = ("No significant risk patterns detected, indicating healthy "
                       "customer engagement and product value realization.")
        
        output.extend(format_wrapped_text(why_text, prefix="WHY:", width=80))
        
        # WHAT: Factual summary
        what_text = f"Churn risk: {assessment.risk_level.value.upper()} (score: {assessment.risk_score:.1%})"
        if assessment.signals:
            what_text += f" | Signals: {len(assessment.signals)}"
        output.append(f"\nWHAT:\n  • {what_text}")
        
        # ACTION: Optional practical step
        if assessment.risk_level.value in ['high', 'medium']:
            output.append("\nACTION:")
            output.extend(format_wrapped_text(assessment.recommended_intervention, prefix="  •", width=80))
        
        # Evidence
        output.append("\nEVIDENCE:")
        for signal in assessment.signals[:3]:
            output.extend(format_wrapped_text(signal, prefix="  •", width=80))
        
        confidence = assessment.risk_score if assessment.risk_score > 0 else 0.7
    
    elif 'adopt' in question_lower or 'feature' in question_lower:
        recommendations = agent.analysis.analyze_feature_adoption(customer)
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        core_features = [f for f in feature_catalog.values() if f.category.value == "core"]
        adopted_core = len([f.id for f in core_features if f.id in adopted])
        
        # WHY: Causal explanation
        adoption_rate = adopted_core / len(core_features) if core_features else 0
        if adoption_rate < 0.5:
            why_text = ("Low core feature adoption suggests delayed time-to-value, "
                       "indicating the customer hasn't realized expected product benefits.")
        else:
            why_text = ("Healthy adoption patterns indicate successful onboarding, "
                       "suggesting the customer is deriving value from core features.")
        
        output.extend(format_wrapped_text(why_text, prefix="WHY:", width=80))
        
        # WHAT: Factual summary
        output.append(f"\nWHAT:\n  • Core features adopted: {adopted_core}/{len(core_features)}")
        output.append(f"  • Total adopted features: {len(adopted)}")
        
        # ACTION: Optional
        if recommendations:
            top_rec = recommendations[0]
            output.append("\nACTION:")
            output.extend(format_wrapped_text(top_rec.suggested_action, prefix="  •", width=80))
        
        # Evidence
        output.append("\nEVIDENCE:")
        output.append(f"  • core_adoption_rate = {adoption_rate:.1%}")
        output.append(f"  • total_adopted_features = {len(adopted)}")
        
        confidence = 0.75 if recommendations else 0.6
    
    else:
        # Generic WHY response
        assessment = agent.analysis.assess_churn_risk(customer)
        why_text = ("Customer engagement patterns suggest moderate product adoption, "
                   "indicating room for improvement in feature utilization.")
        output.extend(format_wrapped_text(why_text, prefix="WHY:", width=80))
        
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        output.append(f"\nWHAT:\n  • Adopted features: {len(adopted)}")
        output.append(f"  • Churn risk: {assessment.risk_level.value.upper()}")
        
        output.append("\nEVIDENCE:")
        output.append(f"  • adopted_features_count = {len(adopted)}")
        output.append(f"  • churn_risk_score = {assessment.risk_score:.1%}")
        
        confidence = 0.65
    
    return output, confidence


def compose_what_response(agent, customer: Customer, question: str, intent: str) -> tuple:
    """
    Compose WHAT response: WHAT (facts) → WHY (optional brief).
    Returns (output_lines, confidence_score).
    """
    from datetime import datetime
    
    output = []
    question_lower = question.lower()
    
    if 'churn' in question_lower or 'risk' in question_lower:
        assessment = agent.analysis.assess_churn_risk(customer)
        
        # WHAT: Facts
        output.append("WHAT:")
        output.append(f"  • Churn risk level: {assessment.risk_level.value.upper()}")
        output.append(f"  • Risk score: {assessment.risk_score:.1%}")
        if assessment.signals:
            output.append(f"  • Risk signals: {len(assessment.signals)}")
        
        # WHY: Optional brief interpretation
        if assessment.risk_level.value == 'high':
            output.append(f"\nWHY: Multiple risk indicators present")
        
        # Evidence
        output.append("\nEVIDENCE:")
        for signal in assessment.signals[:2]:
            output.extend(format_wrapped_text(signal, prefix="  •", width=80))
        
        confidence = 0.85
    
    elif 'adopt' in question_lower or 'feature' in question_lower or 'using' in question_lower:
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        active = customer.get_active_features()
        core_features = [f for f in feature_catalog.values() if f.category.value == "core"]
        adopted_core = len([f.id for f in core_features if f.id in adopted])
        
        # WHAT: Facts
        output.append("WHAT:")
        output.append(f"  • Total adopted features: {len(adopted)}")
        output.append(f"  • Active features: {len(active)}")
        output.append(f"  • Core features adopted: {adopted_core}/{len(core_features)}")
        
        # WHY: Optional brief
        if adopted_core < len(core_features) * 0.5:
            output.append(f"\nWHY: Low core adoption indicates adoption gap")
        
        # Evidence
        output.append("\nEVIDENCE:")
        output.append(f"  • adopted_features_count = {len(adopted)}")
        output.append(f"  • core_adoption_rate = {adopted_core}/{len(core_features)}")
        
        confidence = 0.8
    
    elif 'usage' in question_lower or 'trend' in question_lower:
        recent_30d = 0
        for usage in customer.features.values():
            if usage.last_used:
                days_since = (datetime.now() - usage.last_used).days
                if days_since <= 30:
                    recent_30d += 1
        
        # WHAT: Facts
        output.append("WHAT:")
        output.append(f"  • Features used in last 30 days: {recent_30d}")
        output.append(f"  • Total active features: {len(customer.get_active_features())}")
        
        # Evidence
        output.append("\nEVIDENCE:")
        output.append(f"  • recent_30d_usage_count = {recent_30d}")
        
        confidence = 0.75
    
    else:
        # Generic WHAT response
        summary = generate_customer_summary(agent, customer)
        assessment = agent.analysis.assess_churn_risk(customer)
        
        output.append("WHAT:")
        output.append(f"  • Plan: {summary['plan']} | MRR: {summary['mrr']}")
        output.append(f"  • Churn risk: {assessment.risk_level.value.upper()}")
        output.append(f"  • Core adoption: {summary['core_adoption']}")
        
        output.append("\nEVIDENCE:")
        output.append(f"  • mrr = ${customer.mrr:,.0f}")
        output.append(f"  • churn_risk_score = {assessment.risk_score:.1%}")
        
        confidence = 0.7
    
    return output, confidence


def compose_action_response(agent, customer: Customer, question: str, intent: str) -> tuple:
    """
    Compose ACTION response: ACTION (steps) → WHY (brief) → WHAT (evidence).
    Returns (output_lines, confidence_score).
    """
    from datetime import datetime
    
    output = []
    question_lower = question.lower()
    
    recommendations = agent.analysis.analyze_feature_adoption(customer)
    
    if not recommendations:
        output.append("ACTION:")
        output.append("  • No specific actions needed - customer shows healthy adoption")
        output.append("\nWHY: Customer adoption patterns are within expected range")
        output.append("\nWHAT:")
        feature_catalog = agent.data_access.get_all_features()
        adopted = customer.get_adopted_features(feature_catalog)
        output.append(f"  • Adopted features: {len(adopted)}")
        output.append("\nEVIDENCE:")
        output.append(f"  • adopted_features_count = {len(adopted)}")
        return output, 0.6
    
    top_rec = recommendations[0]
    
    # ACTION: Prioritized steps (who + what + timeframe)
    output.append("ACTION:")
    action_steps = top_rec.suggested_action.split('. ')
    for i, step in enumerate(action_steps[:3], 1):
        step_clean = step.strip()
        if step_clean:
            output.extend(format_wrapped_text(step_clean, prefix=f"  {i}.", width=80))
    
    # WHY: Brief causal sentence linking data → rationale
    why_text = f"Because {top_rec.reason}"
    output.append("\nWHY:")
    output.extend(format_wrapped_text(why_text, prefix="  ", width=80))
    
    # WHAT: Evidence bullets
    output.append("\nWHAT:")
    feature_catalog = agent.data_access.get_all_features()
    usage = customer.features.get(top_rec.feature_id)
    if usage:
        if usage.total_actions == 0:
            output.append(f"  • Feature never used (0 actions)")
        else:
            output.append(f"  • Feature underutilized ({usage.usage_frequency:.1%} frequency)")
    else:
        output.append(f"  • Feature not adopted")
    
    # Evidence
    output.append("\nEVIDENCE:")
    if usage:
        output.append(f"  • {top_rec.feature_id}_actions = {usage.total_actions}")
        output.append(f"  • {top_rec.feature_id}_frequency = {usage.usage_frequency:.1%}")
    else:
        output.append(f"  • {top_rec.feature_id}_adopted = false")
    
    confidence = top_rec.confidence
    
    return output, confidence


def handle_free_form_question(agent, customer_id: str):
    """
    Handle conversational Q&A loop with WHY/WHAT/ACTION intent classification.
    
    Each question is classified as WHY (explanatory), WHAT (factual), or ACTION (prescriptive),
    and responses are composed according to specific rules with evidence and confidence.
    """
    customer = agent.data_access.get_customer(customer_id)
    if not customer:
        print(f"\n[ERROR] Customer not found.\n")
        return
    
    print("\nFree-Form Question Mode")
    print("-" * 80)
    print("Ask questions about this customer. Type 'back' to return to menu.")
    print()
    
    question_count = 0
    
    while True:
        try:
            question = input("Question> ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['back', 'exit', 'quit']:
                break
            
            question_count += 1
            
            # Classify response intent (WHY/WHAT/ACTION)
            response_intent, reason = classify_response_intent(question)
            
            # Print meta-decision
            print(f"\nINTENT: {response_intent} — reason: {reason}")
            
            # Also get domain intent for routing to correct engines
            domain_intent = classify_question_intent(question)
            
            try:
                # Compose response based on response intent
                if response_intent == 'WHY':
                    output_lines, confidence = compose_why_response(agent, customer, question, domain_intent)
                elif response_intent == 'WHAT':
                    output_lines, confidence = compose_what_response(agent, customer, question, domain_intent)
                else:  # ACTION
                    output_lines, confidence = compose_action_response(agent, customer, question, domain_intent)
                
                # Add confidence section
                confidence_pct = int(confidence * 100)
                if confidence_pct >= 70:
                    conf_label = "High"
                elif confidence_pct >= 40:
                    conf_label = "Med"
                else:
                    conf_label = "Low"
                
                output_lines.append(f"\nCONFIDENCE: {conf_label} ({confidence_pct}%)")
                
                # Print response (limit to ~20 lines)
                response_text = "\n".join(output_lines)
                response_lines = response_text.split('\n')
                if len(response_lines) > 20:
                    response_lines = response_lines[:20]
                    response_lines.append("  ... (truncated)")
                
                print("\n" + "\n".join(response_lines) + "\n")
                
                # Log interaction
                log_interaction(customer_id, "free_form_question", question, 
                              f"intent_{response_intent}_confidence_{confidence_pct}")
            
            except KeyError as e:
                # Refusal rule: missing data
                print("\nI don't have enough evidence in the current data to answer that confidently.")
                print(f"Missing data: {str(e)}")
                print("\nFALLBACK:")
                print("  • Try asking about adoption, churn risk, or usage patterns")
                print("  • Use menu options 1-5 for structured analysis")
                
                log_interaction(customer_id, "free_form_question", question, 
                              f"refused_{question_count}")
            
            except Exception as e:
                # Generic error handling
                print(f"\n[ERROR] Unable to process question: {e}")
                print("        Please try rephrasing or ask about adoption, "
                     "recommendations, churn risk, or usage.\n")
                
                log_interaction(customer_id, "free_form_question", question, 
                              f"error_{question_count}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[ERROR] {e}\n")


def handle_customer_menu(agent, customer_id: str):
    """
    Handle menu-driven interaction for a specific customer.
    Allows selective reasoning on individual items.
    """
    customer = agent.data_access.get_customer(customer_id)
    if not customer:
        print(f"\n[ERROR] Customer '{customer_id}' not found.\n")
        return
    
    # Show summary
    print_customer_summary(agent, customer)
    log_interaction(customer_id, "view_summary", "", "summary_displayed")
    
    # Menu loop
    while True:
        print_menu()
        
        try:
            choice = input("Select option (1-8): ").strip()
            
            if not choice:
                continue
            
            if choice == "1":
                # Adoption Snapshot
                output = format_adoption_snapshot(agent, customer)
                print(output)
                log_interaction(customer_id, "adoption_snapshot", "", "snapshot_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "2":
                # Churn Risk Summary
                output = format_churn_risk_summary(agent, customer)
                print(output)
                log_interaction(customer_id, "churn_risk", "", "risk_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "3":
                # Top Recommendations
                output = format_top_recommendations(agent, customer)
                print(output)
                log_interaction(customer_id, "recommendations", "", "recommendations_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "4":
                # Onboarding Playbook
                output = format_onboarding_playbook(agent, customer)
                print(output)
                log_interaction(customer_id, "onboarding", "", "playbook_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "5":
                # Raw Usage Data
                output = format_raw_usage_data(agent, customer)
                print(output)
                log_interaction(customer_id, "raw_usage", "", "usage_data_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "6":
                # Free-form question
                handle_free_form_question(agent, customer_id)
                log_interaction(customer_id, "question_mode", "", "question_session")
            
            elif choice == "7":
                # Expand All
                print("\n" + "=" * 80)
                print("Expanding All Intelligence")
                print("=" * 80)
                
                print(format_adoption_snapshot(agent, customer))
                print(format_churn_risk_summary(agent, customer))
                print(format_top_recommendations(agent, customer))
                print(format_onboarding_playbook(agent, customer))
                
                log_interaction(customer_id, "expand_all", "", "all_intelligence_displayed")
                input("\nPress Enter to continue...")
            
            elif choice == "8":
                # Back
                break
            
            else:
                print("\n[ERROR] Invalid option. Please select 1-8.\n")
        
        except KeyboardInterrupt:
            print("\n\nReturning to main menu...\n")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}\n")
            import traceback
            traceback.print_exc()


def find_closest_customer_id(agent, partial_id: str) -> List[str]:
    """Find closest matching customer IDs for error messages."""
    all_ids = agent.data_access.list_customers()
    partial_lower = partial_id.lower()
    
    matches = [cid for cid in all_ids if partial_lower in cid.lower()]
    return matches[:3]  # Return top 3 matches


def run_interactive_session():
    """Main interactive session loop."""
    agent = AdoptionCopilotAgent()
    
    print_welcome()
    list_customers(agent)
    
    while True:
        try:
            command = input("> ").strip()
            
            if not command:
                continue
            
            command_lower = command.lower()
            
            # Exit commands
            if command_lower in ['quit', 'exit', 'q']:
                print("\nExiting. Goodbye.\n")
                break
            
            # Help command
            if command_lower == 'help':
                print("\nCommands:")
                print("  <customer_id>  - Analyze a customer by ID")
                print("  list [N]       - Show customers (optionally top N by MRR)")
                print("  help           - Show this help")
                print("  quit / exit    - Exit\n")
                continue
            
            # List command with optional limit
            if command_lower.startswith('list'):
                parts = command.split()
                limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                list_customers(agent, limit)
                continue
            
            # Customer analysis - enter menu mode
            customer = agent.data_access.get_customer(command)
            if customer:
                handle_customer_menu(agent, command)
            else:
                # Try to find closest matches
                matches = find_closest_customer_id(agent, command)
                print(f"\n[ERROR] Customer '{command}' not found.")
                if matches:
                    print(f"        Did you mean: {', '.join(matches)}?")
                print("        Use 'list' to see all customers.\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting. Goodbye.\n")
            break
        except EOFError:
            print("\n\nExiting. Goodbye.\n")
            break


if __name__ == "__main__":
    run_interactive_session()
