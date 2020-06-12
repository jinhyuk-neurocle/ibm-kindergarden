#!/bin/bash

if [ -z "$VCAP_APP_PORT" ];
  then SERVER_PORT=5000;
  else SERVER_PORT="$VCAP_APP_PORT";
fi

echo [$0] port is -------------- $SERVER_PORT

python manage.py migrate
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'jinhyuk@neuro-cle.com', 'admin')" | python manage.py shell

echo [$0] Starting Django Server...
python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload