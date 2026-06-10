import sys
import subprocess

# Define the runner executable inside the container
PYTHON_BIN = "python"


def run_full_pipeline() -> None:
    """Invokes both extraction and transcription scripts sequentially."""
    # Capture any arguments passed to this wrapper script (e.g., sample.pdf)
    args = sys.argv[1:]

    # Build execution commands matching the current argument layout
    extract_cmd = [PYTHON_BIN, "extract_pages.py"] + args
    transcribe_cmd = [PYTHON_BIN, "transcribe_pages.py"] + args

    print("--- Phase 1: Extracting PDF pages ---")
    # check=True forces the script to halt immediately if a step fails
    extract_result = subprocess.run(extract_cmd, check=True)

    if extract_result.returncode == 0:
        print("\n--- Phase 2: Transcribing extracted pages via Mistral ---")
        subprocess.run(transcribe_cmd, check=True)


if __name__ == "__main__":
    try:
        run_full_pipeline()
    except subprocess.CalledProcessError as e:
        print(f"\nPipeline interrupted due to an error in a sub-script: {e}")
        sys.exit(1)
