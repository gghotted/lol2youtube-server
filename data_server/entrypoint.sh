export DJANGO_SETTINGS_MODULE=config.settings.deploy

python manage.py makemigrations event match raw_data replay summoner timeline champion youtube && \
python manage.py migrate && \
echo yes | python manage.py collectstatic && \

gunicorn --log-level=DEBUG --bind 0.0.0.0:8000 --timeout 1200 config.wsgi.deploy:application
