# Notes App

A Django-based notes application for creating, editing, deleting, and organizing personal notes with optional image attachments. The app uses PostgreSQL for data storage, AWS S3 for media uploads, and Django authentication for user accounts.

## Features

- User registration and login
- Create, view, update, and delete notes
- Attach one or more images to each note
- Secure note access per authenticated user
- PostgreSQL database support
- S3-compatible media storage for uploaded files
- Clean Django admin integration

## Tech Stack

- Python 3
- Django 6
- PostgreSQL
- Redis
- Docker & Docker Compose
- Django REST Framework
- drf-spectacular (Swagger / OpenAPI)
- Django Storages & boto3
- Pillow
- Python-dotenv

## Running with Docker Compose

The easiest way to run the application with a dedicated local PostgreSQL database and Redis cache is via Docker Compose:

1. **Start all services** (Django web server, PostgreSQL 16, Redis 7):
   ```bash
   docker compose up --build
   ```
   To run in the background (detached mode):
   ```bash
   docker compose up -d --build
   ```

2. **Check running containers**:
   ```bash
   docker compose ps
   ```

3. **Access services**:
   - **Django API**: `http://localhost:8000/api/`
   - **Swagger UI**: `http://localhost:8000/api/docs/`
   - **PostgreSQL**: `localhost:5432` (`db: notes_app_db`, `user: postgres_user`, `password: postgres_password`)
   - **Redis**: `localhost:6379`

4. **Stop the containers**:
   ```bash
   docker compose down
   ```
   To stop and remove persistent database/cache volumes:
   ```bash
   docker compose down -v
   ```


## App Flow

- Register a new account at `main/register/`
- Log in at `main/login/`
- View all notes on the home page at `main/`
- Create a note at `main/create/`
- Edit a note at `main/edit/<note_id>/`
- Delete a note at `main/delete/<note_id>/`
- Delete attached images from the edit page

## Interactive API Documentation (Swagger UI)

Interactive Swagger documentation is available at:
- **Swagger UI**: `/api/docs/`
- **OpenAPI Schema**: `/api/schema/`

You can test every endpoint directly in the browser. For protected endpoints, click **Authorize** in Swagger UI and input your JWT token: `Bearer <your_access_token>`.

## API ENDPOINTS

| PATH | METHOD | PAYLOAD |
|---|---|---|
| `/api/` | `GET` | None |
| `/api/register/` | `POST` | `{ "username": "alice", "email": "alice@example.com", "password": "your-password" }` |
| `/api/verify-registration/` | `POST` | `{ "email": "alice@example.com", "otp": "123456" }` |
| `/api/login/` | `POST` | `{ "username": "alice", "password": "your-password" }` |
| `/api/logout/` | `POST` | `{ "refresh": "<refresh_token>" }` |
| `/api/forgot-password/request/` | `POST` | `{ "email": "alice@example.com" }` |
| `/api/forgot-password/verify/` | `POST` | `{ "email": "alice@example.com", "otp": "123456", "password": "new-password" }` |
| `/api/token/refresh/` | `POST` | `{ "refresh": "<refresh_token>" }` |
| `/api/notes/` | `GET` | None (Supports `?page=1&page_size=10`) |
| `/api/notes/create/` | `POST` | `{ "title": "Note title", "content": "Note content", "image_url": "https://example.com/image.png" }` |
| `/api/notes/edit/<note_id>/` | `GET` | None |
| `/api/notes/edit/<note_id>/` | `PATCH` | Any fields to update: `{ "title": "Updated title", "content": "Updated content", "image_url": "https://example.com/image.png" }` |
| `/api/notes/delete/<note_id>/` | `DELETE` | None |

### Field Validation Rules
- **Username**: `^[a-zA-Z0-9_]{3,30}$` (3-30 characters, letters, numbers, and underscores).
- **Password**: `^(?=.*[A-Za-z])(?=.*\d).{8,}$` (at least 8 characters, at least one letter and one number).
- **OTP**: `^\d{6}$` (exactly 6 digits).