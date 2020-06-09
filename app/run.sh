#!/bin/bash

if [ -z "$VCAP_APP_PORT" ];
  then SERVER_PORT=5000;
  else SERVER_PORT=$VCAP_APP_PORT;
fi

python manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'jinhyuk@neuro-cle.com', 'almightychang')" | python manage.py shell

python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload