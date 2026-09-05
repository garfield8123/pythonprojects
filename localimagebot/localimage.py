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
    """Loads the model into memory once and returns the pipeline and device."""
    project_dir = Path.cwd()
    model_dir = project_dir / "Z-Image-Turbo"
    
    if is_discord:
        model_dir = Path("localimagebot/Z-Image-Turbo")
    
    # Ensure model is extracted before loading
    if not model_dir.exists():
        extractpartzip() 

    # Check if GPU (CUDA) is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use float16 for GPU efficiency, float32 for CPU compatibility
    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    
    print(f"🔄 Loading Z-Image-Turbo model into {device.upper()} memory...")
    
    pipe = ZImagePipeline.from_pretrained(
        str(model_dir),
        torch_dtype=torch_dtype,
        local_files_only=True,
    )
    pipe.to(device)
    print("✅ Model loaded successfully!")
    
    # Returning both pipe and device helps keep generation aligned
    return pipe, device


def generateimage(pipe, text, device="cpu"):
    """Uses the pre-loaded pipeline to generate an image."""
    image = pipe(
        prompt=text,
        height=512,
        width=512,
        num_inference_steps=4,
        guidance_scale=0.0,
        generator=torch.Generator(device).manual_seed(42),
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