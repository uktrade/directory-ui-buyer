# directory-api
[Export Directory registration form](https://www.directory.exportingisgreat.gov.uk/)

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/directory-ui/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/directory-ui/tree/master)

## Requirements

### Docker
[Docker >= 1.10](https://docs.docker.com/engine/installation/) 
[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

### SASS
[node](https://nodejs.org/en/download/)
[SASS](http://sass-lang.com/)

## Local installation

    $ git clone https://github.com/uktrade/directory-ui
    $ cd directory-ui
    $ make

## Running
Requires all host environment variables to be set.

    $ make run

## Running for local development

    $ make run_debug

### CSS development when running outside of docker

To enable easy development, you can have sass watch the scss file for changes.

```bash
npm run sass-watch
```

This will cause sass to rebuld the css files when the scss file changes.

## Running tests

    $ make run_test

## Host environment variables for docker-compose
``.env`` files will be automatically created (with ``env_writer.py`` based on ``env.json``) by ``make run_test``, based on host environment variables with ``DIRECTORY_UI_`` prefix.

### Web server and queue worker
| Host environment variable | Docker environment variable  |
| ------------- | ------------- |
| DIRECTORY_UI_SECRET_KEY | SECRET_KEY |
| DIRECTORY_UI_PORT | PORT |


# Session

We use signed cookies as the session backend. The reason for this is to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.
