#!/bin/bash

curl -X 'GET' \
  "http://127.0.0.1:8000/jobs/$1/prods" \
  -H 'accept: application/json'
