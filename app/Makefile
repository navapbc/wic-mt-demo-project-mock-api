PY_RUN_CMD := poetry run

run:
	docker-compose up -d --build

run-logs:
	docker-compose up --build

#########################
# DB & migrations
#########################

alembic_config := ./api/db/migrations/alembic.ini
alembic_cmd := $(PY_RUN_CMD) alembic --config $(alembic_config)

start-db:
	docker-compose up --detach mock-api-db

db-upgrade: ## Apply pending migrations to db
	$(PY_RUN_CMD) db-migrate-up

db-downgrade: ## Rollback last migration in db
	$(PY_RUN_CMD) db-migrate-down

db-downgrade-all: ## Rollback all migrations
	$(PY_RUN_CMD) db-migrate-down-all

check-migrate-msg:
ifndef MIGRATE_MSG
	$(error MIGRATE_MSG is undefined)
endif

db-migrate-create: check-migrate-msg
	$(alembic_cmd) revision --autogenerate -m "$(MIGRATE_MSG)"

#########################
# Testing
#########################

test:
	$(PY_RUN_CMD) pytest $(args)

#########################
# Formatting and linting
#########################

format:
	$(PY_RUN_CMD) isort --atomic api tests
	$(PY_RUN_CMD) black api tests

lint: lint-spectral lint-py

lint-py: lint-flake lint-mypy lint-poetry-version

lint-flake:
	$(PY_RUN_CMD) flake8 api tests

lint-mypy:
	$(PY_RUN_CMD) mypy --show-error-codes api

lint-poetry-version: ## Check poetry version
	grep --quiet 'lock-version = "1.1"' poetry.lock

lint-spectral:
	docker run --rm --tty --cap-drop=ALL --network=none --read-only --volume=$(PWD):/tmp:ro \
		stoplight/spectral:6 lint /tmp/openapi.yml --ruleset /tmp/.spectral.yaml