SRC:=cachetory tests

.PHONY: all
all: install lint test build

.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	rm -rf *.egg-info build
	rm -rf coverage*.xml .coverage

.PHONY: install
install:
	poetry install --all-extras --with dev

.PHONY: lint
lint: lint/ruff lint/black lint/mypy

.PHONY: lint/black
lint/black:
	poetry run black --diff --check $(SRC)

.PHONY: lint/ruff
lint/ruff:
	poetry run ruff $(SRC)

.PHONY: lint/mypy
lint/mypy:
	poetry run mypy $(SRC)

.PHONY: format
format: format/ruff format/black

.PHONY: format/black
format/black:
	poetry run black $(SRC)

.PHONY: format/ruff
format/ruff:
	poetry run ruff --fix $(SRC)

.PHONY: test
test:
	poetry run pytest tests

.PHONY: build
build:
	poetry build
