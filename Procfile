web: gunicorn app:server
celery -A server.celery worker -l info -c 1