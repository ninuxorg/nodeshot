#!/bin/bash

set -x 

redis-server &
sleep 3

if [ ! -f /app/first_start ]; then
    python manage.py migrate --noinput --no-initial-data
    python manage.py loaddata initial_data
    python manage.py collectstatic
    echo "from nodeshot.community.profiles.models import Profile;\
       Profile.objects.create_superuser('admin', '', 'admin')" | ./manage.py shell
    touch /app/first_start
fi

python manage.py runserver 0.0.0.0:8000
