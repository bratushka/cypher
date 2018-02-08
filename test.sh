#!/usr/bin/env bash
docker exec -it cypher nosetests --with-coverage --nocapture
