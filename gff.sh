#!/bin/bash

curl -X 'GET' \
  "http://127.0.0.1:8000/jobs/$1/prods/gff" \
  -H 'accept: text/plain' -s
