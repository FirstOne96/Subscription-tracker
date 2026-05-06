# 📦 Subscription Management API

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.2-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.29.0-Informational?logo=uvicorn)](https://www.uvicorn.org/)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-Cloud-success?logo=mongodb)](https://www.mongodb.com/atlas)
[![Redis](https://img.shields.io/badge/Redis-InMemoryDB-ff0000?logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-Async-orange?logo=celery)](https://docs.celeryq.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-Testing-yellow?logo=pytest)](https://docs.pytest.org/)
[![Railway](https://img.shields.io/badge/Railway-Hosting-purple?logo=railway)](https://railway.app/)

A production-ready REST API for managing user subscriptions, with JWT authentication, automated reminder emails scheduled via background workers, and per-route rate limiting. Built in Python with FastAPI.

**Live API:** https://web-production-bba32.up.railway.app/  
**Interactive docs (Swagger UI):** https://web-production-bba32.up.railway.app/docs

> _This project is a Python reimplementation of [Adrian Hajdin's subscription-tracker-api](https://github.com/adrianhajdin/subscription-tracker-api), which was originally built in JavaScript with Express, MongoDB, and more._

---

## 💡 What this app does

A signed-up user can create subscriptions (Netflix, Spotify, gym membership, etc.) with a name, price, frequency, and start date. The app automatically computes when the subscription will renew based on this info, and sends email reminders a few days before.

The reminders aren't sent during the API request that creates the subscription; that would be impossible (the request finishes in milliseconds, but the reminder isn't due for days). Instead, the API enqueues a background job to send a reminder email at the right time.

---

## 🛠️ Tech stack

| Layer                | Technology                              | Purpose                                                    |
| -------------------- | --------------------------------------- | ---------------------------------------------------------- |
| Web framework        | **FastAPI**                             | Async HTTP routing, request/response validation, OpenAPI   |
| ASGI server          | **Uvicorn** (workers managed by Gunicorn) | Production process management                            |
| MongoDB ODM          | **Beanie** (built on Motor)             | Async typed document models with lifecycle hooks           |
| Validation           | **Pydantic v2**                         | Request/response schemas, settings management              |
| Auth                 | **python-jose + passlib (bcrypt)**      | JWT signing/verification, password hashing                 |
| Rate limiting        | **SlowAPI**                             | Per-IP token-bucket limiting on auth routes                |
| Background jobs      | **Celery + Redis**                      | Scheduled email reminders                                  |
| Email                | **FastAPI-Mail**                        | Async SMTP via Gmail                                       |
| Database             | **MongoDB Atlas**                       | Hosted document database                                   |
| Hosting              | **Railway**                             | Deployment for web + worker + Redis                        |
| Testing              | **pytest + pytest-asyncio**             | Integration tests for model hooks                          |

---

## 🏛️ Architecture

The application is composed of three independent services that communicate through MongoDB and Redis:

```
┌──────────────┐     HTTP      ┌─────────────────┐
│   Client     │ ────────────► │  FastAPI (web)  │
│  (browser,   │               │  - Gunicorn     │
│   curl, etc) │ ◄──────────── │  - 2 workers    │
└──────────────┘     JSON      └────────┬────────┘
                                        │
                                        │ (1) insert
                                        ▼
                               ┌─────────────────┐
                               │  MongoDB Atlas  │
                               └────────┬────────┘
                                        │
                                        │ (2) read on read endpoints
                                        ▼
                               ┌─────────────────┐
                               │  FastAPI (web)  │
                               └────────┬────────┘
                                        │
                                        │ (3) enqueue job
                                        ▼
                               ┌─────────────────┐
                               │     Redis       │
                               │  (broker)       │
                               └────────┬────────┘
                                        │
                                        │ (4) poll, get task
                                        ▼
                               ┌─────────────────┐
                               │ Celery worker   │     SMTP
                               │ - 2 concurrency │ ─────────► Gmail
                               │ - schedules &   │
                               │   sends emails  │
                               └─────────────────┘
```

### 🤔 Why three services?

The web service handles HTTP requests and finishes them quickly. It can't be the one that "waits 7 days then sends an email" — there'd be nothing waiting; FastAPI requests don't persist that long. The Celery worker handles that.

---

## 📂 Project structure

```
Subscription-Management-System/
├── app.py                          # FastAPI factory, lifespan, middleware, router registration
├── Procfile                        # Railway: web + worker process definitions
├── runtime.txt                     # Pinned Python version for deployment
├── requirements.txt                # All pinned dependencies
├── pytest.ini                      # pytest-asyncio config
│
├── config/
│   ├── env.py                      # Typed pydantic-settings singleton
│   ├── database.py                 # Motor client + Beanie init
│   ├── mail.py                     # FastAPI-Mail ConnectionConfig
│   └── celery_app.py               # Celery app instance
│
├── models/
│   ├── user.py                     # Beanie Document: User
│   └── subscription.py             # Beanie Document: Subscription + lifecycle hooks
│
├── schemas/
│   ├── auth.py                     # SignUpRequest, SignInRequest, AuthResponse
│   ├── user.py                     # UserPublic (password-free)
│   └── subscription.py             # SubscriptionCreate, SubscriptionResponse
│
├── routers/
│   ├── auth.py                     # /api/v1/auth (sign-up, sign-in, sign-out)
│   ├── users.py                    # /api/v1/users
│   ├── subscriptions.py            # /api/v1/subscriptions
│   └── workflows.py                # /api/v1/workflows (manual reminder trigger)
│
├── controllers/
│   ├── auth.py                     # sign_up, sign_in, sign_out
│   ├── users.py                    # get_users, get_user
│   ├── subscriptions.py            # full CRUD + cancel + upcoming-renewals
│   └── workflows.py                # send_reminders
│
├── middleware/
│   ├── auth.py                     # FastAPI Depends: JWT Bearer → current_user
│   ├── rate_limit.py               # SlowAPI Limiter
│   └── error_handler.py            # Exception handlers (400/401/404/422/500)
│
├── tasks/
│   └── reminder.py                 # Celery: schedule_reminders, send_reminder_email_task
│
├── utils/
│   ├── jwt.py                      # JWT encoding + expiry-string parser
│   ├── send_email.py               # Async send_reminder_email
│   └── email_templates.py          # 7/5/2/1-day reminder templates
│
└── tests/
    ├── conftest.py                 # Test DB fixtures
    ├── test_models/
    │   ├── test_subscription.py    # Lifecycle hook tests
    │   └── test_users.py           # User interaction tests
    ├── test_api/
    │   ├── test_auth.py            # Authentification tests
    |   ├── test_subscriptions.py   # Subscriptions tests
    |   └── tests_users.py          # Users tests
    └── test_schemas/
        ├── test_auth_schemas.py            # Authentification schemas tests
        └── test_subscriptions_schemas.py   # Subscriptions schemas tests

```

---

## 📚 API reference

All endpoints are prefixed with `/api/v1`. Full interactive documentation is available at `/docs` on the live deployment.

### 🔐 Auth (`/api/v1/auth`)

| Method | Path        | Description                       | Auth | Rate limit          |
| ------ | ----------- | --------------------------------- | ---- | ------------------- |
| POST   | `/sign-up`  | Create user, return JWT           | —    | 5 / 10 seconds / IP |
| POST   | `/sign-in`  | Verify password, return JWT       | —    | 5 / 10 seconds / IP |
| POST   | `/sign-out` | Stub (token discarded client-side)| —    | —                   |

### 👤 Users (`/api/v1/users`)

| Method | Path           | Description              | Auth |
| ------ | -------------- | ------------------------ | ---- |
| GET    | `/`            | List all users           | —    |
| GET    | `/{user_id}`   | Get one user (no password)| ✓   |
| POST   | `/`            | _501 Not Implemented_    | —    |
| PUT    | `/{user_id}`   | _501 Not Implemented_    | —    |
| DELETE | `/{user_id}`   | _501 Not Implemented_    | —    |

### 📄 Subscriptions (`/api/v1/subscriptions`)

| Method | Path                    | Description                                         | Auth |
| ------ | ----------------------- | --------------------------------------------------- | ---- |
| GET    | `/upcoming-renewals`    | Active subs renewing within 7 days                  | —    |
| GET    | `/user/{user_id}`       | Subs for a specific user (ownership check enforced) | ✓    |
| GET    | `/`                     | List all subscriptions                              | —    |
| GET    | `/{sub_id}`             | Get one subscription                                | —    |
| POST   | `/`                     | Create subscription, enqueue reminder schedule      | ✓    |
| PUT    | `/{sub_id}/cancel`      | Set status to "cancelled"                           | —    |

### 🛠️ Workflows (`/api/v1/workflows`)

| Method | Path                     | Description                                  | Auth |
| ------ | ------------------------ | -------------------------------------------- | ---- |
| POST   | `/subscription/reminder` | Manually re-enqueue reminders for a sub      | —    |

_Swagger UI auto-generated from FastAPI's type annotations and Pydantic schemas._
<img width="900" height="600" alt="image" src="https://github.com/user-attachments/assets/8bce5a23-cc6c-45f3-a101-07e2a27ac181" />

---

## 🖥️ Running locally

### ⚙️ Prerequisites

- Python 3.12
- A MongoDB Atlas account (free tier is fine)
- Redis (run via Docker, native install, or a managed provider)
- A Gmail account with an [app password](https://myaccount.google.com/apppasswords) generated for SMTP

### 🔧 Setup

```bash
# Clone and enter the project
git clone https://github.com/FirstOne96/Subscription-tracker.git
cd Subscription-tracker

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env.development.local` at the project root (it's gitignored — never commit secrets):

```
PORT=8000
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/subscription_db?retryWrites=true&w=majority
JWT_SECRET=<generate with: python -c "import secrets; print(secrets.token_urlsafe(64))">
JWT_EXPIRES_IN=1d
REDIS_URL=redis://localhost:6379/0
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=<your 16-character Gmail app password, no spaces>
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
ALLOWED_ORIGINS=
```

### 🗄️ Start Redis

If you have Docker:
```bash
docker run -d --name redis -p 6379:6379 --restart unless-stopped redis
```

Verify it's reachable: `redis-cli ping` should return `PONG`.

### 🚀 Run the application

You'll need three things running. Open three terminals (or one with tmux/split panes):

**Terminal 1 — Redis** (already running in the background if you used `--restart unless-stopped` above)

**Terminal 2 — FastAPI:**
```bash
uvicorn app:app --reload --port 8000
```

**Terminal 3 — Celery worker:**
```bash
celery -A config.celery_app worker --loglevel=info --concurrency=2
```

Visit http://localhost:8000/docs to interact with the API.

---

## ✅ Running tests

```bash
pytest tests/ -v
```

The tests run against a separate `subscription_db_test` database in your Atlas cluster. The database is dropped at the end of each session.

---

## ☁️ Deployment

The live deployment is on **Railway**, with three services:

1. **Web service** — runs `gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
2. **Worker service** — runs `celery -A config.celery_app worker --loglevel=info --concurrency=2`
3. **Redis service** — Railway-managed, referenced via `${{ Redis.REDIS_URL }}`

Both web and worker services pull from the same GitHub repository, with different start commands. They share the same environment variables (set independently on each service in Railway's dashboard, securely).

MongoDB Atlas hosts the production database (`subscription_db_prod`), with network access opened to `0.0.0.0/0` (still gated by the database password).

_Three services running on Railway: web (FastAPI + Gunicorn), worker (Celery), and Redis (broker)._
<img width="812" height="517" alt="image" src="https://github.com/user-attachments/assets/bc9de4bc-f2ac-4765-88c4-830ffe938e30" />

_Two production databases: `subscription_db_prod` (deployed) and `subscription_db` (local development)._
<img width="240" height="260" alt="image" src="https://github.com/user-attachments/assets/a2dd75e7-d7b4-4473-b587-053f86188e2f" />

---

> The original JavaScript version of this project (Express + Mongoose + Upstash QStash + Arcjet + Nodemailer) is at https://github.com/adrianhajdin/subscription-tracker-api.
> 
> The companion video tutorial is at https://www.youtube.com/watch?v=rOpEN1JDaD0.

---

## 📞 Contact

Andrii Kozlov - andrijkozlov96@gmail.com  | https://t.me/AndrewKozz | https://www.linkedin.com/in/andrii
