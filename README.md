# Handwriting Text Recognition

A local, Docker-based workflow to process scanned handwritten PDF documents and convert them into structured Markdown notes using vision-based language models.

## Project Structure

* `Dockerfile`: Defines the Debian 13 (Trixie) Python environment and installs tools like `poppler-utils` for PDF-to-image conversion.
* `docker-compose.yml`: Handles container orchestration and mounts the local development files and scan directories.

## Directory Mapping

The container maps your host directories as follows:
* `.` (Project Root) $\rightarrow$ `/app` (Inside container)
* `/home/marcel/Dokumente/Scans` $\rightarrow$ `/data` (Inside container)

---

## Getting Started

### 1. Prerequisites
Ensure you have Docker and Docker Compose installed on your host system.

### 2. Build and Start the Container
Since the host environment requires root privileges for Docker, run the setup with `sudo`:

```bash
sudo docker compose up -d --build
```

3. Verify the Setup

Check if the container is running successfully: `sudo docker compose ps`. Verify that the container can correctly see your local scan directory mapped to `/data`: `sudo docker compose exec transcribe-app ls -la /data`