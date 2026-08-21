# Jobtracker
This is a Django application for tracking job applications

## Startup

### Docker
You can start the container in the base directory with
```env
docker-compose up --build
```

### Direct
You can start up the server without Docker directly by accessing Django
from the `jobtracker` directory
```env
python3 .\manage.py runserver
```