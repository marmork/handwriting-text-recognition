import base64
import os
import sys
from pathlib import Path
from mistralai.client import Mistral

# Define paths inside the container
DATA_DIR = Path("/data")
OUTPUT_BASE_DIR = DATA_DIR / "Transkriptionen"

# Read the API key injected by docker-compose from your host .env file
API_KEY = os.environ.get("MISTRAL_API_KEY")
MODEL_NAME = "pixtral-12b"

if not API_KEY:
    print("Error: MISTRAL_API_KEY environment variable is not set.")
    print("Verify that your .env file exists and compose passes it.")
    sys.exit(1)

# Initialize the official Mistral client
client = Mistral(api_key=API_KEY)


def encode_image_to_base64_url(image_path: Path) -> str:
    """Reads an image file and returns a formatted base64 Data URL string."""
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def transcribe_document(doc_dir: Path) -> None:
    """Transcribes all pages within a specific document directory."""
    pages_dir = doc_dir / "pages"
    if not pages_dir.exists():
        print(f"Error: Pages directory not found at {pages_dir}")
        print("Please run extract_pages.py first.")
        return

    image_paths = sorted(list(pages_dir.glob("page_*.jpg")))
    total_pages = len(image_paths)

    if total_pages == 0:
        print(f"No pages found in {pages_dir}")
        return

    print(f"\nProcessing directory: {doc_dir.name}")
    print(f"Found {total_pages} pages to transcribe using {MODEL_NAME}.")
    print("Starting pipeline execution...")

    # Output file is named exactly like the input directory stem
    output_combined_file = doc_dir / f"{doc_dir.name}.md"

    # Using 'w' to fresh-start the file and avoid merge conflicts on re-runs
    with open(output_combined_file, "w", encoding="utf-8") as f_out:
        for idx, image_path in enumerate(image_paths, start=1):
            print(f"[{idx}/{total_pages}] Sending {image_path.name}...")

            try:
                base64_data_url = encode_image_to_base64_url(image_path)

                prompt = (
                    "You are an expert paleographer and academic transcriber. "
                    "Transcribe the handwritten text in this image accurately "
                    "verbatim. The text consists of dense academic notes in "
                    "German and English. Strictly follow these rules:\n"
                    "1. Maintain all original line breaks, indentations, "
                    "and vertical layout.\n"
                    "2. Keep symbols exactly as written (e.g., '->', "
                    "brackets).\n"
                    "3. Do not correct typos, shorthand, or grammar.\n"
                    "4. If a word is completely illegible, use '[?]'.\n"
                    "5. Output ONLY the raw transcribed text. Do not add "
                    "any introductory or concluding remarks, metadata, "
                    "or markdown titles."
                )

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": base64_data_url}
                        ]
                    }
                ]

                response = client.chat.complete(
                    model=MODEL_NAME,
                    messages=messages
                )

                transcription = response.choices[0].message.content.strip()

                if transcription:
                    f_out.write(f"{transcription}\n\n")
                else:
                    f_out.write(
                        f"[Warning: Empty response for page {idx}]\n\n"
                    )

                print(f"  Finished page {idx} successfully.")

            except Exception as e:
                print(f"  Failed page {idx} due to runtime error: {e}")
                f_out.write(f"[Error processing page {idx}: {e}]\n\n")

    print(f"Completed notes saved to: {output_combined_file}")


if __name__ == "__main__":
    # Case 1: A specific filename or folder name was passed as an argument
    if len(sys.argv) > 1:
        input_arg = sys.argv[1]
        doc_name = Path(input_arg).stem
        target_dir = OUTPUT_BASE_DIR / doc_name
        transcribe_document(target_dir)

    # Case 2: No argument passed -> Batch process all subdirectories
    else:
        print(f"Scanning '{OUTPUT_BASE_DIR}' for extracted documents...")
        if not OUTPUT_BASE_DIR.exists():
            print("No extractions found. Please run extract_pages.py first.")
            sys.exit(0)

        doc_dirs = sorted(
            [p for p in OUTPUT_BASE_DIR.iterdir() if p.is_dir()]
        )

        if not doc_dirs:
            print("No document directories found to process.")
            sys.exit(0)

        print(f"Found {len(doc_dirs)} document(s) to transcribe.")
        for target_dir in doc_dirs:
            transcribe_document(target_dir)

        print("\nAll batch transcriptions completed.")
