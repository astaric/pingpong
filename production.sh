#!/bin/bash
export PRODUCTION=True
export DATABASE_URL=postgres://localhost/pingpong
python manage.py collectstatic --noinput
gunicorn -b 127.0.0.1:8001 -w 3 pingpong.wsgi:application
