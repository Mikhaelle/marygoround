.PHONY: help up down build logs restart migrate migration test lint format shell-backend shell-frontend clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all containers
	docker compose build

rebuild: ## Force rebuild all containers
	docker compose build --no-cache

logs: ## Tail logs from all services
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker compose logs -f frontend

restart: ## Restart all services
	docker compose restart

migrate: ## Run alembic migrations
	docker compose exec backend alembic upgrade head

migration: ## Create a new alembic migration (usage: make migration msg="description")
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

test: ## Run backend tests
	docker compose exec backend pytest -v

test-unit: ## Run backend unit tests only
	docker compose exec backend pytest tests/unit -v

lint-backend: ## Lint backend code
	docker compose exec backend ruff check src/ tests/

lint-frontend: ## Lint frontend code
	docker compose exec frontend npm run lint

format-backend: ## Format backend code
	docker compose exec backend ruff format src/ tests/

format-check: ## Check code formatting
	docker compose exec backend ruff format --check src/ tests/

shell-backend: ## Open a shell in the backend container
	docker compose exec backend bash

shell-frontend: ## Open a shell in the frontend container
	docker compose exec frontend sh

shell-db: ## Open psql in the database container
	docker compose exec postgres psql -U $${POSTGRES_USER:-merygoround} -d $${POSTGRES_DB:-merygoround}

clean: ## Remove all containers, volumes, and build cache
	docker compose down -v --rmi local
	docker system prune -f

status: ## Show service status
	docker compose ps
