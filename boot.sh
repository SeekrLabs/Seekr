#!/bin/bash
source venv/bin/activate
python manage.py migrate
python manage.py ingest 28
exec gunicorn -b :5000 --access-logfile - Seekr.wsgi:application