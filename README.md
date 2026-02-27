# Incident Tracker

A full-stack incident tracking application for managing and resolving incidents. Users can create incidents, assign them, track their status through a lifecycle (open, in progress, resolved), and collaborate via comments.

**This is a personal training project** built to learn full-stack development with Python (FastAPI) and React (TypeScript). It is not intended for production use.

## Technology Stack

- [FastAPI](https://fastapi.tiangolo.com) for the Python backend API
  - [SQLModel](https://sqlmodel.tiangolo.com) for database interactions (ORM)
  - [Pydantic](https://docs.pydantic.dev) for data validation and settings management
  - [PostgreSQL](https://www.postgresql.org) as the SQL database
- [React](https://react.dev) for the frontend
  - TypeScript, hooks, and [Vite](https://vitejs.dev)
  - [Tailwind CSS](https://tailwindcss.com) and [shadcn/ui](https://ui.shadcn.com) for UI components
  - Auto-generated API client from OpenAPI spec
- [Docker Compose](https://www.docker.com) for running the database
- JWT authentication with secure password hashing
- [Pytest](https://pytest.org) for backend tests

## Features

- **Incident management** — Create, update, and delete incidents with title, description, status, priority, and category
- **Incident lifecycle** — Track incidents through open, in progress, and resolved states with automatic resolved_at timestamps
- **Assignment** — Assign incidents to users
- **Comments** — Add and delete comments on incidents for collaboration
- **User management** — Admin panel for managing users with role-based access control
- **Authentication** — Login, signup, and password recovery via email

## Architecture

```mermaid
graph TB
    subgraph Client["Browser"]
        FE["Frontend<br/>React + TypeScript<br/>Vite / Tailwind / shadcn"]
    end

    subgraph Server["Server"]
        TR["Traefik<br/>Reverse Proxy + TLS"]
        BE["Backend<br/>FastAPI (Python)<br/>SQLModel / Pydantic"]
        DB["PostgreSQL"]
        AD["Adminer<br/>DB UI"]
        ML["Mailcatcher<br/>(dev / test)"]
    end

    FE -- "HTTPS (api.domain)" --> TR
    TR -- "HTTP :8000" --> BE
    TR -- "HTTP :8080" --> AD
    BE -- "SQL" --> DB
    AD -- "SQL" --> DB
    BE -- "SMTP" --> ML
```

## Incident Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Open : Incident created
    Open --> In_Progress : Work started
    In_Progress --> Open : Reverted
    In_Progress --> Resolved : Issue fixed\n(resolved_at set)
    Resolved --> In_Progress : Reopened\n(resolved_at cleared)
    Resolved --> [*]

    note right of Resolved
        resolved_at timestamp
        is recorded automatically
    end note
```

## Database Schema

```mermaid
erDiagram
    USER {
        uuid id PK
        string email
        string hashed_password
        bool is_active
        bool is_superuser
        string full_name
        datetime created_at
    }

    INCIDENT {
        uuid id PK
        string title
        string description
        enum status
        enum priority
        enum category
        datetime created_at
        datetime resolved_at
        uuid owner_id FK
        uuid assignee_id FK
    }

    COMMENT {
        uuid id PK
        string content
        datetime created_at
        uuid author_id FK
        uuid incident_id FK
    }

    USER ||--o{ INCIDENT : "owns"
    USER ||--o{ INCIDENT : "assigned to"
    USER ||--o{ COMMENT : "authors"
    INCIDENT ||--o{ COMMENT : "has"
```

## Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL

    User->>FE: Enter email + password
    FE->>BE: POST /api/v1/login/access-token
    BE->>DB: Lookup user by email
    DB-->>BE: User record
    BE->>BE: Verify password hash (Argon2/Bcrypt)
    BE-->>FE: JWT token (8-day expiry)
    FE->>FE: Store token in localStorage

    Note over FE,BE: Subsequent requests

    FE->>BE: Request + Authorization: Bearer {token}
    BE->>BE: Validate JWT signature & expiry
    BE-->>FE: Protected resource
```

## CI/CD Pipeline

```mermaid
flowchart LR
    PR["Pull Request\nor push to master"]

    subgraph CI["Continuous Integration"]
        direction TB
        PC["pre-commit\nlinting & formatting"]
        TB["Backend Tests\n(pytest + 90% coverage)"]
        DC["Docker Compose\nintegration test"]
    end

    subgraph CD["Continuous Deployment"]
        direction TB
        ST["Deploy Staging\n(push to master)"]
        PR2["Deploy Production\n(release published)"]
    end

    PR --> CI
    CI --> CD
    ST --> PR2
```

## Application

![img.png](img.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)
![img_3.png](img_3.png)

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Setup

1. Start the database:

```bash
docker compose up -d db
```

2. Run backend migrations and start the server:

```bash
cd backend
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

3. Install frontend dependencies and start the dev server:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

### Running Tests

```bash
cd backend
uv run pytest tests/ -v
```

## Project Structure

```
backend/
  app/
    api/routes/       -- API endpoints (incidents, comments, users, login)
    core/             -- Config, security, database setup
    models.py         -- Database models and schemas
    crud.py           -- Reusable CRUD operations
  tests/              -- Backend tests
  app/alembic/        -- Database migrations

frontend/
  src/
    routes/           -- Pages (file-based routing with TanStack Router)
    components/       -- React components (Incidents, Comments, Admin, UI)
    client/           -- Auto-generated API client
    hooks/            -- Custom React hooks (auth, toast, etc.)
```

## Based On

This project was bootstrapped from the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) and customized for incident tracking.

## License
MIT
