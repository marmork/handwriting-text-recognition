# Handwriting Text Recognition

A local, Docker-based workflow to process scanned handwritten PDF documents and convert them into structured Markdown notes using vision-based language models.

## Project Structure

* `Dockerfile`: Defines the Debian 13 (Trixie) Python environment and installs tools like `poppler-utils` for PDF-to-image conversion.
* `docker-compose.yml`: Handles container orchestration and mounts local development files and scan directories.
* `extract_pages.py`: Python script to split PDF documents into high-quality JPEG images at 200 DPI.
* `transcribe_pages.py`: Python script to send processed page images to a local Ollama service for multimodal transcription.

## Directory Mapping

The container maps your host directories as follows:
* `.` (Project Root) $\rightarrow$ `/app` (Inside container)
* `/home/marcel/Dokumente/Scans` $\rightarrow$ `/data` (Inside container)

---

## Getting Started

### 1. Prerequisites

Ensure you have Docker, Docker Compose, and Ollama installed on your host system.

### 2. Configure Ollama for Container Communication

By default, Ollama only listens on `localhost`. To allow the Docker container to connect, you must expose the service host interface: `sudo systemctl edit ollama.service`  and add the following configuration block:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```
Afterwards, run `sudo systemctl daemon-reload && sudo systemctl restart ollama`.

### 3. Build and Start the Container

Since the host environment requires root privileges for Docker, run the setup with `sudo`: `sudo docker compose up -d --build`.
If you ever need to rebuild the environment from scratch, bypassing the layer cache: `sudo docker compose build --no-cache && sudo docker compose up -d`.

### 4. Verify the environment

Check if the container is running successfully: `sudo docker compose ps`. Verify that the container can correctly see your local scan directory mapped to `/data`: `sudo docker compose exec transcribe-app ls -la /data`.

## Usage

### 1. Page extraction

Place a handwritten PDF scan named sample.pdf into your local /home/marcel/Dokumente/Scans/ folder. Run the extraction script to convert it into individual images: `sudo docker compose exec transcribe-app python extract_pages.py`. This generates high-resolution JPEGs under `/data/Transkriptionen/sample/pages/`.

### 2. Running transcription

Trigger the multimodal pipeline to pass images through minicpm-v via Ollama and create structured Markdown notes: `sudo docker compose exec transcribe-app python transcribe_pages.py`.