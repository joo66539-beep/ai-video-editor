DEPLOYMENT STEPS

1) Vercel (Frontend)
- Go to https://vercel.com/new and import the repository joo66539-beep/ai-video-editor.
- For Project Settings > Root Directory, set: frontend
- Add Environment Variable (in Vercel): NEXT_PUBLIC_API_URL -> https://<your-backend-url>
- Deploy the project. Vercel will build the Next.js frontend from the frontend/ folder.

2) Render (Backend)
- Go to https://dashboard.render.com and create a new Web Service.
- Connect your GitHub account and select the repo joo66539-beep/ai-video-editor.
- Choose Branch: main. Runtime: Docker.
- Build Command: leave empty (we use Dockerfile). Start Command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
- In Environment Variables (Settings) add:
    OPENAI_API_KEY -> <your_openai_key>
    MAX_UPLOAD_MB -> 200
- Deploy. Render will build the Docker image using backend/Dockerfile and expose the service URL.

3) Finalize
- In Vercel, set NEXT_PUBLIC_API_URL to the Render service URL (e.g., https://ai-video-editor-backend.onrender.com).
- Test the app by visiting the Vercel frontend URL; use the upload flow to create a job and then open the preview page (it will query the backend job endpoint).

Notes & Troubleshooting
- Ensure ffmpeg is available in the Render instance. If Render's default Docker image doesn't include ffmpeg, modify backend/Dockerfile to install ffmpeg (example added below).
- If transcription fails with a 401 or 403, double-check OPENAI_API_KEY value.

Recommended Dockerfile change (if ffmpeg missing):

FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
