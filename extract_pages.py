import sys
from pathlib import Path
from pdf2image import convert_from_path

# Define paths inside the container
DATA_DIR = Path("/data")
OUTPUT_BASE_DIR = DATA_DIR / "Transkriptionen"


def extract_pdf_pages(pdf_path: Path) -> None:
    """Converts a single PDF file into high-quality page images."""
    if not pdf_path.exists():
        print(f"Error: File not found at {pdf_path}")
        return

    # Create a specific output folder for this document's images
    document_name = pdf_path.stem
    output_dir = OUTPUT_BASE_DIR / document_name / "pages"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing '{pdf_path.name}'...")
    print(f"  Extracting pages to: {output_dir}")

    try:
        # Convert PDF to a list of PIL Images (200 DPI for HTR/OCR)
        pages = convert_from_path(pdf_path, dpi=200)

        for index, page in enumerate(pages, start=1):
            image_filename = f"page_{index:03d}.jpg"
            image_path = output_dir / image_filename

            # Save the image as JPEG
            page.save(image_path, "JPEG", quality=90)
            print(f"   Saved: {image_filename}")

        print(f"  Success! Extracted {len(pages)} pages.")

    except Exception as e:
        print(f"  An error occurred during conversion: {e}")


if __name__ == "__main__":
    # Case 1: A specific filename was passed as an argument
    if len(sys.argv) > 1:
        target_filename = sys.argv[1]
        target_path = DATA_DIR / target_filename
        extract_pdf_pages(target_path)

    # Case 2: No argument passed -> Batch process all PDFs in directory
    else:
        print(f"Scanning '{DATA_DIR}' for PDF files...")
        pdf_files = sorted(list(DATA_DIR.glob("*.pdf")))

        if not pdf_files:
            print("No PDF files found to process.")
            sys.exit(0)

        print(f"Found {len(pdf_files)} PDF(s) to extract.")
        for pdf_path in pdf_files:
            extract_pdf_pages(pdf_path)

        print("\nAll PDF extractions completed.")
