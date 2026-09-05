from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
import os
from pathlib import Path

app = FastAPI()

JOBS_DIR = Path('./backend/jobs')
JOBS_DIR.mkdir(parents=True, exist_ok=True)

@app.post('/upload')
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Save uploaded file
    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    file_path = job_dir / file.filename
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # Enqueue background processing (scene detection, whisper)
    if background_tasks is not None:
        background_tasks.add_task(process_job, job_id, str(file_path))

    return JSONResponse({'job_id': job_id, 'filename': file.filename})

@app.get('/job/{job_id}')
async def get_job(job_id: str):
    job_dir = JOBS_DIR / job_id
    meta = {}
    meta_file = job_dir / 'meta.json'
    if meta_file.exists():
        import json
        meta = json.loads(meta_file.read_text())
    else:
        meta = {'status': 'processing'}
    return meta


def process_job(job_id: str, file_path: str):
    """
    Placeholder processing pipeline:
    - run ffmpeg or PySceneDetect to detect scenes
    - call OpenAI Whisper API to create subtitles
    - save meta.json with results
    """
    import json, subprocess
    job_dir = JOBS_DIR / job_id
    scenes = []
    # Simple ffprobe-based scene detection placeholder (not production)
    try:
        # This is a placeholder. For robust detection use PySceneDetect or ffmpeg with select filter.
        # Example command (not executed here): ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)'" -frames:v 1 out%03d.jpg
        scenes = [{'start': 0.0, 'end': 10.0}, {'start': 10.0, 'end': 25.0}]
    except Exception as e:
        scenes = []

    # Whisper / OpenAI call placeholder
    subtitles = 'ترجمة تجريبية. ضع مفتاح OpenAI لتوليد ترجمة حقيقية.'

    meta = {'status': 'done', 'scenes': scenes, 'subtitles': subtitles}
    with open(job_dir / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
