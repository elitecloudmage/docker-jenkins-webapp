# Use a slim Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (better layer caching — deps only reinstall if this file changes)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Flask default port
EXPOSE 5000

# Run with gunicorn (production-grade WSGI server, better than flask run)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
