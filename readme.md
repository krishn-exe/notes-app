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

## Project Structure

```text
notes-app/
├── main/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── notesApp/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.example
├── manage.py
├── requirements.txt
├── readme.md
└── notes/
```

## Prerequisites

Before running the app, make sure you have:

- Python 3.10+
- pip
- PostgreSQL database
- AWS S3 bucket and access credentials

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd notes-app
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local environment file:

```bash
copy .env.example .env
```

5. Update the values in `.env` with your own configuration:

```env
SECRET_KEY = "your-secret-key"
DEBUG = "False"

PG_NAME = "your-database-name"
PG_USER = "your-database-user"
PG_PASSWORD = "your-database-password"
PG_HOST = "your-database-host"
PG_PORT = "5432"

AWS_ACCESS_KEY_ID = "your-aws-access-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-key"
AWS_STORAGE_BUCKET_NAME = "your-bucket-name"
AWS_S3_REGION_NAME = "your-region"
```

## Database Setup

Run the migrations to create the database tables:

```bash
python manage.py migrate
```

Create an admin account if needed:

```bash
python manage.py createsuperuser
```

## Run the App

Start the local server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## App Flow

- Register a new account at `/register/`
- Log in at `/login/`
- View all notes on the home page at `/`
- Create a note at `/create/`
- Edit a note at `/edit/<note_id>/`
- Delete a note at `/delete/<note_id>/`
- Delete attached images from the edit page