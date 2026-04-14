# Backend (Django + DRF)

## Quick Start

```bash
cd /code/crm/backend
python3 -m pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py seed_demo
python3 manage.py runserver 0.0.0.0:8000 --noreload
```

## Demo Accounts

- admin: `admin` / `admin123`
- customer: `customer` / `customer123`

## API

- POST `/api/auth/login`
- POST `/api/auth/refresh`
- GET `/api/auth/me`
- GET `/api/customers/`
- GET `/api/orders/`
- GET `/api/confirmations/`
- GET `/api/files/`
- GET `/api/logistics/`
- GET `/api/messages/`

## Database

- Default: SQLite (development)
- Optional MySQL: set `DB_ENGINE=mysql` and related `MYSQL_*` vars from `.env.example`
