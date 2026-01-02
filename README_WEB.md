# Web Demo - Product Adoption & Expansion Intelligence Copilot

## Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Launch web app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### Interactive Customer Analysis
- **Select Customer:** Choose from available customers via dropdown
- **Run Analysis:** One-click analysis generation
- **View Results:** Organized in tabs for easy navigation

### Results Display

1. **Summary Tab**
   - Adoption status metrics
   - Risk signals overview
   - Top recommendation preview

2. **Recommendations Tab**
   - Prioritized feature adoption recommendations
   - WHY/WHAT/ACTION structure for each recommendation
   - Confidence scores and expected impact

3. **Churn Risk Tab**
   - Risk level and score
   - Observed signals with explanations
   - Recommended interventions with urgency

4. **Onboarding Tab**
   - Step-by-step playbook
   - WHY/WHAT/ACTION structure
   - Time estimates for each step

## Deployment

### Free Hosting Options

**Streamlit Cloud (Recommended):**
1. Push code to GitHub
2. Sign in at [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click
4. Share your live URL

See `DEPLOYMENT.md` for detailed instructions.

## Architecture

- **Frontend:** Streamlit (Python-based web framework)
- **Backend:** Reuses all existing agent logic from `src/`
- **Data:** Mock customer data (same as CLI version)
- **No Duplication:** Business logic is shared between CLI and web interfaces

## Design

- **Professional:** Clean, enterprise-appropriate interface
- **CSM-Oriented:** Designed for Customer Success Managers
- **Minimal:** Focus on clarity and usability
- **Interview-Safe:** Suitable for portfolio demonstrations

## Usage Tips

1. **Select a customer** from the sidebar dropdown
2. **Click "Run Analysis"** to generate intelligence
3. **Navigate tabs** to explore different aspects:
   - Start with Summary for overview
   - Check Recommendations for actionable insights
   - Review Churn Risk for retention planning
   - Use Onboarding for enablement steps

## Technical Details

- Built with Streamlit 1.28+
- Python 3.10+ required
- No database or external services needed
- All analysis runs client-side using existing agent logic

