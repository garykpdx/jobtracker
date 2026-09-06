# Jobtracker
This is a Django application for tracking job applications

## Startup

### Docker
You can start the container in the base directory with
```env
docker-compose up --build
```

You can omit the `--build` flag if you have already run this and are
not making changes to the container

### Direct
You can start up the server without Docker directly by accessing Django
from the `jobtracker` directory
```env
python3 .\manage.py runserver
```