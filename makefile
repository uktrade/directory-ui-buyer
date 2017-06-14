build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

API_CLIENT_ENV_VARS := API_SIGNATURE_SECRET=debug API_CLIENT_BASE_URL=http://debug
FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules
PYTEST := pytest . --cov=. --cov-config=.coveragerc --capture=no $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(API_CLIENT_ENV_VARS) $(PYTEST)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput && \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := python ./docker/env_writer.py ./docker/env.json ./docker/env.test.json

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export DIRECTORY_UI_BUYER_API_CLIENT_CLASS_NAME=unit-test; \
	export DIRECTORY_UI_BUYER_API_SIGNATURE_SECRET=debug; \
	export DIRECTORY_UI_BUYER_API_CLIENT_BASE_URL=http://api.trade.great.dev:8000; \
	export DIRECTORY_UI_BUYER_SSO_SIGNATURE_SECRET=api_signature_debug; \
	export DIRECTORY_UI_BUYER_SSO_API_CLIENT_BASE_URL=http://sso.trade.great.dev:8004/api/v1/; \
	export DIRECTORY_UI_BUYER_SSO_LOGIN_URL=http://sso.trade.great.dev:8004/accounts/login/; \
	export DIRECTORY_UI_BUYER_SSO_LOGOUT_URL=http://sso.trade.great.dev:8004/accounts/logout/?next=http://ui.trade.great.dev:8001; \
	export DIRECTORY_UI_BUYER_SSO_SIGNUP_URL=http://sso.trade.great.dev:8004/accounts/signup/; \
	export DIRECTORY_UI_BUYER_SSO_PROFILE_URL=http://profile.trade.great.dev:8006; \
	export DIRECTORY_UI_BUYER_SSO_REDIRECT_FIELD_NAME=next; \
	export DIRECTORY_UI_BUYER_SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export DIRECTORY_UI_BUYER_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_UI_BUYER_PORT=8001; \
	export DIRECTORY_UI_BUYER_SECRET_KEY=debug; \
	export DIRECTORY_UI_BUYER_DEBUG=true; \
	export DIRECTORY_UI_BUYER_COMPANIES_HOUSE_API_KEY=debug; \
	export DIRECTORY_UI_BUYER_FEATURE_PUBLIC_PROFILES_ENABLED=true; \
	export DIRECTORY_UI_BUYER_SUPPLIER_CASE_STUDY_URL=http://supplier.trade.great.dev:8005/case-study/{id}; \
	export DIRECTORY_UI_BUYER_SUPPLIER_PROFILE_LIST_URL=http://supplier.trade.great.dev:8005/suppliers?sectors={sectors}; \
	export DIRECTORY_UI_BUYER_SUPPLIER_PROFILE_URL=http://supplier.trade.great.dev:8005/suppliers/{number}; \
	export DIRECTORY_UI_BUYER_GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export DIRECTORY_UI_BUYER_GOOGLE_TAG_MANAGER_ENV=&gtm_auth=kH9XolShYWhOJg8TA9bW_A&gtm_preview=env-32&gtm_cookies_win=x; \
	export DIRECTORY_UI_BUYER_UTM_COOKIE_DOMAIN=.great.dev; \
	export DIRECTORY_UI_BUYER_DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET=debug; \
	export DIRECTORY_UI_BUYER_CORS_ORIGIN_ALLOW_ALL=true; \
	export DIRECTORY_UI_BUYER_SUPPLIER_SEARCH_URL=http://supplier.trade.great.dev:8005/search

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep directoryui_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it directoryui_webserver_1 sh

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

docker_build:
	docker build -t ukti/directory-ui-buyer:latest .

DEBUG_SET_ENV_VARS := \
	export PORT=8001; \
	export SECRET_KEY=debug; \
	export DEBUG=true ;\
	export API_SIGNATURE_SECRET=debug; \
	export API_CLIENT_BASE_URL=http://api.trade.great.dev:8000; \
	export SSO_SIGNATURE_SECRET=proxy_signature_debug; \
	export SSO_API_CLIENT_BASE_URL=http://sso.trade.great.dev:8004/api/v1/; \
	export SSO_LOGIN_URL=http://sso.trade.great.dev:8004/accounts/login/; \
	export SSO_LOGOUT_URL=http://sso.trade.great.dev:8004/accounts/logout/?next=http://ui.trade.great.dev:8001; \
	export SSO_SIGNUP_URL=http://sso.trade.great.dev:8004/accounts/signup/; \
	export SSO_PROFILE_URL=http://profile.trade.great.dev:8006; \
	export SSO_REDIRECT_FIELD_NAME=next; \
	export SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export SESSION_COOKIE_SECURE=false; \
	export COMPANIES_HOUSE_API_KEY=debug; \
	export FEATURE_PUBLIC_PROFILES_ENABLED=true; \
	export SUPPLIER_CASE_STUDY_URL=http://supplier.trade.great.dev:8005/case-study/{id}; \
	export SUPPLIER_PROFILE_LIST_URL=http://supplier.trade.great.dev:8005/suppliers?sectors={sectors}; \
	export SUPPLIER_PROFILE_URL=http://supplier.trade.great.dev:8005/suppliers/{number}; \
	export GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export GOOGLE_TAG_MANAGER_ENV=&gtm_auth=kH9XolShYWhOJg8TA9bW_A&gtm_preview=env-32&gtm_cookies_win=x; \
	export UTM_COOKIE_DOMAIN=.great.dev; \
	export DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET=debug; \
	export CORS_ORIGIN_ALLOW_ALL=true; \
	export SUPPLIER_SEARCH_URL=http://supplier.trade.great.dev:8005/search


debug_webserver:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_WEBSERVER)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) --cov-report=html

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

debug: test_requirements debug_test

heroku_deploy_dev:
	docker build -t registry.heroku.com/directory-ui-buyer-dev/web .
	docker push registry.heroku.com/directory-ui-buyer-dev/web

smoke_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_smoke_test

.PHONY: build clean test_requirements docker_run docker_debug docker_webserver_bash docker_test debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
