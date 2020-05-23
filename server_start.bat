call ./venv/scripts/activate
python app/manage.py wait_for_db 
python app/manage.py migrate
python app/manage.py runserver localhost:8000