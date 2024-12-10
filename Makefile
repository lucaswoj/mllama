start:
	venv/bin/uvicorn src.pal.main:app --reload

fix: fix_autoflake fix_black

fix_black:
	venv/bin/black .

fix_autoflake:
	venv/bin/autoflake --quiet --in-place --recursive --remove-all-unused-imports --expand-star-imports src

precommit: test

precommit_install:
	echo "make precommit" > .git/hooks/pre-commit

test: test_mypy test_pytest test_black test_autoflake

test_black:
	venv/bin/black --check .

test_mypy:
	venv/bin/mypy src

test_pytest:
	venv/bin/pytest src

test_autoflake:
	venv/bin/autoflake --quiet --check --recursive --remove-all-unused-imports --expand-star-imports src
