import sys
from pathlib import Path
from pdf2image import convert_from_path

# Define paths inside the container
DATA_DIR = Path("/data")
OUTPUT_BASE_DIR = DATA_DIR / "Transkriptionen"


def extract_pdf_pages(pdf_filename: str) -> None:
    pdf_path = DATA_DIR / pdf_filename

    if not pdf_path.exists():
        print(f"Error: File not found at {pdf_path}")
        sys.exit(1)

    # Create a specific output folder for this document's images
    document_name = pdf_path.stem
    output_dir = OUTPUT_BASE_DIR / document_name / "pages"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing '{pdf_filename}'...")
    print(f"Extracting pages to: {output_dir}")

    # Convert PDF to a list of PIL Images (200 DPI is a sweet spot for HTR/OCR)
    try:
        pages = convert_from_path(pdf_path, dpi=200)

        for index, page in enumerate(pages, start=1):
            image_filename = f"page_{index:03d}.jpg"
            image_path = output_dir / image_filename

            # Save the image as JPEG
            page.save(image_path, "JPEG", quality=90)
            print(f" Saved: {image_filename}")

        print(f"\nSuccess! Extracted {len(pages)} pages.")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")


if __name__ == "__main__":
    # For now, we look for a file named 'sample.pdf' in your Scans folder
    extract_pdf_pages("sample.pdf")
