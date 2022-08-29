PY_RUN_CMD := poetry run

run:
	docker-compose up -d --build

run-logs:
	docker-compose up --build

format:
	$(PY_RUN_CMD) isort --atomic api
	$(PY_RUN_CMD) black api

lint: lint-spectral lint-py

lint-py: lint-flake lint-mypy lint-poetry-version

lint-flake:
	$(PY_RUN_CMD) flake8 api

lint-mypy:
	$(PY_RUN_CMD) mypy --show-error-codes api

lint-poetry-version: ## Check poetry version
	grep --quiet 'lock-version = "1.1"' poetry.lock

lint-spectral:
	docker run --rm --tty --cap-drop=ALL --network=none --read-only --volume=$(PWD):/tmp:ro \
		stoplight/spectral:6 lint /tmp/openapi.yml --ruleset /tmp/.spectral.yaml