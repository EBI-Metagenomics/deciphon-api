#!/bin/bash

cp ~/code/deciphon/build/*.dcp .

for file in *.dcp; do
    curl -X 'POST' \
        "http://127.0.0.1:8000/dbs?filename=$file" \
        -H 'accept: application/json' \
        -d '' -s | jq
    echo
done
