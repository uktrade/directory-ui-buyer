# directory-ui-buyer

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

**[Find A Buyer](https://www.great.gov.uk/find-a-buyer/)**

**Find A Buyer (FAB) - the Department for International Trade (DIT) service for exposing motivated British exporters to international buyers seeking British goods and service.**

---

## Development

### Installing
    $ git clone https://github.com/uktrade/directory-ui-buyer
    $ cd directory-ui-buyer
    $ [install and activate virtual environment]
    $ pip install -r requirements_text.txt

### Requirements

[Python 3.9.5](https://www.python.org/downloads/release/)

[redis](https://redis.io/)

### Configuration.

Secrets such as API keys and environment specific configurations are placed in `conf/env/secrets-do-not-commit` - a file that is not added to version control. To create a template secrets file with dummy values run `make secrets`.

### Commands

| Command                       | Description |
| ----------------------------- | ------------|
| make clean                    | Delete pyc files |
| make pytest                   | Run all tests |
| make pytest test_foo.py       | Run all tests in file called test_foo.py |
| make pytest -- --last-failed` | Run the last tests to fail |
| make pytest -- -k foo         | Run the test called foo |
| make pytest -- <foo>          | Run arbitrary pytest command |
| make manage <foo>             | Run arbitrary management command |
| make webserver                | Run the development web server |
| make requirements             | Compile the requirements file |
| make install_requirements     | Installed the compile requirements file |
| make css                      | Compile scss to css |
| make secrets                  | Create your secret env var file |


### CSS development
If you're doing front-end development work you will need to be able to compile the SASS to CSS. For this you need:

    $ npm install yarn
    $ yarn install --production=false

We add compiled CSS files to version control. This will sometimes result in conflicts if multiple developers are working on the same SASS files. However, by adding the compiled CSS to version control we avoid having to install node, npm, node-sass, etc to non-development machines.

You should not edit CSS files directly, instead edit their SCSS counterparts.

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.

## Helpful links
* [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)
* [Gitflow branching](https://uktrade.atlassian.net/wiki/spaces/ED/pages/737182153/Gitflow+and+releases)
* [GDS service standards](https://www.gov.uk/service-manual/service-standard)
* [GDS design principles](https://www.gov.uk/design-principles)

## Related projects:
https://github.com/uktrade?q=directory
https://github.com/uktrade?q=great


[code-climate-image]: https://codeclimate.com/github/uktrade/directory-ui-buyer/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-ui-buyer

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-ui-buyer/tree/develop.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-ui-buyer/tree/develop

[codecov-image]: https://codecov.io/gh/uktrade/directory-ui-buyer/branch/develop/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-ui-buyer

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org

