# Interactive CLI Usage

## Quick Start

Run the interactive command-line interface:

```bash
python run_demo.py
```

## Workflow

1. **Select a Customer**: Enter a customer ID (e.g., `cust_001`)
2. **View Summary**: See a concise one-line summary with key metrics
3. **Choose Analysis**: Select from numbered menu options to drill into specific areas
4. **Explore**: Use menu options to view adoption snapshots, churn risk, recommendations, etc.
5. **Ask Questions**: Option 6 allows free-form questions with conversational context

## Menu Options

After selecting a customer, you'll see:

1. **View Adoption Snapshot** - Detailed analysis of top adoption opportunity
2. **View Churn Risk Summary** - Risk assessment with explainable signals
3. **View Top Recommendations** - Prioritized feature adoption recommendations
4. **View Onboarding Playbook** - Step-by-step enablement guide
5. **Show Raw Usage Data** - Tabular view of feature usage metrics
6. **Ask Free-Form Question** - Conversational Q&A mode
7. **Expand All** - Show all intelligence at once
8. **Back / Exit** - Return to customer selection

## Commands

- `<customer_id>` - Analyze a specific customer
- `list [N]` - Show all customers (optionally top N by MRR)
- `help` - Display help message
- `quit` / `exit` - Exit the application

## Logging

All interactions are logged to `logs/interaction_log.csv` with:
- Timestamp
- Customer ID
- Action type
- Query summary
- Result key

This enables later evaluation and analysis of usage patterns.

## Example Session

```
> cust_005

Customer Summary: Fresh Startup | Plan: basic | MRR: $500 | Age: 30 days
Core Adoption: Low (1/2) | Risk: LOW | Recent Usage: 2 features (last 30d)

Menu:
  1) View Adoption Snapshot
  2) View Churn Risk Summary
  ...

Select option (1-8): 1

Adoption Snapshot — Core Dashboard
Key Claim: Core feature 'Core Dashboard' has never been used.
Evidence:
  • 0 total actions recorded
  • Customer subscribed for 30 days
  ...
```

