# innobot_test/backend/Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
# We add gunicorn explicitly for production serving
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the backend code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]