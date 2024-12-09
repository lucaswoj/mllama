start:
	venv/bin/uvicorn src.pal.main:app --reload --workers 4

fix: fix_autoflake fix_black fix_pip

fix_black:
	venv/bin/black .

fix_pip:
	python3.10 -m venv venv && \
	venv/bin/pip install --quiet --requirement requirements.txt && \
	venv/bin/pip install --quiet --requirement vendor/mlx-engine/requirements.txt && \
	venv/bin/pip freeze | grep -v '^-e' > requirements.txt && \
	venv/bin/pip install --quiet -e . && \
	ln -sf venv/bin/* node_modules/.bin

fix_autoflake:
	venv/bin/autoflake --quiet --in-place --recursive --remove-all-unused-imports --expand-star-imports src

precommit: test

precommit_install:
	echo "make precommit" > .git/hooks/pre-commit

test: test_mypy test_pytest test_black test_autoflake test_pip

test_black:
	venv/bin/black --check .

test_mypy:
	venv/bin/mypy src

test_pip:
	bash -c 'diff <(venv/bin/pip freeze | grep -v '^-e') requirements.txt || (echo pip freeze does not match requirements.txt && exit 1)'

test_pytest:
	venv/bin/pytest src

test_autoflake:
	venv/bin/autoflake --quiet --check --recursive --remove-all-unused-imports --expand-star-imports src
