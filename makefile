build: clean test_requirements pytest

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

heroku_deploy:
	heroku container:push web

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose rm -f && docker-compose pull
CREATE_DOCKER_COMPOSE_ENVS := python env_writer.py env.json
run:
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

SET_DEBUG_ENV_VARS := \
	export DIRECTORY_UI_PORT=8001; \
	export DIRECTORY_UI_SECRET_KEY=debug

REMOVE_WEBSERVERS := \
	docker ps -a | \
	awk '{ print $$1,$$12 }' | \
	grep -e directoryui_webserver | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

run_debug:
	$(REMOVE_WEBSERVERS) && \
	$(SET_DEBUG_ENV_VARS) && \
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	docker-compose rm -f && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run --service-ports webserver make debug_webserver

debug_webserver:
	export DEBUG=true; python /usr/src/app/manage.py collectstatic --noinput; python manage.py migrate; python manage.py runserver 0.0.0.0:8001

webserver_bash:
	docker exec -it directoryui_webserver_1 sh

run_test:
	$(SET_DEBUG_ENV_VARS) && \
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose build && \
	docker-compose run webserver make test_requirements collectstatic pytest

collectstatic:
	python /usr/src/app/manage.py collectstatic --noinput

test_requirements:
	pip install -r test.txt

flake8:
	flake8 . --exclude=migrations --ignore=E501

pytest: flake8
	export SECRET_KEY=test; pytest . --cov=. $(pytest_args)

.PHONY: build clean run run_debug run_test test_requirements flake8 pytest heroku_deploy webserver_bash
