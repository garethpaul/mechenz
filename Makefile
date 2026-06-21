ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\n' "$$path" | sed 's/^ //'); dirname -- "$$path")

.PHONY: build check clean compile fmt lint mutation-test static-check test unit-test

check: clean lint test build

lint: static-check

test: unit-test mutation-test

unit-test:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

mutation-test:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-security-mutations.py

build: compile

compile:
	cd "$(ROOT)" && python3 -c "from pathlib import Path; [compile(path.read_text(), str(path), 'exec') for path in [Path('RoyalMail.py'), Path('main.py'), *Path('tests').glob('*.py')]]"

static-check:
	python3 "$(ROOT)/scripts/check-baseline.py"

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

fmt:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
