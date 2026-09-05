# Backend README

This backend implements video upload, scene detection (PySceneDetect), transcription via OpenAI Whisper API, and export endpoints.

Requirements
- ffmpeg installed on the host (must be in PATH)
- Python packages from requirements.txt
- Set OPENAI_API_KEY in environment to enable transcription

Run locally
- python -m venv .venv
- source .venv/bin/activate
- pip install -r backend/requirements.txt
- export OPENAI_API_KEY=sk-...
- uvicorn backend.app.main:app --reload --port 8000

Notes
- Scene detection parameters are conservative; adjust ContentDetector threshold if needed.
- Transcription uses OpenAI's /v1/audio/transcriptions endpoint.
