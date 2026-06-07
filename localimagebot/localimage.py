from pathlib import Path
import zipfile
import torch
from diffusers import ZImagePipeline


project_dir = Path.cwd()
model_dir = project_dir / "Z-Image-Turbo"

# Rebuild zip
parts = sorted(project_dir.glob("Z-Image-Turbo.zip.part.*"))

with open(project_dir / "Z-Image-Turbo.zip", "wb") as out:
    for part in parts:
        with open(part, "rb") as f:
            out.write(f.read())

# Extract main archive if needed
if not model_dir.exists():
    with zipfile.ZipFile(project_dir / "Z-Image-Turbo.zip", "r") as zf:
        zf.extractall(project_dir)

pipe = ZImagePipeline.from_pretrained(
    str(model_dir),
    torch_dtype=torch.float32,
    local_files_only=True,
)

pipe.to("cpu")
import sys
text=sys.argv[1:]

image = pipe(
    prompt=text,
    height=512,
    width=512,
    num_inference_steps=4,
    guidance_scale=0.0,
    generator=torch.Generator("cpu").manual_seed(42),
).images[0]

image.save("output.png")

import shutil
shutil.rmtree("Z-Image-Turbo")
import os
os.remove("Z-Image-Turbo.zip")