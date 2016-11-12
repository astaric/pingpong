#!/bin/bash
export PRODUCTION=True
export DATABASE_URL=postgres://localhost/pingpong
python manage.py collectstatic --noinput
uwsgi --socket pingpong.sock --module pingpong.wsgi --chmod-socket=666
