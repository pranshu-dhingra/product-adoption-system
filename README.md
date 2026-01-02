# Product Adoption & Expansion Intelligence Copilot

## One-sentence purpose
Help Customer Success, Account Managers, and Product Teams increase feature adoption, expansion revenue, and retention by giving clear, explainable, AI-driven recommendations.

---

## What this repo is
This repository contains a vision-driven prototype and developer skeleton for the **Product Adoption & Expansion Intelligence Copilot** — a single assistant that turns product usage data into adoption guidance, expansion opportunities, and churn-intervention playbooks.

This project is intentionally product-first (business outcomes > algorithmic complexity) and designed to be integrated with agent frameworks such as Amazon Bedrock AgentCore (tutorials, gateway/tools, memory, and blueprints are directly useful). :contentReference[oaicite:1]{index=1}

---

## Core users (explicit)
- Customer Success Managers (primary)
- Account Managers (primary)
- Product Specialists (primary)
- Sales Engineers, RevOps (secondary)

This is **decision-support** for internal teams.

---

## Three layered capabilities (single assistant)
1. **Adoption & Expansion Copilot (foundation)**  
   Detect under-used but relevant features, recommend next-best actions, and surface expansion signals with crisp explanations.

2. **Intelligent Onboarding (built on adoption signals)**  
   Convert early-stage usage patterns into personalized onboarding and enablement steps.

3. **Churn Risk & Intervention Insights (derived layer)**  
   Turn negative-adoption patterns into risk labels and recommended interventions with rationales.

---

## Design principles
- One intelligence layer 
- Explainability first (human-readable reasons for every recommendation)  
- Data-driven, business-weighted signals (usage + plan/context)  
- Agentic architecture (tool calls, memory, and traceable reasoning)  
- Prototype with mock data, but design for real integration

---

## What success looks like (MVP)
Given a `customer_id`, the assistant returns:
- Top 3 adoption recommendations (feature, why, suggested next action)  
- One short enablement playbook for priority feature (1–3 steps)  
- Churn risk label (Low/Medium/High) with explainable signals

Outputs must be concise, structured, and ready for CSM consumption.

---

## How to use this repo (developer guidance)
1. Start with a small mock dataset of product usage + customer context.  
2. Build deterministic, explainable rules first (adoption heuristics, onboarding templates, churn signals).  
3. Expose data lookups and actions as modular tools (so an agent runtime can call them).  
4. Iterate: improve ranking, add simple ML models if and when they show measurable improvement.  
5. When ready to scale, reuse components and wiring patterns from Amazon Bedrock AgentCore (tutorials & blueprints) to add runtime, gateway tools, memory, and observability. :contentReference[oaicite:2]{index=2}

---

## Quick Start

### Web Interface (Recommended for Demos)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch web app
streamlit run streamlit_app.py
```

The app will open in your browser. Perfect for interviews and portfolio showcasing!

See [README_WEB.md](README_WEB.md) for web interface details and [DEPLOYMENT.md](DEPLOYMENT.md) for free hosting instructions.

### CLI Interface

```bash
# Run the interactive CLI
python run_demo.py

# Or analyze a specific customer
python -m src.main cust_001
```

### Available Customers (Mock Data)

- `cust_001`: Acme Corporation (healthy customer)
- `cust_002`: TechStart Inc (normal customer)
- `cust_003`: Legacy Systems Co (at-risk customer)
- `cust_004`: Innovation Labs (champion customer)
- `cust_005`: Fresh Startup (new customer)

## Architecture

The system is built with an agentic architecture inspired by Amazon Bedrock AgentCore principles:

- **Agent Core** (`src/agent/core.py`): Orchestrates reasoning and tool invocation
- **Tools** (`src/tools/`): Data access and analysis capabilities
- **Memory** (`src/memory/context.py`): Context and historical pattern storage
- **Data Models** (`src/data/models.py`): Structured business entities
- **Mock Data** (`src/data/mock_data.py`): Realistic test data generator

## Quick notes for Cursor use
- Give Cursor this README as context, then ask it to propose a minimal file layout, a short mock CSV schema, and a single CLI/demo flow.  
- Prefer short iterations: get one customer example working end-to-end, then generalize.

---

## Why this idea matters to enterprise product teams
- Directly maps to expansion revenue and retention metrics leadership cares about.  
- Low execution risk at PoC stage (mock data + explainable rules).  
- Easy to demonstrate impact to product and GTM leadership with a few customer-level stories.
