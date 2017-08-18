web: python manage.py collectstatic --noinput && gunicorn ui.wsgi --bind [::1]:$PORT --bind 0.0.0.0:$PORT 
