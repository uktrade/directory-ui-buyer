# directory-ui
[Export Directory UI](https://www.directory.exportingisgreat.gov.uk/)

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/directory-ui/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/directory-ui/tree/master)

## Requirements

### Docker
[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)


## Local installation

    $ git clone https://github.com/uktrade/directory-ui
    $ cd directory-ui
    $ make

## Running with Docker
Requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker

    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
``.env`` files will be automatically created (with ``env_writer.py`` based on ``env.json``) by ``make docker_test``, based on host environment variables with ``DIRECTORY_UI_`` prefix.

#### Web server
| Host environment variable | Docker environment variable  |
| ------------- | ------------- |
| DIRECTORY_UI_SECRET_KEY | SECRET_KEY |
| DIRECTORY_UI_PORT | PORT |
| DIRECTORY_UI_API_CLIENT_KEY | API_CLIENT_KEY |
| DIRECTORY_UI_API_CLIENT_BASE_URL | API_CLIENT_BASE_URL |

## Debugging

### Setup debug environment
    
    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test

### CSS development

#### Requirements
[node](https://nodejs.org/en/download/)
[SASS](http://sass-lang.com/)

```bash
npm install
npm run sass-dev
```

#### Update CSS under version control

```bash
npm run sass-prod
```

#### Rebuild the CSS files when the scss file changes

```bash
npm run sass-watch
```

# Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.
