test:
	pytest --cov=src/shapepy --cov-report=xml tests
	python3-coverage report -m --fail-under 95
	python3-coverage html

format:
	isort src
	isort tests
	black src
	black tests
	flake8 src --max-complexity 12
	pylint src

html:
	brave htmlcov/index.html

docs:
	sphinx-autobuild docs/ docs/_build/html
