.PHONY: build check clean compile fmt lint static-check test

check: clean lint test build

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

build: compile

compile:
	python3 -c "from pathlib import Path; [compile(path.read_text(), str(path), 'exec') for path in [Path('RoyalMail.py'), Path('main.py'), *Path('tests').glob('*.py')]]"

static-check:
	python3 scripts/check-baseline.py

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

fmt:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
