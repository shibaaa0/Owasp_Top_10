#!/bin/sh
docker build -t owasp3 .                          
docker run --rm -p 8000:8000 owasp3
