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

- Register a new account at `app/register/`
- Log in at `app/login/`
- View all notes on the home page at `app/`
- Create a note at `app/create/`
- Edit a note at `app/edit/<note_id>/`
- Delete a note at `app/delete/<note_id>/`
- Delete attached images from the edit page