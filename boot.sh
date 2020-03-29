#!/bin/bash
source venv/bin/activate
python manage.py migrate
exec gunicorn -b :5000 --access-logfile - Seekr.wsgi:application
