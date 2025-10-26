import uuid, os, requests
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

SUPPORTED_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/sdxl-turbo",
    "Banana-dev/nano-diffusion",
    "SEDream/SDream-3.0",
    "SEDream/SDream-4.0",
    "black-forest-labs/FLUX.1-dev"
]

def enqueue_generation(prompt, input_path, user_id, model):
    job_id = str(uuid.uuid4())
    outname = f"{job_id}.png"
    outpath = os.path.join(OUT_DIR, outname)

    HF_TOKEN = os.environ.get("HF_API_TOKEN")
    chosen = model

    if not HF_TOKEN:
        # fallback: placeholder image with prompt text
        img = Image.new("RGB", (1024,1024), color=(30,30,30))
        d = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.load_default()
        except Exception:
            fnt = None
        text = f"Model: {chosen}\n\n{prompt}"
        d.multiline_text((20,20), text, fill=(255,255,255), font=fnt)
        img.save(outpath)
    else:
        url = f"https://api-inference.huggingface.co/models/{chosen}"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}
        try:
            r = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
            if r.status_code == 200:
                with open(outpath, "wb") as f:
                    f.write(r.content)
            else:
                img = Image.new("RGB", (1024,1024), color=(120,80,80))
                ImageDraw.Draw(img).text((20,20), f"HF error {r.status_code}", fill=(255,255,255))
                img.save(outpath)
        except Exception as e:
            img = Image.new("RGB", (1024,1024), color=(100,100,100))
            ImageDraw.Draw(img).text((20,20), f"Exception: {str(e)[:200]}", fill=(255,255,255))
            img.save(outpath)

    return job_id
