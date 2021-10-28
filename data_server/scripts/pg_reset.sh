db_name=$1
user=$2

echo "
DROP DATABASE IF EXISTS $db_name;
CREATE DATABASE $db_name OWNER $user ENCODING 'utf-8';
" | psql postgres

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

python manage.py makemigrations
python manage.py migrate
