# Use a lightweight base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir PyMuPDF==1.23.7

# Copy the main script
COPY main.py /app/

# Ensure input/output directories exist
RUN mkdir -p /app/input /app/output

# Command to run the script
CMD ["python", "main.py"]