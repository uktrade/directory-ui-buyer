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

DEBUG_SET_ENV_VARS := \
	export PORT=8001; \
	export SECRET_KEY=debug; \
	export DEBUG=true;\
	export DIRECTORY_API_CLIENT_API_KEY=debug; \
	export DIRECTORY_API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export DIRECTORY_SSO_API_CLIENT_API_KEY=api_signature_debug; \
	export DIRECTORY_SSO_API_CLIENT_BASE_URL=http://sso.trade.great:8003/; \
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
	export UTM_COOKIE_DOMAIN=.trade.great; \
	export DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET=debug; \
	export CORS_ORIGIN_ALLOW_ALL=true; \
	export SUPPLIER_SEARCH_URL=http://supplier.trade.great:8005/search; \
	export COMPANIES_HOUSE_CLIENT_ID=debug-client-id; \
	export COMPANIES_HOUSE_CLIENT_SECRET=debug-client-secret; \
	export SECURE_HSTS_SECONDS=0; \
	export EXPOSE_DIRECTORY_API=true; \
	export HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export HEADER_FOOTER_URLS_FAB=/; \
	export HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export DIRECTORY_CH_SEARCH_CLIENT_BASE_URL=http://test.com; \
	export DIRECTORY_CH_SEARCH_CLIENT_API_KEY=debug; \
	export PRIVACY_COOKIE_DOMAIN=.trade.great


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

compile_requirements:
	python3 -m piptools compile requirements.in
	python3 -m piptools compile requirements_test.in

.PHONY: build clean test_requirements debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
