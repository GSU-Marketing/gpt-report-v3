# GPT-Powered Graduate Marketing Dashboard

An interactive Streamlit dashboard for analyzing marketing funnel performance using GPT-powered summarization.

## 🚀 Features
- Filtered views of application data by program, term, and status
- UTM & geographic insights
- Admin access with Google Sheets log syncing
- GPT-based data summaries per page

## 🛠 Deployment (Render.com)
1. Create a new Web Service
2. Link this repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port 10000`
5. Add env var: `OPENAI_API_KEY`

## 📁 Structure
- `app.py`: main dashboard entry
- `dashboard_pages/`: modular views (funnel, programs, etc.)
- `chat_helpers.py`: GPT integration
- `data_loaders.py`: GDrive / GSheets loaders
- `geo_utils.py`: geolocation helpers
