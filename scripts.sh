#!/bin/sh

# Остановить скрипт, если любая команда завершится с ошибкой
set -e

echo "Применяю миграции..."
python manage.py migrate --noinput

echo "Собираю статику..."
python manage.py collectstatic --noinput

echo "Запускаю Gunicorn..."
exec gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 3