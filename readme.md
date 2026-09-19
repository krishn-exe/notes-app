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
- Django Storages
- boto3
- Pillow
- Python-dotenv
- Django rest Framework

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
| `/api/notes/` | `GET` | None |
| `/api/notes/create/` | `POST` | `{ "title": "Note title", "content": "Note content", "image_url": "https://example.com/image.png" }` |
| `/api/notes/edit/<note_id>/` | `GET` | None |
| `/api/notes/edit/<note_id>/` | `PATCH` | Any fields to update: `{ "title": "Updated title", "content": "Updated content", "image_url": "https://example.com/image.png" }` |
| `/api/notes/delete/<note_id>/` | `DELETE` | None |