# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /jobtracker

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files to the container
COPY . .

WORKDIR /jobtracker/jobtracker

# Collect static files at build time
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run migrations, then start gunicorn
CMD ["sh", "-c", "cd /jobtracker/jobtracker && python manage.py migrate && python manage.py create_admin && gunicorn jobtracker.wsgi:application --bind 0.0.0.0:8000"]