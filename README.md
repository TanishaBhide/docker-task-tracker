
# Dockerized Task Tracker API

A containerized task management REST API built using FastAPI and PostgreSQL. The project demonstrates Docker image creation, container lifecycle management, Docker Compose, service-to-service networking, persistent storage, and basic troubleshooting.

## Features

- Create and list tasks
- Mark tasks as completed
- Delete tasks
- Store tasks in PostgreSQL
- Health endpoint that checks database connectivity
- Dockerized API and database services
- Persistent database storage using a named Docker volume

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- PostgreSQL 17
- Psycopg 3
- Docker
- Docker Compose

## Architecture

```text
Client / Browser
       |
       | http://localhost:8001
       v
+-----------------------+
| FastAPI Container     |
| task-api               |
| Internal port: 8000   |
+-----------------------+
       |
       | PostgreSQL connection
       | Host: db
       | Port: 5432
       v
+-----------------------+
| PostgreSQL Container  |
| task-db                |
| Database: tasksdb     |
+-----------------------+
       |
       v
 Named Volume: postgres_data
```

Docker Compose creates a private network for the services. The API connects to PostgreSQL using the service name `db`, rather than `localhost`.

## Project Structure

```text
docker-task-tracker/
├── app/
│   └── main.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Prerequisites

- Docker Desktop installed and running
- Git (optional, for version control)

## Setup and Run

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd docker-task-tracker
```

### 2. Configure environment variables

Copy the example environment file.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder password with a local development password.

Do not commit `.env` to Git.

### 3. Build and start the services

```bash
docker compose up -d --build
```

This builds the API image and starts the API and PostgreSQL containers.

### 4. Verify the services

```bash
docker compose ps
docker compose logs api
docker compose logs db
```

Open the interactive API documentation:

http://localhost:8001/docs

Check the API:

http://localhost:8001/

Check database connectivity:

http://localhost:8001/health

Expected health response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check that the API is running |
| GET | `/health` | Check database connectivity |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| PATCH | `/tasks/{task_id}` | Mark a task as completed |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Example: Create a task

Send a POST request to `/tasks` with this JSON body:

```json
{
  "title": "Learn Docker networking"
}
```

Example response:

```json
{
  "id": 1,
  "title": "Learn Docker networking",
  "completed": false
}
```

You can also try the endpoints through Swagger UI at `/docs`.

## Docker Commands

Start and rebuild:

```bash
docker compose up -d --build
```

List Compose services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs api
docker compose logs db
docker compose logs -f api
```

Open a shell in the API container:

```bash
docker exec -it task-api sh
```

Connect to PostgreSQL:

```bash
docker exec -it task-db psql -U taskuser -d tasksdb
```

Stop and remove the Compose containers and network:

```bash
docker compose down
```

Remove containers and the named database volume:

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes the project's named database volume and its stored data. Use it only when you intentionally want to reset the database.

## Docker Concepts Demonstrated

- **Images and containers:** Build an API image and run it as a container.
- **Dockerfile layers:** Install dependencies separately from application code to improve build caching.
- **Port mapping:** Map host port `8001` to container port `8000`.
- **Service discovery:** Reach PostgreSQL through the Compose service hostname `db`.
- **Environment variables:** Configure database connection details without hardcoding them in application code.
- **Named volumes:** Preserve PostgreSQL data when its container is recreated.
- **Logs and inspection:** Investigate container status, logs, configuration, and resource usage.
- **Service recovery:** Restart services and test API behavior when PostgreSQL is unavailable.

## Persistence

PostgreSQL stores its data in the named volume `postgres_data`.

Recreating the database container does not normally delete the volume, so existing tasks remain available. Removing the volume with `docker compose down -v` deletes that stored data.

## Troubleshooting

### API cannot connect to PostgreSQL

- Check service status with `docker compose ps`.
- Inspect logs with `docker compose logs api` and `docker compose logs db`.
- Verify the API uses `DB_HOST=db`, not `localhost`.
- Check the database credentials in `.env`.
- Allow PostgreSQL time to finish starting; the API retries its database initialization.

### Port 8001 is already in use

Change the host side of the mapping in `compose.yaml`, for example:

```yaml
ports:
  - "8002:8000"
```

Then rebuild or recreate the services and access the API at `http://localhost:8002/docs`.

### Tasks disappear after a reset

Check that the `postgres_data` named volume still exists. Avoid `docker compose down -v` unless you intend to delete the database data.

## Current Limitations

This is a learning project, not a production-ready service.

- No authentication or authorization
- No database migration framework
- No comprehensive automated test suite
- Local development credentials rather than a production secrets-management system
- No configured production deployment, CI/CD pipeline, or Kubernetes manifests

## Future Improvements

- Add automated API and database integration tests
- Add database migrations
- Add container health checks and improved startup dependency handling
- Add a non-root application user and production security hardening
- Build a CI/CD pipeline
- Explore deployment with Kubernetes and monitoring

## Learning Outcomes

This project provides hands-on practice with Docker images, containers, Dockerfiles, port mapping, Compose, service discovery, environment-based configuration, persistent volumes, logs, and basic failure recovery.
