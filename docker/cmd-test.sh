#!/bin/bash -xe

pip install -r requirements_test.txt --src /usr/local/src
make test
if [ "$COVERALLS_REPO_TOKEN" != "" ]
then
   coveralls
fi
