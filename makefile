build: clean test_requirements pytest

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r test.txt

flake8:
	flake8 . --exclude=migrations --ignore=E501

pytest: flake8
	pytest . --cov=. $(pytest_args)

.PHONY: build clean test_requirements flake8 pytest
