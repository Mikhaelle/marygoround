# MeryGoRound

A gamified household chore app with a spinning wheel and an adult life task bucket.

## What is this?

MeryGoRound turns boring household chores into a game. Spin the wheel, get a task, do it. Simple.

It also has a **Bucket** system for adult life tasks (schedule doctors, pay bills, etc.) that draws one task at a time - you can't get a new one until you finish or return the current one with a justification.

## Features

- **Spinning Wheel** - Canvas-based animated wheel with weighted random selection
- **Daily Reset** - Completed chores are removed for the day, everything resets at midnight
- **Multiplicity** - A chore can appear multiple times on the wheel (e.g., "brush teeth" 4x/day)
- **Time-Based Weights** - Chores can have higher probability at certain hours (e.g., "wash dishes" after dinner)
- **Adult Bucket** - Draw 1 adult task at a time, resolve or return with justification
- **Push Notifications** - Browser push reminders every hour (configurable)
- **Multi-user** - Each user has their own chores and bucket
- **Bilingual** - Portuguese (PT-BR) and English

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic |
| Frontend | Next.js 14+ (App Router), React 19, Tailwind, shadcn/ui, next-intl |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Push | Web Push API, pywebpush, Service Worker |
| Infra | Docker, docker-compose |
| Architecture | Clean Architecture + DDD |

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

That's it. Everything runs in Docker.

### Setup

```bash
git clone https://github.com/Mikhaelle/marygoround.git
cd marygoround

# Copy env file and adjust if needed
cp .env.example .env

# Start everything
make up

# Run database migrations (first time only)
make migrate
```

Open http://localhost:3000 and create an account.

### Available Commands

```bash
make up              # Start all services
make down            # Stop all services
make build           # Build containers
make rebuild         # Force rebuild (no cache)
make logs            # Tail all logs
make logs-backend    # Tail backend logs
make logs-frontend   # Tail frontend logs
make migrate         # Run database migrations
make migration msg="description"  # Create new migration
make test            # Run backend tests
make test-unit       # Run unit tests only
make lint-backend    # Lint Python code
make lint-frontend   # Lint TypeScript code
make format-backend  # Format Python code
make shell-backend   # Shell into backend container
make shell-frontend  # Shell into frontend container
make shell-db        # Open psql
make status          # Show service status
make clean           # Remove everything (containers, volumes, images)
```

## Architecture

```
backend/src/merygoround/
  domain/           # Entities, Value Objects, Repository ABCs, Domain Services
    shared/          # Base Entity, AggregateRoot, exceptions
    identity/        # User, Email VO, auth
    chores/          # Chore aggregate, WheelConfiguration, Duration/Multiplicity VOs
    wheel/           # SpinSession, WheelSpinService (weighted random)
    adult_bucket/    # BucketItem, BucketDraw, BucketDrawService
    notification/    # PushSubscription, NotificationPreference
  application/      # Use Cases (Commands/Queries), DTOs
  infrastructure/   # SQLAlchemy repos, JWT, bcrypt, pywebpush, APScheduler
  api/              # FastAPI routes, DI, middleware

frontend/src/
  app/              # Next.js App Router (locale-based routing)
  components/       # wheel/, chores/, bucket/, auth/, layout/, ui/
  lib/              # API client, hooks, contexts
  messages/         # i18n (pt-BR.json, en.json)
  types/            # TypeScript types
```

### Key Design Decisions

| Decision | Why |
|----------|-----|
| Server-side spin | Prevents manipulation, accurate history |
| Multiplicity as slots | Completing 1 of 4 leaves 3 on the wheel |
| Daily reset by date filter | No cron needed, automatic via query filter |
| Partial unique index for active draw | Database-level guarantee of 1 active draw per user |
| Duration limited to 5 or 10 min | Quick tasks only, keeps things manageable |
| Time weight max 3.0 | Prevents one chore from dominating the wheel |

## API

Backend API docs available at http://localhost:8000/docs (Swagger UI).

See [docs/PRD.md](docs/PRD.md) for the full API reference.

## Development

### Backend

- Python 3.12 with type hints and Google-style docstrings
- Ruff for linting and formatting (`ruff.toml`)
- pytest with async support (`tests/`)
- Alembic for migrations (`alembic/`)

### Frontend

- TypeScript strict mode
- ESLint + Prettier
- All user-facing strings via `useTranslations()` (next-intl)
- shadcn/ui components

### Running Tests

```bash
make test        # All tests
make test-unit   # Unit tests only
```

## License

Private project.
