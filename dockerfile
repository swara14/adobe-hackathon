# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir pymupdf

# Create input/output dirs
RUN mkdir -p input output

# Set entrypoint
CMD ["python", "heading_extractor.py"]
