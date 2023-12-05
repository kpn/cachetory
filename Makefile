SRC := cachetory tests
DJANGO_SETTINGS_MODULE := tests.backends.django.settings

.PHONY: all
all: install lint test build docs

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	rm -rf *.egg-info build
	rm -rf coverage*.xml .coverage
	poetry env remove --all

.PHONY: install
install:
	poetry install --all-extras --with=dev --with=docs

.PHONY: lint
lint: lint/ruff lint/mypy

.PHONY: lint/ruff
lint/ruff:
	poetry run ruff format --diff $(SRC)
	poetry run ruff check $(SRC)

.PHONY: lint/mypy
lint/mypy:
	poetry run mypy $(SRC)

.PHONY: format
format: format/ruff

.PHONY: format/ruff
format/ruff:
	poetry run ruff format $(SRC)
	poetry run ruff check --fix $(SRC)

.PHONY: test
test:
	poetry run pytest tests

.PHONY: build
build:
	poetry build

.PHONY: docs
docs:
	poetry run mkdocs build --site-dir _site
