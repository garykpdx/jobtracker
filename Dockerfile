# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory for build steps
WORKDIR /jobtracker

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files to the container
COPY . .

# Switch to the folder that actually contains manage.py
WORKDIR /jobtracker/jobtracker

# Collect static files
RUN mkdir -p static

# Expose the port that the app runs on
EXPOSE 8000

# Run migrations, then start gunicorn
CMD ["sh", "-c", "cd /jobtracker/jobtracker && python manage.py migrate && python manage.py create_admin && gunicorn jobtracker.wsgi:application --bind 0.0.0.0:8000"]