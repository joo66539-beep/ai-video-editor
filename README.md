# AI Video Editor

Prototype repository for AI-powered video editing (Next.js frontend + FastAPI backend).

This repo contains a starting scaffold. Next steps:
- Implement scene detection (ffmpeg / PySceneDetect)
- Wire OpenAI Whisper API for subtitles (set OPENAI_API_KEY)
- Implement export pipeline (ffmpeg) and background worker
- Deploy frontend (Vercel) and backend (Render/VPS)

See quickstart below.

Quickstart (local)

1. Backend

- Create virtualenv, install requirements:

  python -m venv .venv
  source .venv/bin/activate
  pip install -r backend/requirements.txt

- Create .env from .env.example and set OPENAI_API_KEY and API_BASE_URL

- Run backend:

  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

2. Frontend

- Install and run:

  cd frontend
  npm install
  npm run dev

- Set NEXT_PUBLIC_API_URL to http://localhost:8000 in .env.local

Notes
- This is an MVP scaffold. To fully enable scene-detection and Whisper you must provide an OpenAI key and install ffmpeg on the host. See backend/README for details.
