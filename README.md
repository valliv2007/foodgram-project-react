# Проект Продуктовый помощник (Foodgram)
### Описание проекта:
В проекте Foodgram пользователи могут создать и редактировать  свои рецепты, заходить на страницы других пользователей и подписываться на других пользователей, добавлять рецепты в избранное и в список покупок, скачивать файл с необходимыми ингредиентами для рецептов из списка покупок. Рецепты можно отфильтровать по тэгам.
### Технологии:
Python 3.7.9, Django 2.2.19, djangorestframework 3.12.4, Pillow 8.3.1, PyJWT 2.6.0, gunicorn 20.0.4,
frontend  выполнен на JavaScript c использованием React.
### Проект размещен:
http://158.160.47.246/ логин: admin, пароль: admin
### Как запустить проект:
Установить и запустить Docker 
https://www.docker.com/products/docker-desktop
Скопировать из данного репозитория папку infra
Создать внутри папки env файл со своими данными по образцу:
```sh
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД, по умолчанию 5432
SECRET_KEY = '***********************'# ваш секретный ключ Django
```
Из данной папки выполните следующие команды:
```sh
docker-compose up --build # разверните контейнеры в новой структуре
docker exec web python manage.py migrate # выполните миграции
docker exec web python manage.py createsuperuser # создайте суперпользователя
docker exec web python manage.py collectstatic --no-input # соберите статику
```
Проект будет доступен на http://localhost/
