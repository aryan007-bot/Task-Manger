# Smart Task Management System

A production-grade task management system built with Python/Flask, PostgreSQL, real-time WebSockets, Pandas analytics, and a responsive TailwindCSS UI.

## Features

- **JWT Authentication** — register, login, protected routes
- **Full Task CRUD** — create, read, update, delete with validation
- **Analytics Dashboard** — Pandas + NumPy powered insights (completion %, trends, priority distribution)
- **Real-time Updates** — Flask-SocketIO broadcasts on task create/update/delete
- **Responsive UI** — TailwindCSS + Chart.js dashboard, dark mode, mobile-ready
- **Pagination, Filtering, Sorting, Search** — all task list endpoints
- **Production-ready** — Gunicorn-compatible, security headers, env-based config, Docker support

## Tech Stack

| Layer        | Technology                                    |
|-------------|-----------------------------------------------|
| Backend     | Python 3.12, Flask 3, Flask-SocketIO          |
| Auth        | Flask-JWT-Extended, Werkzeug password hashing |
| Database    | PostgreSQL, SQLAlchemy ORM, Flask-Migrate     |
| Analytics   | Pandas, NumPy                                 |
| Frontend    | HTML5, TailwindCSS (CDN), Vanilla JS, Chart.js|
| Templates   | Jinja2                                        |
| Production  | Gunicorn + Eventlet, Docker                   |

## Project Structure

```
task-manager/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # Flask extensions (db, jwt, socketio)
│   ├── config/config.py     # Environment-based configuration
│   ├── models/
│   │   ├── user_model.py
│   │   └── task_model.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── task_routes.py
│   │   ├── analytics_routes.py
│   │   └── frontend_routes.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   └── analytics_service.py
│   ├── sockets/socket_events.py
│   ├── middleware/auth_middleware.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── response_handler.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       └── dashboard.html
├── tests/
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_analytics.py
├── run.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Environment Variables

| Variable        | Description                        | Default              |
|-----------------|------------------------------------|--------------------- |
| `DATABASE_URL`  | PostgreSQL connection string       | (required)           |
| `SECRET_KEY`    | Flask session secret               | change-me            |
| `JWT_SECRET_KEY`| JWT signing secret                 | change-me            |
| `FLASK_ENV`     | `development` / `production`       | `development`        |
| `PORT`          | HTTP port                          | `8080`               |

## Installation (Local)

```bash
# 1. Clone and enter the directory
cd task-manager

# 2. Create a virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env .env.local
# Edit .env.local and set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY

# 5. Run
python run.py
```

## Docker

```bash
# Build and start all services (PostgreSQL + web)
docker-compose up --build

# App will be available at http://localhost:8080
```

## API Reference

### Authentication

| Method | Endpoint              | Description      | Auth required |
|--------|-----------------------|------------------|---------------|
| POST   | `/api/auth/register`  | Register user    | No            |
| POST   | `/api/auth/login`     | Login            | No            |
| POST   | `/api/auth/logout`    | Logout           | Yes           |
| GET    | `/api/auth/me`        | Current user     | Yes           |

### Tasks

| Method | Endpoint              | Description      | Query Params                              |
|--------|-----------------------|------------------|-------------------------------------------|
| GET    | `/api/tasks`          | List tasks       | `page`, `per_page`, `status`, `priority`, `search`, `sort_by`, `sort_order` |
| POST   | `/api/tasks`          | Create task      | —                                         |
| GET    | `/api/tasks/<id>`     | Get task         | —                                         |
| PUT    | `/api/tasks/<id>`     | Update task      | —                                         |
| DELETE | `/api/tasks/<id>`     | Delete task      | —                                         |

### Analytics

| Method | Endpoint         | Description                  |
|--------|------------------|------------------------------|
| GET    | `/api/analytics` | Dashboard analytics (Pandas) |

### WebSocket (Socket.IO)

Connect to namespace `/tasks`. Events emitted by the server:

| Event          | Payload           | Trigger                 |
|----------------|-------------------|-------------------------|
| `connected`    | `{message}`       | On connect              |
| `task_created` | task dict         | New task saved          |
| `task_updated` | task dict         | Task updated            |
| `task_deleted` | `{id}`            | Task deleted            |

Client can emit `join` with `{room: "global"}` to subscribe to room-based updates.

## Running Tests

```bash
cd task-manager
pytest tests/ -v
```

## Production Deployment

```bash
# Using Gunicorn with Eventlet (required for SocketIO)
gunicorn -k eventlet -w 1 -b 0.0.0.0:8080 "run:app"
```

> **Note:** Use `-w 1` (single worker) with Eventlet/Gevent for correct SocketIO behavior.

## Security Notes

- Passwords hashed with Werkzeug's `pbkdf2:sha256`
- JWT tokens expire after 1 hour
- Security headers set on every response (X-Content-Type-Options, X-Frame-Options, XSS protection)
- All inputs validated and sanitized before hitting the database
- SQLAlchemy ORM prevents SQL injection by design
- Secrets never hardcoded — always read from environment
