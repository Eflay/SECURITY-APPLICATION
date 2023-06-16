#!/bin/bash

# Execute migrations
python manage.py makemigrations
python manage.py migrate
while [ $? -ne 0 ]; do
	echo "Waiting 2s before restarting migration ..."
	sleep 2
    	python manage.py migrate
done

# Replace secret key
secret_key=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
sed -i "/^SECRET_KEY =/ c\SECRET_KEY = '$secret_key'" health/settings.py

# Collect static files
python manage.py collectstatic --noinput

# Start server
python -m gunicorn --bind 0.0.0.0:8000 health.wsgi

