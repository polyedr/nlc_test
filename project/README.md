# NLC Test — Django + DRF (+ Celery)

Мини-API на Django/DRF с моделями `Page`, `Video`, `Audio` и связками `PageContent`.  
Детальный эндпоинт страницы возвращает контент в заданном порядке и **инкрементирует** счётчики просмотров у привязанных объектов (атомарно, в фоне через Celery или синхронно в EAGER-режиме).

## Содержимое

- [Требования](#требования)
- [Быстрый старт (локально)](#быстрый-старт-локально)
- [.env — конфигурация](#env--конфигурация)
- [PostgreSQL — создание пользователя и БД](#postgresql--создание-пользователя-и-бд)
- [Redis — брокер для Celery](#redis--брокер-для-celery)
- [Миграции, суперпользователь, запуск](#миграции-суперпользователь-запуск)
- [Демоданные](#демоданные)
- [API](#api)
- [Админка](#админка)
- [Celery: фоновые инкременты](#celery-фоновые-инкременты)
- [Тесты](#тесты)

---

## Требования

- Python 3.12
- Django 5.2, DRF 3.15
- (По желанию) PostgreSQL 14+ (проверял локально на версии PostgreSQL 17.5)
- (По желанию) Redis 5+ (для фонового исполнения задач Celery)

> Для простого запуска достаточно SQLite и «синхронного» режима Celery.

---

## Быстрый старт (локально)

```bash
# 1) Клонируем репозиторий
git clone <repo-url> nlc_test
cd nlc_test

# 2) Создаём и активируем виртуальное окружение (пример для Linux/macOS)
python3.12 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

# 3) Ставим зависимости
pip install -r requirements.txt

# 4) Переходим в папку с manage.py
cd project

# 5) Создаём .env (см. ниже)
cp .env.example .env    # если есть example; иначе создайте .env вручную

# 6) Миграции + суперпользователь + запуск сервера
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте:
- API список: http://127.0.0.1:8000/api/pages/
- Админка: http://127.0.0.1:8000/admin/

---

## .env — конфигурация

Файл `.env` лежит рядом с `manage.py` (в папке `project/`).  
Пример для **Postgres + Redis**:

```dotenv
# Django
DJANGO_SECRET_KEY=super-secret-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# DB: Postgres
DB_ENGINE=postgres
DB_NAME=nlc_db
DB_USER=nlc_user
DB_PASSWORD=nlc_password
DB_HOST=localhost
DB_PORT=5432

# Celery (фоновость)
CELERY_TASK_ALWAYS_EAGER=False
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

**Простой режим (SQLite + Celery eager):**
```dotenv
DJANGO_SECRET_KEY=dev
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# SQLite: просто не указываем DB_ENGINE
CELERY_TASK_ALWAYS_EAGER=True
CELERY_BROKER_URL=memory://
CELERY_RESULT_BACKEND=
```

---

## PostgreSQL — создание пользователя и БД

```sql
-- в psql под суперпользователем postgres
CREATE USER nlc_user WITH PASSWORD 'nlc_password';
CREATE DATABASE nlc_db OWNER nlc_user;

-- убедимся, что схема public принадлежит юзеру
\c nlc_db
ALTER SCHEMA public OWNER TO nlc_user;
GRANT ALL ON SCHEMA public TO nlc_user;
GRANT ALL PRIVILEGES ON DATABASE nlc_db TO nlc_user;
```

---

## Redis — брокер для Celery

```bash
sudo apt-get update && sudo apt-get install -y redis-server
sudo systemctl enable --now redis-server
redis-cli ping  # ожидаем "PONG"
```

Python-клиент:
```bash
pip install redis==5.*
```

---

## Миграции, суперпользователь, запуск

```bash
cd project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Демоданные

```bash
# Очистить старые и создать новые
python manage.py seed_demo --flush

# Пример с параметрами
python manage.py seed_demo \
  --flush \
  --pages 37 \
  --videos 20 \
  --audios 20 \
  --min-items 2 \
  --max-items 5 \
  --seed 42
```

---

## API

- `GET /api/pages/` — список страниц (пагинация, по умолчанию 5 на страницу).  
- `GET /api/pages/<id>/` — детальная страница, контент в порядке `position`.  
  **Каждый вызов увеличивает счётчики у привязанного контента.**

Примеры:
```bash
curl http://127.0.0.1:8000/api/pages/
curl "http://127.0.0.1:8000/api/pages/?page=2&page_size=3"
curl http://127.0.0.1:8000/api/pages/1/
```

---

## Админка

- Pages: поиск по `title` (начало строки). В карточке Page — inline блок PageContent (можно добавлять/сортировать контент).  
- Videos / Audios: поиск по `title`, виден `counter`.  

---

## Celery: фоновые инкременты

- **Вариант 1 (просто):** синхронно в процессе  
  ```dotenv
  CELERY_TASK_ALWAYS_EAGER=True
  CELERY_BROKER_URL=memory://
  CELERY_RESULT_BACKEND=
  ```

- **Вариант 2 (фон):** через Redis  (проверял локально)
  ```dotenv
  CELERY_TASK_ALWAYS_EAGER=False
  CELERY_BROKER_URL=redis://localhost:6379/0
  CELERY_RESULT_BACKEND=redis://localhost:6379/1
  ```

  Запуск воркера (из папки project/):
  ```bash
  celery -A project worker -l info
  ```

---

## Тесты

Для тестов есть `project/settings_test.py` (SQLite + Celery eager).  
`pytest.ini` указывает `DJANGO_SETTINGS_MODULE=project.settings_test`.

Запуск:
```bash
cd project
pytest
```

Покрыто:
- список страниц (`test_pages_list.py`);
- детальная страница + инкремент (`test_page_detail.py`).

---
