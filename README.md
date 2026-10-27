# FastAPI + React Template

Готовый шаблон для fullstack-проектов: **FastAPI** (async) + **PostgreSQL** + **fastapi-users** (JWT) + **Vite + React**.
Клонируешь, поднимаешь базу, накатываешь миграцию — и можно писать свои роуты и компоненты.

## 🚀 Стек

**Backend**
- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async) + asyncpg
- PostgreSQL 16 (Docker)
- Alembic (миграции через синхронный `psycopg`)
- fastapi-users 15 (JWT-аутентификация из коробки)
- Pydantic v2 + pydantic-settings

**Frontend**
- Vite
- React

**Инфраструктура**
- Docker / Docker Compose

## 📁 Структура

```
.
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (.env)
│   │   └── users.py         # UserManager, JWT, current_active_user
│   ├── db/
│   │   ├── base.py          # DeclarativeBase
│   │   └── session.py       # Async engine + session factory
│   ├── models/
│   │   └── user.py          # Модель User (SQLAlchemyBaseUserTableUUID)
│   ├── schemas/
│   │   └── user.py          # Pydantic-схемы (UserRead, UserCreate, UserUpdate)
│   └── api/
│       └── routes/          # Сюда добавляй свои роуты
├── alembic/                 # Миграции
├── frontend/                # Vite + React
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Быстрый старт

### 1. Клонировать и создать venv

```bash
git clone <repo-url>
cd <project-name>
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. Настроить `.env`

Скопируй `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполни:

```env
DATABASE_URL=postgresql+asyncpg://app:app_pass@localhost:5433/app_db
SECRET_KEY=change-me-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ `SECRET_KEY` в проде обязательно замени на случайную строку (например, `openssl rand -hex 32`).

### 3. Поднять базу

```bash
docker compose up -d db
```

Подожди, пока `docker ps` не покажет `healthy`.

### 4. Применить миграции

```bash
alembic upgrade head
```

### 5. Запустить бэкенд

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 6. Запустить фронтенд (в отдельном терминале)

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173

Прокси `/api/*` → `http://127.0.0.1:8000` уже настроен в `vite.config.js`, поэтому CORS в dev-режиме не мешает.

## 🔐 Аутентификация (fastapi-users)

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация (`email`, `password`) |
| POST | `/auth/jwt/login` | Логин (**form-data**: `username`=email, `password`) |
| GET | `/users/me` | Текущий пользователь (`Authorization: Bearer <token>`) |
| POST | `/auth/forgot-password` | Запрос сброса пароля |
| POST | `/auth/reset-password` | Сброс пароля по токену |
| POST | `/auth/verify` | Подтверждение email |

### Пример регистрации

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'
```

### Пример логина

```bash
curl -X POST http://127.0.0.1:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=secret123"
```

Ответ:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### Защищённый запрос

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

## 🛡️ Защита своих роутов

В любом своём роуте используй готовую зависимость:

```python
from fastapi import APIRouter, Depends
from app.core.users import current_active_user
from app.models.user import User

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/")
async def get_notes(user: User = Depends(current_active_user)):
    return {"user_id": user.id, "email": user.email}
```

Без валидного Bearer-токена такой роут вернёт `401`.

## 🐳 Docker

`docker-compose.yml` содержит два сервиса:

- `db` — PostgreSQL 16, порт `5433:5432` (внешний:внутренний)
- `api` — FastAPI, порт `8000`, монтирует `./app` для hot-reload

Запустить весь стек:

```bash
docker compose up --build
```

Только базу:

```bash
docker compose up -d db
```

Снести базу вместе с данными:

```bash
docker compose down -v
```

## 🗄️ Миграции (Alembic)

Создать миграцию после изменения моделей:

```bash
alembic revision --autogenerate -m "add notes table"
```

⚠️ **Всегда открывай сгенерированный файл** в `alembic/versions/` и проверяй его. Если в миграции используется `fastapi_users_db_sqlalchemy.generics.GUID()` — добавь в шапку файла:

```python
import fastapi_users_db_sqlalchemy
```

Применить миграции:

```bash
alembic upgrade head
```

Откатить последнюю:

```bash
alembic downgrade -1
```

## ⚠️ Известные нюансы

- **SQLAlchemy зафиксирован на `2.0.55`.** Версия 2.1.x ломает `fastapi-users` с `MappedAnnotationError`. Не обновляй без проверки.
- **Два драйвера PostgreSQL** — это нормально:
  - `asyncpg` — для приложения (асинхронный);
  - `psycopg` — для Alembic (синхронный, миграции — одноразовая операция).
- **При генерации миграций** с `fastapi-users` может понадобиться ручной `import fastapi_users_db_sqlalchemy` (Alembic не всегда добавляет его сам).
- **Windows + asyncpg**: если ловишь `WinError 64` / `ConnectionDoesNotExistError`, проверь, что локальный PostgreSQL не занимает порт `5432` — отсюда маппинг на `5433`.
- **venv нельзя переносить** между папками — при переносе проекта создавай заново (`python -m venv venv` + `pip install -r requirements.txt`).

## 📝 TODO для развития шаблона

- [ ] Страница логина/регистрации на React
- [ ] Защищённые роуты на фронте (React Router + guard)
- [ ] Aiogram-бот, стучащийся в API
- [ ] Nginx + Dockerfile для фронта (multi-stage build)
- [ ] Тесты (pytest + httpx AsyncClient)
- [ ] CI/CD (GitHub Actions: lint + test + build)
- [ ] Rate limiting (Redis)
- [ ] OpenTelemetry / Sentry

## 📄 Лицензия

MIT — используй как хочешь.
