# This Makefile requires the following commands to be available:
# * python3.7

SRC:=cachetory tests setup.py

.PHONY: pyclean
pyclean:
	-find . -name "*.pyc" -delete
	-rm -rf *.egg-info build
	-rm -rf coverage*.xml .coverage

.PHONY: clean
clean: pyclean
	-rm -rf venv
	-rm -rf .tox

venv: PYTHON?=python3.7
venv:
	$(PYTHON) -m venv venv
	venv/bin/pip install -U "pip>=7.0" -q
	venv/bin/pip install -U setuptools -q
	venv/bin/pip install -r requirements.txt

## Code style
.PHONY: lint
lint: lint/black lint/flake8 lint/isort lint/mypy

.PHONY: lint/black
lint/black: venv
	venv/bin/black --diff --check $(SRC)

.PHONY: lint/flake8
lint/flake8: venv
	venv/bin/flake8 $(SRC)

.PHONY: lint/isort
lint/isort: venv
	venv/bin/isort --diff --check $(SRC)

.PHONY: lint/mypy
lint/mypy: venv
	venv/bin/mypy $(SRC)

.PHONY: format
format: format/isort format/black

.PHONY: format/isort
format/isort: venv
	venv/bin/isort $(SRC)

.PHONY: format/black
format/black: venv
	venv/bin/black $(SRC)

## Tests
.PHONY: unittests
unittests: TOX_ENV?=ALL
unittests: TOX_EXTRA_PARAMS?=""
unittests: venv
	venv/bin/tox -e $(TOX_ENV) $(TOX_EXTRA_PARAMS)

.PHONY: test
test: pyclean venv unittests

## Distribution
.PHONY: build
build: venv
	-rm -rf dist build
	venv/bin/python setup.py sdist bdist_wheel
	venv/bin/twine check dist/*
