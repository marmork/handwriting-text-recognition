import base64
import sys
from pathlib import Path
import requests

# Define paths inside the container
DATA_DIR = Path("/data")
DOCUMENT_DIR = DATA_DIR / "Transkriptionen" / "sample"
PAGES_DIR = DOCUMENT_DIR / "pages"

# Llama 3.2 Vision handles multimodal chat via /api/chat smoothly
OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
MODEL_NAME = "llama3.2-vision"


def encode_image_to_base64(image_path: Path) -> str:
    """Reads an image file and returns its base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def transcribe_batch() -> None:
    if not PAGES_DIR.exists():
        print(f"Error: Pages directory not found at {PAGES_DIR}")
        print("Please run extract_pages.py first.")
        sys.exit(1)

    # Find and sort all jpeg pages numerically (page_001.jpg, page_002.jpg, etc.)
    image_paths = sorted(list(PAGES_DIR.glob("page_*.jpg")))
    total_pages = len(image_paths)

    if total_pages == 0:
        print(f"No pages found in {PAGES_DIR}")
        sys.exit(0)

    print(f"Found {total_pages} pages to transcribe using {MODEL_NAME}.")
    print("Starting batch process. This will run entirely in the background...\n")

    # Final combined output file path
    output_combined_file = DOCUMENT_DIR / "complete_transcription.md"

    # Open the file in write mode to clear past attempts, then we append
    with open(output_combined_file, "w", encoding="utf-8") as f_out:
        f_out.write(f"# Transcription: sample.pdf\n\n")

    # Loop through each page
    for idx, image_path in enumerate(image_paths, start=1):
        print(f"[{idx}/{total_pages}] Processing {image_path.name}...")

        try:
            base64_image = encode_image_to_base64(image_path)

            # Context-focused prompt for dense handwriting + sociology definitions
            prompt = (
                "Transcribe the handwritten text in this image accurately. "
                "The text contains academic notes in a mix of German and English. "
                "Maintain the original formatting, line breaks, and structural layout where possible. "
                "Do not add any explanations, commentary, or introduction—output ONLY the transcribed text verbatim."
            )

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

            # Request without timeout constraint to allow deep CPU layer offloading calculations
            response = requests.post(OLLAMA_URL, json=payload, timeout=None)
            response.raise_for_status()

            result = response.json()
            transcription = result.get("message", {}).get("content", "").strip()

            # Append this page's result to the combined file
            with open(output_combined_file, "a", encoding="utf-8") as f_out:
                f_out.write(f"## --- PAGE {idx} ---\n\n")
                if transcription:
                    f_out.write(f"{transcription}\n\n")
                else:
                    f_out.write(f"* [Warning: Empty response returned for page {idx}] *\n\n")

            print(f" ✅ Finished page {idx} successfully.")

        except requests.exceptions.RequestException as e:
            print(f" ❌ Failed page {idx} due to connection error: {e}")
            with open(output_combined_file, "a", encoding="utf-8") as f_out:
                f_out.write(f"## --- PAGE {idx} ---\n\n❌ Error processing page: {e}\n\n")
        except Exception as e:
            print(f" ❌ Unexpected error on page {idx}: {e}")

    print(f"\nAll done! Full combined notes saved to: {output_combined_file}")


if __name__ == "__main__":
    transcribe_batch()
