from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from generate import enqueue_generation, OUT_DIR, SUPPORTED_MODELS

app = FastAPI(title="WalloAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(OUT_DIR, exist_ok=True)

@app.get("/api/test")
def test():
    return {"status":"WalloAI backend running ✅"}

@app.post("/api/generate")
def generate(prompt: str = Form(...), model: str = Form(None), image: UploadFile = File(None)):
    chosen = model or os.environ.get("HF_MODEL", SUPPORTED_MODELS[0])
    if chosen not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Model not supported: {chosen}")
    input_path = None
    if image:
        filename = f"input_{image.filename}"
        input_path = os.path.join(OUT_DIR, filename)
        with open(input_path, "wb") as f:
            f.write(image.file.read())
    job_id = enqueue_generation(prompt, input_path, user_id=0, model=chosen)
    return JSONResponse(content={"ok": True, "job_id": job_id, "model": chosen})

@app.get("/api/images")
def list_images():
    files = []
    for fn in os.listdir(OUT_DIR):
        if fn.lower().endswith(('.png', '.jpg', '.jpeg')):
            files.append({'url': f'/api/outputs/{fn}', 'prompt': ''})
    files_sorted = sorted(files, key=lambda x: x['url'], reverse=True)
    return {'images': files_sorted}

@app.get("/api/outputs/{filename}")
def output_file(filename: str):
    path = os.path.join(OUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path)
