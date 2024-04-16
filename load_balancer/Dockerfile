# Dockerfile for API Server
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY backend.py /app/
COPY postgres_communication.py /app/

# Expose the port the app runs on
EXPOSE 8000

# Use Uvicorn to run the app
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
