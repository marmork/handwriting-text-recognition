# Handwriting Text Recognition

A local, Docker-based workflow to process scanned handwritten PDF documents and convert them into structured Markdown notes using vision-based language models.

## Project Structure

* `Dockerfile`: Defines the Debian 13 (Trixie) Python environment and installs tools like `poppler-utils` for PDF-to-image conversion.
* `docker-compose.yml`: Handles container orchestration and mounts local development files and scan directories.
* `requirements.txt`: Lists explicit Python dependencies (`pdf2image`,
  `Pillow`, `mistralai`).
* `extract_pages.py`: Converts PDF documents into high-quality JPEG images.
* `transcribe_pages.py`: Transcribes extracted page images via the Mistral AI
  API.
* `run_pipeline.py`: The entry-point wrapper script that combines extraction
  and transcription into a single execution step.

## Directory Mapping

The container maps your host directories as follows:
* `.` (Project Root) $\rightarrow$ `/app` (Inside container)
* `/home/marcel/Dokumente/Scans` $\rightarrow$ `/data` (Inside container)

---

## Getting Started

### 1. Environment Configuration

Before launching the services, you must provide your API authorization.
Create a file named `.env` in the project root directory and add your key:

```env
MISTRAL_API_KEY=your_actual_api_key_here
```

### 2. Build and Start the Container

Build the environment from scratch, bypassing layer caches, and bring the
container up in detached mode: `sudo docker compose build --no-cache && sudo docker compose up -d`

### 3. Verify the environment

1. Verify that the container is up and running: `sudo docker compose ps`.   
2. Confirm that the application can successfully access your API key variable: `sudo docker compose exec transcribe-app printenv MISTRAL_API_KEY`.

---

## Usage

You can execute parts of the workflow independently or use the unified pipeline to run everything end-to-end.

### 1. The Unified Pipeline (Recommended)

Place your handwritten PDF files into `/home/marcel/Dokumente/Scans/`.

To process all files in the directory automatically: `sudo docker compose exec transcribe-app python run_pipeline.py`

To process one specific file only: `sudo docker compose exec transcribe-app python run_pipeline.py file.pdf`.

The pipeline extracts pages into individual image tracks and compiles a clean, combined transcription file named exactly like your input file (e.g.,
`file.md`) inside `/data/Transkriptionen/[filename]/`.

### 2. Independent Steps

If you want to perform actions separately, you can invoke the modular component scripts directly.

#### 1. Page extraction

```bash
# Process all files
sudo docker compose exec transcribe-app python extract_pages.py
# Process a single file
sudo docker compose exec transcribe-app python extract_pages.py file.pdf
```

#### 2. Cloud transcription

```bash
# Process all extracted folders
sudo docker compose exec transcribe-app python transcribe_pages.py
# Process a single extracted folder
sudo docker compose exec transcribe-app python transcribe_pages.py file.pdf
```