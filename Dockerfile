FROM python:3-slim-trixie

# Install system dependencies for PDF processing (poppler-utils for pdftoppm)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip beforehand
RUN pip install --no-cache-dir --upgrade pip

# Keep the container running so we can execute scripts inside it later
CMD ["tail", "-f", "/dev/null"]