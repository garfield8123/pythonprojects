from pathlib import Path
import zipfile
import torch
from diffusers import ZImagePipeline

def extractpartzip():
    project_dir = Path.cwd()
    model_dir = project_dir / "Z-Image-Turbo"

    # Rebuild zip
    parts = sorted(project_dir.glob("Z-Image-Turbo.zip.part.*"))

    with open(project_dir / "Z-Image-Turbo.zip", "wb") as out:
        for part in parts:
            with open(part, "rb") as f:
                out.write(f.read())
    extractfullzip()

def extractfullzip():
    project_dir = Path.cwd()
    model_dir = project_dir / "Z-Image-Turbo"
    # Extract main archive if needed
    if not model_dir.exists():
        with zipfile.ZipFile(project_dir / "Z-Image-Turbo.zip", "r") as zf:
            zf.extractall(project_dir)


def load_model(is_discord=False):
    """Loads the model into memory once and returns the pipeline."""
    project_dir = Path.cwd()
    model_dir = project_dir / "Z-Image-Turbo"
    
    if is_discord:
        model_dir = Path("localimagebot/Z-Image-Turbo")
    
    # Ensure model is extracted before loading
    if not model_dir.exists():
        # Optional: You can trigger your extraction functions here if needed
        extractpartzip() 

    print("🔄 Loading Z-Image-Turbo model into CPU memory...")
    pipe = ZImagePipeline.from_pretrained(
        str(model_dir),
        torch_dtype=torch.float32,
        local_files_only=True,
    )
    pipe.to("cpu")
    print("✅ Model loaded successfully!")
    return pipe


def generateimage(pipe, text):
    """Uses the pre-loaded pipeline to generate an image."""
    image = pipe(
        prompt=text,
        height=512,
        width=512,
        num_inference_steps=4,
        guidance_scale=0.0,
        generator=torch.Generator("cpu").manual_seed(42),
    ).images[0]

    output_path = "output.png"
    image.save(output_path)
    return output_path

def cleanmodel():
    import shutil
    shutil.rmtree("Z-Image-Turbo")

if __name__ == "__main__":
    import sys, asyncio
    print(generateimage(sys.argv[1:]))