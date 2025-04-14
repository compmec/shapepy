
test:
	pytest tests

format:
	isort src
	isort tests
	black src
	black tests
