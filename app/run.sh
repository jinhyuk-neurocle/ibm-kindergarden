#!/bin/bash

if [ -z "$VCAP_APP_PORT" ];
  then SERVER_PORT=5000;
<<<<<<< HEAD
  else SERVER_PORT=$VCAP_APP_PORT;
fi

python manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'jinhyuk@neuro-cle.com', 'almightychang')" | python manage.py shell

=======
  else SERVER_PORT="$VCAP_APP_PORT";
fi

echo [$0] port is -------------- $SERVER_PORT

python manage.py migrate
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'jinhyuk@neuro-cle.com', 'admin')" | python manage.py shell

echo [$0] Starting Django Server...
>>>>>>> 61c2f1f478f684469cc4c2f4147abab8f21459fd
python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload