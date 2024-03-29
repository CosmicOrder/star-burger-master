#!/bin/bash
set -e

git pull
source venv/bin/activate
pip install -r requirements.txt
npm ci --dev
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl reload nginx
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'X-Rollbar-Access-Token: 6f1b2573f71147ab9d34e6e882ec7563' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
     "environment": "production",
     "revision": "'$(git rev-parse HEAD)'"
}
'
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Диплой прошёл успешно!"
