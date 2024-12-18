start:
	venv/bin/uvicorn src.mllama.main:app --reload --log-level info

install:
	brew install python@3.11
	python3.11 -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r vendor/mlx-engine/requirements.txt
	venv/bin/pip install --quiet -e .
	echo "make precommit" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

fix: fix_autoflake fix_black

fix_black:
	venv/bin/black .

fix_autoflake:
	venv/bin/autoflake --quiet --in-place --recursive --remove-all-unused-imports --expand-star-imports src

precommit: test

test: test_mypy test_pytest test_black test_autoflake

test_black:
	venv/bin/black --check .

test_mypy:
	venv/bin/mypy src

test_pytest:
	venv/bin/pytest src

test_autoflake:
	venv/bin/autoflake --quiet --check --recursive --remove-all-unused-imports --expand-star-imports src
