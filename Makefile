.PHONY: deps install lint build publish test

deps:  ## Install dependencies
	python -m pip install --upgrade pip
	python -m pip install .[dev,test]

install:  ## Install the package
	python -m flit install

lint:  ## Lint and static-check
	python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

build:  ## Build dist
	python -m flit build

publish:  ## Publish to PyPi
	python -m flit publish

test:  ## Run tests
	python -m pytest -ra --junitxml=reports/python/tests.xml