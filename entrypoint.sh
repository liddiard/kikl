#!/bin/sh
# Docker script to set up and run the Django app

# Run Django management commands
python manage.py collectstatic --noinput
python manage.py makemigrations shortener
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py seed_words # add default adjectives and nouns to the database

# Start supercronic and put it in the background
supercronic /app/shortener/config/cron-jobs &

# Start Gunicorn server
exec gunicorn kikl.wsgi:application --bind 0.0.0.0:$PORT
