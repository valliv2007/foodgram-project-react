# Project Grocery Assistant (Foodgram)
### Description of the project:
"Grocery Assistant" is a website where you can publish your own recipes, add other people's recipes to favorites, subscribe to other authors and create a shopping list for the chosen meals. Here's what was done during the work on the project:
configured interaction of a Python application with external API services;
created a custom API service based on the Django project;
connected SPA to the backend on Django via API;
created images and launched Docker containers;
created multi-container applications, deployed and launched on the server;
### Tools and stack:
Python 3.7.9, Django 2.2.19, djangorestframework 3.12.4, Pillow 8.3.1, PyJWT 2.6.0, gunicorn 20.0.4,
frontend  made by JavaScript  with React.
### How to launch a project:
Download and start Docker 
https://www.docker.com/products/docker-desktop
Copy folder "infra" from this  repo 
Make inside the folder env file  with your sample data  like as a sample below:
```sh
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres # DB name 
POSTGRES_USER=postgres # DB login
POSTGRES_PASSWORD=password # DB password (make your own)
DB_HOST=db # container name
DB_PORT=5432 # DB port,default=5432
SECRET_KEY = '***********************'# your secret key Django
```
From this folder run next commands:
```sh
docker-compose up --build # expand the containers in the new structure
docker exec web python manage.py migrate # apply migrations
docker exec web python manage.py createsuperuser # create superuser
docker exec web python manage.py collectstatic --no-input # collect static
```
And launch the project on  http://localhost/
