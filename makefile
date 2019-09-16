ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

pytest:
	ENV_FILES='test,dev' \
	pytest $(ARGUMENTS) \
	--numprocesses auto \
	--dist=loadfile \
	--ignore=node_modules \
	--capture=no \
	-Wignore::DeprecationWarning \
	-vv

flake8:
	flake8 . \
	--exclude=.venv,venv,node_modules \
	--max-line-length=120

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver 0.0.0.0:8001 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

secrets:
	cp conf/env/secrets-template conf/env/secrets-do-not-commit; \
	sed -i -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' conf/env/secrets-do-not-commit

.PHONY: clean pytest flake8 manage webserver requirements install_requirements css secrets

