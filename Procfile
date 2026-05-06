web: gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: celery -A config.celery_app worker --loglevel=info