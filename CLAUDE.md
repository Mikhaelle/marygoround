# MeryGoRound - Project Instructions

## Overview
Household chore spinning wheel app with adult life task bucket. Multi-user, i18n (PT-BR/EN).

## Tech Stack
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL 16
- **Frontend**: Next.js 14+ (App Router) + React + Tailwind + shadcn/ui + next-intl
- **Infrastructure**: Docker + docker-compose + Redis 7
- **Push**: pywebpush + Service Worker + Web Push API

## Architecture
- **Clean Architecture** with DDD tactical patterns
- Dependency rule: API -> Application -> Domain <- Infrastructure
- Domain layer has ZERO external dependencies
- 5 bounded contexts: Identity, Chores, Wheel, AdultBucket, Notification

## Directory Layout
```
backend/src/merygoround/
  domain/       # Entities, Value Objects, Repository ABCs, Domain Services
  application/  # Use Cases (Commands/Queries), DTOs
  infrastructure/ # SQLAlchemy repos, JWT, bcrypt, pywebpush, APScheduler
  api/          # FastAPI routes, DI, middleware

frontend/src/
  app/          # Next.js App Router pages
  components/   # React components by domain
  lib/          # API client, hooks, contexts, utils
  messages/     # i18n JSON files (pt-BR.json, en.json)
  types/        # TypeScript type definitions
```

## Commands

### Backend
```bash
# Run locally
docker-compose up backend

# Lint + format
cd backend && ruff check . && ruff format .

# Tests
cd backend && pytest

# New migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head
```

### Frontend
```bash
# Run locally
docker-compose up frontend

# Lint + format
cd frontend && npm run lint && npm run format

# Type check
cd frontend && npx tsc --noEmit
```

### Full stack
```bash
docker-compose up        # Start all services
docker-compose down      # Stop all services
docker-compose up --build # Rebuild and start
```

## Coding Conventions

### Python (Backend)
- Use `ruff` for linting and formatting (config in `ruff.toml`)
- Type hints on all public functions
- Docstrings (Google style) on all public classes and functions
- Domain entities must NOT import from infrastructure or application layers
- Abstract repositories in domain layer, concrete in infrastructure
- Use Pydantic v2 models for DTOs and API schemas
- Async everywhere (async def, AsyncSession, asyncpg)

### TypeScript (Frontend)
- ESLint + Prettier for formatting
- All components as named exports (no default exports)
- Props interfaces defined inline or co-located
- API calls in `lib/api/` modules, never directly in components
- Hooks in `lib/hooks/` for data fetching
- All user-facing strings via `useTranslations()` (next-intl)

### i18n
- Code (variables, functions, commits, comments) always in English
- UI text in PT-BR and EN via next-intl
- Translation keys use dot notation: `chores.form.name`

### Git
- Conventional commits: feat:, fix:, docs:, test:, refactor:, chore:
- Never commit .env files
- Never commit with failing tests

## Key Business Rules
1. Chore duration: 1-10 minutes only
2. Wheel multiplicity: >= 1 per chore
3. Time weight rules: hour 0-23, weight > 0, default 1.0 if no rule
4. Spin is determined SERVER-SIDE (not client-side random)
5. Adult bucket: max 1 ACTIVE draw per user at any time
6. Bucket return requires justification (min 10 chars)
7. Resolved bucket items are excluded from future draws
8. Push notifications respect quiet hours
