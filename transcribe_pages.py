import base64
import sys
from pathlib import Path
import requests

# Define paths inside the container
DATA_DIR = Path("/data")
PAGES_DIR = DATA_DIR / "Transkriptionen" / "sample" / "pages"
OUTPUT_DIR = DATA_DIR / "Transkriptionen" / "sample"

# Standard multimodal chat endpoint for Ollama
OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
# Change from minicpm-v:latest to llama3.2-vision
MODEL_NAME = "llama3.2-vision"


def encode_image_to_base64(image_path: Path) -> str:
    """Reads an image file and returns its base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def transcribe_page(image_filename: str) -> None:
    image_path = PAGES_DIR / image_filename

    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)

    print(f"Encoding {image_filename}...")
    base64_image = encode_image_to_base64(image_path)

    # Prompt optimized for strict handwriting transcription
    prompt = (
        "Transcribe the handwritten text in this image accurately. "
        "Maintain the original formatting, line breaks, and structure where possible. "
        "Do not add any explanations, commentary, or introduction—output ONLY the transcribed text."
    )

    # Structure strictly required by Ollama's vision architecture
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [base64_image]
            }
        ],
        "stream": False
    }

    print(f"Sending {image_filename} to Ollama ({MODEL_NAME})... This might take a moment.")

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()

        result = response.json()
        # Parse the structured chat response content
        transcription = result.get("message", {}).get("content", "")

        # Save transcription to a markdown file next to the pages folder
        output_file = OUTPUT_DIR / f"{image_path.stem}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)

        print(f"\n--- Transcription for {image_filename} ---")
        print(transcription)
        print(f"----------------------------------------")
        print(f"Saved to: {output_file}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        if response := getattr(e, 'response', None):
            print(f"Server Response Content: {response.text}")


if __name__ == "__main__":
    # Test with the very first page extracted
    transcribe_page("page_001.jpg")
