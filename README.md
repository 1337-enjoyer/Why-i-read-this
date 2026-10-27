# Why I Read This

Пет-проект: читает случайные статьи из Википедии через API и показывает их на своём сайте (без редиректа). Авторизованные пользователи видят историю прочитанного.

## 🚀 Стек

**Backend:** FastAPI, SQLAlchemy 2.0 (async), asyncpg, PostgreSQL 16, Alembic, fastapi-users (JWT), httpx, Pydantic v2
**Frontend:** Vite, React
**Инфра:** Docker Compose

## 📁 Структура

```
.
├── app/
│   ├── main.py
│   ├── core/          # config, users (fastapi-users)
│   ├── db/            # base, session
│   ├── models/        # user, read_article
│   ├── schemas/       # user
│   └── api/routes/    # wiki (random, history, article)
├── alembic/
├── frontend/          # Vite + React
├── docker-compose.yml
└── requirements.txt
```

## ⚙️ Запуск

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env    # заполни DATABASE_URL, SECRET_KEY

docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

Фронт (в отдельном терминале):

```bash
cd frontend
npm install
npm run dev
```

- Backend: http://127.0.0.1:8000/docs
- Frontend: http://localhost:5173

## 🔌 API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/wiki/random` | Случайная статья (гость) |
| GET | `/wiki/random/auth` | Случайная статья + сохранить в историю |
| GET | `/wiki/article/{page_id}` | Статья по ID (из истории) |
| GET | `/wiki/history` | История текущего юзера |
| DELETE | `/wiki/history` | Очистить историю |
| POST | `/auth/register` | Регистрация |
| POST | `/auth/jwt/login` | Логин (form-data) |
| GET | `/users/me` | Текущий юзер (Bearer) |

## 🎨 Фронт

- Главная: кнопка «Случайная статья», картинка + текст.
- Гость: может читать без авторизации.
- Авторизованный: слева сайдбар с историей, клик открывает статью, кнопка очистки истории.
- Стили в `src/styles/` (`global.css`, `app.css`, `auth.css`), адаптив ≤768px / ≤480px.
