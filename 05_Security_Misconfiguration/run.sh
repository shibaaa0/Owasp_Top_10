#!/bin/sh
docker build -t owasp5 .                          
docker run --rm -p 8000:8000 owasp5
