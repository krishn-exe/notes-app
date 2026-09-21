# Notes App REST API

A secure, scalable REST API built with Django, Django REST Framework, and Gunicorn for managing personal notes with image attachments. Containerized with Docker and Docker Compose, featuring PostgreSQL for persistent data storage, Redis for high-performance query caching and rate limiting, and AWS S3 for media uploads.

---

## Features

- **JWT Authentication**: Secure access & refresh tokens with rotation and blacklisting.
- **Two-Step Email OTP Verification**: Automated 6-digit OTP codes for account registration and password resets.
- **Notes CRUD**: Create, read, update, and delete notes linked to authenticated users.
- **Image Attachments**: Attach image URLs to notes with optional AWS S3 bucket integration.
- **Pagination**: Scalable list querying with customizable page sizing (`?page=1&page_size=10`).
- **Redis Cache-Aside**: Dynamic query caching with instant atomic invalidation on note mutation.
- **Rate Limiting**: Throttling powered by Redis (20 requests/min for anonymous, 60 requests/min for authenticated users).
- **Interactive Swagger UI**: Full OpenAPI 3.0 schema and in-browser testing via `drf-spectacular`.
- **Fully Containerized**: Ready for local development and EC2 production deployment via Docker Compose.

---

## Tech Stack

- **Backend**: Python 3.12, Django 6, Django REST Framework
- **WSGI Server**: Gunicorn
- **Reverse Proxy & Static Files**: Nginx (Alpine)
- **Database**: PostgreSQL 16
- **Cache & Throttling**: Redis 7, `django-redis`
- **Containerization**: Docker & Docker Compose
- **Documentation**: `drf-spectacular` (Swagger UI & OpenAPI 3.0)
- **Cloud Storage**: AWS S3 via `boto3` and `django-storages`
- **CI/CD**: GitHub Actions (`appleboy/ssh-action`)

---

## Running Locally with Docker Compose

Docker Compose automatically launches the entire stack: Nginx reverse proxy, Django application (Gunicorn), local PostgreSQL database, and local Redis cache with health checks and persistent storage.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine + Docker Compose (Linux).

### 1. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```
*(Optional: add your AWS S3 credentials or SMTP email settings if you wish to test live email sending/S3 image uploads locally).*

### 2. Build and Start Containers
```bash
docker compose up --build
```
To run in the background (detached mode):
```bash
docker compose up -d --build
```

On initial startup, Docker will:
1. Pull and start `postgres:16-alpine` and `redis:7-alpine`.
2. Build the Django `web` image with Gunicorn and all dependencies.
3. Automatically collect static files (`python manage.py collectstatic --noinput`) and apply database migrations (`python manage.py migrate`).
4. Start Nginx reverse proxy on port `80` (proxying to Gunicorn on port `8000`).

### 3. Service URLs & Ports
- **REST API (via Nginx)**: `http://localhost/api/`
- **Swagger Documentation**: `http://localhost/api/docs/`
- **Direct Gunicorn (Dev)**: `http://localhost:8000/api/docs/`
- **PostgreSQL**: `localhost:5432` (`db: notes_app_db`, `user: postgres_user`, `password: postgres_password`)
- **Redis**: `localhost:6379`

### 4. Useful Docker Commands
```bash
# Check container status
docker compose ps

# View live logs
docker compose logs -f web

# Run Django management commands inside container
docker compose exec web python manage.py createsuperuser

# Stop all containers
docker compose down

# Stop containers and wipe database/cache volumes
docker compose down -v
```

---

## Deploying on AWS EC2 with Docker

### Option A: Automated CI/CD (GitHub Actions)

A preconfigured deployment pipeline is available in `.github/workflows/deploy.yaml`. It triggers automatically on every push to `production` or `main`, or manually via **Workflow Dispatch**.

1. **Add GitHub Secrets**:
   In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions** and add:
   - `EC2_HOST`: Your EC2 instance public IP or public DNS hostname.
   - `EC2_USERNAME`: Your SSH username (e.g., `ubuntu` for Ubuntu AMIs, `ec2-user` for Amazon Linux).
   - `EC2_SSH_KEY`: Your private SSH key (`.pem` file content).

2. **Trigger Deployment**:
   Push your changes to the `production` or `main` branch:
   ```bash
   git push origin main
   ```
   Or trigger manually from the **Actions** tab in GitHub by selecting **Deploy to EC2** > **Run workflow**.

3. **What the Pipeline Does**:
   - SSHs into your EC2 instance.
   - Pulls the latest commits for the deployed branch.
   - Detects Docker & Compose installations.
   - Rebuilds and launches the containers (`docker compose up -d --build --remove-orphans`).
   - Prunes dangling Docker images to preserve EC2 disk storage.

---

### Option B: Manual Deployment on EC2

To deploy manually or perform initial server setup on EC2:

1. **Connect to EC2**:
   ```bash
   ssh -i your-key.pem ubuntu@<your-ec2-ip>
   ```

2. **Install Docker & Docker Compose** (if not already installed on Ubuntu):
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/notes-app.git ~/notes-app
   cd ~/notes-app
   ```

4. **Set Up Environment Variables**:
   ```bash
   cp .env.example .env
   nano .env
   ```
   Configure your production variables (`SECRET_KEY`, `DEBUG=False`, AWS credentials, SMTP email credentials).

5. **Start Docker Stack**:
   ```bash
   docker compose up -d --build
   ```

6. **Access Application & Nginx**:
   The Docker stack includes a containerized Nginx reverse proxy listening on port `80`:
   - Access the API: `http://<EC2_PUBLIC_IP>/api/`
   - Access Swagger Docs: `http://<EC2_PUBLIC_IP>/api/docs/`

   *(Optional: SSL/TLS with Certbot)*: If you map a custom domain name and want HTTPS/SSL on EC2, you can terminate SSL on the EC2 host using Certbot or map port `443` to Nginx with SSL certificates.

---

## Interactive API Documentation (Swagger UI)

Interactive Swagger documentation is available at:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Testing Protected Endpoints
1. Obtain an access token by registering and verifying via OTP (`/api/register/` and `/api/verify-registration/`) or logging in (`/api/login/`).
2. Click **Authorize** (top right in Swagger UI).
3. Enter `Bearer <your_access_token>` and submit.
4. Test any protected route directly from the browser.

---

## API Endpoints Reference

| Method | Endpoint | Auth | Request Body | Description |
|---|---|---|---|---|
| `GET` | `/api/` | None | None | API index and route directory |
| `POST` | `/api/register/` | None | `{ "username": "alice", "email": "alice@example.com", "password": "Password123" }` | Register inactive user & dispatch 6-digit OTP |
| `POST` | `/api/verify-registration/` | None | `{ "email": "alice@example.com", "otp": "123456" }` | Verify OTP, activate user, & issue JWT tokens |
| `POST` | `/api/login/` | None | `{ "username": "alice", "password": "Password123" }` | Authenticate user & issue JWT tokens |
| `POST` | `/api/logout/` | JWT | `{ "refresh": "<refresh_token>" }` | Blacklist refresh token & log out |
| `POST` | `/api/forgot-password/request/` | None | `{ "email": "alice@example.com" }` | Request 6-digit password reset OTP |
| `POST` | `/api/forgot-password/verify/` | None | `{ "email": "alice@example.com", "otp": "123456", "password": "NewPassword123" }` | Verify OTP & update account password |
| `POST` | `/api/token/refresh/` | None | `{ "refresh": "<refresh_token>" }` | Rotate access & refresh tokens |
| `GET` | `/api/notes/` | JWT | None (supports `?page=1&page_size=10`) | List notes with pagination & Redis caching |
| `POST` | `/api/notes/create/` | JWT | `{ "title": "Meeting Notes", "content": "Discussion points...", "image_url": "https://..." }` | Create note & invalidate user cache |
| `GET` | `/api/notes/edit/<id>/` | JWT | None | Fetch single note detail for editing |
| `PATCH` | `/api/notes/edit/<id>/` | JWT | `{ "title": "Updated", "content": "Updated content" }` | Partially update note & invalidate cache |
| `DELETE` | `/api/notes/delete/<id>/` | JWT | None | Delete note & invalidate user cache |

---

## Field Validation Rules

- **Username**: `^[a-zA-Z0-9_]{3,30}$` (3-30 characters, letters, numbers, and underscores).
- **Password**: `^(?=.*[A-Za-z])(?=.*\d).{8,}$` (minimum 8 characters, at least one letter and one digit).
- **OTP**: `^\d{6}$` (strictly 6 numeric digits).