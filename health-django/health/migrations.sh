find . -path '*/migrations/__init__.py' -exec truncate -s 0 {} + -o -path '*/migrations/*' -delete
python3 manage.py makemigrations
python3 manage.py migrate
