#!/usr/bin/env bash
set -e

# --- wait for DB if Postgres is used ---
if [ "${DB_ENGINE:-sqlite}" = "postgres" ]; then
  echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT}..."
  until nc -z "${DB_HOST}" "${DB_PORT}"; do
    sleep 1
  done
fi

# --- Django manage dir ---
cd /app/project

# Collect static (если нужно для prod)
# python manage.py collectstatic --noinput

# Migrations
python manage.py migrate --noinput

# Create superuser (admin / admin) if it doesn't exist
echo "from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
" | python manage.py shell

# Seed (опционально, по флагу)
if [ "${SEED_DEMO}" = "true" ]; then
  echo "Seeding demo data..."
  python manage.py seed_demo --flush --pages 20 --videos 12 --audios 12 --min-items 2 --max-items 5 --seed 42
fi

# Run the server (gunicorn для prod; runserver локально)
if [ "${RUNSERVER}" = "true" ]; then
  echo "Starting Django development server..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "Starting gunicorn..."
  exec gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
