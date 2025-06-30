web: gunicorn tracking_api.wsgi:application --bind 0.0.0.0:$PORT --workers 3
release: python manage.py migrate
