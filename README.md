[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.ya

# Проект «Продуктовый помощник»

Cервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

---

## Ниже представлены доступные адреса проекта:

- http://51.250.98.200 - доступ по IP (временно)
- http://localhost/ - главная страница сайта;
- http://localhost/admin/ - админ панель;
- http://localhost/api/ - API проекта
- http://localhost/api/docs/redoc.html - документация к API

### Для доступа в админ-зону:

- Email: `1@yandex.ru`
- Password: `admin`

---

Скриншот главной страницы сайта
![Скриншот главной страницы сайта](https://github.com/Dron-71/foodgram-project-react/blob/master/foodgram.png)

---

### Для запуска приложения в контейнерах:

- Установите Docker
- Клонируйте репозиторий
  ```
  git clone git@github.com:Dron-71/foodgram-project-react.git
  ```
- Создайте и заполните файл .env (в корне проекта)

---

### Заполнение .env файла:

- POSTGRES_USER=django_user
- POSTGRES_PASSWORD=mysecretpassword
- POSTGRES_DB=django
- DB_HOST=db
- DB_PORT=5432
- ALLOWED_HOSTS=,51.250.98.200,127.0.0.1,localhost
- SECRET_KEY=django_secret_key
- DEBUG=True

---

- Запустите docker-compose:
  ```
  docker-compose up -d --build
  ```
- Выполните миграции:
  ```
  docker-compose exec backend python manage.py migrate
  ```
- Для сбора статики воспользуйтесь командами:
  ```
  docker-compose exec backend python manage.py collectstatic
  ```
  ```
  docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
  ```
- Для загрузки базы данных ингрединтов:
  ```
  docker-compose exec backend python manage.py import_ingredients
  ```
- Для создания или загрузки суперпользователя:
  ```
  docker-compose exec backend python manage.py createsuperuser
  ```
  ```
  docker-compose exec backend python manage.py import_createsuperuser
  ```

---

## Запуск проекта на удаленном сервере

- Выполните вход на свой удаленный сервер

* Установите docker на сервер:

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

Создайте на сервере пустой файл docker-compose.production.yml, и с помощью редактора nano добавьте в него содержимое из локального docker-compose.production.yml.
Скопируйте файл .env на сервер, в директорию foodgram/.

```
mkdir foodgram && cd foodgram
```

```
touch docker-compose.production.yml && nano docker-compose.production.yml
```

```
touch .env && nano .env
```

---

## Запускаем контейнеры

После запуска, выполните миграции и соберите статические файлы бэкенда

```
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

---

### Автор:

[Андрей Л.](https://github.com/Dron-71?tab=repositories) 2023

---

### Визуальное представление:

![Визуальное представление](https://github.com/Dron-71/foodgram-project-react/blob/master/foodgram.gif)
