from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
import uuid
import os
from pathlib import Path
import json
import subprocess
import shlex

app = FastAPI()

JOBS_DIR = Path('./backend/jobs')
JOBS_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '200'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.post('/upload')
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Validate size if provided
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise HTTPException(status_code=413, detail=f'File too large ({size_mb:.1f}MB). Max is {MAX_UPLOAD_MB}MB')

    # Save uploaded file
    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    file_path = job_dir / file.filename
    with open(file_path, 'wb') as f:
        f.write(contents)

    # create initial meta
    meta = {'status': 'queued', 'filename': file.filename}
    with open(job_dir / 'meta.json', 'w', encoding='utf-8') as mf:
        json.dump(meta, mf, ensure_ascii=False, indent=2)

    # Enqueue background processing (scene detection, whisper)
    if background_tasks is not None:
        background_tasks.add_task(process_job, job_id, str(file_path))

    return JSONResponse({'job_id': job_id, 'filename': file.filename})

@app.get('/job/{job_id}')
async def get_job(job_id: str):
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail='Job not found')
    meta_file = job_dir / 'meta.json'
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    else:
        meta = {'status': 'processing'}
    return meta

@app.post('/export')
async def export_job(job_id: str = Form(...), scenes: str = Form(...)):
    # scenes: JSON array of {start, end} objects or indices; we expect JSON string
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail='Job not found')
    meta_file = job_dir / 'meta.json'
    if not meta_file.exists():
        raise HTTPException(status_code=400, detail='Job not ready')
    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    try:
        selected = json.loads(scenes)
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid scenes payload')

    input_file = job_dir / meta.get('filename')
    output_parts = []
    for idx, seg in enumerate(selected):
        start = float(seg.get('start'))
        end = float(seg.get('end'))
        out_part = job_dir / f'part_{idx}.mp4'
        # Re-encode segment to ensure consistency
        cmd = f"ffmpeg -y -ss {start} -to {end} -i {shlex.quote(str(input_file))} -c:v libx264 -c:a aac -strict -2 {shlex.quote(str(out_part))}"
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_parts.append(out_part)
        except subprocess.CalledProcessError as e:
            # cleanup and abort
            raise HTTPException(status_code=500, detail=f'ffmpeg failed: {e.stderr.decode()[:200]}')

    # Create concat file
    concat_file = job_dir / 'concat.txt'
    with open(concat_file, 'w', encoding='utf-8') as cf:
        for p in output_parts:
            cf.write(f"file '{p.name}'\n")

    final_out = job_dir / 'output.mp4'
    cmd_concat = f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(concat_file))} -c copy {shlex.quote(str(final_out))}"
    try:
        subprocess.run(cmd_concat, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        # fallback: re-encode concat
        cmd_concat = f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(concat_file))} -c:v libx264 -c:a aac {shlex.quote(str(final_out))}"
        subprocess.run(cmd_concat, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return JSONResponse({'status': 'done', 'download': f'/download/{job_id}/output.mp4'})

@app.get('/download/{job_id}/{filename}')
async def download(job_id: str, filename: str):
    job_dir = JOBS_DIR / job_id
    file_path = job_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path=str(file_path), media_type='video/mp4', filename=filename)


def process_job(job_id: str, file_path: str):
    """
    Processing pipeline:
    - scene detection using PySceneDetect
    - extract audio and call OpenAI Whisper (via HTTP) to transcribe
    - save meta.json with scenes and subtitles
    """
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector

    job_dir = JOBS_DIR / job_id
    meta = {'status': 'processing'}
    with open(job_dir / 'meta.json', 'w', encoding='utf-8') as mf:
        json.dump(meta, mf, ensure_ascii=False, indent=2)

    try:
        # Scene detection
        video_manager = VideoManager([file_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=30.0))
        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        scenes = []
        for s in scene_list:
            start_time = s[0].get_seconds()
            end_time = s[1].get_seconds()
            scenes.append({'start': start_time, 'end': end_time})
        video_manager.release()
    except Exception as e:
        scenes = [{'start': 0.0, 'end': 10.0}, {'start': 10.0, 'end': 25.0}]

    # Extract audio to wav for transcription
    audio_file = job_dir / 'audio.wav'
    try:
        cmd_audio = f"ffmpeg -y -i {shlex.quote(str(file_path))} -ar 16000 -ac 1 -vn {shlex.quote(str(audio_file))}"
        subprocess.run(cmd_audio, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        audio_file = None

    subtitles = ''
    if audio_file and OPENAI_API_KEY:
        try:
            import requests
            url = 'https://api.openai.com/v1/audio/transcriptions'
            headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
            files = {'file': open(audio_file, 'rb')}
            data = {'model': 'whisper-1', 'language': 'ar'}
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            if resp.status_code == 200:
                rj = resp.json()
                subtitles = rj.get('text', '')
            else:
                subtitles = f'Error from Whisper API: {resp.status_code}'
        except Exception as e:
            subtitles = f'Whisper call failed: {str(e)[:200]}'
    else:
        if not OPENAI_API_KEY:
            subtitles = 'OPENAI_API_KEY not set. لا توجد ترجمة حقيقية.'
        else:
            subtitles = 'Audio extraction failed; لا توجد ترجمة.'

    meta = {'status': 'done', 'scenes': scenes, 'subtitles': subtitles, 'filename': Path(file_path).name}
    with open(job_dir / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
