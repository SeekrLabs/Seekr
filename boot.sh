#!/bin/bash
source venv/bin/activate
ls
exec gunicorn -b :5000 --access-logfile - --error-logfile - Seekr.wsgi:application