"""
Web-based demo for Product Adoption & Expansion Intelligence Copilot.

A clean, interactive interface for showcasing customer intelligence analysis.
Built with Streamlit for easy deployment and sharing.

Run locally: streamlit run streamlit_app.py
Deploy: Push to GitHub and deploy via Streamlit Cloud (free)
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # type: ignore
from datetime import datetime

from src.agent.core import AdoptionCopilotAgent
from src.data.models import CustomerIntelligence

# Import free-form question handlers from CLI (reuse existing logic)
from run_demo import (
    classify_response_intent,
    compose_why_response,
    compose_what_response,
    compose_action_response,
    classify_question_intent
)


# Page configuration
st.set_page_config(
    page_title="Product Adoption System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = AdoptionCopilotAgent()

if 'selected_customer_id' not in st.session_state:
    st.session_state.selected_customer_id = None

if 'intelligence' not in st.session_state:
    st.session_state.intelligence = None


def get_customer_list(agent):
    """Get list of customers for selection."""
    return agent.data_access.list_customers()


def format_risk_badge(risk_level: str) -> str:
    """Return emoji badge for risk level."""
    badges = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }
    return badges.get(risk_level.lower(), '⚪')


def format_confidence_badge(confidence: float) -> str:
    """Return emoji badge for confidence."""
    if confidence >= 0.7:
        return '🟢'
    elif confidence >= 0.4:
        return '🟡'
    else:
        return '🟠'


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("📊 Product Adoption & Expansion Intelligence System")
    st.markdown("**Internal Enterprise Tool** — Analyze customer adoption, expansion opportunities, and churn risk")
    st.divider()
    
    # Sidebar: Customer Selection
    with st.sidebar:
        st.header("Customer Selection")
        
        agent = st.session_state.agent
        customers = get_customer_list(agent)
        
        # Customer dropdown
        customer_options = {}
        for cust_id in sorted(customers):
            customer = agent.data_access.get_customer(cust_id)
            if customer:
                display_name = f"{customer.name} ({cust_id})"
                customer_options[display_name] = cust_id
        
        selected_display = st.selectbox(
            "Select Customer",
            options=list(customer_options.keys()),
            index=0 if not st.session_state.selected_customer_id else 
                  list(customer_options.values()).index(st.session_state.selected_customer_id) 
                  if st.session_state.selected_customer_id in customer_options.values() else 0
        )
        
        selected_customer_id = customer_options[selected_display]
        st.session_state.selected_customer_id = selected_customer_id
        
        # Customer info card
        if selected_customer_id:
            customer = agent.data_access.get_customer(selected_customer_id)
            if customer:
                st.markdown("### Customer Info")
                st.markdown(f"**Name:** {customer.name}")
                st.markdown(f"**Plan:** {customer.plan_tier.title()}")
                st.markdown(f"**MRR:** ${customer.mrr:,.0f}/month")
                st.markdown(f"**Industry:** {customer.industry}")
                st.markdown(f"**Account Manager:** {customer.account_manager}")
                
                days_since_start = (datetime.now() - customer.subscription_start).days
                st.markdown(f"**Customer Age:** {days_since_start} days")
        
        st.divider()
        
        # Analyze button
        if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing customer..."):
                try:
                    intelligence = agent.analyze_customer(selected_customer_id)
                    st.session_state.intelligence = intelligence
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool helps CSMs and Account Managers:
        - Identify feature adoption opportunities
        - Assess churn risk with explainable signals
        - Generate personalized onboarding playbooks
        - Make data-driven expansion recommendations
        """)


    # Main content area
    if st.session_state.intelligence is None:
        st.info("👈 Select a customer and click 'Run Analysis' to begin")
        
        # Show available customers
        st.markdown("### Available Customers")
        agent = st.session_state.agent
        customers = get_customer_list(agent)
        
        cols = st.columns(3)
        for idx, cust_id in enumerate(sorted(customers)):
            customer = agent.data_access.get_customer(cust_id)
            if customer:
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"**{customer.name}**")
                        st.caption(f"{cust_id} | {customer.plan_tier} | ${customer.mrr:,.0f}/mo")
    
    else:
        intelligence = st.session_state.intelligence
        
        # Customer Summary Header
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### {intelligence.customer_name}")
            st.caption(f"Analysis generated: {intelligence.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            risk_badge = format_risk_badge(intelligence.churn_risk.risk_level.value)
            st.metric(
                "Churn Risk",
                f"{risk_badge} {intelligence.churn_risk.risk_level.value.upper()}",
                f"{intelligence.churn_risk.risk_score:.1%}"
            )
        
        with col3:
            st.metric(
                "Recommendations",
                len(intelligence.adoption_recommendations),
                "Top priorities"
            )
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary",
            "🎯 Recommendations",
            "⚠️ Churn Risk",
            "📚 Onboarding",
            "💬 Ask Questions"
        ])
        
        # Tab 1: Summary
        with tab1:
            st.markdown("### Customer Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Adoption Status")
                feature_catalog = agent.data_access.get_all_features()
                adopted = agent.data_access.get_customer(intelligence.customer_id).get_adopted_features(feature_catalog)
                active = agent.data_access.get_customer(intelligence.customer_id).get_active_features()
                
                core_features = [f for f in feature_catalog.values() if f.category.value == "core"]
                adopted_core = len([f.id for f in core_features if f.id in adopted])
                
                st.metric("Adopted Features", len(adopted))
                st.metric("Active Features", len(active))
                st.metric("Core Adoption", f"{adopted_core}/{len(core_features)}")
            
            with col2:
                st.markdown("#### Risk Signals")
                for signal in intelligence.churn_risk.signals[:5]:
                    st.markdown(f"• {signal}")
            
            st.markdown("---")
            st.markdown("#### Top Recommendation Preview")
            if intelligence.adoption_recommendations:
                top_rec = intelligence.adoption_recommendations[0]
                confidence_badge = format_confidence_badge(top_rec.confidence)
                st.markdown(f"**{top_rec.feature_name}** {confidence_badge} ({int(top_rec.confidence * 100)}% confidence)")
                st.markdown(f"*{top_rec.reason[:150]}...*")
        
        # Tab 2: Recommendations
        with tab2:
            st.markdown("### Adoption Recommendations")
            
            if not intelligence.adoption_recommendations:
                st.info("No specific recommendations at this time. Customer shows healthy adoption patterns.")
            else:
                for idx, rec in enumerate(intelligence.adoption_recommendations, 1):
                    with st.expander(f"#{idx} {rec.feature_name} (Priority {rec.priority})", expanded=(idx == 1)):
                        confidence_badge = format_confidence_badge(rec.confidence)
                        st.markdown(f"**Confidence:** {confidence_badge} {int(rec.confidence * 100)}%")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**WHY:**")
                            st.markdown(rec.reason)
                            
                            st.markdown("**WHAT:**")
                            usage = agent.data_access.get_customer(intelligence.customer_id).features.get(rec.feature_id)
                            if usage and usage.total_actions == 0:
                                st.markdown("• Feature not adopted")
                            elif usage:
                                st.markdown(f"• Feature underutilized ({usage.usage_frequency:.1%} frequency)")
                            else:
                                st.markdown("• Feature adoption gap")
                        
                        with col2:
                            st.markdown("**ACTION:**")
                            st.markdown(rec.suggested_action)
                            
                            st.markdown("**Expected Impact:**")
                            st.markdown(rec.expected_impact)
        
        # Tab 3: Churn Risk
        with tab3:
            st.markdown("### Churn Risk Assessment")
            
            risk = intelligence.churn_risk
            risk_badge = format_risk_badge(risk.risk_level.value)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Level", f"{risk_badge} {risk.risk_level.value.upper()}")
            with col2:
                st.metric("Risk Score", f"{risk.risk_score:.1%}")
            with col3:
                st.metric("Urgency", f"{risk.urgency_days} days")
            
            st.divider()
            
            st.markdown("#### Observed Signals")
            for signal in risk.signals:
                st.markdown(f"• {signal}")
            
            st.divider()
            
            st.markdown("#### Interpretation")
            if risk.risk_level.value == 'high':
                st.warning("Multiple risk indicators suggest elevated churn probability.")
            elif risk.risk_level.value == 'medium':
                st.info("Some risk signals present, but not yet critical.")
            else:
                st.success("No significant risk patterns detected.")
            
            st.divider()
            
            st.markdown("#### Recommended Intervention")
            st.markdown(risk.recommended_intervention)
        
        # Tab 4: Onboarding
        with tab4:
            st.markdown("### Onboarding Playbook")
            
            if not intelligence.onboarding_playbook:
                st.info("No specific onboarding steps available.")
            else:
                if intelligence.adoption_recommendations:
                    top_rec = intelligence.adoption_recommendations[0]
                    st.markdown("#### WHY")
                    st.markdown(top_rec.reason[:200])
                
                st.divider()
                
                feature_catalog = agent.data_access.get_all_features()
                adopted = agent.data_access.get_customer(intelligence.customer_id).get_adopted_features(feature_catalog)
                st.markdown(f"#### WHAT")
                st.markdown(f"• {len(adopted)} features currently adopted")
                
                st.divider()
                
                st.markdown("#### ACTION")
                for step in intelligence.onboarding_playbook:
                    with st.container():
                        st.markdown(f"**Step {step.step_number}: {step.title}**")
                        st.markdown(step.description)
                        if step.feature_id:
                            st.caption(f"Feature: {step.feature_id}")
                        st.caption(f"⏱️ Estimated time: {step.estimated_time_minutes} minutes")
                        if step != intelligence.onboarding_playbook[-1]:
                            st.divider()
        
        # Tab 5: Free-form Questions
        with tab5:
            st.markdown("### Free-form Analysis")
            st.markdown("Ask questions about this customer. Questions are analyzed using the same reasoning engine as the structured analysis above.")
            
            # Initialize question history in session state
            if 'question_history' not in st.session_state:
                st.session_state.question_history = []
            
            # Question input
            question = st.text_input(
                "Enter your question:",
                placeholder="e.g., Why is adoption low? What features should they use?",
                key="question_input"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                submit_question = st.button("Submit", type="primary")
            
            # Process question if submitted
            if submit_question and question.strip():
                customer = agent.data_access.get_customer(intelligence.customer_id)
                
                if customer:
                    with st.spinner("Analyzing question..."):
                        try:
                            # Classify response intent (WHY/WHAT/ACTION)
                            response_intent, reason = classify_response_intent(question)
                            
                            # Get domain intent for routing
                            domain_intent = classify_question_intent(question)
                            
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
                            
                            # Store in history
                            st.session_state.question_history.append({
                                'question': question,
                                'intent': response_intent,
                                'reason': reason,
                                'response': output_lines,
                                'confidence': confidence_pct
                            })
                            
                        except KeyError as e:
                            # Refusal rule: missing data
                            error_response = [
                                "I don't have enough evidence in the current data to answer that confidently.",
                                f"Missing data: {str(e)}",
                                "",
                                "FALLBACK:",
                                "  • Try asking about adoption, churn risk, or usage patterns",
                                "  • Use other tabs for structured analysis"
                            ]
                            st.session_state.question_history.append({
                                'question': question,
                                'intent': 'ERROR',
                                'reason': 'Missing data',
                                'response': error_response,
                                'confidence': 0
                            })
                        except Exception as e:
                            error_response = [
                                f"[ERROR] Unable to process question: {e}",
                                "Please try rephrasing or ask about adoption, recommendations, churn risk, or usage."
                            ]
                            st.session_state.question_history.append({
                                'question': question,
                                'intent': 'ERROR',
                                'reason': 'Processing error',
                                'response': error_response,
                                'confidence': 0
                            })
            
            # Display question history
            if st.session_state.question_history:
                st.divider()
                st.markdown("#### Question History")
                
                # Show most recent first
                for idx, qa in enumerate(reversed(st.session_state.question_history), 1):
                    with st.expander(f"Q{len(st.session_state.question_history) - idx + 1}: {qa['question']}", expanded=(idx == 1)):
                        # Meta-decision
                        st.caption(f"INTENT: {qa['intent']} — reason: {qa['reason']}")
                        
                        # Response
                        st.markdown("**Response:**")
                        for line in qa['response']:
                            if line.strip():
                                st.markdown(line)
                    
                    if idx < len(st.session_state.question_history):
                        st.divider()
                
                # Clear history button
                if st.button("Clear History", key="clear_history"):
                    st.session_state.question_history = []
                    st.rerun()
        
        # Footer
        st.divider()
        st.markdown("---")
        st.caption("Product Adoption & Expansion Intelligence Copilot — Internal Enterprise Tool")


if __name__ == "__main__":
    main()

