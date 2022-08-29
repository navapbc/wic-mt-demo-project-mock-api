###########
# Constants
###########

APP_NAME := app

# A few commands need adjustments if they're run in CI, specify those here
# TODO - when CI gets hooked up, actually test this.
ifdef CI
 DOCKER_EXEC_ARGS := -T -e CI -e PYTEST_ADDOPTS="--color=yes"
 FLAKE8_FORMAT := '::warning file=api/%(path)s,line=%(row)d,col=%(col)d::%(path)s:%(row)d:%(col)d: %(code)s %(text)s'
 MYPY_FLAGS := --no-pretty
 MYPY_POSTPROC := | perl -pe "s/^(.+):(\d+):(\d+): error: (.*)/::warning file=api\/\1,line=\2,col=\3::\4/"
 SPECTRAL_POSTPROC := --format=text | perl -pe "s/^\/tmp\/(.+):(\d+):(\d+) (error|warning) (.*)/::warning file=api\/\1,line=\2,col=\3::\4 \5/"
else
 FLAKE8_FORMAT := default
endif

# By default, all python/poetry commands will run outside of the docker container
# if you wish to run this differently, add PY_RUN_APPROACH=docker to your environment vars
# You can set this by either running `export PY_RUN_APPROACH=docker` in your shell or add
# it to your ~/.zshrc file (and run `source ~/.zshrc`)
ifeq "$(PY_RUN_APPROACH)" "docker"
PY_RUN_CMD := docker-compose run $(DOCKER_EXEC_ARGS) --rm $(APP_NAME) poetry run
else
PY_RUN_CMD := poetry run
endif

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
	$(PY_RUN_CMD) flake8 --format=$(FLAKE8_FORMAT) api

lint-mypy:
	$(PY_RUN_CMD) mypy --show-error-codes $(MYPY_FLAGS) api $(MYPY_POSTPROC)

lint-poetry-version: ## Check poetry version
	grep --quiet 'lock-version = "1.1"' poetry.lock

lint-spectral:
	docker run --rm --tty --cap-drop=ALL --network=none --read-only --volume=$(PWD):/tmp:ro \
		stoplight/spectral:6 lint /tmp/openapi.yml --ruleset /tmp/.spectral.yaml $(SPECTRAL_POSTPROC)