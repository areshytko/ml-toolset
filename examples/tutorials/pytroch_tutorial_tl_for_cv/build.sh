#!/usr/bin/env bash

VERSION=0.1

docker build -t areshytko/vygo:$VERSION .
docker push areshytko/vygo:$VERSION
