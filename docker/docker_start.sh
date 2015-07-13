#!/bin/bash

set -x 
if [ ! -f /app/first_start ]; then
    python manage.py migrate --noinput --no-initial-data
    python manage.py loaddata initial_data

    touch /app/first_start
fi

python manage.py runserver