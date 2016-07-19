#!/bin/bash -xe

python /usr/src/app/manage.py migrate
gunicorn -c /usr/src/app/gunicorn/conf.py ui.wsgi --log-file -

