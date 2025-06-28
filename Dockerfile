# Dockerfile
# Use a Python base image. It's good practice to pin to a specific version.
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
# This means if requirements.txt doesn't change, these layers won't be rebuilt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
# The .dockerignore file will prevent unwanted files from being copied
COPY . .

# Ensure scripts are executable if needed (e.g., project_setup.sh)
# Though project_setup.sh is primarily for local dev, if used in container, ensure executable.
RUN chmod +x project_setup.sh || true # '|| true' to prevent build failure if file doesn't exist or isn't used

# Expose any ports your application might listen on (e.g., if it had a web UI)
# Not strictly necessary for this email sending script, but good practice for future expansion.
# EXPOSE 8000

# Command to run your application when the container starts
# This will execute your main.py script
CMD ["python3", "main.py"]
