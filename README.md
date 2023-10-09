# praktikum_new_diplom

docker build -t dron71/foodgram_backend:v9.2 backend/
docker build -t dron71/foodgram_frontend:v9.2 frontend/

docker push dron71/foodgram_backend:v9.2
docker push dron71/foodgram_frontend:v9.2

mkdir foodgram && cd foodgram
touch docker-compose.production.yml && nano docker-compose.production.yml
touch .env && nano .env
touch nginx.conf && nano nginx.conf

sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

Админ:
Email: 1@yandex.ru
Password: admin
