# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10 or later
- pip

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the app:**
   - The app will open automatically in your browser
   - Default URL: http://localhost:8501

## Free Hosting on Streamlit Cloud

Streamlit Cloud offers free hosting for public GitHub repositories.

### Steps to Deploy

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Your app will be live at:**
   ```
   https://<your-app-name>.streamlit.app
   ```

### Alternative: Streamlit Community Cloud

If you prefer a different subdomain:
- Use Streamlit Community Cloud
- Same deployment process
- Free tier available

## Architecture

### File Structure
```
product-adoption-copilot/
├── streamlit_app.py          # Web interface (Streamlit)
├── run_demo.py               # CLI interface
├── src/                      # Core business logic
│   ├── agent/               # Agent orchestration
│   ├── tools/               # Analysis tools
│   ├── memory/              # Context storage
│   └── data/                # Models and mock data
└── requirements.txt         # Dependencies
```

### Design Principles

- **Separation of Concerns:** UI (streamlit_app.py) is separate from business logic (src/)
- **Reuse:** All agent logic is reused without duplication
- **Stateless:** Each analysis is independent (no session state for business logic)
- **Professional:** Clean, CSM-oriented interface suitable for enterprise demos

## Features

### Customer Selection
- Dropdown menu with all available customers
- Customer info card in sidebar
- Quick customer overview

### Analysis Results
- **Summary Tab:** Overview of adoption and risk
- **Recommendations Tab:** Detailed adoption recommendations with WHY/WHAT/ACTION
- **Churn Risk Tab:** Risk assessment with signals and interventions
- **Onboarding Tab:** Step-by-step playbook

### Data Display
- Metrics and badges for quick scanning
- Expandable sections for detailed views
- Tables and structured layouts
- Color-coded risk indicators

## Customization

### Styling
Streamlit uses a clean default theme. To customize:
- Create `.streamlit/config.toml` for theme settings
- Modify colors, fonts, and layout in `streamlit_app.py`

### Adding Features
- All business logic is in `src/` - modify there
- UI components are in `streamlit_app.py` - add new tabs/sections as needed
- No changes needed to core agent logic

## Troubleshooting

### Common Issues

1. **Import errors:**
   - Ensure you're in the project root directory
   - Check that `src/` directory structure is intact

2. **Port already in use:**
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

3. **Streamlit Cloud deployment fails:**
   - Ensure `requirements.txt` includes `streamlit>=1.28.0`
   - Check that all imports are available
   - Verify Python version compatibility (3.10+)

## Security Notes

- This is a demo/prototype tool
- Uses mock data (no real customer information)
- Suitable for portfolio/interview demonstrations
- For production use, add authentication and data security measures

