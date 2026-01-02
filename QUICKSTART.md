# Quick Start Guide

## Web Demo (Best for Interviews/Portfolio)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run streamlit_app.py
```

### 3. Use the Interface
1. Select a customer from the sidebar dropdown
2. Click "🔍 Run Analysis"
3. Explore results in the tabs:
   - **Summary**: Overview metrics
   - **Recommendations**: Feature adoption opportunities
   - **Churn Risk**: Risk assessment and signals
   - **Onboarding**: Step-by-step playbook

### 4. Deploy (Optional)
- Push to GitHub
- Deploy on [Streamlit Cloud](https://share.streamlit.io) (free)
- Share your live URL

## CLI Interface (Alternative)

```bash
python run_demo.py
```

Interactive command-line interface with menu-driven analysis.

## What You'll See

### Customer Analysis Includes:
- **Adoption Recommendations**: Prioritized features with WHY/WHAT/ACTION
- **Churn Risk Assessment**: Risk level, signals, and interventions
- **Onboarding Playbook**: Personalized enablement steps
- **Evidence & Confidence**: All recommendations backed by data

### Key Features:
- ✅ Professional, CSM-oriented interface
- ✅ Evidence-backed recommendations
- ✅ Explainable reasoning (WHY/WHAT/ACTION)
- ✅ Clean, interview-safe presentation
- ✅ Free hosting available

## Architecture

- **Business Logic**: `src/` (agent, tools, memory, data)
- **Web Interface**: `streamlit_app.py` (reuses all business logic)
- **CLI Interface**: `run_demo.py` (alternative interface)

No code duplication - all interfaces share the same agent logic!

