# directory-ui-buyer

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![snyk-image]][snyk]

**[Export Directory UI](https://find-a-buyer.export.great.gov.uk/)**

**Find A Buyer (FAB) - the Department for International Trade (DIT) service for exposing motivated British exporters to international buyers seeking British goods and service.**

---
### See also:
| [directory-api](https://github.com/uktrade/directory-api) | [directory-ui-buyer](https://github.com/uktrade/directory-ui-buyer) | [directory-ui-supplier](https://github.com/uktrade/directory-ui-supplier) | [directory-ui-export-readiness](https://github.com/uktrade/directory-ui-export-readiness) |
| --- | --- | --- | --- |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | **[directory-sso-profile](https://github.com/uktrade/directory-sso-profile)** |  |

For more information on installation please check the [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)

## Development

The back-end framework is Django 1.9. The front-end uses minimal Javascript. The motivation for this is for accessibility reasons, to reduce technical complexity, and reduce cross-browser compatibility issues. Therefore most front-end work will be HTML and SASS/CSS development.

We aim to follow [GDS service standards](https://www.gov.uk/service-manual/service-standard) and [GDS design principles](https://www.gov.uk/design-principles).

### Dependencies

Some views allow creating and updating a company. Therefore FAB has a dependency on the following services:

| Service | Location  | Notes |
| ------------- | ------------- | ------------- |
| **[directory-api](https://github.com/uktrade/directory-api)** | http://api.trade.great:8000 | See instructions below under 'SSO' |
| **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | http://sso.trade.great:8004 | See instructions below under 'SSO' |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | http://localhost:8003 | Requests must go through `directory-sso-proxy`. |

**[directory-sso](https://github.com/uktrade/directory-sso)** is required for user authentication and sign up.
**[directory-api](https://github.com/uktrade/directory-api)** is required for creating companies.

The user will need to sign up/register on SSO to create a company on FAB.

Follow the **data loading** instructions on **[directory-sso](https://github.com/uktrade/directory-sso)** and then **[directory-api](https://github.com/uktrade/directory-api)** to create a dummy user and a dummy company for use in development.


## Requirements
[Python 3.5](https://www.python.org/downloads/release/python-352/)

### Docker
The production environment uses Docker containerization technology. To use this technology in your local development environment you will also need the following dependencies:

[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

### SASS
We use SASS CSS pre-compiler. If you're doing front-end work your local machine will also need the following dependencies:

[node](https://nodejs.org/en/download/)

## Running locally with Docker
This requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker

    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
``.env`` files will be automatically created (with ``env_writer.py`` based on ``env.json``) by ``make docker_test``, based on host environment variables with ``DIRECTORY_UI_BUYER_`` prefix.

## Running locally without Docker

### Installing
    $ git clone https://github.com/uktrade/directory-ui-buyer
    $ cd directory-ui-buyer
    $ virtualenv .venv -p python3.5
    $ source .venv/bin/activate
    $ pip install -r requirements_text.txt

### Running the webserver
	$ source .venv/bin/activate
    $ make debug_webserver

### Running the tests

    $ make debug_test

### CSS development

If you're doing front-end development work you will need to be able to compile the SASS to CSS. For this you need:

```bash
npm install
gulp
```

We add compiled CSS files to version control. This will sometimes result in conflicts if multiple developers are working on the same SASS files. However, by adding the compiled CSS to version control we avoid having to install node, npm, node-sass, etc to non-development machines.

You should not edit CSS files directly, instead edit their SCSS counterparts.

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.


## SSO
To make sso work locally add the following to your machine's `/etc/hosts`:

| IP Adress | URL                      |
| --------  | ------------------------ |
| 127.0.0.1 | buyer.trade.great    |
| 127.0.0.1 | supplier.trade.great |
| 127.0.0.1 | sso.trade.great      |
| 127.0.0.1 | api.trade.great      |
| 127.0.0.1 | profile.trade.great  |
| 127.0.0.1 | exred.trade.great    |

Then log into `directory-sso` via `sso.trade.great:8004`, and use `directory-ui-buyer` on `buyer.trade.great:8001`

Note in production, the `directory-sso` session cookie is shared with all subdomains that are on the same parent domain as `directory-sso`. However in development we cannot share cookies between subdomains using `localhost` - that would be like trying to set a cookie for `.com`, which is not supported by any RFC.

Therefore to make cookie sharing work in development we need the apps to be running on subdomains. Some stipulations:
 - `directory-ui-buyer` and `directory-sso` must both be running on sibling subdomains (with same parent domain)
 - `directory-sso` must be told to target cookies at the parent domain.

[code-climate-image]: https://codeclimate.com/github/uktrade/directory-ui-buyer/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-ui-buyer

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-ui-buyer/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-ui-buyer/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-ui-buyer/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-ui-buyer

[snyk-image]: https://snyk.io/test/github/uktrade/directory-ui-buyer/badge.svg
[snyk]: https://snyk.io/test/github/uktrade/directory-ui-buyer
