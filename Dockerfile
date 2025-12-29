# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the file with the dependencies
COPY requirements.txt .

# Install dependencies
# (We install system dependencies if needed, but for this app it should be fine)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port env variable
ENV PORT 8080

# Command to run on container start
# We bind to 0.0.0.0:$PORT to make it compatible with Cloud Run / Heroku etc.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
