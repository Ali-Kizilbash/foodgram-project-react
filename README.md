## Описание

Онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

buminkaan.ddns.net

---
## База данных и переменные окружения

Проект использует базу данных PostgreSQL.  
Для подключения и выполнения запросов к базе данных необходимо создать файл ".env" с переменными окружения в корневой директории.

Шаблон файла ".env":
```python
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Секретный ключ Django'
ALLOWED_HOSTS='Список разрешенных хостов'
```

---
## Запуск в Docker-контейнерах

Склонируйте проект и перейдите в директорию "./infra/" и выполните команду:
```bash
docker compose up --build -d
```
Проект будет развёрнут в четырёх контейнерах: db, backend, frontend, nginx

После успешного запуска контейнеров выполните миграции:
```bash
docker compose exec backend python3 manage.py migrate
```

Создайте суперпользователя (при необходимости):
```bash
docker compose exec -it backend bash
python3 manage.py createsuperuser
```

---
## Заполнение базы данных

С проектом поставляются данные ингредиентов и тегов.  
Заполнить базу можно выполнив следующую команду:
```bash
docker compose exec backend python3 manage.py import_json
```

## Стек технологий

* Python 3.9,
* Django
* Django Rest Framework
* React
* Docker
* PostgreSQL
* nginx
* gunicorn
