#!/bin/sh
# Docker script to set up and run the Django app

# Load environment variables from .env file, stripping comments
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# Run Django management commands
python manage.py collectstatic --noinput
python manage.py makemigrations shortener
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py seed_words # add default adjectives and nouns to the database

# Start the cron service
service cron start

# Start Gunicorn server
exec gunicorn kikl.wsgi:application --bind 0.0.0.0:8000
