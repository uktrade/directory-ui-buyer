build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules
PYTEST := pytest . -v --ignore=node_modules --cov=. --cov-config=.coveragerc --capture=no $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

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
	export DIRECTORY_UI_BUYER_API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export DIRECTORY_UI_BUYER_SSO_SIGNATURE_SECRET=api_signature_debug; \
	export DIRECTORY_UI_BUYER_SSO_API_CLIENT_BASE_URL=http://sso.trade.great:8003; \
	export DIRECTORY_UI_BUYER_SSO_PROXY_LOGIN_URL=http://sso.trade.great:8004/accounts/login/; \
	export DIRECTORY_UI_BUYER_SSO_PROXY_LOGOUT_URL=http://sso.trade.great:8004/accounts/logout/?next=http://buyer.trade.great:8001; \
	export DIRECTORY_UI_BUYER_SSO_PROXY_SIGNUP_URL=http://sso.trade.great:8004/accounts/signup/; \
	export DIRECTORY_UI_BUYER_SSO_PROFILE_URL=http://profile.trade.great:8006/find-a-buyer/; \
	export DIRECTORY_UI_BUYER_SSO_PROXY_REDIRECT_FIELD_NAME=next; \
	export DIRECTORY_UI_BUYER_SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export DIRECTORY_UI_BUYER_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_UI_BUYER_PORT=8001; \
	export DIRECTORY_UI_BUYER_SECRET_KEY=debug; \
	export DIRECTORY_UI_BUYER_DEBUG=true; \
	export DIRECTORY_UI_BUYER_COMPANIES_HOUSE_API_KEY=debug; \
	export DIRECTORY_UI_BUYER_SUPPLIER_CASE_STUDY_URL=http://supplier.trade.great:8005/case-study/{id}; \
	export DIRECTORY_UI_BUYER_SUPPLIER_PROFILE_LIST_URL=http://supplier.trade.great:8005/suppliers?sectors={sectors}; \
	export DIRECTORY_UI_BUYER_SUPPLIER_PROFILE_URL=http://supplier.trade.great:8005/suppliers/{number}; \
	export DIRECTORY_UI_BUYER_GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export DIRECTORY_UI_BUYER_GOOGLE_TAG_MANAGER_ENV=&gtm_auth=kH9XolShYWhOJg8TA9bW_A&gtm_preview=env-32&gtm_cookies_win=x; \
	export DIRECTORY_UI_BUYER_UTM_COOKIE_DOMAIN=.great; \
	export DIRECTORY_UI_BUYER_DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET=debug; \
	export DIRECTORY_UI_BUYER_CORS_ORIGIN_ALLOW_ALL=true; \
	export DIRECTORY_UI_BUYER_SUPPLIER_SEARCH_URL=http://supplier.trade.great:8005/search; \
	export DIRECTORY_UI_BUYER_COMPANIES_HOUSE_CLIENT_ID=debug-client-id; \
	export DIRECTORY_UI_BUYER_COMPANIES_HOUSE_CLIENT_SECRET=debug-client-secret; \
	export DIRECTORY_UI_BUYER_SECURE_HSTS_SECONDS=0; \
	export DIRECTORY_UI_BUYER_PYTHONWARNINGS=all; \
	export DIRECTORY_UI_BUYER_PYTHONDEBUG=true; \
	export DIRECTORY_UI_BUYER_EXPOSE_DIRECTORY_API=true; \
	export DIRECTORY_UI_BUYER_HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export DIRECTORY_UI_BUYER_HEADER_FOOTER_URLS_FAB=/; \
	export DIRECTORY_UI_BUYER_HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export DIRECTORY_UI_BUYER_HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export DIRECTORY_UI_BUYER_SECURE_SSL_REDIRECT=false; \
	export DIRECTORY_UI_BUYER_HEALTH_CHECK_TOKEN=debug; \
	export DIRECTORY_UI_BUYER_INTERNAL_CH_BASE_URL=http://test.com; \
	export DIRECTORY_UI_BUYER_INTERNAL_CH_API_KEY=debug

docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS)

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
	export DEBUG=true;\
	export API_SIGNATURE_SECRET=debug; \
	export API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export SSO_SIGNATURE_SECRET=api_signature_debug; \
	export SSO_API_CLIENT_BASE_URL=http://sso.trade.great:8003/; \
	export SSO_PROXY_LOGIN_URL=http://sso.trade.great:8004/accounts/login/; \
	export SSO_PROXY_LOGOUT_URL=http://sso.trade.great:8004/accounts/logout/?next=http://buyer.trade.great:8001; \
	export SSO_PROXY_SIGNUP_URL=http://sso.trade.great:8004/accounts/signup/; \
	export SSO_PROFILE_URL=http://profile.trade.great:8006/find-a-buyer/; \
	export SSO_PROXY_REDIRECT_FIELD_NAME=next; \
	export SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export SESSION_COOKIE_SECURE=false; \
	export COMPANIES_HOUSE_API_KEY=$$DIRECTORY_UI_BUYER_COMPANIES_HOUSE_API_KEY; \
	export SUPPLIER_CASE_STUDY_URL=http://supplier.trade.great:8005/case-study/{id}; \
	export SUPPLIER_PROFILE_LIST_URL=http://supplier.trade.great:8005/suppliers?sectors={sectors}; \
	export SUPPLIER_PROFILE_URL=http://supplier.trade.great:8005/suppliers/{number}; \
	export GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export GOOGLE_TAG_MANAGER_ENV=&gtm_auth=kH9XolShYWhOJg8TA9bW_A&gtm_preview=env-32&gtm_cookies_win=x; \
	export UTM_COOKIE_DOMAIN=.great; \
	export DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET=debug; \
	export CORS_ORIGIN_ALLOW_ALL=true; \
	export SUPPLIER_SEARCH_URL=http://supplier.trade.great:8005/search; \
	export COMPANIES_HOUSE_CLIENT_ID=debug-client-id; \
	export COMPANIES_HOUSE_CLIENT_SECRET=debug-client-secret; \
	export SECURE_HSTS_SECONDS=0; \
	export PYTHONWARNINGS=all; \
	export PYTHONDEBUG=true; \
	export EXPOSE_DIRECTORY_API=true; \
	export HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export HEADER_FOOTER_URLS_FAB=/; \
	export HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export INTERNAL_CH_BASE_URL=http://test.com; \
	export INTERNAL_CH_API_KEY=debug

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
	./docker/install_heroku_cli.sh
	docker login --username=$$HEROKU_EMAIL --password=$$HEROKU_TOKEN registry.heroku.com
	~/bin/heroku-cli/bin/heroku container:push web --app directory-ui-buyer-dev
	~/bin/heroku-cli/bin/heroku container:release web --app directory-ui-buyer-dev

integration_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_integration_tests

compile_requirements:
	python3 -m piptools compile requirements.in

compile_test_requirements:
	python3 -m piptools compile requirements_test.in

compile_all_requirements: compile_requirements compile_test_requirements

.PHONY: build clean test_requirements docker_run docker_debug docker_webserver_bash docker_test debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
