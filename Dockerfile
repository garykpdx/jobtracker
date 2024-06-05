# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /jobtracker/jobtracker

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files to the container
COPY . .

# Collect static files
RUN mkdir -p static
#RUN python manage.py collectstatic --noinput

# Expose the port that the app runs on
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
