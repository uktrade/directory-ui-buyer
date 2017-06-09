#!/bin/bash -xe

pip install -r requirements_test.txt --src /usr/local/src
make test
if [ "$CODECOV_REPO_TOKEN" != "" ]
then
   codecov --token=$CODECOV_REPO_TOKEN
fi
