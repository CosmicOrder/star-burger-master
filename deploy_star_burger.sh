#!/bin/bash
set -e

git pull
source venv/bin/activate
pip install -r requirements.txt
npm ci --dev
python manage.py collectstatic --noinput
python manage.py migrate
systemctl reload nginx
echo "Диплой прошёл успешно!"
