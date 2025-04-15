
test:
	pytest --cov=src/shapepy --cov-report=html tests

format:
	isort src
	isort tests
	black src
	black tests
	flake8 src
	pylint src

html:
	brave htmlcov/index.html