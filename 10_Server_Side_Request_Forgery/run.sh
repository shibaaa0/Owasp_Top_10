#!/bin/sh
docker build -t owasp10 .                          
docker run --rm -p 8000:8000 owasp10
