# Foodgram - «Продуктовый помощник»

Cервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Запуск проекта

- Клонируем репозиторий:

```bash
git clone git@github.com:Dron-71/foodgram-project-react.git
```

- Установка и развертывание виртуального окружения:

```bash
python3 -m venv venv && source venv/bin/activate
```

- Обновляем менеджер пакетов pip -> Устанавливает зависимости -> Устанавливаем Django:

```bash
python3 -m pip install --upgrade pip && cd backend/ && pip install -r requirements.txt
```

- Создание и применение миграций:

```bash
python3 manage.py makemigrations
```

```bash
python3 manage.py migrate
```

- Заполнение базы данных:

```bash
python3 manage.py import_ingredients
```

- Создаем суперпользователя:

```bash
python3 manage.py createsuperuser
```

- Запускать сервер разработки:

```bash
python3 manage.py runserver
```

### Установка и запуск проекта на локальном компьютере

Перейти в директорию /infra и создать файл .env:

```bash
cd infra && touch .env
```

- Сборка контейнеров:

* контейнер базы данных db
* контейнер приложения backend
* контейнер веб-сервера nginx

```bash
cd infra docker-compose up -d
```

- Создание и применение миграций:

```bash
docker-compose exec backend python manage.py makemigrations
```

```bash
docker-compose exec backend python manage.py migrate
```

- Собрать статику:

```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

- Заполнение базы данных:

```bash
docker-compose exec backend python manage.py import_ingredients
```

```bash
sudo docker-compose exec backend python manage.py import_tags
```

- Создаем суперпользователя:

```bash
sudo docker-compose exec backend python manage.py import_tags createsuperuser
```

### Запуск проекта на удаленном сервере

- Выполните вход на свой удаленный сервер

* Установите docker на сервер:

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

Создайте на сервере пустой файл docker-compose.production.yml и с помощью редактора nano добавьте в него содержимое из локального docker-compose.production.yml.
Скопируйте файл .env на сервер, в директорию foodgram/.

```bash
mkdir foodgram && cd foodgram
```

```bash
touch docker-compose.production.yml && nano docker-compose.production.yml
```

```bash
touch .env && nano .env
```

```bash
touch nginx.conf && nano nginx.conf
```

## Запускаем контейнеры

Выполните миграции, соберите статические файлы бэкенда

```bash
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Админ:

Email: 1@yandex.ru
Password: admin
Сайт доступен по IP: http://51.250.98.200
