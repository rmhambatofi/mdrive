# CLAUDE.md — MDrive Project Guide

## Project Overview

MDrive is a full-stack cloud storage application (Google Drive-like) built with:
- **Backend**: Python/Flask REST API with MySQL
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Infrastructure**: Docker Compose (MySQL + Flask + Nginx)

---

## Architecture

### Backend (`backend/`)
```
app/
├── __init__.py          # Flask app factory
├── config.py            # Dev/Prod configuration classes
├── controllers/         # Request handlers (auth, file)
├── middleware/          # JWT auth decorator
├── models/              # SQLAlchemy ORM (User, File)
├── routes/              # Flask Blueprints (/api/auth, /api/files)
├── services/            # Business logic (auth, file, storage)
└── utils/               # Validators and helpers
```

Pattern: **Routes → Controllers → Services → Models**

### Frontend (`frontend/src/`)
```
components/
├── Auth/          # Login, Register
├── FileManager/   # FileList, FileUpload
├── Layout/        # Navbar, Sidebar
└── Common/        # Breadcrumb, Modals, PrivateRoute
contexts/          # AuthContext (global auth state)
services/          # Axios API clients (auth, file)
pages/             # Dashboard
```

Pattern: **Context API for state, Axios interceptors for JWT**

---

## Tech Stack

| Layer | Tech | Version |
|-------|------|---------|
| Backend | Flask | 3.0.0 |
| ORM | SQLAlchemy | 3.1.1 |
| DB | MySQL | 8.0 |
| Auth | Flask-JWT-Extended | 4.6.0 |
| Passwords | bcrypt | 4.1.2 |
| Migrations | Flask-Migrate | 4.0.5 |
| Frontend | React | 18.2.0 |
| Build | Vite | 5.0.7 |
| Routing | React Router DOM | 6.20.0 |
| HTTP | Axios | 1.6.2 |
| CSS | Tailwind CSS | 3.3.6 |
| Icons | Lucide React | 0.294.0 |

---

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python init_db.py              # Initialize database
python run.py                  # Dev server on port 5000
pytest tests/                  # Run tests
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # Dev server on port 3000 (proxy → port 5000)
npm run build      # Build to dist/
```

### Docker (full stack)
```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
docker exec -it mdrive-backend python init_db.py
```

---

## Environment Variables

### Backend (`backend/.env`)
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mdrive
DB_USER=root
DB_PASSWORD=your_password
JWT_SECRET_KEY=secret
JWT_ACCESS_TOKEN_EXPIRES=86400     # 24h in seconds
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=flask-secret
MAX_FILE_SIZE=104857600            # 100MB
UPLOAD_FOLDER=userdata
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,png,jpg,jpeg,gif,zip,rar,mp4,mp3
DEFAULT_STORAGE_QUOTA=5368709120   # 5GB
```

### Frontend (`frontend/.env`)
- Dev proxy: `/api` → `http://localhost:5000` (configured in `vite.config.js`)
- Production: see `frontend/.env.production`

---

## Database Schema

### Users
- `uuid` (PK), `email` (unique), `password_hash`, `full_name`
- `storage_quota` (default 5GB), `storage_used`

### Files
- `uuid` (PK), `user_uuid` (FK), `parent_folder_uuid` (self-ref for nested folders)
- `file_name`, `file_path`, `file_size`, `mime_type`, `is_folder`
- Indexes on `(user_uuid, parent_folder_uuid)` and `(user_uuid, is_folder)`

---

## Key API Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/profile        # JWT required
PUT    /api/auth/profile        # JWT required

GET    /api/files               # List files (query: ?folder_uuid=)
GET    /api/files/<uuid>
POST   /api/files/upload        # Multipart, max 100MB
GET    /api/files/download/<uuid>
DELETE /api/files/<uuid>
POST   /api/files/folder        # Create folder
PUT    /api/files/<uuid>/rename
```

All file endpoints require `Authorization: Bearer <jwt_token>` header.

---

## Security Conventions
- **Never** use auto-increment IDs — always UUIDs
- **Always** use SQLAlchemy ORM (no raw SQL)
- **Always** validate file extensions against the whitelist
- **Always** check storage quota before upload
- Protect against path traversal in file paths
- Use parameterized queries (already enforced by SQLAlchemy)

---

## Code Conventions

### Python (Backend)
- Type hints on all functions
- Docstrings for all public functions and classes
- Error responses format: `{"error": "message"}` with appropriate HTTP status
- Success responses: `{"data": ..., "message": "..."}` or resource object
- Services return `(result, error)` or raise exceptions — controllers catch and respond

### JavaScript (Frontend)
- Functional components with React hooks only
- Async/await for all API calls
- Services in `src/services/` handle all HTTP calls (never `fetch` directly in components)
- Tailwind classes for all styling (no custom CSS unless necessary)

---

## Deployment

See dedicated docs:
- [DEPLOYMENT.md](DEPLOYMENT.md) — Docker / VPS / Cloud
- [DEPLOYMENT_CPANEL.md](DEPLOYMENT_CPANEL.md) — Shared hosting (cPanel)
- [TROUBLESHOOTING_DASHBOARD.md](TROUBLESHOOTING_DASHBOARD.md) — Common issues

### Quick Production Checklist
- Change `JWT_SECRET_KEY` and `SECRET_KEY` to strong random values
- Set `FLASK_ENV=production`
- Set `DB_PASSWORD` to a strong password
- Configure Nginx/Apache for HTTPS
- Run `flask db upgrade` for migrations

---

## File Storage

User files are stored in `backend/userdata/<user_uuid>/<uuid>.<ext>`.
Never expose raw filesystem paths in API responses — use UUIDs only.

---

## Testing

```bash
cd backend
pytest tests/           # All tests
pytest tests/test_auth.py  # Auth tests only
```

Tests use pytest with Flask test client. See `backend/pytest.ini` for config.
