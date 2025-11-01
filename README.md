# NeuroBot — NeuroTech UIUC (September 2025)

NeuroBot is a small demo scaffold implementing a basic EEG-based student mental-wellness platform. It demonstrates:

- Django + Channels for a client-server UI with live neurofeedback (WebSockets).
- A REST endpoint to upload EEG data, compute simple features (NumPy/pandas), store raw data in AWS S3 (boto3),
  and call the OpenAI API for a short mood inference.
- PostgreSQL-ready settings (uses DATABASE_URL) but falls back to SQLite for quick local dev.

Summary bullets (as requested):

- Built EEG-based student mental-wellness platform that infers real-time emotion & triggers a therapy chatbot with custom exercises; made client–server UI with live neurofeedback (WebSockets/SSE) leveraging OpenAI API.
- Surpassed prior 83% accuracy fusing EEG biomarkers with psychological frameworks (Goleman EI) for mood inference using MATLAB/NumPy/pandas; stored EEG analysis in AWS S3 with CI & OAuth testing.

Quick start (local development):

1. Copy `.env.example` to `.env` and fill values for keys (OpenAI, AWS, DATABASE_URL if desired).
2. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run migrations and start the dev server (ASGI):

```bash
python manage.py migrate
python manage.py runserver
```

4. Open http://localhost:8000/ to see the live demo page.

Notes:

- This is a minimal scaffold to demonstrate integration points (EEG processing, OpenAI, S3, live websocket feedback). It intentionally keeps EEG processing simple (mean/std) and uses OpenAI calls as a lightweight inference helper — replace with your own model or MATLAB pipeline for production.
- The Channels layer uses an in-memory channel layer for convenience. For production, configure Redis.
# NeuroBot