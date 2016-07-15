#!/bin/bash -xe

python /usr/src/app/manage.py migrate
gunicorn -c /usr/src/app/gunicorn/conf.py data.wsgi --log-file -

